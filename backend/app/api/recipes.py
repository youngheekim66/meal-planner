from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from pydantic import BaseModel      # ← 이 줄만 추가

from app.core.database import get_db
from app.models.models import Recipe, RecipeIngredient, Ingredient, CuisineType
from app.schemas.schemas import RecipeOut, RecipeCreate, RecipeIngredientOut, IngredientOut, NutritionSummary
from app.services.nutrition_service import calculate_recipe_nutrition

router = APIRouter(prefix="/api/recipes", tags=["Recipes"])


def _recipe_to_out(db: Session, recipe: Recipe) -> RecipeOut:
    nutrition = calculate_recipe_nutrition(db, recipe.id, servings=1.0)
    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        cuisine=recipe.cuisine.value,
        tags=recipe.tags or [],
        meal_types=recipe.meal_types or [],
        difficulty=recipe.difficulty,
        cook_time_min=recipe.cook_time_min,
        servings=recipe.servings,
        steps=recipe.steps or [],
        source_type=recipe.source_type.value if recipe.source_type else "MANUAL",
        source_url=recipe.source_url,
        thumbnail_url=recipe.thumbnail_url,
        youtube_url=recipe.youtube_url,
        kcal_per_serving=nutrition.kcal if nutrition.calculable else None,
        macros_per_serving={
            "carb": nutrition.carb_g, "protein": nutrition.protein_g,
            "fat": nutrition.fat_g, "sodium": nutrition.sodium_mg,
        } if nutrition.calculable else None,
    )


@router.get("/", response_model=list[RecipeOut])
def list_recipes(
    cuisine: Optional[str] = None,
    tag: Optional[str] = None,
    meal_type: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Recipe).filter(Recipe.is_active == True)
    if cuisine:
        q = q.filter(Recipe.cuisine == CuisineType(cuisine))
    recipes = q.offset(offset).limit(limit).all()
    return [_recipe_to_out(db, r) for r in recipes]


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(404, "레시피를 찾을 수 없습니다")
    return _recipe_to_out(db, recipe)


@router.get("/{recipe_id}/ingredients")
def get_recipe_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    ri_list = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).all()
    result = []
    for ri in ri_list:
        ing = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
        result.append({
            "ingredient": {"id": ing.id, "name_std": ing.name_std, "category": ing.category} if ing else None,
            "qty": ri.qty, "unit": ri.unit,
            "qty_in_grams": ri.qty_in_grams, "note": ri.note,
        })
    return result


@router.get("/{recipe_id}/nutrition", response_model=NutritionSummary)
def get_recipe_nutrition(recipe_id: int, servings: float = 1.0, db: Session = Depends(get_db)):
    return calculate_recipe_nutrition(db, recipe_id, servings)


@router.post("/", response_model=RecipeOut)
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)):
    recipe = Recipe(
        title=data.title, cuisine=CuisineType(data.cuisine),
        tags=data.tags, meal_types=data.meal_types,
        difficulty=data.difficulty, cook_time_min=data.cook_time_min,
        servings=data.servings, steps=data.steps,
        source_type=data.source_type, source_url=data.source_url,
        thumbnail_url=data.thumbnail_url,
    )
    db.add(recipe)
    db.flush()

    for ing_data in data.ingredients:
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_data["ingredient_id"],
            qty=ing_data["qty"],
            unit=ing_data.get("unit", "g"),
            qty_in_grams=ing_data.get("qty_in_grams"),
            note=ing_data.get("note"),
        )
        db.add(ri)

    db.commit()
    db.refresh(recipe)
    return _recipe_to_out(db, recipe)


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """레시피 삭제 (soft delete)"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # 연결된 재료 먼저 삭제
    db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).delete()

    # soft delete (is_active = False)
    recipe.is_active = False
    db.commit()

    return {"message": f"Recipe {recipe_id} ({recipe.title}) deleted"}


@router.delete("/hard/{recipe_id}")
def hard_delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """레시피 완전 삭제 (DB에서 제거)"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # 연결된 재료 먼저 삭제
    db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).delete()

    db.delete(recipe)
    db.commit()

    return {"message": f"Recipe {recipe_id} ({recipe.title}) permanently deleted"}


# === YouTube URL 업데이트 ===
class RecipeUpdate(BaseModel):
    youtube_url: str = None

@router.patch("/{recipe_id}")
def update_recipe_youtube(recipe_id: int, data: RecipeUpdate, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if data.youtube_url is not None:
        recipe.youtube_url = data.youtube_url
    db.commit()
    db.refresh(recipe)
    return {"id": recipe.id, "title": recipe.title, "youtube_url": recipe.youtube_url}