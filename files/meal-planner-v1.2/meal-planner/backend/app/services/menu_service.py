"""
주간 메뉴 자동 생성 서비스
- 2주 로테이션 (A/B)
- 월~금 한식 위주, 주말 자유
- 중복/연속 페널티 기반 선택
- 장보기 리스트 자동 생성
"""
import random
from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models import (
    Recipe, RecipeIngredient, Ingredient, CuisineType, MealType,
    MenuPlan, MenuPlanItem, ShoppingList, ShoppingListItem,
    UserPreference
)
from app.services.nutrition_service import calculate_recipe_nutrition

# ─── 상비 재료 (장보기에서 분리) ──────────
PANTRY_CATEGORIES = {"양념"}
PANTRY_INGREDIENTS = {
    "간장", "된장", "고추장", "고춧가루", "소금", "설탕", "식용유",
    "참기름", "들기름", "식초", "후추", "다진마늘", "생강", "맛술",
    "굴소스", "국간장", "깨", "참깨", "통깨"
}

# ─── 주재료(단백질) 태그 ──────────────────
PROTEIN_TAGS = {"돼지고기", "소고기", "닭고기", "생선", "해산물", "두부", "달걀"}

APP_EPOCH = date(2025, 1, 6)  # 기준 월요일


def _get_rotation_key(week_start: date) -> str:
    """2주 로테이션: A/B"""
    weeks = (week_start - APP_EPOCH).days // 7
    return "A" if weeks % 2 == 0 else "B"


def _score_recipe(recipe: Recipe, selected: list[dict], current_date: date,
                  meal_type: str, user_pref: UserPreference | None) -> float:
    """
    후보 레시피에 페널티 점수를 매김 (낮을수록 좋음)
    """
    score = 0.0
    recipe_tags = set(recipe.tags or [])

    # 1) 7일 내 동일 레시피 사용 → 사실상 금지
    for item in selected:
        if item["recipe_id"] == recipe.id:
            days_diff = abs((current_date - item["date"]).days)
            if days_diff < 7:
                score += 1000

    # 2) 연속 같은 태그(국/찌개/볶음 등) 페널티
    yesterday_items = [s for s in selected if s["date"] == current_date - timedelta(days=1)]
    for yi in yesterday_items:
        overlap = recipe_tags & set(yi.get("tags", []))
        if overlap - PROTEIN_TAGS:  # 조리법 태그 겹침
            score += 30

    # 3) 연속 같은 주재료(단백질) 페널티
    for yi in yesterday_items:
        protein_overlap = recipe_tags & set(yi.get("tags", [])) & PROTEIN_TAGS
        if protein_overlap:
            score += 20

    # 4) 사용자 기피 재료
    if user_pref and user_pref.disliked_ingredients:
        # recipe.tags에 기피 재료가 포함되어 있으면 큰 페널티
        # (실제로는 recipe_ingredients에서 체크해야 정확하지만 MVP에서는 태그로)
        for tag in recipe_tags:
            if tag in [str(d) for d in user_pref.disliked_ingredients]:
                score += 500

    # 5) 약간의 랜덤성
    score += random.uniform(0, 5)

    return score


def generate_weekly_menu(db: Session, user_id: int, week_start: date) -> MenuPlan:
    """
    주간 메뉴 자동 생성 (월~일, 아침/점심/저녁)
    """
    rotation_key = _get_rotation_key(week_start)

    # 기존 메뉴 삭제 (재생성)
    existing = db.query(MenuPlan).filter(
        and_(MenuPlan.user_id == user_id, MenuPlan.week_start == week_start)
    ).first()
    if existing:
        db.delete(existing)
        db.flush()

    # 사용자 선호도
    user_pref = db.query(UserPreference).filter(
        UserPreference.user_id == user_id
    ).first()

    # 후보 레시피 로드
    all_recipes = db.query(Recipe).filter(Recipe.is_active == True).all()

    korean_recipes = [r for r in all_recipes if r.cuisine == CuisineType.KOREAN]
    breakfast_recipes = [r for r in all_recipes if "BREAKFAST" in (r.meal_types or [])]
    lunch_dinner_korean = [r for r in korean_recipes if
                           any(m in (r.meal_types or []) for m in ["LUNCH", "DINNER"])]
    lunch_dinner_all = [r for r in all_recipes if
                        any(m in (r.meal_types or []) for m in ["LUNCH", "DINNER"])]

    # 아침 후보가 적으면 전체에서 간편식 추가
    if len(breakfast_recipes) < 5:
        breakfast_recipes = [r for r in all_recipes if r.cook_time_min <= 15] or all_recipes[:10]

    # 메뉴 플랜 생성
    menu_plan = MenuPlan(
        user_id=user_id,
        week_start=week_start,
        rotation_key=rotation_key,
    )
    db.add(menu_plan)
    db.flush()

    selected_items = []  # 선택 기록 (중복 방지용)

    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)
        is_weekday = current_date.weekday() < 5  # 월(0)~금(4)

        for meal_type_str in ["BREAKFAST", "LUNCH", "DINNER"]:
            # 후보 풀 결정
            if meal_type_str == "BREAKFAST":
                candidates = breakfast_recipes
            elif is_weekday:
                candidates = lunch_dinner_korean if lunch_dinner_korean else lunch_dinner_all
            else:
                candidates = lunch_dinner_all

            if not candidates:
                candidates = all_recipes

            # 샘플링 + 최적 선택
            sample_size = min(30, len(candidates))
            sample = random.sample(candidates, sample_size)

            best_recipe = None
            best_score = float("inf")

            for recipe in sample:
                score = _score_recipe(recipe, selected_items, current_date, meal_type_str, user_pref)
                if score < best_score:
                    best_score = score
                    best_recipe = recipe

            if best_recipe is None:
                best_recipe = random.choice(candidates)

            # 영양 계산
            nutrition = calculate_recipe_nutrition(db, best_recipe.id, servings=1.0)

            item = MenuPlanItem(
                menu_plan_id=menu_plan.id,
                date=current_date,
                meal_type=MealType(meal_type_str),
                recipe_id=best_recipe.id,
                servings_for_user=1.0,
                kcal_est=nutrition.kcal if nutrition.calculable else None,
                macros_est={
                    "carb": nutrition.carb_g,
                    "protein": nutrition.protein_g,
                    "fat": nutrition.fat_g,
                    "sodium": nutrition.sodium_mg,
                } if nutrition.calculable else None,
            )
            db.add(item)

            selected_items.append({
                "recipe_id": best_recipe.id,
                "date": current_date,
                "meal_type": meal_type_str,
                "tags": best_recipe.tags or [],
            })

    db.flush()

    # 장보기 리스트 생성
    _generate_shopping_list(db, menu_plan)

    db.commit()
    db.refresh(menu_plan)
    return menu_plan


def _generate_shopping_list(db: Session, menu_plan: MenuPlan):
    """주간 메뉴의 모든 재료를 합산하여 장보기 리스트 생성"""
    shopping_list = ShoppingList(menu_plan_id=menu_plan.id)
    db.add(shopping_list)
    db.flush()

    # 재료 합산
    ingredient_totals: dict[int, dict] = {}

    items = db.query(MenuPlanItem).filter(
        MenuPlanItem.menu_plan_id == menu_plan.id
    ).all()

    for item in items:
        ri_list = db.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == item.recipe_id
        ).all()

        for ri in ri_list:
            key = ri.ingredient_id
            qty = ri.qty * item.servings_for_user

            if key in ingredient_totals:
                ingredient_totals[key]["qty"] += qty
            else:
                ingredient = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
                ingredient_totals[key] = {
                    "qty": qty,
                    "unit": ri.unit,
                    "ingredient": ingredient,
                }

    # 장보기 아이템 저장
    for ing_id, data in ingredient_totals.items():
        ingredient = data["ingredient"]
        is_pantry = (
            (ingredient and ingredient.category in PANTRY_CATEGORIES) or
            (ingredient and ingredient.name_std in PANTRY_INGREDIENTS)
        )

        sl_item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_id=ing_id,
            total_qty=round(data["qty"], 1),
            unit=data["unit"],
            is_pantry=is_pantry,
            checked=False,
        )
        db.add(sl_item)

    db.flush()


def replace_single_meal(db: Session, menu_plan_item_id: int) -> MenuPlanItem:
    """한 끼만 다른 레시피로 교체"""
    item = db.query(MenuPlanItem).filter(MenuPlanItem.id == menu_plan_item_id).first()
    if not item:
        raise ValueError("메뉴 아이템을 찾을 수 없습니다")

    is_weekday = item.date.weekday() < 5
    meal_type = item.meal_type.value

    all_recipes = db.query(Recipe).filter(Recipe.is_active == True).all()

    if meal_type == "BREAKFAST":
        candidates = [r for r in all_recipes if "BREAKFAST" in (r.meal_types or [])]
    elif is_weekday:
        candidates = [r for r in all_recipes
                      if r.cuisine == CuisineType.KOREAN
                      and any(m in (r.meal_types or []) for m in ["LUNCH", "DINNER"])]
    else:
        candidates = [r for r in all_recipes
                      if any(m in (r.meal_types or []) for m in ["LUNCH", "DINNER"])]

    # 현재 레시피 제외
    candidates = [r for r in candidates if r.id != item.recipe_id]

    if not candidates:
        candidates = [r for r in all_recipes if r.id != item.recipe_id]

    new_recipe = random.choice(candidates) if candidates else None
    if new_recipe:
        item.recipe_id = new_recipe.id
        nutrition = calculate_recipe_nutrition(db, new_recipe.id, servings=1.0)
        item.kcal_est = nutrition.kcal if nutrition.calculable else None
        item.macros_est = {
            "carb": nutrition.carb_g, "protein": nutrition.protein_g,
            "fat": nutrition.fat_g, "sodium": nutrition.sodium_mg,
        } if nutrition.calculable else None

        db.commit()
        db.refresh(item)

    return item
