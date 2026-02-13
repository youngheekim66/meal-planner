# ☁️ 클라우드 배포 가이드

로컬이 아닌 **외부에서도 접속 가능**하도록 클라우드에 배포하는 방법입니다.

---

## 추천 순서 (쉬운 순)

| 서비스 | 난이도 | 무료 | 특징 |
|--------|--------|------|------|
| **Railway.app** | ⭐ 쉬움 | 월 $5 크레딧 | GitHub 연결만으로 배포 |
| **Render.com** | ⭐ 쉬움 | 무료 (느림) | 무료 PostgreSQL 포함 |
| **Fly.io** | ⭐⭐ 보통 | 무료 | Docker 직접 배포 |

---

## 방법 1: Railway.app (가장 쉬움)

### 1-1. 사전 준비

**GitHub 계정이 필요합니다.**

GitHub에 프로젝트를 업로드합니다:

```bash
cd C:\Projects\meal-planner

# Git 초기화
git init
git add .
git commit -m "식단 플래너 v1.2"

# GitHub에서 새 저장소 만들기 (https://github.com/new)
# 저장소 이름: meal-planner

git remote add origin https://github.com/YOUR_USERNAME/meal-planner.git
git branch -M main
git push -u origin main
```

### 1-2. Railway 설정

1. **https://railway.app** 접속 → GitHub로 로그인

2. **New Project** 클릭 → "Deploy from GitHub repo" 선택

3. **meal-planner 저장소** 선택

4. **"Add Database"** → PostgreSQL 추가

5. **backend 서비스 설정:**
   - Root Directory: `/backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Variables에 추가:
     ```
     DATABASE_URL = (Railway가 자동 연결)
     JWT_SECRET_KEY = (랜덤 문자열 입력)
     ```

6. **Deploy** 클릭

7. 1~2분 후 배포 완료 → Railway가 제공하는 URL로 접속
   ```
   https://meal-planner-xxxxx.railway.app/docs
   ```

### 1-3. Flutter 앱에서 연결

`frontend/lib/services/api_service.dart`에서:

```dart
// 로컬 대신 Railway URL 사용
static const String baseUrl = 'https://meal-planner-xxxxx.railway.app/api';
```

---

## 방법 2: Render.com (완전 무료)

### 2-1. Render 설정

1. **https://render.com** 접속 → GitHub로 로그인

2. **New → PostgreSQL** → 무료 플랜으로 DB 생성
   - Name: `meal-planner-db`
   - Region: Oregon 또는 Singapore
   - 생성 후 **Internal Database URL** 복사

3. **New → Web Service** → GitHub 저장소 연결
   - Name: `meal-planner-api`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables** 추가:
   ```
   DATABASE_URL = (2단계에서 복사한 Internal URL)
   JWT_SECRET_KEY = my-secret-key-change-this
   ```

5. **Create Web Service** 클릭

6. 5~10분 후 배포 완료:
   ```
   https://meal-planner-api.onrender.com/docs
   ```

> ⚠️ 무료 플랜은 15분 비활동 시 슬립 → 첫 접속에 30초 소요

---

## 방법 3: Fly.io (Docker 직접 배포)

### 3-1. Fly CLI 설치

```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# macOS
brew install flyctl
```

### 3-2. 로그인 및 배포

```bash
cd C:\Projects\meal-planner\backend

# 로그인
fly auth login

# 앱 생성
fly launch --name meal-planner-api

# PostgreSQL 추가
fly postgres create --name meal-planner-db
fly postgres attach meal-planner-db --app meal-planner-api

# JWT 시크릿 설정
fly secrets set JWT_SECRET_KEY="your-secret-key-here" --app meal-planner-api

# 배포
fly deploy
```

### 3-3. 접속

```
https://meal-planner-api.fly.dev/docs
```

---

## 배포 후 확인사항

### ✅ 헬스체크
```bash
curl https://YOUR-URL/health
# {"status":"ok"}
```

### ✅ 레시피 확인
```bash
curl https://YOUR-URL/api/recipes/?limit=5
```

### ✅ 회원가입 테스트
```bash
curl -X POST https://YOUR-URL/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@meal.com","password":"1234","name":"테스트"}'
```

---

## Flutter 앱 연결 (실제 기기)

배포 후 API URL을 클라우드 주소로 변경합니다:

```dart
// frontend/lib/services/api_service.dart

class ApiService {
  // 개발 환경
  // static const String baseUrl = 'http://10.0.2.2:8000/api';

  // 배포 환경 (아래 URL을 실제 배포 주소로 변경)
  static const String baseUrl = 'https://meal-planner-xxxxx.railway.app/api';
}
```

그 후 Flutter 앱을 빌드합니다:

```bash
cd frontend

# Android APK
flutter build apk --release

# iOS (macOS 필요)
flutter build ios --release
```

생성된 APK를 핸드폰에 설치하면 어디서든 사용 가능합니다.

---

## 보안 참고

운영 환경에서는 아래 사항을 반드시 변경하세요:

1. **JWT_SECRET_KEY**: 랜덤 문자열로 변경 (최소 32자)
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **PostgreSQL 비밀번호**: `postgres` → 강력한 비밀번호로 변경

3. **CORS 설정**: `allow_origins=["*"]` → 실제 도메인만 허용

4. **HTTPS**: 클라우드 서비스들은 기본 제공

---

*식단 플래너 v1.2 — 2026-02-10*
