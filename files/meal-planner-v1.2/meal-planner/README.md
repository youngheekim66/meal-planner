# 🍱 식단 플래너 v1.2

50~70대를 위한 **AI 건강 식단 관리** 앱

## 🚀 빠른 시작 (Docker)

```bash
tar -xzf meal-planner-v1.2.tar.gz
cd meal-planner
docker compose up --build
```

**접속:** http://localhost:8000/docs

## 📊 주요 스펙

| 항목 | 수치 |
|------|------|
| 레시피 | **105개** (한식 79 + 자유 26) |
| 재료 | 99개 |
| 영양 DB | 100% 매핑 |
| 식사 분류 | 아침 17 / 점심 90 / 저녁 85 |
| 밥 자동합산 | 40+ 레시피 (+310 kcal) |
| 일평균 칼로리 | ~1,184 kcal |

## 🔐 인증 API

| 엔드포인트 | 설명 |
|-----------|------|
| `POST /api/auth/signup` | 회원가입 → JWT 토큰 발급 |
| `POST /api/auth/login` | 로그인 → JWT 토큰 발급 |
| `GET /api/auth/me` | 내 정보 (Bearer 토큰 필요) |

## 📡 기존 API

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /api/recipes/` | 레시피 목록 |
| `GET /api/recipes/{id}` | 레시피 상세 |
| `GET /api/recipes/{id}/nutrition` | 영양정보 (밥 자동포함) |
| `POST /api/menu/generate` | 주간 메뉴 자동 생성 |
| `GET /api/menu/{user_id}/today` | 오늘 식단 |
| `POST /api/menu/item/{id}/replace` | 한 끼 교체 |
| `GET /api/shopping/{user_id}/current` | 장보기 리스트 |

## 🛠 기술 스택

- **백엔드:** FastAPI + SQLAlchemy + PostgreSQL
- **인증:** JWT (python-jose) + bcrypt
- **프론트엔드:** Flutter (Dart) + Provider
- **배포:** Docker Compose
- **UI 프로토타입:** prototype.html (React 시뮬레이션)

## 📱 Flutter 앱 구조

```
frontend/lib/
├── main.dart              # 앱 진입점 + 인증 게이트
├── models/models.dart     # 데이터 모델
├── screens/
│   ├── auth_screen.dart   # 로그인/회원가입 화면
│   ├── today_screen.dart  # 오늘 식단 탭
│   ├── weekly_screen.dart # 주간 메뉴 탭
│   ├── shopping_screen.dart # 장보기 탭
│   └── recipe_detail_screen.dart
├── services/
│   ├── api_service.dart   # HTTP 클라이언트 (JWT 포함)
│   └── app_state.dart     # 상태 관리 (Provider)
└── theme/app_theme.dart   # 앱 테마
```

## 📱 Flutter 앱 실행

```bash
cd frontend
flutter pub get
flutter run
```

**API 서버 주소 변경:**
- `lib/services/api_service.dart`의 `baseUrl` 수정
  - Android 에뮬레이터: `http://10.0.2.2:8000/api`
  - iOS 시뮬레이터: `http://localhost:8000/api`
  - 실제 기기: `http://<PC IP>:8000/api`

## 🔄 앱 흐름

```
로그인/회원가입 → JWT 토큰 발급
    ↓
오늘 식단 보기 (메뉴 자동 생성)
    ↓
주간 메뉴 확인 / 한 끼 교체
    ↓
장보기 리스트 (자동 집계)
```

## 📋 변경 이력

### v1.2 (2026-02-10)
- ✨ 레시피 105개로 확대 (70→105)
- 🔐 JWT 인증 (회원가입/로그인/내정보)
- 📱 Flutter 로그인/회원가입 화면
- 🔒 API 토큰 인증 지원
- 📝 Docker 가이드 문서 (DOCKER_GUIDE.md)

### v1.1 (2026-02-10)
- 📱 UI 프로토타입 (prototype.html)
- 🍳 레시피 70개 (27→70)
- 🍚 밥 자동합산 로직 (673→1,184 kcal/day)
- 🐳 Docker 배포 구성

### v1.0 (2026-02-10)
- 🎉 최초 릴리스, 27 레시피, 13 API 엔드포인트
