"""
영양 계산 서비스
- BMR/TDEE 계산 (Mifflin-St Jeor)
- 레시피별 영양소 합산
- 밥 자동 합산 (국/찌개/반찬에 밥 포함)
"""
from sqlalchemy.orm import Session
from app.models.models import (
    Recipe, RecipeIngredient, IngredientNutrientMap, FoodNutrient, Ingredient
)
from app.schemas.schemas import NutritionSummary


# ─── 활동계수 ────────────────────────
ACTIVITY_MULTIPLIERS = {
    1: 1.2,    # 비활동적 (좌식)
    2: 1.375,  # 가벼운 활동
    3: 1.55,   # 보통 활동
    4: 1.725,  # 활발한 활동
    5: 1.9,    # 매우 활발
}

# ─── 밥 자동 합산 설정 ────────────────
# 1인분 밥 (200g 기준) 영양소
RICE_NUTRITION = {
    "grams": 200,       # 1공기 기준
    "kcal": 310,         # 200g 기준
    "carb_g": 68.0,
    "protein_g": 5.4,
    "fat_g": 0.6,
    "sodium_mg": 2.0,
}

# 제목에 이미 밥이 포함된 레시피 (밥 추가 불필요)
RICE_INCLUDED_KEYWORDS = [
    "밥", "죽", "볶음밥", "김밥", "국밥", "비빔밥", "덮밥",
    "라면", "떡볶이", "떡국", "만두국", "수제비", "칼국수",
    "우동", "누룽지", "토스트", "빵", "수프", "샐러드",
]

# 밥과 함께 먹는 레시피 태그 (밥 추가 필요)
NEEDS_RICE_TAGS = [
    "국", "찌개", "탕", "조림", "볶음", "구이", "나물",
    "찜", "전", "무침", "반찬", "쌈",
]


def recipe_needs_rice(recipe: Recipe) -> bool:
    """레시피가 밥을 별도 추가해야 하는지 판단"""
    title = recipe.title or ""

    # 1) 이미 밥이 포함된 레시피 제외
    for kw in RICE_INCLUDED_KEYWORDS:
        if kw in title:
            return False

    # 2) 아침 전용이면 제외 (죽, 토스트 등)
    if recipe.meal_types == ["BREAKFAST"]:
        return False

    # 3) 태그 기반 판단
    tags = recipe.tags or []
    for tag in tags:
        if tag in NEEDS_RICE_TAGS:
            return True

    # 4) 한식 메인 요리는 기본적으로 밥과 함께
    from app.models.models import CuisineType
    if recipe.cuisine == CuisineType.KOREAN:
        return True

    return False


def calculate_bmr(sex: str, age: int, height_cm: float, weight_kg: float) -> float:
    """Mifflin-St Jeor 공식"""
    if sex == "M":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(sex: str, age: int, height_cm: float, weight_kg: float,
                   activity_level: int = 2) -> dict:
    """TDEE + 끼니별 권장 칼로리"""
    bmr = calculate_bmr(sex, age, height_cm, weight_kg)
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.375)
    tdee = bmr * multiplier

    recommended = round(tdee)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "recommended_kcal": recommended,
        "breakdown": {
            "breakfast": round(recommended * 0.25),
            "lunch": round(recommended * 0.40),
            "dinner": round(recommended * 0.35),
        }
    }


def calculate_recipe_nutrition(db: Session, recipe_id: int, servings: float = 1.0,
                                include_rice: bool = None) -> NutritionSummary:
    """
    레시피의 1인분 영양소 계산
    include_rice: None이면 자동 판단, True/False면 강제 지정
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        return NutritionSummary(calculable=False)

    ri_list = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).all()

    total_kcal = 0.0
    total_carb = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_sodium = 0.0
    missing = []
    calculable = True

    for ri in ri_list:
        if ri.qty_in_grams is None or ri.qty_in_grams <= 0:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
            missing.append(ingredient.name_std if ingredient else f"재료#{ri.ingredient_id}")
            calculable = False
            continue

        mapping = db.query(IngredientNutrientMap).filter(
            IngredientNutrientMap.ingredient_id == ri.ingredient_id
        ).first()

        if not mapping:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
            missing.append(ingredient.name_std if ingredient else f"재료#{ri.ingredient_id}")
            calculable = False
            continue

        nutrient = db.query(FoodNutrient).filter(
            FoodNutrient.id == mapping.food_nutrient_id
        ).first()

        if not nutrient:
            continue

        grams = ri.qty_in_grams
        total_kcal += grams * nutrient.kcal_per_100g / 100
        total_carb += grams * nutrient.carb_g_per_100g / 100
        total_protein += grams * nutrient.protein_g_per_100g / 100
        total_fat += grams * nutrient.fat_g_per_100g / 100
        total_sodium += grams * nutrient.sodium_mg_per_100g / 100

    # 1인분 기준
    recipe_servings = recipe.servings or 1
    per_serving = servings / recipe_servings if recipe_servings > 0 else 1

    kcal = total_kcal * per_serving
    carb = total_carb * per_serving
    protein = total_protein * per_serving
    fat = total_fat * per_serving
    sodium = total_sodium * per_serving

    # ─── 밥 자동 합산 ───
    add_rice = include_rice if include_rice is not None else recipe_needs_rice(recipe)
    if add_rice:
        rice = RICE_NUTRITION
        kcal += rice["kcal"]
        carb += rice["carb_g"]
        protein += rice["protein_g"]
        fat += rice["fat_g"]
        sodium += rice["sodium_mg"]

    return NutritionSummary(
        kcal=round(kcal, 1),
        carb_g=round(carb, 1),
        protein_g=round(protein, 1),
        fat_g=round(fat, 1),
        sodium_mg=round(sodium, 1),
        calculable=calculable,
        missing_ingredients=missing,
        includes_rice=add_rice,
    )
