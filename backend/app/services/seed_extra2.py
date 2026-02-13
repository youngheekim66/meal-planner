"""
추가 레시피 35개 시드 (3차)
기존 70개 → 총 105개 레시피
부족 카테고리 보강: 아침(+5), 생선(+5), 닭(+3), 채소(+4), 주말자유(+8), 한식반찬(+10)
"""
from app.core.database import SessionLocal
from app.models.models import (
    Recipe, Ingredient, RecipeIngredient, FoodNutrient,
    IngredientNutrientMap, CuisineType, MealType, SourceType, MatchMethod
)


def _get_or_create_ingredient(db, name, category, default_unit, weight=None):
    ing = db.query(Ingredient).filter(Ingredient.name_std == name).first()
    if not ing:
        kwargs = {"name_std": name, "category": category, "default_unit": default_unit}
        if default_unit in ("개", "장") and weight:
            kwargs["avg_weight_per_piece_g"] = weight
        ing = Ingredient(**kwargs)
        db.add(ing)
        db.flush()
    return ing


def _get_or_create_nutrient(db, name, kcal, carb, pro, fat, sod):
    fn = db.query(FoodNutrient).filter(FoodNutrient.food_name == name).first()
    if not fn:
        fn = FoodNutrient(food_name=name, kcal_per_100g=kcal, carb_g_per_100g=carb,
                          protein_g_per_100g=pro, fat_g_per_100g=fat, sodium_mg_per_100g=sod)
        db.add(fn)
        db.flush()
    return fn


def _ensure_mapping(db, ing, fn):
    existing = db.query(IngredientNutrientMap).filter(
        IngredientNutrientMap.ingredient_id == ing.id).first()
    if not existing:
        db.add(IngredientNutrientMap(
            ingredient_id=ing.id, food_nutrient_id=fn.id,
            match_confidence=1.0, match_method=MatchMethod.MANUAL))


def run_seed_extra2(db):
    existing = db.query(Recipe).count()
    if existing >= 100:
        print(f"이미 {existing}개 레시피 존재 - 스킵")
        return

    # ── 신규 재료 ──
    new_ingredients = [
        ("삼치", "해산물", "g", None, 153, 0, 20.0, 8.0, 60),
        ("코다리", "해산물", "g", None, 82, 0, 18.0, 0.8, 150),
        ("꽃게", "해산물", "g", None, 63, 0, 12.5, 1.0, 300),
        ("전복", "해산물", "g", None, 78, 6.0, 14.0, 0.5, 300),
        ("바지락", "해산물", "g", None, 72, 2.5, 12.6, 1.0, 400),
        ("오징어(건)", "해산물", "g", None, 280, 5.0, 60.0, 2.0, 500),
        ("닭날개", "육류", "g", None, 203, 0, 18.3, 14.0, 75),
        ("목살", "육류", "g", None, 220, 0, 17.0, 16.0, 60),
        ("고구마", "채소", "g", None, 86, 20.1, 1.6, 0.1, 34),
        ("단호박", "채소", "g", None, 40, 8.8, 1.2, 0.2, 1),
        ("연근", "채소", "g", None, 66, 16.0, 1.6, 0.1, 40),
        ("우엉", "채소", "g", None, 72, 17.0, 1.5, 0.1, 18),
        ("미나리", "채소", "g", None, 17, 2.4, 2.0, 0.3, 64),
        ("청경채", "채소", "g", None, 13, 2.2, 1.5, 0.2, 65),
        ("치즈", "유제품", "g", None, 371, 0.4, 23.0, 30.0, 640),
        ("베이컨", "육류", "g", None, 417, 1.0, 12.0, 42.0, 1500),
        ("어묵", "해산물", "g", None, 113, 11.0, 9.0, 4.0, 800),
        ("당면(건)", "곡류", "g", None, 332, 83.0, 0.1, 0.1, 10),
        ("메밀면", "곡류", "g", None, 115, 24.0, 5.0, 0.7, 200),
        ("현미", "곡류", "g", None, 350, 74.0, 7.0, 2.7, 7),
        ("잣", "기타", "g", None, 673, 13.0, 14.0, 68.0, 2),
        ("깨", "기타", "g", None, 586, 18.0, 18.0, 50.0, 11),
    ]

    for name, cat, unit, weight, kcal, carb, pro, fat, sod in new_ingredients:
        ing = _get_or_create_ingredient(db, name, cat, unit, weight)
        fn = _get_or_create_nutrient(db, name, kcal, carb, pro, fat, sod)
        _ensure_mapping(db, ing, fn)
    db.flush()

    def ing(name):
        return db.query(Ingredient).filter(Ingredient.name_std == name).first()

    new_recipes = [
        # ── 아침 추가 5개 ──
        {
            "title": "고구마죽", "cuisine": CuisineType.KOREAN, "tags": ["죽", "간편식"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 25, "servings": 1,
            "steps": [{"step": 1, "text": "고구마를 삶아 으깬다"},
                      {"step": 2, "text": "찹쌀가루와 물을 넣고 약불에 끓인다"},
                      {"step": 3, "text": "소금으로 간해 잣을 올려 완성"}],
            "ingredients": [("고구마", 150, "g", 150), ("찹쌀", 30, "g", 30), ("소금", 1, "g", 1)]
        },
        {
            "title": "현미밥 + 달걀프라이", "cuisine": CuisineType.KOREAN, "tags": ["밥", "간편식"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "현미밥을 준비한다"},
                      {"step": 2, "text": "달걀을 프라이해 밥 위에 올린다"},
                      {"step": 3, "text": "간장을 살짝 뿌려 완성"}],
            "ingredients": [("현미", 200, "g", 200), ("달걀", 1, "개", 60), ("간장", 5, "ml", 5)]
        },
        {
            "title": "단호박수프", "cuisine": CuisineType.FREE, "tags": ["수프", "간편식"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "단호박을 삶아 껍질을 벗기고 으깬다"},
                      {"step": 2, "text": "우유와 함께 냄비에 끓인다"},
                      {"step": 3, "text": "소금으로 간해 완성"}],
            "ingredients": [("단호박", 200, "g", 200), ("우유", 200, "ml", 200), ("소금", 1, "g", 1)]
        },
        {
            "title": "전복죽", "cuisine": CuisineType.KOREAN, "tags": ["죽", "해산물"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 2, "cook_time_min": 30, "servings": 1,
            "steps": [{"step": 1, "text": "전복을 손질해 잘게 다진다"},
                      {"step": 2, "text": "참기름에 전복과 불린 쌀을 볶는다"},
                      {"step": 3, "text": "물을 넣고 약불에 저으며 끓여 완성"}],
            "ingredients": [("전복", 60, "g", 60), ("쌀", 80, "g", 80), ("참기름", 5, "ml", 5)]
        },
        {
            "title": "베이컨 토스트", "cuisine": CuisineType.FREE, "tags": ["토스트", "간편식"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "베이컨을 바삭하게 굽는다"},
                      {"step": 2, "text": "빵을 토스트한다"},
                      {"step": 3, "text": "빵 위에 베이컨과 치즈를 올려 완성"}],
            "ingredients": [("빵", 60, "g", 60), ("베이컨", 30, "g", 30), ("치즈", 20, "g", 20)]
        },

        # ── 생선/해산물 보강 5개 ──
        {
            "title": "삼치 구이", "cuisine": CuisineType.KOREAN, "tags": ["구이", "생선"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "삼치에 소금을 뿌려 10분 재운다"},
                      {"step": 2, "text": "팬에 기름을 두르고 앞뒤로 굽는다"},
                      {"step": 3, "text": "레몬즙이나 간장을 곁들여 완성"}],
            "ingredients": [("삼치", 150, "g", 150), ("소금", 2, "g", 2), ("식용유", 5, "ml", 5)]
        },
        {
            "title": "코다리조림", "cuisine": CuisineType.KOREAN, "tags": ["조림", "생선"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "코다리를 토막내어 준비한다"},
                      {"step": 2, "text": "고추장, 간장, 설탕 양념장을 만든다"},
                      {"step": 3, "text": "무를 깔고 코다리와 양념장을 넣어 조린다"}],
            "ingredients": [("코다리", 200, "g", 200), ("무", 100, "g", 100),
                           ("고추장", 15, "g", 15), ("간장", 15, "ml", 15)]
        },
        {
            "title": "꽃게탕", "cuisine": CuisineType.KOREAN, "tags": ["탕", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "꽃게를 깨끗이 손질한다"},
                      {"step": 2, "text": "애호박, 두부, 대파를 준비한다"},
                      {"step": 3, "text": "된장을 풀고 꽃게와 채소를 넣어 끓인다"}],
            "ingredients": [("꽃게", 200, "g", 200), ("애호박", 80, "g", 80),
                           ("두부", 100, "g", 100), ("된장", 15, "g", 15)]
        },
        {
            "title": "바지락칼국수", "cuisine": CuisineType.KOREAN, "tags": ["면류", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "바지락을 해감한 후 육수를 낸다"},
                      {"step": 2, "text": "칼국수면과 애호박을 넣고 끓인다"},
                      {"step": 3, "text": "대파를 넣어 완성"}],
            "ingredients": [("바지락", 100, "g", 100), ("칼국수면", 150, "g", 150),
                           ("애호박", 50, "g", 50), ("대파", 15, "g", 15)]
        },
        {
            "title": "어묵탕", "cuisine": CuisineType.KOREAN, "tags": ["탕", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "어묵을 꼬치에 꿰거나 먹기 좋게 자른다"},
                      {"step": 2, "text": "멸치육수에 무를 넣고 끓인다"},
                      {"step": 3, "text": "어묵과 대파를 넣고 간장으로 간해 완성"}],
            "ingredients": [("어묵", 150, "g", 150), ("무", 80, "g", 80),
                           ("대파", 20, "g", 20), ("간장", 10, "ml", 10)]
        },

        # ── 닭고기 보강 3개 ──
        {
            "title": "닭날개조림", "cuisine": CuisineType.KOREAN, "tags": ["조림", "닭고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "닭날개를 끓는 물에 데쳐 기름기를 뺀다"},
                      {"step": 2, "text": "간장, 설탕, 마늘 양념장을 만든다"},
                      {"step": 3, "text": "닭날개를 양념장에 넣고 졸여 완성"}],
            "ingredients": [("닭날개", 300, "g", 300), ("간장", 30, "ml", 30),
                           ("설탕", 15, "g", 15), ("마늘", 10, "g", 10)]
        },
        {
            "title": "닭가슴살 덮밥", "cuisine": CuisineType.FREE, "tags": ["덮밥", "닭고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "닭가슴살을 한입 크기로 썰어 볶는다"},
                      {"step": 2, "text": "양파, 파프리카를 넣고 간장소스로 볶는다"},
                      {"step": 3, "text": "밥 위에 올려 완성"}],
            "ingredients": [("닭가슴살", 150, "g", 150), ("양파", 80, "g", 80),
                           ("파프리카", 50, "g", 50), ("쌀", 200, "g", 200)]
        },
        {
            "title": "삼계탕(간편)", "cuisine": CuisineType.KOREAN, "tags": ["탕", "닭고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 40, "servings": 1,
            "steps": [{"step": 1, "text": "닭고기에 찹쌀, 마늘, 대파를 넣는다"},
                      {"step": 2, "text": "물을 넣고 40분간 끓인다"},
                      {"step": 3, "text": "소금, 후추로 간해 완성"}],
            "ingredients": [("닭고기", 300, "g", 300), ("찹쌀", 30, "g", 30),
                           ("마늘", 10, "g", 10), ("대파", 20, "g", 20)]
        },

        # ── 채소/건강 반찬 보강 4개 ──
        {
            "title": "연근조림", "cuisine": CuisineType.KOREAN, "tags": ["조림", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "연근을 얇게 슬라이스한다"},
                      {"step": 2, "text": "식초물에 데쳐 아린 맛을 뺀다"},
                      {"step": 3, "text": "간장, 설탕, 물엿으로 조린다"}],
            "ingredients": [("연근", 200, "g", 200), ("간장", 20, "ml", 20), ("설탕", 10, "g", 10)]
        },
        {
            "title": "우엉조림", "cuisine": CuisineType.KOREAN, "tags": ["조림", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "우엉을 얇게 어슷 썬다"},
                      {"step": 2, "text": "식초물에 담가 변색을 방지한다"},
                      {"step": 3, "text": "간장, 설탕, 참기름으로 볶아 조린다"}],
            "ingredients": [("우엉", 150, "g", 150), ("간장", 15, "ml", 15),
                           ("설탕", 10, "g", 10), ("참기름", 5, "ml", 5)]
        },
        {
            "title": "고구마줄기볶음", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "고구마줄기를 삶아 껍질을 벗긴다"},
                      {"step": 2, "text": "들기름에 볶는다"},
                      {"step": 3, "text": "간장, 깨로 간해 완성"}],
            "ingredients": [("고구마", 200, "g", 200), ("간장", 10, "ml", 10), ("참기름", 5, "ml", 5)]
        },
        {
            "title": "청경채볶음", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "채소"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "청경채를 반으로 자른다"},
                      {"step": 2, "text": "마늘을 넣고 센 불에 볶는다"},
                      {"step": 3, "text": "소금으로 간해 완성"}],
            "ingredients": [("청경채", 200, "g", 200), ("마늘", 5, "g", 5),
                           ("식용유", 10, "ml", 10), ("소금", 1, "g", 1)]
        },

        # ── 주말 자유메뉴 보강 8개 ──
        {
            "title": "볶음밥(베이컨)", "cuisine": CuisineType.FREE, "tags": ["볶음밥", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "베이컨을 잘게 썰어 볶는다"},
                      {"step": 2, "text": "달걀을 넣어 스크램블한다"},
                      {"step": 3, "text": "밥을 넣고 간장으로 간해 완성"}],
            "ingredients": [("베이컨", 40, "g", 40), ("달걀", 1, "개", 60),
                           ("쌀", 200, "g", 200), ("간장", 10, "ml", 10)]
        },
        {
            "title": "치즈떡볶이", "cuisine": CuisineType.FREE, "tags": ["떡볶이", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "고추장 양념장을 만든다"},
                      {"step": 2, "text": "떡과 어묵을 넣고 끓인다"},
                      {"step": 3, "text": "치즈를 올려 녹여 완성"}],
            "ingredients": [("떡", 200, "g", 200), ("어묵", 80, "g", 80),
                           ("고추장", 20, "g", 20), ("치즈", 30, "g", 30)]
        },
        {
            "title": "메밀국수", "cuisine": CuisineType.FREE, "tags": ["면류", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "메밀면을 삶아 찬물에 헹군다"},
                      {"step": 2, "text": "간장 양념장을 만든다"},
                      {"step": 3, "text": "면 위에 김, 대파를 올려 양념장에 찍어 먹는다"}],
            "ingredients": [("메밀면", 150, "g", 150), ("간장", 15, "ml", 15),
                           ("김", 2, "장", 6), ("대파", 10, "g", 10)]
        },
        {
            "title": "오므라이스", "cuisine": CuisineType.FREE, "tags": ["덮밥", "달걀"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "양파, 당근을 다져 볶은 뒤 밥을 넣어 볶음밥을 만든다"},
                      {"step": 2, "text": "달걀 2개를 풀어 얇게 부친다"},
                      {"step": 3, "text": "볶음밥을 달걀로 감싸 케첩을 뿌려 완성"}],
            "ingredients": [("달걀", 2, "개", 120), ("쌀", 200, "g", 200),
                           ("양파", 50, "g", 50), ("당근", 30, "g", 30)]
        },
        {
            "title": "소시지 김밥", "cuisine": CuisineType.FREE, "tags": ["김밥", "간편식"],
            "meal_types": [MealType.LUNCH], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "밥에 참기름, 소금을 넣고 섞는다"},
                      {"step": 2, "text": "소시지를 길게 구워 준비한다"},
                      {"step": 3, "text": "김에 밥, 소시지, 당근, 시금치를 올려 말아 완성"}],
            "ingredients": [("쌀", 300, "g", 300), ("소시지", 80, "g", 80),
                           ("김", 4, "장", 12), ("당근", 50, "g", 50)]
        },
        {
            "title": "어묵볶음", "cuisine": CuisineType.FREE, "tags": ["볶음", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "어묵을 먹기 좋게 썬다"},
                      {"step": 2, "text": "양파, 대파와 함께 볶는다"},
                      {"step": 3, "text": "간장, 고추장 양념으로 간해 완성"}],
            "ingredients": [("어묵", 150, "g", 150), ("양파", 80, "g", 80),
                           ("대파", 20, "g", 20), ("간장", 10, "ml", 10)]
        },

        # ── 한식 메인 보강 5개 ──
        {
            "title": "목살구이", "cuisine": CuisineType.KOREAN, "tags": ["구이", "돼지고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "목살을 1cm 두께로 썬다"},
                      {"step": 2, "text": "소금, 후추로 간해 팬에 굽는다"},
                      {"step": 3, "text": "깻잎, 마늘과 함께 쌈으로 완성"}],
            "ingredients": [("목살", 200, "g", 200), ("깻잎", 20, "g", 20),
                           ("마늘", 10, "g", 10), ("소금", 2, "g", 2)]
        },
        {
            "title": "소불고기", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "소고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "소고기를 간장, 설탕, 배즙 양념에 30분 재운다"},
                      {"step": 2, "text": "양파, 대파, 당근과 함께 팬에 볶는다"},
                      {"step": 3, "text": "참기름을 넣어 완성"}],
            "ingredients": [("소고기", 200, "g", 200), ("양파", 80, "g", 80),
                           ("당근", 30, "g", 30), ("간장", 30, "ml", 30)]
        },
        {
            "title": "오징어무침", "cuisine": CuisineType.KOREAN, "tags": ["무침", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "오징어를 데쳐서 먹기 좋게 썬다"},
                      {"step": 2, "text": "고추장, 식초, 설탕으로 양념장을 만든다"},
                      {"step": 3, "text": "오징어와 채소를 양념에 버무려 완성"}],
            "ingredients": [("오징어(건)", 80, "g", 80), ("양파", 50, "g", 50),
                           ("고추장", 15, "g", 15), ("설탕", 5, "g", 5)]
        },
        {
            "title": "고구마맛탕", "cuisine": CuisineType.KOREAN, "tags": ["간식", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "고구마를 깍둑 썰어 기름에 튀긴다"},
                      {"step": 2, "text": "설탕 시럽을 만든다"},
                      {"step": 3, "text": "고구마에 시럽을 입혀 완성"}],
            "ingredients": [("고구마", 300, "g", 300), ("설탕", 30, "g", 30),
                           ("식용유", 30, "ml", 30)]
        },
        {
            "title": "단호박찜", "cuisine": CuisineType.KOREAN, "tags": ["찜", "채소"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "단호박을 반으로 갈라 씨를 제거한다"},
                      {"step": 2, "text": "찜기에 20분 찐다"},
                      {"step": 3, "text": "꿀이나 설탕을 뿌려 완성"}],
            "ingredients": [("단호박", 300, "g", 300), ("설탕", 5, "g", 5)]
        },
    ]

    added = 0
    for r_data in new_recipes:
        existing = db.query(Recipe).filter(Recipe.title == r_data["title"]).first()
        if existing:
            continue

        recipe = Recipe(
            title=r_data["title"],
            cuisine=r_data["cuisine"],
            tags=r_data.get("tags", []),
            meal_types=[mt.value for mt in r_data["meal_types"]],
            difficulty=r_data["difficulty"],
            cook_time_min=r_data["cook_time_min"],
            servings=r_data["servings"],
            steps=r_data["steps"],
            source_type=SourceType.MANUAL,
        )
        db.add(recipe)
        db.flush()

        for ing_name, qty, unit, qty_g in r_data["ingredients"]:
            ingredient = ing(ing_name)
            if not ingredient:
                print(f"  ⚠️ 재료 미발견: {ing_name}")
                continue
            db.add(RecipeIngredient(
                recipe_id=recipe.id, ingredient_id=ingredient.id,
                qty=qty, unit=unit, qty_in_grams=qty_g
            ))
        added += 1

    db.commit()
    print(f"✅ 3차 레시피 {added}개 추가 완료 (총 {db.query(Recipe).count()}개)")


if __name__ == "__main__":
    db = SessionLocal()
    run_seed_extra2(db)
    db.close()


def run_seed_extra2b(db):
    """105개 달성용 추가 7개"""
    from app.models.models import Recipe, Ingredient, RecipeIngredient, CuisineType, MealType, SourceType
    existing = db.query(Recipe).count()
    if existing >= 105:
        print(f"이미 {existing}개 - 스킵")
        return

    def ing(name):
        return db.query(Ingredient).filter(Ingredient.name_std == name).first()

    extra7 = [
        {
            "title": "잔치국수", "cuisine": CuisineType.KOREAN, "tags": ["면류", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "멸치육수를 끓인다"},
                      {"step": 2, "text": "소면을 삶아 찬물에 헹군다"},
                      {"step": 3, "text": "그릇에 면을 담고 육수를 부어 김치, 김을 올려 완성"}],
            "ingredients": [("소면", 100, "g", 100), ("배추김치", 50, "g", 50), ("김", 2, "장", 6), ("대파", 10, "g", 10)]
        },
        {
            "title": "된장비빔밥", "cuisine": CuisineType.KOREAN, "tags": ["밥", "된장"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "밥 위에 나물들을 올린다"},
                      {"step": 2, "text": "된장, 참기름, 고춧가루로 양념장을 만든다"},
                      {"step": 3, "text": "양념장을 넣고 비벼 완성"}],
            "ingredients": [("쌀", 200, "g", 200), ("된장", 15, "g", 15), ("참기름", 5, "ml", 5), ("콩나물", 80, "g", 80)]
        },
        {
            "title": "황태해장국", "cuisine": CuisineType.KOREAN, "tags": ["국", "해산물"],
            "meal_types": [MealType.BREAKFAST, MealType.LUNCH], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "북어를 불려 먹기 좋게 찢는다"},
                      {"step": 2, "text": "참기름에 볶다 물을 넣고 끓인다"},
                      {"step": 3, "text": "두부와 달걀을 넣어 완성"}],
            "ingredients": [("북어(황태)", 40, "g", 40), ("두부", 100, "g", 100), ("달걀", 1, "개", 60), ("대파", 15, "g", 15)]
        },
        {
            "title": "감자볶음", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "감자를 채 썰어 물에 담가 전분을 뺀다"},
                      {"step": 2, "text": "팬에 기름을 두르고 볶는다"},
                      {"step": 3, "text": "소금과 깨로 간해 완성"}],
            "ingredients": [("감자", 200, "g", 200), ("식용유", 10, "ml", 10), ("소금", 2, "g", 2)]
        },
        {
            "title": "두부탕국", "cuisine": CuisineType.KOREAN, "tags": ["국", "두부"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "멸치육수를 끓인다"},
                      {"step": 2, "text": "두부를 넣고 간장으로 간한다"},
                      {"step": 3, "text": "달걀을 풀어 넣고 대파를 올려 완성"}],
            "ingredients": [("두부", 200, "g", 200), ("달걀", 1, "개", 60), ("간장", 10, "ml", 10), ("대파", 15, "g", 15)]
        },
        {
            "title": "고추장불고기", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "돼지고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "돼지고기를 고추장, 간장, 설탕 양념에 재운다"},
                      {"step": 2, "text": "양파, 당근과 함께 팬에 볶는다"},
                      {"step": 3, "text": "참기름을 넣어 완성"}],
            "ingredients": [("돼지고기", 200, "g", 200), ("고추장", 20, "g", 20), ("양파", 80, "g", 80), ("당근", 30, "g", 30)]
        },
        {
            "title": "치킨너겟 + 밥", "cuisine": CuisineType.FREE, "tags": ["간편식", "닭고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "닭가슴살을 한입 크기로 썬다"},
                      {"step": 2, "text": "부침가루와 달걀물을 입혀 기름에 튀긴다"},
                      {"step": 3, "text": "밥과 함께 차려 완성"}],
            "ingredients": [("닭가슴살", 150, "g", 150), ("부침가루", 30, "g", 30), ("달걀", 1, "개", 60), ("쌀", 200, "g", 200)]
        },
    ]

    added = 0
    for r_data in extra7:
        existing_r = db.query(Recipe).filter(Recipe.title == r_data["title"]).first()
        if existing_r:
            continue
        recipe = Recipe(
            title=r_data["title"], cuisine=r_data["cuisine"], tags=r_data.get("tags", []),
            meal_types=[mt.value for mt in r_data["meal_types"]], difficulty=r_data["difficulty"],
            cook_time_min=r_data["cook_time_min"], servings=r_data["servings"],
            steps=r_data["steps"], source_type=SourceType.MANUAL)
        db.add(recipe)
        db.flush()
        for ing_name, qty, unit, qty_g in r_data["ingredients"]:
            ingredient = ing(ing_name)
            if not ingredient:
                print(f"  ⚠️ 재료 미발견: {ing_name}")
                continue
            db.add(RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredient.id,
                                    qty=qty, unit=unit, qty_in_grams=qty_g))
        added += 1
    db.commit()
    print(f"✅ 보충 레시피 {added}개 추가 (총 {db.query(Recipe).count()}개)")
