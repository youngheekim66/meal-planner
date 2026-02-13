"""
인증 API: 회원가입, 로그인, 내 정보
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, UserPreference
from app.schemas.schemas import (
    SignupRequest, LoginRequest, TokenResponse, MeResponse, UserOut
)
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, require_login
)

router = APIRouter(prefix="/api/auth", tags=["인증"])


@router.post("/signup", response_model=TokenResponse, status_code=201,
             summary="회원가입")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 이메일입니다"
        )

    # 사용자 생성
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

    # 칼로리 자동계산
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
    """해리스-베네딕트 공식으로 칼로리 계산"""
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
