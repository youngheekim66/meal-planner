"""
인증 API: 회원가입, 로그인, 카카오 로그인, 내 정보
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx

from app.core.database import get_db
from app.models.models import User, UserPreference
from app.schemas.schemas import (
    SignupRequest, LoginRequest, TokenResponse, MeResponse, UserOut
)
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, require_login
)

router = APIRouter(prefix="/api/auth", tags=["인증"])

# ── 카카오 설정 ──
KAKAO_REST_API_KEY = "60fc8e550a28085642c3cdadc246d319"
KAKAO_REDIRECT_URI = "https://meal-planner-production-81ed.up.railway.app/api/auth/kakao/callback"
KAKAO_CLIENT_SECRET = "VBssKHU95uyiMREPeYkGioKpoeYI5SvR"

@router.post("/signup", response_model=TokenResponse, status_code=201,
             summary="회원가입")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 이메일입니다"
        )
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
        birth_year=req.birth_year,
        sex=req.sex,
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
        activity_level=req.activity_level,
    )
    db.add(user)
    db.flush()
    kcal = _calc_kcal(user)
    pref = UserPreference(user_id=user.id, kcal_target=kcal)
    db.add(pref)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user.id, name=user.name, birth_year=user.birth_year,
            sex=user.sex.value if user.sex else None,
            height_cm=user.height_cm, weight_kg=user.weight_kg,
            activity_level=user.activity_level, kcal_target=kcal
        )
    )


@router.post("/login", response_model=TokenResponse, summary="로그인")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")
    token = create_access_token(user.id)
    kcal = user.preferences.kcal_target if user.preferences else None
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user.id, name=user.name, birth_year=user.birth_year,
            sex=user.sex.value if user.sex else None,
            height_cm=user.height_cm, weight_kg=user.weight_kg,
            activity_level=user.activity_level, kcal_target=kcal
        )
    )


# ── 카카오 로그인 ──
@router.get("/kakao/login", summary="카카오 로그인 페이지로 이동")
def kakao_login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return RedirectResponse(url=kakao_auth_url)


@router.get("/kakao/callback", summary="카카오 로그인 콜백")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    # 1. 인가코드로 액세스 토큰 받기
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_REST_API_KEY,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "code": code,                "client_secret": KAKAO_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if token_res.status_code != 200:
        return RedirectResponse(
            url=f"/static/?error={token_res.text}"
        )

    kakao_token = token_res.json().get("access_token")

    # 2. 사용자 정보 가져오기
    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {kakao_token}"},
        )

    if user_res.status_code != 200:
        return RedirectResponse(
            url="/static/?error=kakao_user_failed"
        )

    kakao_data = user_res.json()
    kakao_id = str(kakao_data.get("id"))
    kakao_account = kakao_data.get("kakao_account", {})
    kakao_profile = kakao_account.get("profile", {})

    nickname = kakao_profile.get("nickname", "카카오유저")
    email = kakao_account.get("email")

    # 3. 기존 사용자 찾기 (kakao_id 또는 email)
    user = db.query(User).filter(User.kakao_id == kakao_id).first()

    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.kakao_id = kakao_id
            db.commit()

    # 4. 신규 사용자 생성
    if not user:
        user = User(
            kakao_id=kakao_id,
            email=email,
            name=nickname,
            hashed_password=None,
        )
        db.add(user)
        db.flush()
        pref = UserPreference(user_id=user.id, kcal_target=1800)
        db.add(pref)
        db.commit()
        db.refresh(user)

    # 5. JWT 토큰 생성 → 프론트엔드로 리다이렉트
    jwt_token = create_access_token(user.id)
    kcal = user.preferences.kcal_target if user.preferences else 1800

    redirect_url = (
        f"/static/"
        f"?token={jwt_token}"
        f"&user_id={user.id}"
        f"&user_name={nickname}"
        f"&user_kcal={kcal}"
    )
    return RedirectResponse(url=redirect_url)


@router.get("/me", response_model=MeResponse, summary="내 정보")
def get_me(user: User = Depends(require_login)):
    kcal = user.preferences.kcal_target if user.preferences else None
    return MeResponse(
        id=user.id, email=user.email, name=user.name,
        birth_year=user.birth_year,
        sex=user.sex.value if user.sex else None,
        height_cm=user.height_cm, weight_kg=user.weight_kg,
        activity_level=user.activity_level, kcal_target=kcal
    )


def _calc_kcal(user: User) -> int:
    if not all([user.birth_year, user.height_cm, user.weight_kg, user.sex]):
        return 1800
    from datetime import date
    age = date.today().year - user.birth_year
    if user.sex.value == "M":
        bmr = 66.5 + (13.75 * user.weight_kg) + (5.003 * user.height_cm) - (6.755 * age)
    else:
        bmr = 655.1 + (9.563 * user.weight_kg) + (1.850 * user.height_cm) - (4.676 * age)
    multiplier = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
    return int(bmr * multiplier.get(user.activity_level, 1.375))
