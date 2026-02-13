# ============================================
# recipes.py 에 추가할 DELETE 엔드포인트
# ============================================
# 위치: backend/app/api/recipes.py
# 기존 코드 맨 아래에 아래 함수를 추가하세요.
# ============================================

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
