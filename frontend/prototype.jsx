import { useState, useEffect } from "react";

// ─── 시드 데이터 (API 응답 시뮬레이션) ──────────
const WEEKLY_MENU = {
  "2026-02-09": {
    day: "월", meals: {
      BREAKFAST: { id: 1, title: "토스트 + 우유", cuisine: "FREE", kcal: 281, time: 5, diff: 1, steps: ["식빵을 토스터에 굽는다", "우유와 함께 낸다"], ingredients: [{ name: "빵", qty: "60g" }, { name: "우유", qty: "200ml" }] },
      LUNCH: { id: 2, title: "닭볶음탕", cuisine: "KOREAN", kcal: 245, time: 40, diff: 2, steps: ["닭고기를 끓는 물에 데친다", "양념장(고추장+간장+고춧가루)에 감자, 당근과 함께 졸인다"], ingredients: [{ name: "닭고기", qty: "300g" }, { name: "감자", qty: "150g" }, { name: "당근", qty: "80g" }, { name: "양파", qty: "100g" }] },
      DINNER: { id: 3, title: "콩나물국", cuisine: "KOREAN", kcal: 28, time: 15, diff: 1, steps: ["물을 끓여 콩나물을 넣는다", "대파, 마늘을 넣고 간장으로 간을 한다"], ingredients: [{ name: "콩나물", qty: "150g" }, { name: "대파", qty: "20g" }] }
    }
  },
  "2026-02-10": {
    day: "화", isToday: true, meals: {
      BREAKFAST: { id: 4, title: "누룽지", cuisine: "KOREAN", kcal: 149, time: 10, diff: 1, steps: ["누룽지에 물을 넣고 끓인다"], ingredients: [{ name: "쌀", qty: "100g" }] },
      LUNCH: { id: 5, title: "김치찌개", cuisine: "KOREAN", kcal: 210, time: 25, diff: 2, steps: ["돼지고기를 볶는다", "김치, 물을 넣고 끓인다", "두부, 대파를 넣어 완성"], ingredients: [{ name: "돼지고기", qty: "150g" }, { name: "배추김치", qty: "200g" }, { name: "두부", qty: "150g" }, { name: "대파", qty: "30g" }] },
      DINNER: { id: 6, title: "잡채", cuisine: "KOREAN", kcal: 202, time: 30, diff: 2, steps: ["당면을 삶아 물기를 뺀다", "채소를 각각 볶는다", "모두 섞어 간장+참기름으로 버무린다"], ingredients: [{ name: "당면", qty: "100g" }, { name: "시금치", qty: "50g" }, { name: "당근", qty: "50g" }, { name: "양파", qty: "80g" }, { name: "버섯", qty: "50g" }] }
    }
  },
  "2026-02-11": {
    day: "수", meals: {
      BREAKFAST: { id: 7, title: "시금치 된장국 + 밥", cuisine: "KOREAN", kcal: 366, time: 15, diff: 1, steps: ["멸치육수에 된장을 풀어 끓인다", "시금치, 두부를 넣어 완성"], ingredients: [{ name: "시금치", qty: "50g" }, { name: "된장", qty: "15g" }, { name: "두부", qty: "50g" }, { name: "쌀", qty: "200g" }] },
      LUNCH: { id: 8, title: "두부 조림", cuisine: "KOREAN", kcal: 130, time: 15, diff: 1, steps: ["두부를 팬에 노릇하게 굽는다", "간장 양념을 끼얹고 조린다"], ingredients: [{ name: "두부", qty: "300g" }, { name: "간장", qty: "30ml" }, { name: "대파", qty: "20g" }] },
      DINNER: { id: 9, title: "소고기 무국", cuisine: "KOREAN", kcal: 116, time: 35, diff: 2, steps: ["소고기를 참기름에 볶는다", "무를 넣고 함께 볶다가 물을 넣는다", "간장으로 간을 맞추고 끓인다"], ingredients: [{ name: "소고기", qty: "100g" }, { name: "무", qty: "200g" }, { name: "대파", qty: "20g" }] }
    }
  },
  "2026-02-12": {
    day: "목", meals: {
      BREAKFAST: { id: 10, title: "달걀죽", cuisine: "KOREAN", kcal: 207, time: 15, diff: 1, steps: ["쌀을 물에 불린다", "냄비에 쌀과 물을 넣고 끓인다", "달걀을 넣고 저어 완성"], ingredients: [{ name: "쌀", qty: "80g" }, { name: "달걀", qty: "1개" }] },
      LUNCH: { id: 11, title: "제육볶음", cuisine: "KOREAN", kcal: 221, time: 20, diff: 2, steps: ["돼지고기에 고추장 양념을 버무린다", "양파, 대파와 함께 볶는다"], ingredients: [{ name: "돼지고기", qty: "200g" }, { name: "고추장", qty: "30g" }, { name: "양파", qty: "100g" }] },
      DINNER: { id: 12, title: "고등어 구이", cuisine: "KOREAN", kcal: 274, time: 20, diff: 1, steps: ["고등어에 소금을 뿌려 10분 둔다", "팬에 앞뒤로 굽는다"], ingredients: [{ name: "고등어", qty: "300g" }, { name: "소금", qty: "3g" }] }
    }
  },
  "2026-02-13": {
    day: "금", meals: {
      BREAKFAST: { id: 13, title: "콩나물국밥", cuisine: "KOREAN", kcal: 259, time: 15, diff: 1, steps: ["멸치육수를 끓인다", "콩나물, 대파를 넣고 끓인다", "밥을 넣어 완성"], ingredients: [{ name: "콩나물", qty: "100g" }, { name: "쌀", qty: "150g" }, { name: "대파", qty: "20g" }] },
      LUNCH: { id: 14, title: "감자조림", cuisine: "KOREAN", kcal: 137, time: 20, diff: 1, steps: ["감자를 깍둑 썰어 간장에 조린다", "국물이 자작해지면 참기름을 뿌린다"], ingredients: [{ name: "감자", qty: "300g" }, { name: "간장", qty: "30ml" }] },
      DINNER: { id: 15, title: "애호박 된장찌개", cuisine: "KOREAN", kcal: 70, time: 20, diff: 1, steps: ["멸치육수에 된장을 풀고 애호박, 두부를 넣는다", "끓으면 대파를 넣어 완성"], ingredients: [{ name: "애호박", qty: "150g" }, { name: "된장", qty: "25g" }, { name: "두부", qty: "100g" }] }
    }
  },
  "2026-02-14": {
    day: "토", meals: {
      BREAKFAST: { id: 16, title: "계란후라이 + 밥", cuisine: "KOREAN", kcal: 518, time: 10, diff: 1, steps: ["팬에 달걀을 프라이한다", "밥과 함께 낸다"], ingredients: [{ name: "달걀", qty: "2개" }, { name: "쌀", qty: "200g" }] },
      LUNCH: { id: 17, title: "새우볶음밥", cuisine: "FREE", kcal: 472, time: 15, diff: 2, steps: ["새우를 볶다가 달걀을 넣는다", "밥과 야채를 넣고 볶는다"], ingredients: [{ name: "새우", qty: "80g" }, { name: "쌀", qty: "200g" }, { name: "달걀", qty: "1개" }, { name: "양파", qty: "50g" }] },
      DINNER: { id: 18, title: "김치볶음밥", cuisine: "FREE", kcal: 457, time: 10, diff: 1, steps: ["김치를 잘게 썰어 볶는다", "밥을 넣고 함께 볶는다", "달걀프라이를 올린다"], ingredients: [{ name: "배추김치", qty: "150g" }, { name: "쌀", qty: "200g" }, { name: "달걀", qty: "1개" }] }
    }
  },
  "2026-02-15": {
    day: "일", meals: {
      BREAKFAST: { id: 19, title: "누룽지", cuisine: "KOREAN", kcal: 149, time: 10, diff: 1, steps: ["누룽지에 물을 넣고 끓인다"], ingredients: [{ name: "쌀", qty: "100g" }] },
      LUNCH: { id: 20, title: "소고기 미역국", cuisine: "KOREAN", kcal: 98, time: 40, diff: 2, steps: ["미역을 불린다", "소고기를 참기름에 볶는다", "물을 넣고 끓여 간장으로 간을 한다"], ingredients: [{ name: "소고기", qty: "100g" }, { name: "간장", qty: "15ml" }] },
      DINNER: { id: 21, title: "된장찌개", cuisine: "KOREAN", kcal: 116, time: 25, diff: 2, steps: ["멸치육수에 된장을 풀어 끓인다", "애호박, 두부, 감자를 넣는다", "대파, 고추를 넣어 완성"], ingredients: [{ name: "된장", qty: "30g" }, { name: "애호박", qty: "100g" }, { name: "두부", qty: "150g" }, { name: "감자", qty: "80g" }] }
    }
  }
};

const SHOPPING_LIST = [
  { id: 1, name: "쌀", qty: "1,330g", cat: "곡류", pantry: false, checked: false },
  { id: 2, name: "빵", qty: "60g", cat: "곡류", pantry: false, checked: false },
  { id: 3, name: "떡", qty: "300g", cat: "곡류", pantry: false, checked: false },
  { id: 4, name: "달걀", qty: "11개", cat: "기타", pantry: false, checked: false },
  { id: 5, name: "돼지고기", qty: "350g", cat: "육류", pantry: false, checked: false },
  { id: 6, name: "소고기", qty: "400g", cat: "육류", pantry: false, checked: false },
  { id: 7, name: "닭고기", qty: "300g", cat: "육류", pantry: false, checked: false },
  { id: 8, name: "고등어", qty: "300g", cat: "해산물", pantry: false, checked: false },
  { id: 9, name: "새우", qty: "80g", cat: "해산물", pantry: false, checked: false },
  { id: 10, name: "배추김치", qty: "350g", cat: "채소", pantry: false, checked: false },
  { id: 11, name: "두부", qty: "650g", cat: "채소", pantry: false, checked: false },
  { id: 12, name: "대파", qty: "175g", cat: "채소", pantry: false, checked: false },
  { id: 13, name: "양파", qty: "200g", cat: "채소", pantry: false, checked: false },
  { id: 14, name: "감자", qty: "530g", cat: "채소", pantry: false, checked: false },
  { id: 15, name: "콩나물", qty: "300g", cat: "채소", pantry: false, checked: false },
  { id: 16, name: "시금치", qty: "100g", cat: "채소", pantry: false, checked: false },
  { id: 17, name: "애호박", qty: "250g", cat: "채소", pantry: false, checked: false },
  { id: 18, name: "당근", qty: "130g", cat: "채소", pantry: false, checked: false },
  { id: 19, name: "무", qty: "200g", cat: "채소", pantry: false, checked: false },
  { id: 20, name: "간장", qty: "120ml", cat: "양념", pantry: true, checked: false },
  { id: 21, name: "된장", qty: "45g", cat: "양념", pantry: true, checked: false },
  { id: 22, name: "고추장", qty: "45g", cat: "양념", pantry: true, checked: false },
  { id: 23, name: "식용유", qty: "15ml", cat: "양념", pantry: true, checked: false },
  { id: 24, name: "소금", qty: "4g", cat: "양념", pantry: true, checked: false },
  { id: 25, name: "설탕", qty: "30g", cat: "양념", pantry: true, checked: false },
  { id: 26, name: "우유", qty: "200ml", cat: "유제품", pantry: false, checked: false },
];

const USER = { name: "홍길동", birthYear: 1960, sex: "F", height: 158, weight: 60, activity: 2, kcalTarget: 1508 };
const MEAL_LABELS = { BREAKFAST: { icon: "🌅", label: "아침" }, LUNCH: { icon: "☀️", label: "점심" }, DINNER: { icon: "🌙", label: "저녁" } };
const CAT_COLORS = { "채소": "#43A047", "육류": "#E53935", "해산물": "#1E88E5", "양념": "#FFA000", "곡류": "#6D4C41", "유제품": "#8E24AA", "기타": "#546E7A" };
const CAT_ICONS = { "채소": "🥬", "육류": "🥩", "해산물": "🐟", "양념": "🧂", "곡류": "🌾", "유제품": "🥛", "기타": "🥚" };

// ─── 메인 앱 ───────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState(0);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [shoppingItems, setShoppingItems] = useState(SHOPPING_LIST);
  const [showSettings, setShowSettings] = useState(false);
  const [menuData, setMenuData] = useState(WEEKLY_MENU);

  const toggleCheck = (id) => {
    setShoppingItems(prev => prev.map(i => i.id === id ? { ...i, checked: !i.checked } : i));
  };

  const replaceMeal = (dateKey, mealType) => {
    const alternatives = ["비빔밥", "불고기", "달걀말이", "떡볶이", "라면 + 달걀", "갈치 조림", "오징어볶음"];
    const newTitle = alternatives[Math.floor(Math.random() * alternatives.length)];
    setMenuData(prev => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[dateKey]?.meals?.[mealType]) {
        updated[dateKey].meals[mealType].title = newTitle;
        updated[dateKey].meals[mealType].kcal = Math.floor(Math.random() * 300 + 100);
      }
      return updated;
    });
  };

  if (selectedRecipe) {
    return <RecipeDetail recipe={selectedRecipe} onBack={() => setSelectedRecipe(null)} />;
  }

  if (showSettings) {
    return <SettingsScreen user={USER} onBack={() => setShowSettings(false)} />;
  }

  return (
    <div style={{ maxWidth: 420, margin: "0 auto", minHeight: "100vh", background: "#F5F5F0", fontFamily: "'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif", display: "flex", flexDirection: "column", borderLeft: "1px solid #E0E0E0", borderRight: "1px solid #E0E0E0" }}>
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

      {/* 앱바 */}
      <div style={{ background: "linear-gradient(135deg, #2E7D32, #388E3C)", padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between", boxShadow: "0 2px 8px rgba(46,125,50,0.3)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 26 }}>🍚</span>
          <span style={{ color: "white", fontSize: 21, fontWeight: 700, letterSpacing: -0.5 }}>
            {["오늘 식단", "주간 메뉴", "장보기"][tab]}
          </span>
        </div>
        {tab === 0 && (
          <button onClick={() => setShowSettings(true)} style={{ background: "rgba(255,255,255,0.2)", border: "none", borderRadius: 10, padding: "8px 12px", cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "white", fontSize: 18 }}>⚙️</span>
            <span style={{ color: "white", fontSize: 15 }}>설정</span>
          </button>
        )}
      </div>

      {/* 콘텐츠 */}
      <div style={{ flex: 1, overflowY: "auto", paddingBottom: 80 }}>
        {tab === 0 && <TodayTab data={menuData} onRecipe={setSelectedRecipe} onReplace={replaceMeal} user={USER} />}
        {tab === 1 && <WeeklyTab data={menuData} onRecipe={setSelectedRecipe} onReplace={replaceMeal} />}
        {tab === 2 && <ShoppingTab items={shoppingItems} onToggle={toggleCheck} />}
      </div>

      {/* 하단 네비게이션 */}
      <div style={{ position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)", width: "100%", maxWidth: 420, background: "white", borderTop: "1px solid #E0E0E0", display: "flex", zIndex: 100, boxShadow: "0 -2px 10px rgba(0,0,0,0.06)" }}>
        {[
          { icon: "🍽️", label: "오늘", idx: 0 },
          { icon: "📅", label: "주간", idx: 1 },
          { icon: "🛒", label: "장보기", idx: 2 },
        ].map(t => (
          <button key={t.idx} onClick={() => setTab(t.idx)} style={{
            flex: 1, padding: "12px 0 10px", border: "none", background: "none", cursor: "pointer",
            display: "flex", flexDirection: "column", alignItems: "center", gap: 3,
            opacity: tab === t.idx ? 1 : 0.5, transition: "all 0.2s"
          }}>
            <span style={{ fontSize: 26 }}>{t.icon}</span>
            <span style={{ fontSize: 14, fontWeight: tab === t.idx ? 700 : 400, color: tab === t.idx ? "#2E7D32" : "#757575" }}>{t.label}</span>
            {tab === t.idx && <div style={{ width: 24, height: 3, borderRadius: 2, background: "#2E7D32", marginTop: 2 }} />}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── 오늘 식단 탭 ──────────────────────────────────
function TodayTab({ data, onRecipe, onReplace, user }) {
  const todayKey = Object.keys(data).find(k => data[k].isToday) || Object.keys(data)[1];
  const today = data[todayKey];
  const meals = today?.meals || {};
  const totalKcal = Object.values(meals).reduce((s, m) => s + (m.kcal || 0), 0);
  const ratio = user.kcalTarget > 0 ? totalKcal / user.kcalTarget : 0;
  const kcalColor = ratio > 1.1 ? "#E53935" : ratio > 0.9 ? "#FFA000" : "#43A047";
  const dt = new Date(todayKey);
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];

  return (
    <div style={{ padding: 16 }}>
      {/* 날짜 헤더 */}
      <div style={{ background: "linear-gradient(135deg, #E8F5E9, #C8E6C9)", borderRadius: 14, padding: "14px 18px", marginBottom: 12, display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 28 }}>📆</span>
        <div>
          <div style={{ fontSize: 20, fontWeight: 700, color: "#1B5E20" }}>
            오늘 {dt.getMonth() + 1}월 {dt.getDate()}일 ({weekdays[dt.getDay()]})
          </div>
          <div style={{ fontSize: 14, color: "#4CAF50", marginTop: 2 }}>B주차 · 건강한 하루를 시작하세요</div>
        </div>
      </div>

      {/* 칼로리 요약 카드 */}
      <div style={{ background: "white", borderRadius: 16, padding: 20, marginBottom: 16, boxShadow: "0 2px 8px rgba(0,0,0,0.06)", display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            <span style={{ fontSize: 32, fontWeight: 800, color: kcalColor }}>{totalKcal}</span>
            <span style={{ fontSize: 16, color: "#757575" }}>kcal</span>
          </div>
          <div style={{ fontSize: 15, color: "#9E9E9E", marginTop: 4 }}>권장 {user.kcalTarget} kcal</div>
          <div style={{ background: "#F5F5F5", borderRadius: 8, height: 10, marginTop: 10, overflow: "hidden" }}>
            <div style={{ background: `linear-gradient(90deg, ${kcalColor}, ${kcalColor}dd)`, height: "100%", width: `${Math.min(ratio * 100, 100)}%`, borderRadius: 8, transition: "width 0.5s" }} />
          </div>
        </div>
        <div style={{ width: 70, height: 70, borderRadius: "50%", border: `4px solid ${kcalColor}`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
          <span style={{ fontSize: 18, fontWeight: 800, color: kcalColor }}>{Math.round(ratio * 100)}%</span>
        </div>
      </div>

      {/* 끼니별 카드 */}
      {["BREAKFAST", "LUNCH", "DINNER"].map(mt => {
        const meal = meals[mt];
        if (!meal) return null;
        const ml = MEAL_LABELS[mt];
        const diffDots = "●".repeat(meal.diff) + "○".repeat(3 - meal.diff);
        return (
          <div key={mt} style={{ background: "white", borderRadius: 16, marginBottom: 12, boxShadow: "0 2px 8px rgba(0,0,0,0.06)", overflow: "hidden" }}>
            {/* 끼니 라벨 */}
            <div style={{ padding: "12px 20px 0", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 22 }}>{ml.icon}</span>
              <span style={{ fontSize: 15, color: "#9E9E9E", fontWeight: 500 }}>{ml.label}</span>
              {meal.cuisine === "FREE" && <span style={{ fontSize: 11, background: "#FFF3E0", color: "#E65100", padding: "2px 8px", borderRadius: 6, fontWeight: 600 }}>자유</span>}
            </div>
            {/* 메뉴 이름 + 정보 */}
            <div style={{ padding: "8px 20px 16px" }}>
              <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 10, color: "#212121" }}>{meal.title}</div>
              <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 14 }}>
                <InfoBadge icon="🔥" text={`${meal.kcal} kcal`} color="#FF6D00" />
                <InfoBadge icon="⏱️" text={`${meal.time}분`} color="#616161" />
                <InfoBadge icon="📊" text={`난이도 ${diffDots}`} color="#616161" />
              </div>
              {/* 버튼 */}
              <div style={{ display: "flex", gap: 10 }}>
                <button onClick={() => onRecipe(meal)} style={{ flex: 1, padding: "14px 0", borderRadius: 12, border: "2px solid #2E7D32", background: "white", color: "#2E7D32", fontSize: 16, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                  📋 조리순서
                </button>
                <button onClick={() => onReplace(todayKey, mt)} style={{ flex: 1, padding: "14px 0", borderRadius: 12, border: "2px solid #E0E0E0", background: "white", color: "#757575", fontSize: 16, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                  🔄 메뉴 변경
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function InfoBadge({ icon, text, color }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
      <span style={{ fontSize: 15 }}>{icon}</span>
      <span style={{ fontSize: 15, color, fontWeight: 500 }}>{text}</span>
    </div>
  );
}

// ─── 주간 메뉴 탭 ──────────────────────────────────
function WeeklyTab({ data, onRecipe, onReplace }) {
  return (
    <div style={{ padding: 16 }}>
      {/* 로테이션 헤더 */}
      <div style={{ background: "linear-gradient(135deg, #E8F5E9, #C8E6C9)", borderRadius: 14, padding: "14px 18px", marginBottom: 14, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 26 }}>📅</span>
          <div>
            <span style={{ fontSize: 18, fontWeight: 700, color: "#1B5E20" }}>2026년 2월 2주차</span>
            <div style={{ fontSize: 14, color: "#4CAF50" }}>로테이션 B</div>
          </div>
        </div>
        <div style={{ background: "#2E7D32", color: "white", padding: "6px 14px", borderRadius: 10, fontSize: 14, fontWeight: 700 }}>B주</div>
      </div>

      {/* 요일별 카드 */}
      {Object.entries(data).map(([dateKey, dayData]) => {
        const meals = dayData.meals;
        const dayKcal = Object.values(meals).reduce((s, m) => s + (m.kcal || 0), 0);
        const isWeekend = ["토", "일"].includes(dayData.day);
        const dt = new Date(dateKey);

        return (
          <div key={dateKey} style={{
            background: "white", borderRadius: 14, marginBottom: 10, overflow: "hidden",
            boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
            border: dayData.isToday ? "2px solid #2E7D32" : "1px solid #F0F0F0"
          }}>
            {/* 요일 헤더 */}
            <div style={{ padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid #F5F5F5" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{
                  display: "inline-block", padding: "4px 12px", borderRadius: 8, fontSize: 15, fontWeight: 700,
                  background: dayData.isToday ? "#2E7D32" : isWeekend ? "#FFF3E0" : "#F5F5F5",
                  color: dayData.isToday ? "white" : isWeekend ? "#E65100" : "#424242"
                }}>
                  {dayData.day}
                </span>
                <span style={{ fontSize: 14, color: "#9E9E9E" }}>{dt.getMonth() + 1}/{dt.getDate()}</span>
                {dayData.isToday && <span style={{ fontSize: 13, color: "#2E7D32", fontWeight: 700, background: "#E8F5E9", padding: "2px 8px", borderRadius: 6 }}>오늘</span>}
              </div>
              <span style={{ fontSize: 14, color: "#9E9E9E", fontWeight: 500 }}>{dayKcal} kcal</span>
            </div>

            {/* 끼니별 */}
            <div style={{ padding: "8px 16px 12px" }}>
              {["BREAKFAST", "LUNCH", "DINNER"].map(mt => {
                const meal = meals[mt];
                if (!meal) return null;
                const ml = MEAL_LABELS[mt];
                return (
                  <div key={mt} style={{ display: "flex", alignItems: "center", padding: "7px 0", gap: 8 }}>
                    <span style={{ fontSize: 18, width: 28, textAlign: "center" }}>{ml.icon}</span>
                    <span style={{ fontSize: 14, color: "#9E9E9E", width: 36, flexShrink: 0 }}>{ml.label}</span>
                    <span onClick={() => onRecipe(meal)} style={{ flex: 1, fontSize: 16, fontWeight: 500, cursor: "pointer", color: "#212121" }}>{meal.title}</span>
                    <span style={{ fontSize: 13, color: "#BDBDBD", width: 60, textAlign: "right" }}>{meal.kcal} kcal</span>
                    <button onClick={() => onReplace(dateKey, mt)} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 18, padding: 4, opacity: 0.5 }}>🔄</button>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── 장보기 탭 ──────────────────────────────────────
function ShoppingTab({ items, onToggle }) {
  const [activeFilter, setActiveFilter] = useState("전체");
  const [hideChecked, setHideChecked] = useState(false);

  const checkedCount = items.filter(i => i.checked).length;
  const categories = ["전체", "채소", "육류", "해산물", "곡류", "유제품", "양념", "기타"];

  let filtered = activeFilter === "전체" ? items : items.filter(i => i.cat === activeFilter);
  if (hideChecked) filtered = filtered.filter(i => !i.checked);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* 상단 요약 */}
      <div style={{ background: "linear-gradient(135deg, #E8F5E9, #C8E6C9)", padding: "14px 18px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 26 }}>🛒</span>
          <div>
            <span style={{ fontSize: 18, fontWeight: 700, color: "#1B5E20" }}>이번 주 장보기</span>
            <div style={{ fontSize: 14, color: "#4CAF50" }}>{checkedCount}/{items.length} 완료</div>
          </div>
        </div>
        <button onClick={() => setHideChecked(!hideChecked)} style={{
          background: hideChecked ? "#2E7D32" : "rgba(255,255,255,0.7)", border: "none", borderRadius: 10,
          padding: "8px 14px", cursor: "pointer", fontSize: 14, fontWeight: 600,
          color: hideChecked ? "white" : "#616161"
        }}>
          {hideChecked ? "👁️ 전체 보기" : "✅ 완료 숨기기"}
        </button>
      </div>

      {/* 진행률 바 */}
      <div style={{ padding: "0 18px", background: "#E8F5E9" }}>
        <div style={{ background: "rgba(255,255,255,0.5)", borderRadius: 6, height: 6, overflow: "hidden", marginBottom: 14 }}>
          <div style={{ background: "#2E7D32", height: "100%", width: `${(checkedCount / items.length) * 100}%`, borderRadius: 6, transition: "width 0.3s" }} />
        </div>
      </div>

      {/* 카테고리 탭 */}
      <div style={{ display: "flex", gap: 6, padding: "10px 16px", overflowX: "auto", background: "white", borderBottom: "1px solid #F0F0F0" }}>
        {categories.map(cat => {
          const count = cat === "전체" ? items.length : items.filter(i => i.cat === cat).length;
          if (count === 0 && cat !== "전체") return null;
          return (
            <button key={cat} onClick={() => setActiveFilter(cat)} style={{
              padding: "8px 14px", borderRadius: 10, border: "none", cursor: "pointer", whiteSpace: "nowrap",
              fontSize: 14, fontWeight: activeFilter === cat ? 700 : 400,
              background: activeFilter === cat ? "#2E7D32" : "#F5F5F5",
              color: activeFilter === cat ? "white" : "#616161",
              transition: "all 0.2s"
            }}>
              {CAT_ICONS[cat] || "📦"} {cat} ({count})
            </button>
          );
        })}
      </div>

      {/* 리스트 */}
      <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
        {filtered.map(item => (
          <div key={item.id} onClick={() => onToggle(item.id)} style={{
            display: "flex", alignItems: "center", padding: "14px 18px", gap: 14,
            borderBottom: "1px solid #F5F5F5", cursor: "pointer",
            background: item.checked ? "#FAFAFA" : "white",
            transition: "all 0.2s"
          }}>
            {/* 체크박스 */}
            <div style={{
              width: 30, height: 30, borderRadius: 8, flexShrink: 0,
              border: item.checked ? "none" : "2px solid #BDBDBD",
              background: item.checked ? "#43A047" : "white",
              display: "flex", alignItems: "center", justifyContent: "center",
              transition: "all 0.2s"
            }}>
              {item.checked && <span style={{ color: "white", fontSize: 18, fontWeight: 700 }}>✓</span>}
            </div>

            {/* 재료명 */}
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: 18, fontWeight: 500,
                textDecoration: item.checked ? "line-through" : "none",
                color: item.checked ? "#BDBDBD" : "#212121"
              }}>
                {item.name}
              </div>
              {item.pantry && <div style={{ fontSize: 13, color: "#FFA000", marginTop: 2 }}>🏠 상비 재료</div>}
            </div>

            {/* 수량 */}
            <div style={{
              padding: "6px 14px", borderRadius: 10,
              background: `${CAT_COLORS[item.cat]}15`,
              color: item.checked ? "#BDBDBD" : CAT_COLORS[item.cat],
              fontSize: 16, fontWeight: 700, whiteSpace: "nowrap"
            }}>
              {item.qty}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── 레시피 상세 화면 ──────────────────────────────
function RecipeDetail({ recipe, onBack }) {
  const [activeTab, setActiveTab] = useState("steps");
  const [step, setStep] = useState(0);
  const steps = recipe.steps || [];
  const ings = recipe.ingredients || [];
  const diffDots = "●".repeat(recipe.diff) + "○".repeat(3 - recipe.diff);

  const macros = { carb: Math.round(recipe.kcal * 0.5 / 4), protein: Math.round(recipe.kcal * 0.25 / 4), fat: Math.round(recipe.kcal * 0.25 / 9), sodium: Math.round(recipe.kcal * 1.5) };

  return (
    <div style={{ maxWidth: 420, margin: "0 auto", minHeight: "100vh", background: "#F5F5F0", fontFamily: "'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif", display: "flex", flexDirection: "column", borderLeft: "1px solid #E0E0E0", borderRight: "1px solid #E0E0E0" }}>
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

      {/* 헤더 */}
      <div style={{ background: "linear-gradient(135deg, #2E7D32, #388E3C)", padding: "16px 20px", display: "flex", alignItems: "center", gap: 14, boxShadow: "0 2px 8px rgba(46,125,50,0.3)" }}>
        <button onClick={onBack} style={{ background: "rgba(255,255,255,0.2)", border: "none", borderRadius: 10, padding: "10px 14px", cursor: "pointer", color: "white", fontSize: 18, fontWeight: 600 }}>
          ← 뒤로
        </button>
        <span style={{ color: "white", fontSize: 20, fontWeight: 700 }}>{recipe.title}</span>
      </div>

      {/* 요약 */}
      <div style={{ background: "white", padding: 20, display: "flex", justifyContent: "space-around", borderBottom: "1px solid #F0F0F0" }}>
        {[
          { icon: "🔥", value: `${recipe.kcal} kcal` },
          { icon: "⏱️", value: `${recipe.time}분` },
          { icon: "📊", value: diffDots },
          { icon: "👤", value: "1인분" },
        ].map((info, i) => (
          <div key={i} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24 }}>{info.icon}</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#424242", marginTop: 4 }}>{info.value}</div>
          </div>
        ))}
      </div>

      {/* 탭 */}
      <div style={{ display: "flex", background: "white", borderBottom: "2px solid #F0F0F0" }}>
        {[
          { key: "steps", label: "조리순서" },
          { key: "ingredients", label: "재료" },
          { key: "nutrition", label: "영양정보" },
        ].map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)} style={{
            flex: 1, padding: "14px 0", border: "none", cursor: "pointer",
            fontSize: 17, fontWeight: activeTab === t.key ? 700 : 400,
            color: activeTab === t.key ? "#2E7D32" : "#9E9E9E",
            background: "none",
            borderBottom: activeTab === t.key ? "3px solid #2E7D32" : "3px solid transparent"
          }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* 탭 내용 */}
      <div style={{ flex: 1, overflow: "auto" }}>
        {activeTab === "steps" && (
          <div style={{ padding: 24, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 350 }}>
            <div style={{ width: 60, height: 60, borderRadius: 30, background: "#2E7D32", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
              <span style={{ color: "white", fontSize: 26, fontWeight: 800 }}>{step + 1}</span>
            </div>
            <div style={{ fontSize: 22, lineHeight: 1.7, textAlign: "center", color: "#212121", marginBottom: 16, padding: "0 12px" }}>
              {steps[step]}
            </div>
            <div style={{ fontSize: 15, color: "#9E9E9E" }}>{step + 1} / {steps.length}</div>

            <div style={{ display: "flex", gap: 16, marginTop: 30, width: "100%" }}>
              <button disabled={step === 0} onClick={() => setStep(s => s - 1)} style={{
                flex: 1, padding: "16px 0", borderRadius: 14, fontSize: 18, fontWeight: 600, cursor: step === 0 ? "default" : "pointer",
                border: "2px solid #E0E0E0", background: "white", color: step === 0 ? "#E0E0E0" : "#616161"
              }}>
                ← 이전
              </button>
              <button disabled={step === steps.length - 1} onClick={() => setStep(s => s + 1)} style={{
                flex: 1, padding: "16px 0", borderRadius: 14, fontSize: 18, fontWeight: 600, cursor: step === steps.length - 1 ? "default" : "pointer",
                border: "none", background: step === steps.length - 1 ? "#E0E0E0" : "#2E7D32", color: "white"
              }}>
                {step === steps.length - 1 ? "✓ 완료" : "다음 →"}
              </button>
            </div>
          </div>
        )}

        {activeTab === "ingredients" && (
          <div style={{ padding: 16 }}>
            {ings.map((ing, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", padding: "14px 8px", borderBottom: "1px solid #F5F5F5", gap: 12 }}>
                <div style={{ width: 6, height: 36, borderRadius: 3, background: "#43A047" }} />
                <span style={{ flex: 1, fontSize: 18, color: "#212121" }}>{ing.name}</span>
                <span style={{ fontSize: 18, fontWeight: 700, color: "#2E7D32" }}>{ing.qty}</span>
              </div>
            ))}
          </div>
        )}

        {activeTab === "nutrition" && (
          <div style={{ padding: 24 }}>
            <div style={{ background: "#FFF8E1", borderRadius: 16, padding: 24, textAlign: "center", marginBottom: 24 }}>
              <div style={{ fontSize: 15, color: "#9E9E9E" }}>1인분 기준</div>
              <div style={{ fontSize: 40, fontWeight: 800, color: "#FF8F00", marginTop: 4 }}>{recipe.kcal} <span style={{ fontSize: 18 }}>kcal</span></div>
            </div>
            {[
              { label: "탄수화물", value: macros.carb, max: 100, color: "#FFA000", unit: "g" },
              { label: "단백질", value: macros.protein, max: 100, color: "#E53935", unit: "g" },
              { label: "지방", value: macros.fat, max: 50, color: "#1E88E5", unit: "g" },
              { label: "나트륨", value: macros.sodium, max: 2000, color: "#8E24AA", unit: "mg" },
            ].map((n, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
                <span style={{ width: 72, fontSize: 16, color: "#616161" }}>{n.label}</span>
                <div style={{ flex: 1, background: "#F5F5F5", borderRadius: 8, height: 22, overflow: "hidden" }}>
                  <div style={{ background: n.color, height: "100%", width: `${Math.min((n.value / n.max) * 100, 100)}%`, borderRadius: 8, transition: "width 0.5s" }} />
                </div>
                <span style={{ width: 70, fontSize: 16, fontWeight: 700, textAlign: "right", color: "#424242" }}>{n.value} {n.unit}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── 설정 화면 ──────────────────────────────────────
function SettingsScreen({ user, onBack }) {
  return (
    <div style={{ maxWidth: 420, margin: "0 auto", minHeight: "100vh", background: "#F5F5F0", fontFamily: "'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif", borderLeft: "1px solid #E0E0E0", borderRight: "1px solid #E0E0E0" }}>
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      <div style={{ background: "linear-gradient(135deg, #2E7D32, #388E3C)", padding: "16px 20px", display: "flex", alignItems: "center", gap: 14 }}>
        <button onClick={onBack} style={{ background: "rgba(255,255,255,0.2)", border: "none", borderRadius: 10, padding: "10px 14px", cursor: "pointer", color: "white", fontSize: 18, fontWeight: 600 }}>← 뒤로</button>
        <span style={{ color: "white", fontSize: 20, fontWeight: 700 }}>⚙️ 설정</span>
      </div>
      <div style={{ padding: 20 }}>
        <div style={{ background: "white", borderRadius: 16, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.06)" }}>
          <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 20, color: "#1B5E20" }}>👤 내 정보</div>
          {[
            ["이름", user.name],
            ["성별", user.sex === "M" ? "남성" : "여성"],
            ["출생연도", `${user.birthYear}년 (${2026 - user.birthYear}세)`],
            ["키 / 몸무게", `${user.height}cm / ${user.weight}kg`],
            ["활동량", `${"⬤".repeat(user.activity)}${"○".repeat(5 - user.activity)} (${user.activity}/5)`],
            ["일일 권장 칼로리", `${user.kcalTarget} kcal`],
          ].map(([label, value], i) => (
            <div key={i} style={{ display: "flex", padding: "12px 0", borderBottom: i < 5 ? "1px solid #F5F5F5" : "none" }}>
              <span style={{ width: 120, fontSize: 16, color: "#9E9E9E" }}>{label}</span>
              <span style={{ fontSize: 18, fontWeight: 500, color: "#212121" }}>{value}</span>
            </div>
          ))}
        </div>

        <div style={{ background: "white", borderRadius: 16, padding: 24, marginTop: 16, boxShadow: "0 2px 8px rgba(0,0,0,0.06)" }}>
          <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 16, color: "#1B5E20" }}>🍽️ 끼니별 칼로리 배분</div>
          {[
            { label: "🌅 아침 (25%)", value: Math.round(user.kcalTarget * 0.25), color: "#FFA000" },
            { label: "☀️ 점심 (40%)", value: Math.round(user.kcalTarget * 0.40), color: "#FF6D00" },
            { label: "🌙 저녁 (35%)", value: Math.round(user.kcalTarget * 0.35), color: "#E65100" },
          ].map((m, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", padding: "10px 0", gap: 12 }}>
              <span style={{ fontSize: 16, width: 130 }}>{m.label}</span>
              <div style={{ flex: 1, background: "#F5F5F5", borderRadius: 6, height: 14, overflow: "hidden" }}>
                <div style={{ background: m.color, height: "100%", width: `${(m.value / user.kcalTarget) * 100}%`, borderRadius: 6 }} />
              </div>
              <span style={{ fontSize: 16, fontWeight: 700, width: 70, textAlign: "right" }}>{m.value} kcal</span>
            </div>
          ))}
        </div>

        <button style={{ width: "100%", padding: "16px 0", marginTop: 20, borderRadius: 14, border: "none", background: "#2E7D32", color: "white", fontSize: 18, fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 12px rgba(46,125,50,0.3)" }}>
          🔄 이번 주 메뉴 새로 만들기
        </button>

        <div style={{ textAlign: "center", marginTop: 24, color: "#BDBDBD", fontSize: 14 }}>
          식단 플래너 v1.0<br />50~70대를 위한 건강한 식단 관리
        </div>
      </div>
    </div>
  );
}
