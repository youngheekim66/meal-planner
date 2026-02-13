"""
추가 레시피 45개 시드 스크립트
기존 27개 → 총 72개 레시피로 확대
"""
from app.core.database import SessionLocal
from app.models.models import (
    Recipe, Ingredient, RecipeIngredient, FoodNutrient,
    IngredientNutrientMap, CuisineType, MealType, SourceType, MatchMethod
)

def get_or_create_ingredient(db, name, category, default_unit, qty_g):
    ing = db.query(Ingredient).filter(Ingredient.name_std == name).first()
    if not ing:
        kwargs = {"name_std": name, "category": category, "default_unit": default_unit}
        if default_unit == "개":
            kwargs["avg_weight_per_piece_g"] = qty_g
        elif default_unit == "ml":
            kwargs["density_g_per_ml"] = 1.0
        elif default_unit == "장":
            kwargs["avg_weight_per_piece_g"] = qty_g
        ing = Ingredient(**kwargs)
        db.add(ing)
        db.flush()
    return ing

def get_or_create_nutrient(db, name, kcal, carb, pro, fat, sod):
    fn = db.query(FoodNutrient).filter(FoodNutrient.food_name == name).first()
    if not fn:
        fn = FoodNutrient(food_name=name, kcal_per_100g=kcal, carb_g_per_100g=carb,
                          protein_g_per_100g=pro, fat_g_per_100g=fat, sodium_mg_per_100g=sod)
        db.add(fn)
        db.flush()
    return fn

def ensure_mapping(db, ing, fn):
    existing = db.query(IngredientNutrientMap).filter(
        IngredientNutrientMap.ingredient_id == ing.id).first()
    if not existing:
        db.add(IngredientNutrientMap(
            ingredient_id=ing.id, food_nutrient_id=fn.id,
            match_confidence=1.0, match_method=MatchMethod.MANUAL))

def run_seed_extra(db):
    existing = db.query(Recipe).count()
    if existing >= 50:
        print(f"이미 {existing}개 레시피 존재 - 스킵")
        return

    # ── 신규 재료 + 영양 ──
    new_ingredients = [
        # (이름, 카테고리, 단위, g당무게, kcal, carb, pro, fat, sodium)
        ("미나리", "채소", "g", 1.0, 17, 2.4, 2.0, 0.3, 64),
        ("고사리", "채소", "g", 1.0, 34, 6.0, 3.1, 0.4, 3),
        ("도라지", "채소", "g", 1.0, 65, 14.3, 2.3, 0.1, 7),
        ("깻잎", "채소", "g", 1.0, 37, 4.6, 3.3, 0.6, 3),
        ("쑥갓", "채소", "g", 1.0, 20, 2.6, 2.3, 0.4, 46),
        ("비타민", "채소", "g", 1.0, 13, 1.8, 1.5, 0.3, 65),
        ("브로콜리", "채소", "g", 1.0, 34, 6.6, 2.8, 0.4, 33),
        ("파프리카", "채소", "g", 1.0, 31, 6.0, 1.0, 0.3, 4),
        ("양배추", "채소", "g", 1.0, 25, 5.8, 1.3, 0.1, 18),
        ("미역(건)", "해산물", "g", 1.0, 45, 8.0, 3.0, 0.6, 2500),
        ("미역(불린)", "해산물", "g", 1.0, 16, 2.8, 1.0, 0.2, 870),
        ("북어(황태)", "해산물", "g", 1.0, 308, 0, 70.0, 1.0, 300),
        ("조개", "해산물", "g", 1.0, 72, 2.5, 12.6, 1.0, 400),
        ("참치캔", "해산물", "g", 1.0, 190, 0, 26.0, 9.0, 350),
        ("꽁치캔", "해산물", "g", 1.0, 220, 0, 20.0, 15.0, 400),
        ("동태", "해산물", "g", 1.0, 73, 0, 16.0, 0.6, 90),
        ("게맛살", "해산물", "g", 1.0, 95, 11.0, 7.0, 2.0, 700),
        ("소시지", "육류", "g", 1.0, 275, 3.0, 12.0, 24.0, 1050),
        ("햄", "육류", "g", 1.0, 200, 5.0, 14.0, 14.0, 1100),
        ("닭가슴살", "육류", "g", 1.0, 165, 0, 31.0, 3.6, 74),
        ("라면", "곡류", "개", 120.0, 500, 65.0, 10.0, 16.0, 1800),
        ("수제비반죽", "곡류", "g", 1.0, 340, 72.0, 10.0, 1.0, 5),
        ("우동면", "곡류", "개", 200.0, 140, 28.0, 5.0, 0.5, 500),
        ("칼국수면", "곡류", "g", 1.0, 280, 56.0, 9.0, 1.5, 10),
        ("찹쌀", "곡류", "g", 1.0, 350, 80.0, 6.0, 0.6, 2),
        ("감자전분", "곡류", "g", 1.0, 330, 82.0, 0.1, 0.1, 10),
        ("부침가루", "곡류", "g", 1.0, 350, 72.0, 8.0, 2.0, 600),
        ("두부(순두부)", "채소", "g", 1.0, 47, 1.6, 5.3, 2.3, 5),
        ("호박잎", "채소", "g", 1.0, 19, 2.7, 2.1, 0.3, 3),
        ("열무", "채소", "g", 1.0, 18, 2.4, 1.8, 0.3, 30),
        ("가지", "채소", "g", 1.0, 25, 5.9, 1.0, 0.2, 2),
        ("김", "해산물", "장", 3.0, 178, 4.0, 35.0, 2.0, 50),
        ("볶음김치", "채소", "g", 1.0, 50, 6.0, 2.0, 2.0, 600),
        ("묵(도토리묵)", "곡류", "g", 1.0, 43, 10.0, 0.4, 0.1, 3),
        ("떡국떡", "곡류", "g", 1.0, 225, 50.0, 4.0, 0.3, 5),
        ("만두", "곡류", "개", 25.0, 200, 25.0, 8.0, 8.0, 500),
    ]

    for name, cat, unit, qty_g, kcal, carb, pro, fat, sod in new_ingredients:
        ing = get_or_create_ingredient(db, name, cat, unit, qty_g)
        fn = get_or_create_nutrient(db, name, kcal, carb, pro, fat, sod)
        ensure_mapping(db, ing, fn)

    db.flush()
    print(f"✅ 신규 재료/영양 {len(new_ingredients)}개 추가")

    # ── 기존 재료 참조 헬퍼 ──
    def ing(name):
        return db.query(Ingredient).filter(Ingredient.name_std == name).first()

    # ── 추가 레시피 데이터 ──
    new_recipes = [
        # ── 아침 추가 (4개) ──
        {
            "title": "호박죽", "cuisine": CuisineType.KOREAN, "tags": ["죽", "간편식"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 25, "servings": 1,
            "steps": [{"step": 1, "text": "늙은호박(또는 단호박)을 삶아 으깬다"},
                      {"step": 2, "text": "찹쌀가루 물에 풀어 넣고 약불에 저으며 끓인다"},
                      {"step": 3, "text": "소금으로 간해 완성"}],
            "ingredients": [("애호박", 200, "g", 200), ("찹쌀", 30, "g", 30), ("소금", 1, "g", 1)]
        },
        {
            "title": "김치죽", "cuisine": CuisineType.KOREAN, "tags": ["죽", "김치"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "김치를 잘게 다진다"},
                      {"step": 2, "text": "참기름에 김치를 볶다가 쌀과 물을 넣는다"},
                      {"step": 3, "text": "약불에 저으며 끓여 완성"}],
            "ingredients": [("쌀", 80, "g", 80), ("배추김치", 80, "g", 80), ("참기름", 5, "ml", 5)]
        },
        {
            "title": "미역국 + 밥", "cuisine": CuisineType.KOREAN, "tags": ["국", "해산물"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "불린 미역을 참기름에 볶는다"},
                      {"step": 2, "text": "물을 넣고 간장으로 간해 끓인다"},
                      {"step": 3, "text": "밥과 함께 차려 완성"}],
            "ingredients": [("미역(불린)", 50, "g", 50), ("쌀", 200, "g", 200),
                           ("참기름", 5, "ml", 5), ("간장", 10, "ml", 10)]
        },
        {
            "title": "감자수프", "cuisine": CuisineType.FREE, "tags": ["수프", "간편식"],
            "meal_types": [MealType.BREAKFAST], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "감자를 삶아 으깬다"},
                      {"step": 2, "text": "우유와 함께 냄비에 넣고 끓인다"},
                      {"step": 3, "text": "소금, 후추로 간해 완성"}],
            "ingredients": [("감자", 200, "g", 200), ("우유", 200, "ml", 200),
                           ("소금", 1, "g", 1)]
        },

        # ── 한식 점심/저녁 추가 (28개) ──
        {
            "title": "순두부찌개", "cuisine": CuisineType.KOREAN, "tags": ["찌개", "두부", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "참기름에 다진마늘, 고춧가루를 볶는다"},
                      {"step": 2, "text": "물과 순두부를 넣고 끓인다"},
                      {"step": 3, "text": "조개를 넣고 입이 벌어질 때까지 끓인다"},
                      {"step": 4, "text": "달걀을 톡 깨뜨려 넣고 완성"}],
            "ingredients": [("두부(순두부)", 300, "g", 300), ("조개", 80, "g", 80),
                           ("달걀", 1, "개", 60), ("고춧가루", 5, "g", 5), ("대파", 20, "g", 20)]
        },
        {
            "title": "북어국", "cuisine": CuisineType.KOREAN, "tags": ["국", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "북어를 물에 불려 먹기 좋게 찢는다"},
                      {"step": 2, "text": "참기름에 북어를 볶다 물을 넣는다"},
                      {"step": 3, "text": "달걀을 풀어 넣고 대파 넣어 완성"}],
            "ingredients": [("북어(황태)", 50, "g", 50), ("달걀", 1, "개", 60),
                           ("대파", 20, "g", 20), ("간장", 10, "ml", 10)]
        },
        {
            "title": "동태찌개", "cuisine": CuisineType.KOREAN, "tags": ["찌개", "생선"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "동태를 토막내어 준비한다"},
                      {"step": 2, "text": "고추장 양념장을 만든다"},
                      {"step": 3, "text": "무, 두부, 동태를 넣고 양념장과 끓인다"},
                      {"step": 4, "text": "대파, 쑥갓을 넣어 완성"}],
            "ingredients": [("동태", 200, "g", 200), ("무", 100, "g", 100), ("두부", 100, "g", 100),
                           ("대파", 30, "g", 30), ("고추장", 15, "g", 15)]
        },
        {
            "title": "참치김치찌개", "cuisine": CuisineType.KOREAN, "tags": ["찌개", "김치"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "참치캔 기름을 넣고 김치를 볶는다"},
                      {"step": 2, "text": "물을 넣고 끓인다"},
                      {"step": 3, "text": "두부를 넣고 대파 올려 완성"}],
            "ingredients": [("참치캔", 100, "g", 100), ("배추김치", 200, "g", 200),
                           ("두부", 100, "g", 100), ("대파", 20, "g", 20)]
        },
        {
            "title": "미역국(소고기)", "cuisine": CuisineType.KOREAN, "tags": ["국", "소고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "소고기를 참기름에 볶는다"},
                      {"step": 2, "text": "불린 미역을 넣고 함께 볶는다"},
                      {"step": 3, "text": "물을 넣고 20분 끓인다"},
                      {"step": 4, "text": "간장과 소금으로 간해 완성"}],
            "ingredients": [("소고기", 100, "g", 100), ("미역(불린)", 80, "g", 80),
                           ("참기름", 10, "ml", 10), ("간장", 15, "ml", 15)]
        },
        {
            "title": "시금치나물", "cuisine": CuisineType.KOREAN, "tags": ["나물", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "시금치를 끓는 물에 데친다"},
                      {"step": 2, "text": "참기름, 간장, 깨로 무쳐 완성"}],
            "ingredients": [("시금치", 200, "g", 200), ("참기름", 5, "ml", 5),
                           ("간장", 10, "ml", 10)]
        },
        {
            "title": "멸치볶음", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "멸치를 마른 팬에 살짝 볶는다"},
                      {"step": 2, "text": "간장, 설탕, 물엿 양념을 넣고 볶는다"},
                      {"step": 3, "text": "깨를 뿌려 완성"}],
            "ingredients": [("멸치", 50, "g", 50), ("간장", 10, "ml", 10), ("설탕", 10, "g", 10)]
        },
        {
            "title": "가지나물", "cuisine": CuisineType.KOREAN, "tags": ["나물", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "가지를 길게 찢어 찜기에 쪄낸다"},
                      {"step": 2, "text": "간장, 참기름, 다진마늘로 양념한다"},
                      {"step": 3, "text": "깨를 뿌려 완성"}],
            "ingredients": [("가지", 200, "g", 200), ("간장", 10, "ml", 10), ("참기름", 5, "ml", 5)]
        },
        {
            "title": "소고기장조림", "cuisine": CuisineType.KOREAN, "tags": ["조림", "소고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 40, "servings": 4,
            "steps": [{"step": 1, "text": "소고기를 큰 덩어리로 삶아 건진다"},
                      {"step": 2, "text": "간장, 설탕으로 양념장을 만든다"},
                      {"step": 3, "text": "소고기를 결대로 찢어 양념장에 조린다"},
                      {"step": 4, "text": "달걀을 삶아 함께 조려 완성"}],
            "ingredients": [("소고기", 300, "g", 300), ("달걀", 4, "개", 240),
                           ("간장", 50, "ml", 50), ("설탕", 20, "g", 20)]
        },
        {
            "title": "김치전", "cuisine": CuisineType.KOREAN, "tags": ["전", "김치"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "김치를 잘게 썬다"},
                      {"step": 2, "text": "부침가루와 물을 섞어 반죽한다"},
                      {"step": 3, "text": "기름 두른 팬에 앞뒤로 노릇하게 부친다"}],
            "ingredients": [("배추김치", 200, "g", 200), ("부침가루", 80, "g", 80),
                           ("식용유", 15, "ml", 15)]
        },
        {
            "title": "해물파전", "cuisine": CuisineType.KOREAN, "tags": ["전", "해산물"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "부침가루 반죽을 만든다"},
                      {"step": 2, "text": "대파를 길게 깔고 반죽을 부어 새우를 올린다"},
                      {"step": 3, "text": "앞뒤로 노릇하게 부쳐 완성"}],
            "ingredients": [("부침가루", 100, "g", 100), ("새우", 80, "g", 80),
                           ("대파", 60, "g", 60), ("식용유", 15, "ml", 15)]
        },
        {
            "title": "감자탕", "cuisine": CuisineType.KOREAN, "tags": ["탕", "돼지고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 40, "servings": 2,
            "steps": [{"step": 1, "text": "돼지등뼈를 찬물에 담가 핏물을 뺀다"},
                      {"step": 2, "text": "냄비에 등뼈와 물을 넣고 30분 끓인다"},
                      {"step": 3, "text": "감자, 대파, 된장을 넣고 10분 더 끓여 완성"}],
            "ingredients": [("돼지고기", 250, "g", 250), ("감자", 200, "g", 200),
                           ("대파", 30, "g", 30), ("된장", 15, "g", 15)]
        },
        {
            "title": "닭가슴살 샐러드", "cuisine": CuisineType.FREE, "tags": ["샐러드", "닭고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "닭가슴살을 삶아 찢는다"},
                      {"step": 2, "text": "양배추, 파프리카를 먹기 좋게 썬다"},
                      {"step": 3, "text": "모든 재료를 섞고 드레싱으로 완성"}],
            "ingredients": [("닭가슴살", 150, "g", 150), ("양배추", 100, "g", 100),
                           ("파프리카", 50, "g", 50)]
        },
        {
            "title": "콩나물 무침", "cuisine": CuisineType.KOREAN, "tags": ["나물", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "콩나물을 삶아 찬물에 헹군다"},
                      {"step": 2, "text": "참기름, 간장, 고춧가루로 무쳐 완성"}],
            "ingredients": [("콩나물", 200, "g", 200), ("참기름", 5, "ml", 5),
                           ("간장", 5, "ml", 5), ("고춧가루", 3, "g", 3)]
        },
        {
            "title": "떡국", "cuisine": CuisineType.KOREAN, "tags": ["국", "소고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 25, "servings": 1,
            "steps": [{"step": 1, "text": "소고기 육수를 끓인다"},
                      {"step": 2, "text": "떡국떡을 넣고 떠오를 때까지 끓인다"},
                      {"step": 3, "text": "달걀을 풀어 넣고 대파 올려 완성"}],
            "ingredients": [("떡국떡", 200, "g", 200), ("소고기", 80, "g", 80),
                           ("달걀", 1, "개", 60), ("대파", 10, "g", 10)]
        },
        {
            "title": "만두국", "cuisine": CuisineType.KOREAN, "tags": ["국", "만두"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "육수를 끓인다"},
                      {"step": 2, "text": "냉동만두를 넣고 떠오를 때까지 끓인다"},
                      {"step": 3, "text": "간장, 대파로 간해 완성"}],
            "ingredients": [("만두", 8, "개", 200), ("대파", 10, "g", 10), ("간장", 10, "ml", 10)]
        },
        {
            "title": "수제비", "cuisine": CuisineType.KOREAN, "tags": ["면류", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "밀가루 반죽을 만들어 30분 숙성한다"},
                      {"step": 2, "text": "감자, 애호박을 썰어 멸치육수에 끓인다"},
                      {"step": 3, "text": "반죽을 얇게 떼어 넣고 익히면 완성"}],
            "ingredients": [("수제비반죽", 150, "g", 150), ("감자", 100, "g", 100),
                           ("애호박", 80, "g", 80), ("대파", 15, "g", 15)]
        },
        {
            "title": "칼국수", "cuisine": CuisineType.KOREAN, "tags": ["면류", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "멸치육수를 끓인다"},
                      {"step": 2, "text": "애호박, 감자를 넣고 끓인다"},
                      {"step": 3, "text": "칼국수면을 넣고 7분 끓여 완성"}],
            "ingredients": [("칼국수면", 150, "g", 150), ("애호박", 80, "g", 80),
                           ("감자", 80, "g", 80), ("대파", 15, "g", 15)]
        },
        {
            "title": "우동", "cuisine": CuisineType.FREE, "tags": ["면류", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "멸치육수에 간장, 맛술로 간한다"},
                      {"step": 2, "text": "우동면을 넣고 끓인다"},
                      {"step": 3, "text": "대파, 김을 올려 완성"}],
            "ingredients": [("우동면", 1, "개", 200), ("대파", 15, "g", 15),
                           ("간장", 15, "ml", 15), ("김", 2, "장", 6)]
        },
        {
            "title": "된장국(시래기)", "cuisine": CuisineType.KOREAN, "tags": ["국", "된장"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "시래기(열무) 데쳐서 준비한다"},
                      {"step": 2, "text": "멸치육수에 된장을 풀고 끓인다"},
                      {"step": 3, "text": "열무 넣고 5분 더 끓여 완성"}],
            "ingredients": [("열무", 150, "g", 150), ("된장", 20, "g", 20), ("대파", 15, "g", 15)]
        },
        {
            "title": "꽁치김치찌개", "cuisine": CuisineType.KOREAN, "tags": ["찌개", "생선"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "김치를 냄비에 깔고 꽁치캔을 올린다"},
                      {"step": 2, "text": "물과 고추장을 넣고 끓인다"},
                      {"step": 3, "text": "두부, 대파 넣어 완성"}],
            "ingredients": [("꽁치캔", 100, "g", 100), ("배추김치", 150, "g", 150),
                           ("두부", 100, "g", 100), ("대파", 15, "g", 15)]
        },
        {
            "title": "도토리묵 무침", "cuisine": CuisineType.KOREAN, "tags": ["무침", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "도토리묵을 먹기 좋게 썬다"},
                      {"step": 2, "text": "양념장(간장+고추가루+참기름)을 만든다"},
                      {"step": 3, "text": "묵에 양념장 끼얹고 김 뿌려 완성"}],
            "ingredients": [("묵(도토리묵)", 250, "g", 250), ("간장", 15, "ml", 15),
                           ("고춧가루", 3, "g", 3), ("참기름", 5, "ml", 5), ("김", 2, "장", 6)]
        },
        {
            "title": "호박잎 쌈밥", "cuisine": CuisineType.KOREAN, "tags": ["쌈", "채소"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "호박잎을 찜기에 5분 쪄낸다"},
                      {"step": 2, "text": "쌈장(된장+고추장)을 만든다"},
                      {"step": 3, "text": "밥을 호박잎에 싸서 쌈장과 함께 먹는다"}],
            "ingredients": [("호박잎", 100, "g", 100), ("쌀", 200, "g", 200),
                           ("된장", 10, "g", 10), ("고추장", 10, "g", 10)]
        },
        {
            "title": "깻잎찜", "cuisine": CuisineType.KOREAN, "tags": ["찜", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "깻잎을 깨끗이 씻는다"},
                      {"step": 2, "text": "양념장(간장+고춧가루+다진마늘)을 사이사이 넣는다"},
                      {"step": 3, "text": "찜기에 10분 쪄서 완성"}],
            "ingredients": [("깻잎", 50, "g", 50), ("간장", 15, "ml", 15),
                           ("고춧가루", 5, "g", 5)]
        },
        {
            "title": "부대찌개", "cuisine": CuisineType.KOREAN, "tags": ["찌개", "돼지고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "김치, 소시지, 햄, 두부를 한쪽씩 담는다"},
                      {"step": 2, "text": "고추장 양념과 물을 넣고 끓인다"},
                      {"step": 3, "text": "대파를 넣고 라면사리를 넣어 완성"}],
            "ingredients": [("소시지", 60, "g", 60), ("햄", 60, "g", 60),
                           ("배추김치", 100, "g", 100), ("두부", 100, "g", 100),
                           ("대파", 20, "g", 20), ("고추장", 15, "g", 15)]
        },
        {
            "title": "브로콜리 소고기볶음", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "소고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "소고기를 간장 양념에 재운다"},
                      {"step": 2, "text": "브로콜리를 한입 크기로 잘라 데친다"},
                      {"step": 3, "text": "팬에 소고기를 볶다 브로콜리를 넣어 완성"}],
            "ingredients": [("소고기", 150, "g", 150), ("브로콜리", 150, "g", 150),
                           ("간장", 15, "ml", 15), ("식용유", 10, "ml", 10)]
        },
        {
            "title": "고사리나물 + 밥", "cuisine": CuisineType.KOREAN, "tags": ["나물", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "삶은 고사리를 먹기 좋게 자른다"},
                      {"step": 2, "text": "들기름에 볶다가 간장으로 간한다"},
                      {"step": 3, "text": "밥과 함께 차려 완성"}],
            "ingredients": [("고사리", 100, "g", 100), ("쌀", 200, "g", 200),
                           ("간장", 10, "ml", 10)]
        },

        # ── 주말 자유 메뉴 추가 (13개) ──
        {
            "title": "참치김밥", "cuisine": CuisineType.FREE, "tags": ["김밥", "간편식"],
            "meal_types": [MealType.LUNCH], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "밥에 참기름, 소금을 섞는다"},
                      {"step": 2, "text": "참치캔에 마요네즈를 섞는다"},
                      {"step": 3, "text": "김에 밥, 당근, 시금치, 참치를 올려 말아 완성"}],
            "ingredients": [("쌀", 300, "g", 300), ("참치캔", 100, "g", 100),
                           ("김", 4, "장", 12), ("당근", 50, "g", 50), ("시금치", 50, "g", 50)]
        },
        {
            "title": "계란덮밥", "cuisine": CuisineType.FREE, "tags": ["덮밥", "달걀"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "양파를 채 썰어 간장 육수에 끓인다"},
                      {"step": 2, "text": "달걀 2개를 풀어 넣어 반숙으로 익힌다"},
                      {"step": 3, "text": "밥 위에 올려 완성"}],
            "ingredients": [("달걀", 2, "개", 120), ("양파", 80, "g", 80),
                           ("쌀", 200, "g", 200), ("간장", 15, "ml", 15)]
        },
        {
            "title": "참치마요덮밥", "cuisine": CuisineType.FREE, "tags": ["덮밥", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "참치캔의 기름을 빼고 마요네즈를 섞는다"},
                      {"step": 2, "text": "밥 위에 참치마요, 김가루를 올린다"},
                      {"step": 3, "text": "간장을 살짝 뿌려 완성"}],
            "ingredients": [("참치캔", 100, "g", 100), ("쌀", 200, "g", 200),
                           ("김", 2, "장", 6)]
        },
        {
            "title": "게맛살 볶음밥", "cuisine": CuisineType.FREE, "tags": ["볶음밥", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "게맛살을 잘게 찢는다"},
                      {"step": 2, "text": "달걀을 풀어 볶다가 밥과 게맛살을 넣는다"},
                      {"step": 3, "text": "간장으로 간해 완성"}],
            "ingredients": [("게맛살", 80, "g", 80), ("달걀", 1, "개", 60),
                           ("쌀", 200, "g", 200), ("대파", 15, "g", 15)]
        },
        {
            "title": "소시지야채볶음", "cuisine": CuisineType.FREE, "tags": ["볶음", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "소시지를 어슷 썬다"},
                      {"step": 2, "text": "양파, 파프리카를 함께 볶는다"},
                      {"step": 3, "text": "케첩, 간장으로 간해 완성"}],
            "ingredients": [("소시지", 80, "g", 80), ("양파", 80, "g", 80),
                           ("파프리카", 50, "g", 50)]
        },
        {
            "title": "볶음우동", "cuisine": CuisineType.FREE, "tags": ["면류", "간편식"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "우동면을 끓는 물에 데친다"},
                      {"step": 2, "text": "양파, 양배추를 팬에 볶는다"},
                      {"step": 3, "text": "면을 넣고 간장소스로 볶아 완성"}],
            "ingredients": [("우동면", 1, "개", 200), ("양배추", 80, "g", 80),
                           ("양파", 50, "g", 50), ("간장", 15, "ml", 15)]
        },
        {
            "title": "햄야채죽", "cuisine": CuisineType.FREE, "tags": ["죽", "간편식"],
            "meal_types": [MealType.BREAKFAST, MealType.LUNCH], "difficulty": 1, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "쌀을 불려 물과 함께 끓인다"},
                      {"step": 2, "text": "잘게 다진 햄과 당근을 넣는다"},
                      {"step": 3, "text": "참기름을 넣어 완성"}],
            "ingredients": [("쌀", 80, "g", 80), ("햄", 30, "g", 30), ("당근", 30, "g", 30)]
        },
        {
            "title": "닭가슴살 볶음밥", "cuisine": CuisineType.FREE, "tags": ["볶음밥", "닭고기"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "닭가슴살을 작게 썰어 볶는다"},
                      {"step": 2, "text": "양파, 당근을 넣고 함께 볶는다"},
                      {"step": 3, "text": "밥을 넣고 간장으로 간해 완성"}],
            "ingredients": [("닭가슴살", 100, "g", 100), ("쌀", 200, "g", 200),
                           ("양파", 50, "g", 50), ("당근", 30, "g", 30)]
        },
        {
            "title": "김치볶음 + 밥", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "김치"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "김치를 먹기 좋게 썰어 팬에 볶는다"},
                      {"step": 2, "text": "설탕, 참기름을 넣고 마무리한다"},
                      {"step": 3, "text": "밥과 함께 차려 완성"}],
            "ingredients": [("배추김치", 200, "g", 200), ("설탕", 5, "g", 5),
                           ("참기름", 5, "ml", 5), ("쌀", 200, "g", 200)]
        },
        {
            "title": "미나리무침 + 밥", "cuisine": CuisineType.KOREAN, "tags": ["무침", "채소"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "미나리를 데쳐 먹기 좋게 자른다"},
                      {"step": 2, "text": "고추장, 식초, 참기름으로 양념한다"},
                      {"step": 3, "text": "밥과 함께 차려 완성"}],
            "ingredients": [("미나리", 100, "g", 100), ("고추장", 10, "g", 10),
                           ("참기름", 5, "ml", 5), ("쌀", 200, "g", 200)]
        },
        {
            "title": "도라지나물 + 밥", "cuisine": CuisineType.KOREAN, "tags": ["나물", "반찬"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 2, "cook_time_min": 20, "servings": 1,
            "steps": [{"step": 1, "text": "도라지를 소금에 주물러 씁쓸한 맛을 뺀다"},
                      {"step": 2, "text": "참기름에 볶다가 간장으로 간한다"},
                      {"step": 3, "text": "밥과 함께 차려 완성"}],
            "ingredients": [("도라지", 100, "g", 100), ("참기름", 5, "ml", 5),
                           ("간장", 10, "ml", 10), ("쌀", 200, "g", 200)]
        },
        {
            "title": "두부김치", "cuisine": CuisineType.KOREAN, "tags": ["볶음", "두부", "김치"],
            "meal_types": [MealType.LUNCH, MealType.DINNER], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "두부를 도톰하게 썰어 팬에 굽는다"},
                      {"step": 2, "text": "돼지고기와 김치를 함께 볶는다"},
                      {"step": 3, "text": "접시에 두부와 김치볶음을 나란히 담아 완성"}],
            "ingredients": [("두부", 200, "g", 200), ("돼지고기", 100, "g", 100),
                           ("배추김치", 150, "g", 150), ("식용유", 10, "ml", 10)]
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
    print(f"✅ 레시피 {added}개 추가 완료 (총 {db.query(Recipe).count()}개)")


if __name__ == "__main__":
    db = SessionLocal()
    run_seed_extra(db)
    db.close()
