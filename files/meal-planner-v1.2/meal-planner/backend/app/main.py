"""
식단 플래너 API - 메인 진입점
실행: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base, SessionLocal
from app.api import users, recipes, menu, auth
from app.services.seed_data import run_seed


def _run_extra_seeds(db):
    """추가 레시피 + 영양 매핑 보강"""
    try:
        from app.services.seed_extra import run_seed_extra
        run_seed_extra(db)
    except Exception as e:
        print(f"⚠️ Extra seed: {e}")

    try:
        from app.services.seed_extra2 import run_seed_extra2, run_seed_extra2b
        # 소면 재료 보강
        from app.models.models import (
            Ingredient as Ing2, FoodNutrient as FN2,
            IngredientNutrientMap as INM2, MatchMethod as MM2
        )
        fn = db.query(FN2).filter(FN2.food_name == "소면").first()
        if not fn:
            fn = FN2(food_name="소면", kcal_per_100g=350, carb_g_per_100g=75,
                     protein_g_per_100g=10, fat_g_per_100g=1, sodium_mg_per_100g=5)
            db.add(fn); db.flush()
        ing = db.query(Ing2).filter(Ing2.name_std == "소면").first()
        if not ing:
            ing = Ing2(name_std="소면", category="곡류", default_unit="g")
            db.add(ing); db.flush()
            db.add(INM2(ingredient_id=ing.id, food_nutrient_id=fn.id,
                        match_confidence=1.0, match_method=MM2.MANUAL))
            db.commit()
        run_seed_extra2(db)
        run_seed_extra2b(db)
    except Exception as e:
        print(f"⚠️ Extra seed2: {e}")

    # 양념류 영양 매핑 보강
    try:
        from app.models.models import (
            Ingredient, FoodNutrient, IngredientNutrientMap, MatchMethod
        )
        extras = [
            ("된장", 128, 13.3, 12.0, 4.1, 4150),
            ("고추장", 180, 36.0, 5.0, 2.0, 3500),
            ("고춧가루", 282, 44.0, 12.0, 6.0, 100),
            ("간장", 53, 8.0, 8.0, 0.0, 5637),
            ("소금", 0, 0, 0, 0, 38758),
            ("설탕", 387, 100.0, 0, 0, 1),
            ("참기름", 884, 0, 0, 100.0, 0),
            ("식용유", 884, 0, 0, 100.0, 0),
            ("후추", 296, 55.8, 11.3, 3.3, 10),
            ("맛술", 134, 7.8, 0.1, 0, 7),
            ("멸치육수", 3, 0.2, 0.5, 0.1, 200),
            ("깻잎", 37, 4.6, 3.3, 0.6, 3),
            ("오이", 12, 2.4, 0.7, 0.1, 2),
            ("부추", 28, 3.3, 2.8, 0.4, 5),
            ("고추", 29, 5.3, 1.3, 0.3, 3),
            ("생강", 47, 8.6, 1.4, 0.6, 9),
            ("치즈", 371, 0.4, 23.0, 30.0, 640),
            ("멸치", 233, 0, 47.0, 4.0, 1860),
        ]
        for name, kcal, carb, pro, fat, sod in extras:
            fn = db.query(FoodNutrient).filter(FoodNutrient.food_name == name).first()
            if not fn:
                fn = FoodNutrient(
                    food_name=name, kcal_per_100g=kcal, carb_g_per_100g=carb,
                    protein_g_per_100g=pro, fat_g_per_100g=fat, sodium_mg_per_100g=sod
                )
                db.add(fn)
                db.flush()
            ing = db.query(Ingredient).filter(Ingredient.name_std == name).first()
            if ing:
                existing = db.query(IngredientNutrientMap).filter(
                    IngredientNutrientMap.ingredient_id == ing.id
                ).first()
                if not existing:
                    db.add(IngredientNutrientMap(
                        ingredient_id=ing.id, food_nutrient_id=fn.id,
                        match_confidence=1.0, match_method=MatchMethod.MANUAL
                    ))
        db.commit()
    except Exception as e:
        print(f"⚠️ Nutrient mapping: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 테이블 생성 + 시드 데이터
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_seed(db)
        _run_extra_seeds(db)
    except Exception as e:
        print(f"⚠️ Seed warning: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title="🍚 식단 플래너 API",
    description="50~70대를 위한 주간 메뉴/장보기/칼로리 관리",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS (Flutter 앱에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(menu.router)


@app.get("/")
def root():
    return {
        "app": "식단 플래너 API",
        "version": "1.1.0",
        "docs": "/docs",
        "features": ["70+ recipes", "auto rice nutrition", "weekly menu AI"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
