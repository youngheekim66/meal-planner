# 🐳 식단 플래너 Docker 배포 가이드

50~70대를 위한 식단 플래너를 **어디서든 똑같이** 실행하기 위한 완전한 Docker 가이드입니다.

---

## 목차

1. [Docker란?](#1-docker란)
2. [Docker Desktop 설치](#2-docker-desktop-설치)
3. [프로젝트 준비](#3-프로젝트-준비)
4. [Docker 실행하기](#4-docker-실행하기)
5. [정상 동작 확인](#5-정상-동작-확인)
6. [자주 쓰는 명령어](#6-자주-쓰는-명령어)
7. [문제 해결 (트러블슈팅)](#7-문제-해결-트러블슈팅)
8. [프로젝트 구조 설명](#8-프로젝트-구조-설명)

---

## 1. Docker란?

Docker는 앱을 **컨테이너**라는 독립된 공간에 넣어서 실행하는 기술입니다.

| 항목 | Docker 없이 | Docker 있으면 |
|------|------------|--------------|
| Python 설치 | 직접 설치 필요 | 자동 |
| PostgreSQL 설치 | 직접 설치 필요 | 자동 |
| 라이브러리 충돌 | 버전 문제 발생 가능 | 격리되어 충돌 없음 |
| 다른 PC에서 실행 | 처음부터 설정 | 동일하게 실행 |

**우리 프로젝트의 Docker 구성:**

```
┌─────────────────────────────────────────┐
│           Docker Desktop                │
│                                         │
│  ┌─────────────────┐  ┌──────────────┐  │
│  │  backend 컨테이너 │  │  db 컨테이너  │  │
│  │                 │  │              │  │
│  │  Python 3.12    │──│  PostgreSQL  │  │
│  │  FastAPI        │  │  16          │  │
│  │  70+ 레시피      │  │  데이터 저장   │  │
│  │                 │  │              │  │
│  │  :8000          │  │  :5432       │  │
│  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────┘
          │
          ▼
   http://localhost:8000
   (브라우저에서 접속)
```

---

## 2. Docker Desktop 설치

### Windows

1. **시스템 요구사항 확인**
   - Windows 10 64비트 (빌드 19041 이상) 또는 Windows 11
   - 최소 4GB RAM (8GB 권장)

2. **WSL2 활성화** (Windows에서 Linux를 실행하는 기능)

   PowerShell을 **관리자 권한**으로 실행하고 입력:

   ```powershell
   wsl --install
   ```

   **컴퓨터를 재부팅합니다.**

3. **Docker Desktop 다운로드 및 설치**

   아래 주소에서 다운로드:
   - https://www.docker.com/products/docker-desktop/

   다운로드한 파일을 실행하고 기본 설정으로 설치합니다.

4. **설치 확인**

   **컴퓨터를 재부팅한 후**, 명령 프롬프트(cmd) 또는 PowerShell을 열고:

   ```cmd
   docker --version
   docker compose version
   ```

   아래와 비슷하게 나오면 성공:
   ```
   Docker version 27.x.x, build xxxxx
   Docker Compose version v2.x.x
   ```

### macOS

1. **Docker Desktop 다운로드**
   - https://www.docker.com/products/docker-desktop/
   - Apple Silicon(M1/M2/M3/M4): "Apple Chip" 선택
   - Intel Mac: "Intel Chip" 선택

2. **.dmg 파일 실행 → Docker를 Applications로 드래그**

3. **Docker Desktop 실행** → 상단 메뉴바에 🐳 아이콘 확인

4. **터미널에서 확인:**
   ```bash
   docker --version
   docker compose version
   ```

---

## 3. 프로젝트 준비

### 3-1. 다운로드한 파일 압축 풀기

Claude에서 다운로드한 `meal-planner-v1.1-final.tar.gz` 파일의 위치를 확인합니다.

**Windows (PowerShell):**
```powershell
# 다운로드 폴더로 이동
cd $HOME\Downloads

# 압축 풀기
tar -xzf meal-planner-v1.1-final.tar.gz

# 프로젝트 폴더로 이동
cd meal-planner
```

**macOS / Linux (터미널):**
```bash
# 다운로드 폴더로 이동
cd ~/Downloads

# 압축 풀기
tar -xzf meal-planner-v1.1-final.tar.gz

# 프로젝트 폴더로 이동
cd meal-planner
```

### 3-2. 파일 구조 확인

프로젝트 폴더에 아래 파일들이 있는지 확인합니다:

```
meal-planner/
├── docker-compose.yml      ← Docker 설정 (핵심!)
├── README.md               ← 프로젝트 문서
├── backend/
│   ├── Dockerfile          ← 백엔드 컨테이너 설정
│   ├── requirements.txt    ← Python 라이브러리 목록
│   └── app/
│       ├── main.py         ← API 서버 진입점
│       ├── core/           ← 설정, DB 연결
│       ├── models/         ← 데이터베이스 모델
│       ├── schemas/        ← API 스키마
│       ├── services/       ← 비즈니스 로직
│       └── api/            ← API 엔드포인트
└── frontend/
    ├── prototype.html      ← UI 프로토타입
    └── lib/                ← Flutter 앱 소스
```

**확인 명령어:**

```bash
# Windows
dir

# macOS/Linux
ls -la
```

`docker-compose.yml` 파일이 보여야 합니다.

---

## 4. Docker 실행하기

### ⚠️ 실행 전 필수 확인

1. **Docker Desktop이 실행 중인지 확인**
   - Windows: 시스템 트레이(오른쪽 하단)에 🐳 아이콘
   - macOS: 메뉴바(상단)에 🐳 아이콘
   - 아이콘이 없으면 Docker Desktop 앱을 실행하세요

2. **현재 위치가 meal-planner 폴더인지 확인**
   ```bash
   # 이 명령어로 현재 위치 확인
   # Windows
   cd

   # macOS/Linux
   pwd
   ```
   출력에 `meal-planner`가 포함되어야 합니다.

### 4-1. 최초 실행 (빌드 + 시작)

```bash
docker compose up --build
```

> **`docker-compose` vs `docker compose`:**
> 최신 Docker Desktop은 `docker compose` (공백) 형식을 사용합니다.
> 오래된 버전은 `docker-compose` (하이픈)입니다.
> 하나가 안 되면 다른 것을 시도하세요.

### 4-2. 정상 실행 로그 예시

아래와 비슷한 로그가 나오면 성공입니다:

```
[+] Building 45.2s (10/10) FINISHED
 => [backend] FROM python:3.12-slim
 => [backend] RUN apt-get update && apt-get install -y ...
 => [backend] RUN pip install --no-cache-dir -r requirements.txt
 => [backend] COPY . .

[+] Running 3/3
 ✔ Network meal-planner_default  Created
 ✔ Container meal-planner-db     Created
 ✔ Container meal-planner-api    Created

meal-planner-db   | LOG:  database system is ready to accept connections
meal-planner-api  | ⏳ DB 연결 대기...
meal-planner-api  | 🚀 서버 시작
meal-planner-api  | 🌱 Seeding ingredients...
meal-planner-api  |    → 44 ingredients
meal-planner-api  | 🌱 Seeding nutrients...
meal-planner-api  |    → 28 nutrients
meal-planner-api  | 🌱 Seeding recipes...
meal-planner-api  |    → 27 recipes
meal-planner-api  | ✅ Seed complete!
meal-planner-api  | ✅ 신규 재료/영양 36개 추가
meal-planner-api  | ✅ 레시피 43개 추가 완료 (총 70개)
meal-planner-api  | INFO:     Uvicorn running on http://0.0.0.0:8000
meal-planner-api  | INFO:     Started server process
```

**핵심 확인 포인트:**
- `database system is ready` → DB 정상
- `총 70개` → 레시피 로딩 완료
- `Uvicorn running on http://0.0.0.0:8000` → 서버 시작 완료

### 4-3. 터미널을 닫지 마세요!

로그가 계속 나오는 상태에서 **이 터미널은 그대로 두고**, 새 브라우저 탭을 엽니다.

(백그라운드 실행을 원하면 → [6. 자주 쓰는 명령어](#6-자주-쓰는-명령어) 참고)

---

## 5. 정상 동작 확인

### 5-1. 브라우저에서 확인

아래 주소를 브라우저에 입력하세요:

| 주소 | 설명 | 정상 응답 |
|------|------|----------|
| http://localhost:8000 | 루트 | `{"app":"식단 플래너 API", ...}` |
| http://localhost:8000/health | 헬스체크 | `{"status":"ok"}` |
| http://localhost:8000/docs | API 문서 (Swagger) | 예쁜 API 문서 페이지 |

### 5-2. Swagger UI로 테스트

`http://localhost:8000/docs` 에 접속하면 모든 API를 브라우저에서 직접 테스트할 수 있습니다.

**사용자 등록 테스트:**

1. `POST /api/users/` 클릭
2. "Try it out" 클릭
3. 아래 내용 입력:

```json
{
  "name": "홍길동",
  "sex": "F",
  "birth_year": 1960,
  "height_cm": 158,
  "weight_kg": 60,
  "activity_level": 2
}
```

4. "Execute" 클릭
5. 응답에서 `kcal_target: 1508` 확인 ✅

**주간 메뉴 생성 테스트:**

1. `POST /api/menu/generate` 클릭
2. "Try it out" 클릭
3. 아래 내용 입력:

```json
{
  "user_id": 1
}
```

4. "Execute" 클릭
5. 21개 메뉴(7일 × 3끼) 생성 확인 ✅

### 5-3. 명령어로 확인

새 터미널을 열고:

```bash
# 루트 확인
curl http://localhost:8000/

# 헬스체크
curl http://localhost:8000/health

# 레시피 목록 (JSON 응답)
curl http://localhost:8000/api/recipes/?limit=5
```

Windows PowerShell에서는:
```powershell
Invoke-RestMethod http://localhost:8000/health
```

---

## 6. 자주 쓰는 명령어

### 기본 명령어

```bash
# 시작 (로그가 터미널에 표시됨)
docker compose up

# 시작 (백그라운드 실행 - 터미널 닫아도 계속 실행)
docker compose up -d

# 종료
docker compose down

# 재시작
docker compose restart

# 상태 확인
docker compose ps
```

### 로그 확인

```bash
# 전체 로그
docker compose logs

# 실시간 로그 (Ctrl+C로 종료)
docker compose logs -f

# 백엔드만 보기
docker compose logs -f backend

# DB만 보기
docker compose logs -f db

# 최근 50줄만
docker compose logs --tail=50 backend
```

### 데이터 초기화 (완전 리셋)

```bash
# 컨테이너 종료 + DB 데이터 삭제
docker compose down -v

# 처음부터 다시 빌드
docker compose up --build
```

### 코드 수정 후 반영

```bash
# 방법 1: 자동 반영 (--reload 옵션이 있어서 Python 파일 수정 시 자동 재시작)
# docker compose up 상태에서 backend/app/ 파일을 수정하면 자동 반영됨

# 방법 2: 수동 재시작
docker compose restart backend

# 방법 3: 완전 재빌드 (requirements.txt 변경 시)
docker compose up --build backend
```

---

## 7. 문제 해결 (트러블슈팅)

### 🔴 "localhost 연결을 거부했습니다"

**원인 1: Docker Desktop이 실행 중이 아닙니다**

확인:
```bash
docker info
```

에러가 나오면 → Docker Desktop 앱을 실행하세요.

---

**원인 2: 컨테이너가 실행 중이 아닙니다**

확인:
```bash
docker compose ps
```

```
NAME                STATUS
meal-planner-db     Up (healthy)     ← 이렇게 나와야 정상
meal-planner-api    Up (healthy)     ← 이렇게 나와야 정상
```

`Exited` 또는 아무것도 안 나오면:
```bash
docker compose up --build
```

---

**원인 3: 포트가 이미 사용 중입니다**

확인:
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

이미 8000번 포트를 사용하는 프로그램이 있다면:
1. 그 프로그램을 종료하거나
2. `docker-compose.yml`에서 포트를 변경:

```yaml
# 8000 대신 8080 사용
ports:
  - "8080:8000"
```

그러면 `http://localhost:8080` 으로 접속합니다.

---

**원인 4: DB 연결 실패 (backend가 계속 재시작)**

로그 확인:
```bash
docker compose logs backend
```

`Connection refused` 또는 `could not connect to server` 가 보이면:

```bash
# 완전 초기화 후 재시작
docker compose down -v
docker compose up --build
```

---

### 🔴 "docker compose" 명령어를 찾을 수 없습니다

```bash
# 하이픈 버전 시도
docker-compose up --build

# 그래도 안 되면 Docker Desktop을 최신 버전으로 업데이트
```

---

### 🔴 빌드 중 에러 (pip install 실패)

```bash
# 캐시 없이 완전 재빌드
docker compose build --no-cache
docker compose up
```

---

### 🔴 WSL2 관련 에러 (Windows)

```
"WSL 2 installation is incomplete"
```

PowerShell (관리자)에서:
```powershell
wsl --update
wsl --set-default-version 2
```

그래도 안 되면:
1. Windows 기능 켜기/끄기 → "Linux용 Windows 하위 시스템" 체크
2. Windows 기능 켜기/끄기 → "가상 머신 플랫폼" 체크
3. 재부팅

---

### 🔴 "permission denied" (macOS/Linux)

```bash
# Docker 그룹에 사용자 추가 (Linux)
sudo usermod -aG docker $USER
# 로그아웃 후 다시 로그인

# macOS에서는 보통 발생하지 않음
```

---

### 🟡 서버는 뜨지만 레시피가 0개

```bash
# DB 초기화 후 재시작
docker compose down -v
docker compose up --build
```

---

### 🟡 느리게 실행됨

Docker Desktop 설정에서 리소스 조정:
- Settings → Resources
- CPU: 2개 이상
- Memory: 4GB 이상

---

## 8. 프로젝트 구조 설명

### docker-compose.yml 해설

```yaml
version: '3.8'

services:
  # ── 1) PostgreSQL 데이터베이스 ──
  db:
    image: postgres:16-alpine        # PostgreSQL 16 경량 이미지
    container_name: meal-planner-db   # 컨테이너 이름
    environment:
      POSTGRES_DB: meal_planner       # 데이터베이스 이름
      POSTGRES_USER: postgres         # 사용자명
      POSTGRES_PASSWORD: postgres     # 비밀번호
      TZ: Asia/Seoul                  # 한국 시간대
    ports:
      - "5432:5432"                   # DB 포트
    volumes:
      - pgdata:/var/lib/postgresql/data  # 데이터 영구 저장
    healthcheck:                      # 건강 상태 확인
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10

  # ── 2) FastAPI 백엔드 ──
  backend:
    build:
      context: ./backend              # backend 폴더의 Dockerfile 사용
    container_name: meal-planner-api
    ports:
      - "8000:8000"                   # ← 이 포트로 접속!
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/meal_planner
                                      # ↑ "db"는 위의 서비스 이름
    depends_on:
      db:
        condition: service_healthy    # DB가 준비된 후 시작
    volumes:
      - ./backend:/app                # 코드 변경 시 자동 반영

volumes:
  pgdata:                             # DB 데이터 영구 저장 볼륨
```

### Dockerfile 해설

```dockerfile
FROM python:3.12-slim       # 1) Python 3.12 기반 이미지

RUN apt-get update && \     # 2) PostgreSQL 연결용 시스템 패키지
    apt-get install -y libpq-dev gcc curl

WORKDIR /app                # 3) 작업 디렉토리 설정

COPY requirements.txt .     # 4) 라이브러리 목록 복사
RUN pip install -r requirements.txt  # 5) 라이브러리 설치

COPY . .                    # 6) 앱 코드 전체 복사

EXPOSE 8000                 # 7) 8000번 포트 사용 선언

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
                            # 8) 서버 시작 명령어
```

### 데이터 흐름

```
사용자 (브라우저/앱)
    │
    ▼ HTTP 요청 (http://localhost:8000)
    │
┌───┴───────────────────────────┐
│  backend 컨테이너 (port 8000)  │
│                               │
│  FastAPI 앱                    │
│    ├── /api/users/            │
│    ├── /api/recipes/          │
│    ├── /api/menu/generate     │
│    └── /api/shopping/         │
│                               │
│  서버 시작 시:                 │
│    1. 테이블 자동 생성          │
│    2. 27 기본 레시피 시드       │
│    3. 43 추가 레시피 시드       │
│    4. 영양 매핑 보강           │
│                               │
└───┬───────────────────────────┘
    │ SQL 쿼리
    ▼
┌───┴───────────────────────────┐
│  db 컨테이너 (port 5432)       │
│                               │
│  PostgreSQL 16                 │
│    ├── ingredients (78개)      │
│    ├── recipes (70개)          │
│    ├── food_nutrients (64개)   │
│    ├── users                   │
│    ├── menu_plans              │
│    └── shopping_lists          │
│                               │
│  pgdata 볼륨 (영구 저장)       │
└───────────────────────────────┘
```

---

## 부록: 빠른 참조 카드

### 처음 설치 & 실행 (5분)

```bash
# 1. Docker Desktop 설치 후 실행
# 2. 압축 풀기
tar -xzf meal-planner-v1.1-final.tar.gz
cd meal-planner

# 3. 실행
docker compose up --build

# 4. 브라우저 접속
# → http://localhost:8000/docs
```

### 매일 사용

```bash
# 시작
cd meal-planner
docker compose up -d

# 종료
docker compose down

# 상태
docker compose ps
```

### 문제가 생기면

```bash
# 1단계: 상태 확인
docker compose ps

# 2단계: 로그 확인
docker compose logs --tail=30 backend

# 3단계: 완전 초기화
docker compose down -v
docker compose up --build
```

---

*식단 플래너 v1.1 — 2026-02-10*
