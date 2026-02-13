"""
날씨 기반 식단 추천 서비스
- Open-Meteo API로 7일 예보 조회 (무료, API키 불필요)
- 기온/날씨/계절 기반 음식 태그 가중치 산출
"""
import httpx
from datetime import date, timedelta
from functools import lru_cache
import time
import logging

logger = logging.getLogger(__name__)

# ═══ Open-Meteo API (서울 기본) ═══════════════════════
SEOUL_LAT = 37.5665
SEOUL_LON = 126.9780

# WMO Weather interpretation codes
WMO_CODES = {
    0: ("맑음", "☀️"), 1: ("대체로 맑음", "🌤️"), 2: ("부분 흐림", "⛅"),
    3: ("흐림", "☁️"), 45: ("안개", "🌫️"), 48: ("안개", "🌫️"),
    51: ("이슬비", "🌦️"), 53: ("이슬비", "🌦️"), 55: ("이슬비", "🌦️"),
    61: ("비", "🌧️"), 63: ("비", "🌧️"), 65: ("폭우", "🌧️"),
    66: ("진눈깨비", "🌨️"), 67: ("진눈깨비", "🌨️"),
    71: ("눈", "🌨️"), 73: ("눈", "❄️"), 75: ("폭설", "❄️"),
    77: ("싸라기눈", "🌨️"), 80: ("소나기", "🌦️"), 81: ("소나기", "🌦️"),
    82: ("폭우", "⛈️"), 85: ("눈", "🌨️"), 86: ("폭설", "❄️"),
    95: ("뇌우", "⛈️"), 96: ("우박", "⛈️"), 99: ("우박", "⛈️"),
}

# ═══ 날씨 → 음식 태그 매핑 ═══════════════════════════

# 기온 기반 선호 태그 (점수 보너스)
COLD_TAGS = {"국", "탕", "찌개", "국물요리", "죽", "수프", "보양식", "조림"}
COOL_TAGS = {"국", "찌개", "국물요리", "죽", "조림", "볶음", "탕"}
WARM_TAGS = {"무침", "비빔밥", "샐러드", "나물", "볶음밥", "덮밥"}
HOT_TAGS = {"면", "냉면", "비빔밥", "샐러드", "무침", "나물"}

# 날씨 조건 기반 선호 태그
RAIN_TAGS = {"전", "칼국수", "수제비", "면", "분식", "국물요리", "찌개"}
SNOW_TAGS = {"국", "탕", "찌개", "국물요리", "죽", "보양식"}

# 계절 기반 선호 태그
SPRING_TAGS = {"나물", "무침", "비빔밥", "국"}    # 3~5월
SUMMER_TAGS = {"면", "냉면", "비빔밥", "샐러드", "무침"}  # 6~8월
AUTUMN_TAGS = {"볶음", "조림", "구이", "탕", "찌개"}       # 9~11월
WINTER_TAGS = {"국", "탕", "찌개", "국물요리", "죽", "전", "보양식"}  # 12~2월


def _get_season_tags(d: date) -> set:
    """월 기준 계절 태그"""
    month = d.month
    if month in (3, 4, 5):
        return SPRING_TAGS
    elif month in (6, 7, 8):
        return SUMMER_TAGS
    elif month in (9, 10, 11):
        return AUTUMN_TAGS
    else:
        return WINTER_TAGS


def _get_temperature_tags(temp_max: float) -> tuple[set, str]:
    """기온 기반 선호 태그 + 체감 설명"""
    if temp_max <= 0:
        return COLD_TAGS, "매우 추움"
    elif temp_max <= 10:
        return COOL_TAGS, "쌀쌀"
    elif temp_max <= 20:
        return set(), "선선"  # 중립 - 보너스 없음
    elif temp_max <= 27:
        return WARM_TAGS, "따뜻"
    else:
        return HOT_TAGS, "더움"


def _is_rainy(weather_code: int) -> bool:
    return weather_code in (51, 53, 55, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99)


def _is_snowy(weather_code: int) -> bool:
    return weather_code in (71, 73, 75, 77, 85, 86)


# ═══ 날씨 데이터 캐싱 (1시간) ═══════════════════════
_weather_cache = {}
_cache_time = 0
CACHE_TTL = 3600  # 1시간


def fetch_weekly_weather(lat: float = SEOUL_LAT, lon: float = SEOUL_LON) -> list[dict]:
    """
    Open-Meteo API로 7일 날씨 예보 조회
    Returns: [{"date": "2026-02-13", "temp_max": 5.2, "temp_min": -3.1,
               "weather_code": 3, "weather_desc": "흐림", "weather_icon": "☁️",
               "precipitation_prob": 20}, ...]
    """
    global _weather_cache, _cache_time

    cache_key = f"{lat},{lon}"
    now = time.time()
    if cache_key in _weather_cache and (now - _cache_time) < CACHE_TTL:
        return _weather_cache[cache_key]

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
            "timezone": "Asia/Seoul",
            "forecast_days": 7,
        }
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temp_maxs = daily.get("temperature_2m_max", [])
        temp_mins = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        precip_probs = daily.get("precipitation_probability_max", [])

        result = []
        for i, d in enumerate(dates):
            code = codes[i] if i < len(codes) else 0
            desc, icon = WMO_CODES.get(code, ("알 수 없음", "❓"))
            result.append({
                "date": d,
                "temp_max": temp_maxs[i] if i < len(temp_maxs) else None,
                "temp_min": temp_mins[i] if i < len(temp_mins) else None,
                "weather_code": code,
                "weather_desc": desc,
                "weather_icon": icon,
                "precipitation_prob": precip_probs[i] if i < len(precip_probs) else 0,
            })

        _weather_cache[cache_key] = result
        _cache_time = now
        logger.info(f"날씨 데이터 조회 성공: {len(result)}일")
        return result

    except Exception as e:
        logger.warning(f"날씨 API 조회 실패: {e}")
        # 실패 시 빈 리스트 반환 (날씨 없이 기존 로직으로 동작)
        return []


def get_weather_for_date(weather_data: list[dict], target_date: date) -> dict | None:
    """특정 날짜의 날씨 데이터 반환"""
    target_str = target_date.isoformat()
    for w in weather_data:
        if w["date"] == target_str:
            return w
    return None


def calculate_weather_score(recipe_tags: set, weather: dict | None, target_date: date) -> float:
    """
    날씨/계절 기반 레시피 적합도 점수 계산
    - 음수 = 적합 (낮을수록 좋음, 기존 scoring과 동일 방향)
    - 0 = 중립
    - 양수 = 부적합
    """
    score = 0.0

    # 1) 계절 보너스
    season_tags = _get_season_tags(target_date)
    season_overlap = recipe_tags & season_tags
    if season_overlap:
        score -= len(season_overlap) * 8  # 계절 매칭 보너스

    if weather is None:
        return score

    temp_max = weather.get("temp_max")
    weather_code = weather.get("weather_code", 0)

    # 2) 기온 보너스
    if temp_max is not None:
        temp_tags, _ = _get_temperature_tags(temp_max)
        temp_overlap = recipe_tags & temp_tags
        if temp_overlap:
            score -= len(temp_overlap) * 12  # 기온 매칭 보너스 (더 강하게)

        # 기온 역매칭 페널티 (더운 날 뜨거운 국 등)
        if temp_max >= 28 and (recipe_tags & COLD_TAGS):
            score += 15  # 더운 날 뜨거운 음식 감점
        if temp_max <= 5 and (recipe_tags & HOT_TAGS - {"면"}):
            score += 10  # 추운 날 차가운 음식 감점

    # 3) 비/눈 보너스
    if _is_rainy(weather_code):
        rain_overlap = recipe_tags & RAIN_TAGS
        if rain_overlap:
            score -= len(rain_overlap) * 15  # 비오는 날 전/칼국수 강력 보너스

    if _is_snowy(weather_code):
        snow_overlap = recipe_tags & SNOW_TAGS
        if snow_overlap:
            score -= len(snow_overlap) * 12

    return score


def get_weather_summary_for_menu(week_start: date) -> list[dict]:
    """
    주간 식단용 날씨 요약 데이터 반환
    프론트엔드에서 표시할 수 있는 형태
    """
    weather_data = fetch_weekly_weather()
    result = []

    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)
        weather = get_weather_for_date(weather_data, current_date)

        if weather:
            temp_max = weather.get("temp_max")
            _, temp_feel = _get_temperature_tags(temp_max) if temp_max else (set(), "")

            # 음식 추천 힌트
            hints = []
            if _is_rainy(weather.get("weather_code", 0)):
                hints.append("전·칼국수가 딱!")
            elif _is_snowy(weather.get("weather_code", 0)):
                hints.append("따뜻한 국물요리 추천")
            elif temp_max is not None:
                if temp_max <= 0:
                    hints.append("뜨끈한 탕·찌개 추천")
                elif temp_max <= 10:
                    hints.append("따뜻한 국물요리 추천")
                elif temp_max >= 28:
                    hints.append("시원한 면·비빔밥 추천")

            result.append({
                "date": current_date.isoformat(),
                "temp_max": weather["temp_max"],
                "temp_min": weather["temp_min"],
                "weather_desc": weather["weather_desc"],
                "weather_icon": weather["weather_icon"],
                "precipitation_prob": weather["precipitation_prob"],
                "temp_feel": temp_feel,
                "food_hint": hints[0] if hints else "",
            })
        else:
            # 예보 범위 밖 (과거 또는 7일 초과)
            season_tags = _get_season_tags(current_date)
            month = current_date.month
            if month in (12, 1, 2):
                default_desc, default_icon = "겨울", "❄️"
            elif month in (6, 7, 8):
                default_desc, default_icon = "여름", "☀️"
            elif month in (3, 4, 5):
                default_desc, default_icon = "봄", "🌸"
            else:
                default_desc, default_icon = "가을", "🍂"

            result.append({
                "date": current_date.isoformat(),
                "temp_max": None,
                "temp_min": None,
                "weather_desc": default_desc,
                "weather_icon": default_icon,
                "precipitation_prob": None,
                "temp_feel": "",
                "food_hint": "",
            })

    return result
