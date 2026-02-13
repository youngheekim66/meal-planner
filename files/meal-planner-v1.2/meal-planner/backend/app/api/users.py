from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.models.models import User, UserPreference
from app.schemas.schemas import (
    UserCreate, UserPreferenceUpdate, UserOut, TDEERequest, TDEEResponse
)
from app.services.nutrition_service import calculate_tdee

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = User(**data.model_dump())
    db.add(user)
    db.flush()

    pref = UserPreference(user_id=user.id)
    # TDEE 자동 계산
    if user.sex and user.height_cm and user.weight_kg and user.birth_year:
        age = date.today().year - user.birth_year
        tdee = calculate_tdee(user.sex.value, age, user.height_cm, user.weight_kg, user.activity_level)
        pref.kcal_target = tdee["recommended_kcal"]

    db.add(pref)
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id, name=user.name, birth_year=user.birth_year,
        sex=user.sex.value if user.sex else None,
        height_cm=user.height_cm, weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        kcal_target=pref.kcal_target,
    )


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다")
    pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    return UserOut(
        id=user.id, name=user.name, birth_year=user.birth_year,
        sex=user.sex.value if user.sex else None,
        height_cm=user.height_cm, weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        kcal_target=pref.kcal_target if pref else None,
    )


@router.put("/{user_id}/preferences")
def update_preferences(user_id: int, data: UserPreferenceUpdate, db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not pref:
        pref = UserPreference(user_id=user_id)
        db.add(pref)

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(pref, key, val)

    db.commit()
    return {"message": "설정이 업데이트되었습니다"}


@router.post("/tdee", response_model=TDEEResponse)
def calc_tdee(data: TDEERequest):
    result = calculate_tdee(data.sex.value, data.age, data.height_cm, data.weight_kg, data.activity_level)
    return TDEEResponse(**result)
