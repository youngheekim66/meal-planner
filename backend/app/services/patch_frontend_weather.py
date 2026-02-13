# -*- coding: utf-8 -*-
"""
프론트엔드 index.html에 날씨 기능 추가 패치
- 날씨 CSS 스타일 추가
- 날씨 API 호출 함수 추가
- renderMenu에 날씨 표시 통합
"""
import re

HTML_PATH = r"backend\static\index.html"

def patch():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # ═══ 1) CSS 추가 (</style> 앞에 삽입) ═══
    weather_css = """
/* Weather Display */
.weather-bar { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); border-radius: 10px; margin-bottom: 8px; font-size: 13px; }
.weather-bar.rain { background: linear-gradient(135deg, #E8EAF6 0%, #C5CAE9 100%); }
.weather-bar.snow { background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%); }
.weather-bar.hot { background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); }
.weather-bar.cold { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); }
.weather-icon { font-size: 22px; }
.weather-temp { font-weight: 700; color: #1565C0; }
.weather-desc { color: #555; }
.weather-hint { font-size: 11px; color: #E65100; font-weight: 600; margin-left: auto; }
.weather-bar.rain .weather-hint { color: #283593; }
.weather-bar.snow .weather-hint { color: #6A1B9A; }
"""
    html = html.replace("</style>", weather_css + "</style>")

    # ═══ 2) JavaScript: 날씨 변수 + loadWeather 함수 추가 ═══
    # weekOffset 선언 뒤에 날씨 변수 추가
    html = html.replace(
        "var weekOffset = 0;",
        "var weekOffset = 0;\nvar weeklyWeather = {};"
    )

    # ═══ 3) generateMenu 함수 수정 - 날씨 데이터 함께 로드 ═══
    old_generate = """async function generateMenu() {
  var content = document.getElementById('menuContent');
  content.innerHTML = '<div class="loading">식단을 생성하고 있습니다...</div>';
  try {
    var res = await fetch(API + '/api/menu/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: user.id, week_start: getWeekStart() }) });
    var data = await res.json(); if (!res.ok) throw new Error(data.detail || 'Error');
    currentMenuId = data.id; renderMenu(data); showToast('식단이 생성되었습니다!');
  } catch (e) { content.innerHTML = '<div class="empty"><div class="icon">⚠️</div><p>식단 생성 실패<br>' + e.message + '</p></div>'; }
}"""

    # 인코딩 문제로 실제 파일에서 찾을 수 없을 수 있으므로 패턴 매칭
    # generateMenu 함수를 정규식으로 찾아 교체
    new_generate = """async function generateMenu() {
  var content = document.getElementById('menuContent');
  content.innerHTML = '<div class="loading">날씨를 확인하고 식단을 생성 중...</div>';
  try {
    // 날씨 데이터 먼저 로드
    await loadWeather();
    var res = await fetch(API + '/api/menu/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: user.id, week_start: getWeekStart() }) });
    var data = await res.json(); if (!res.ok) throw new Error(data.detail || 'Error');
    currentMenuId = data.id; renderMenu(data); showToast('날씨 맞춤 식단이 생성되었습니다! 🌤️');
  } catch (e) { content.innerHTML = '<div class="empty"><div class="icon">⚠️</div><p>식단 생성 실패<br>' + e.message + '</p></div>'; }
}"""

    # generateMenu 함수 교체 (정규식으로)
    pattern = r'async function generateMenu\(\)\s*\{.*?content\.innerHTML = .*?생성.*?실패.*?\}\s*\}'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        html = html[:match.start()] + new_generate + html[match.end():]
        print("  ✅ generateMenu 함수 교체 완료")
    else:
        print("  ⚠️ generateMenu 함수를 찾을 수 없어 끝에 추가합니다")

    # ═══ 4) renderMenu 함수 수정 - 날씨 바 추가 ═══
    # renderMenu 내부의 day-section 생성 부분 수정
    # 기존: html += '<div class="day-section"><div class="day-title">' + dateStr + '</div><div class="card">';
    # 변경: 날씨 바 추가

    old_day_section = """html += '<div class="day-section"><div class="day-title">' + dateStr + '</div><div class="card">';"""
    new_day_section = """var weatherBar = getWeatherBar(date);
    html += '<div class="day-section"><div class="day-title">' + dateStr + '</div>' + weatherBar + '<div class="card">';"""

    if old_day_section in html:
        html = html.replace(old_day_section, new_day_section)
        print("  ✅ renderMenu 날씨바 삽입 완료")
    else:
        print("  ⚠️ renderMenu day-section 패턴 미발견 - 수동 확인 필요")

    # ═══ 5) 새 함수들 추가 (showToast 함수 앞에) ═══
    new_functions = """
// ★ 날씨 관련 함수들
async function loadWeather() {
  try {
    var res = await fetch(API + '/api/weather/weekly?week_start=' + getWeekStart());
    var data = await res.json();
    weeklyWeather = {};
    if (data.weather) {
      data.weather.forEach(function(w) { weeklyWeather[w.date] = w; });
    }
  } catch (e) { console.log('날씨 로드 실패:', e); weeklyWeather = {}; }
}

function getWeatherBar(dateStr) {
  var w = weeklyWeather[dateStr];
  if (!w || w.temp_max === null) return '';
  var cls = 'weather-bar';
  var code = w.weather_desc || '';
  if (code.indexOf('비') >= 0 || code.indexOf('소나기') >= 0) cls += ' rain';
  else if (code.indexOf('눈') >= 0) cls += ' snow';
  else if (w.temp_max >= 28) cls += ' hot';
  else if (w.temp_max <= 5) cls += ' cold';
  var tempStr = Math.round(w.temp_min) + '°/' + Math.round(w.temp_max) + '°';
  var hint = w.food_hint ? '<span class="weather-hint">' + w.food_hint + '</span>' : '';
  var precip = w.precipitation_prob > 30 ? ' 💧' + w.precipitation_prob + '%' : '';
  return '<div class="' + cls + '">' +
    '<span class="weather-icon">' + w.weather_icon + '</span>' +
    '<span class="weather-temp">' + tempStr + '</span>' +
    '<span class="weather-desc">' + w.weather_desc + precip + '</span>' +
    hint + '</div>';
}

"""

    html = html.replace("function showToast(", new_functions + "function showToast(")
    print("  ✅ 날씨 함수 추가 완료")

    # ═══ 6) 버전 업데이트 ═══
    html = html.replace("v1.3.0", "v1.4.0")
    html = html.replace("v1.2.0", "v1.4.0")

    # ═══ 저장 ═══
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("\n🎉 프론트엔드 패치 완료! (v1.4.0 - 날씨 기반 식단)")


if __name__ == "__main__":
    patch()
