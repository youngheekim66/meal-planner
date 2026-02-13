from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from collections import defaultdict

from app.core.database import get_db
from app.models.models import (
    MenuPlan, MenuPlanItem, ShoppingList, ShoppingListItem,
    Recipe, Ingredient
)
from app.schemas.schemas import (
    MenuPlanOut, MenuPlanItemOut, MenuPlanGenerate, RecipeOut,
    ShoppingListOut, ShoppingListItemOut, ShoppingItemCheck, IngredientOut
)
from app.services.menu_service import generate_weekly_menu, replace_single_meal
from app.services.nutrition_service import calculate_recipe_nutrition

router = APIRouter(prefix="/api", tags=["Menu & Shopping"])


# ─── Menu Plans ──────────────────────────────────────

def _build_menu_plan_out(db: Session, plan: MenuPlan) -> MenuPlanOut:
    items_out = []
    daily_kcal = defaultdict(float)

    for item in plan.items:
        recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
        if not recipe:
            continue

        nutrition = calculate_recipe_nutrition(db, recipe.id, servings=1.0)
        recipe_out = RecipeOut(
            id=recipe.id, title=recipe.title,
            cuisine=recipe.cuisine.value, tags=recipe.tags or [],
            meal_types=recipe.meal_types or [],
            difficulty=recipe.difficulty, cook_time_min=recipe.cook_time_min,
            servings=recipe.servings, steps=recipe.steps or [],
            source_type=recipe.source_type.value if recipe.source_type else "MANUAL",
            source_url=recipe.source_url, thumbnail_url=recipe.thumbnail_url,
            kcal_per_serving=nutrition.kcal if nutrition.calculable else None,
            macros_per_serving={
                "carb": nutrition.carb_g, "protein": nutrition.protein_g,
                "fat": nutrition.fat_g, "sodium": nutrition.sodium_mg,
            } if nutrition.calculable else None,
        )

        items_out.append(MenuPlanItemOut(
            id=item.id, date=item.date,
            meal_type=item.meal_type.value,
            recipe=recipe_out,
            servings_for_user=item.servings_for_user,
            kcal_est=item.kcal_est,
            macros_est=item.macros_est,
        ))

        if item.kcal_est:
            daily_kcal[str(item.date)] += item.kcal_est

    # 일별 요약
    daily_summary = [
        {"date": d, "total_kcal": round(k, 1)}
        for d, k in sorted(daily_kcal.items())
    ]
    total_kcal = round(sum(daily_kcal.values()), 1)

    return MenuPlanOut(
        id=plan.id, week_start=plan.week_start,
        rotation_key=plan.rotation_key,
        items=items_out, total_kcal=total_kcal,
        daily_summary=daily_summary,
    )


@router.post("/menu/generate", response_model=MenuPlanOut)
def generate_menu(data: MenuPlanGenerate, db: Session = Depends(get_db)):
    """주간 메뉴 자동 생성"""
    plan = generate_weekly_menu(db, data.user_id, data.week_start)
    return _build_menu_plan_out(db, plan)


@router.get("/menu/{user_id}/current", response_model=MenuPlanOut)
def get_current_menu(user_id: int, db: Session = Depends(get_db)):
    """현재 주 메뉴 조회"""
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    plan = db.query(MenuPlan).filter(
        MenuPlan.user_id == user_id,
        MenuPlan.week_start == monday,
    ).first()

    if not plan:
        raise HTTPException(404, "이번 주 메뉴가 아직 생성되지 않았습니다")

    return _build_menu_plan_out(db, plan)


@router.get("/menu/{user_id}/today")
def get_today_menu(user_id: int, db: Session = Depends(get_db)):
    """오늘 식단 조회 (홈 화면용)"""
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    plan = db.query(MenuPlan).filter(
        MenuPlan.user_id == user_id,
        MenuPlan.week_start == monday,
    ).first()

    if not plan:
        raise HTTPException(404, "이번 주 메뉴가 아직 생성되지 않았습니다")

    today_items = [item for item in plan.items if item.date == today]
    result = {"date": str(today), "meals": {}}
    total_kcal = 0

    for item in today_items:
        recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
        nutrition = calculate_recipe_nutrition(db, recipe.id, servings=1.0) if recipe else None

        meal_data = {
            "item_id": item.id,
            "recipe_id": recipe.id if recipe else None,
            "title": recipe.title if recipe else "알 수 없음",
            "cook_time_min": recipe.cook_time_min if recipe else 0,
            "difficulty": recipe.difficulty if recipe else 0,
            "thumbnail_url": recipe.thumbnail_url if recipe else None,
            "kcal": item.kcal_est,
            "steps": recipe.steps if recipe else [],
        }
        result["meals"][item.meal_type.value] = meal_data
        if item.kcal_est:
            total_kcal += item.kcal_est

    result["total_kcal"] = round(total_kcal, 1)
    return result


@router.post("/menu/item/{item_id}/replace")
def replace_menu_item(item_id: int, db: Session = Depends(get_db)):
    """한 끼 교체"""
    try:
        item = replace_single_meal(db, item_id)
        recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first()
        return {
            "item_id": item.id,
            "new_recipe": recipe.title if recipe else None,
            "kcal_est": item.kcal_est,
        }
    except ValueError as e:
        raise HTTPException(404, str(e))


# ─── Shopping Lists ──────────────────────────────────

@router.get("/shopping/{user_id}/current", response_model=ShoppingListOut)
def get_current_shopping(user_id: int, db: Session = Depends(get_db)):
    """이번 주 장보기 리스트"""
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    plan = db.query(MenuPlan).filter(
        MenuPlan.user_id == user_id,
        MenuPlan.week_start == monday,
    ).first()

    if not plan or not plan.shopping_list:
        raise HTTPException(404, "장보기 리스트가 없습니다")

    sl = plan.shopping_list
    items = []
    categories = defaultdict(list)

    for si in sl.items:
        ing = db.query(Ingredient).filter(Ingredient.id == si.ingredient_id).first()
        item_out = ShoppingListItemOut(
            id=si.id,
            ingredient=IngredientOut(
                id=ing.id, name_std=ing.name_std,
                category=ing.category, default_unit=ing.default_unit
            ) if ing else None,
            total_qty=si.total_qty,
            unit=si.unit,
            is_pantry=si.is_pantry,
            checked=si.checked,
            note=si.note,
        )
        items.append(item_out)
        cat = ing.category if ing else "기타"
        categories[cat].append(item_out.model_dump())

    return ShoppingListOut(
        id=sl.id, menu_plan_id=sl.menu_plan_id,
        items=items, categories=dict(categories),
    )


@router.patch("/shopping/item/check")
def check_shopping_item(data: ShoppingItemCheck, db: Session = Depends(get_db)):
    """장보기 아이템 체크/해제"""
    item = db.query(ShoppingListItem).filter(ShoppingListItem.id == data.item_id).first()
    if not item:
        raise HTTPException(404, "아이템을 찾을 수 없습니다")
    item.checked = data.checked
    db.commit()
    return {"message": "업데이트 완료"}
