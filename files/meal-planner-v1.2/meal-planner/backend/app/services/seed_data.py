"""
MVP 시드 데이터: 레시피 30개 + 재료 + 영양 DB
실행: python -m app.services.seed_data
"""
from sqlalchemy.orm import Session
from app.models.models import (
    Recipe, Ingredient, RecipeIngredient, FoodNutrient,
    IngredientNutrientMap, CuisineType, SourceType, MatchMethod
)


def seed_ingredients(db: Session) -> dict[str, int]:
    """표준 재료 사전 등록, {name_std: id} 반환"""
    items = [
        # 채소
        ("배추김치", "채소", "g", None, None),
        ("대파", "채소", "g", None, 60),
        ("양파", "채소", "g", None, 200),
        ("애호박", "채소", "g", None, 250),
        ("감자", "채소", "g", None, 150),
        ("무", "채소", "g", None, 500),
        ("시금치", "채소", "g", None, None),
        ("콩나물", "채소", "g", None, None),
        ("두부", "채소", "g", None, 300),  # 모(300g)
        ("당근", "채소", "g", None, 150),
        ("마늘", "양념", "g", None, 5),
        ("생강", "양념", "g", None, 15),
        ("고추", "채소", "g", None, 10),
        ("버섯", "채소", "g", None, None),
        ("깻잎", "채소", "g", None, 2),
        ("오이", "채소", "g", None, 200),
        ("부추", "채소", "g", None, None),
        # 육류
        ("돼지고기", "육류", "g", None, None),
        ("소고기", "육류", "g", None, None),
        ("닭고기", "육류", "g", None, None),
        ("달걀", "기타", "개", None, 60),
        # 해산물
        ("고등어", "해산물", "g", None, 300),
        ("갈치", "해산물", "g", None, 250),
        ("오징어", "해산물", "g", None, 250),
        ("새우", "해산물", "g", None, 15),
        ("멸치", "해산물", "g", None, None),
        # 곡류
        ("쌀", "곡류", "g", None, None),
        ("떡", "곡류", "g", None, None),
        ("당면", "곡류", "g", None, None),
        # 양념
        ("간장", "양념", "ml", 1.15, None),
        ("된장", "양념", "g", None, None),
        ("고추장", "양념", "g", None, None),
        ("고춧가루", "양념", "g", None, None),
        ("참기름", "양념", "ml", 0.92, None),
        ("식용유", "양념", "ml", 0.92, None),
        ("소금", "양념", "g", None, None),
        ("설탕", "양념", "g", None, None),
        ("후추", "양념", "g", None, None),
        ("맛술", "양념", "ml", 1.0, None),
        ("멸치육수", "양념", "ml", 1.0, None),
        # 기타
        ("우유", "유제품", "ml", 1.03, None),
        ("치즈", "유제품", "g", None, None),
        ("빵", "곡류", "g", None, None),
        ("라면", "곡류", "g", None, 120),
    ]

    id_map = {}
    for name, cat, unit, density, weight in items:
        existing = db.query(Ingredient).filter(Ingredient.name_std == name).first()
        if existing:
            id_map[name] = existing.id
            continue
        ing = Ingredient(
            name_std=name, category=cat, default_unit=unit,
            density_g_per_ml=density, avg_weight_per_piece_g=weight,
        )
        db.add(ing)
        db.flush()
        id_map[name] = ing.id
    return id_map


def seed_nutrients(db: Session) -> dict[str, int]:
    """식품영양성분 DB (100g 기준), {food_name: id}"""
    items = [
        ("배추김치", 18, 2.4, 1.6, 0.5, 747),
        ("대파", 34, 7.4, 1.6, 0.3, 3),
        ("양파", 36, 8.0, 1.2, 0.1, 3),
        ("애호박", 16, 2.7, 1.2, 0.2, 1),
        ("감자", 66, 15.0, 1.7, 0.1, 3),
        ("무", 15, 3.0, 0.6, 0.1, 27),
        ("시금치", 20, 2.0, 2.6, 0.4, 51),
        ("콩나물", 29, 3.3, 3.7, 0.8, 4),
        ("두부", 79, 1.8, 8.5, 4.2, 7),
        ("당근", 36, 8.0, 0.7, 0.2, 43),
        ("마늘", 117, 24.0, 5.3, 0.3, 10),
        ("버섯(표고)", 34, 5.2, 3.0, 0.4, 6),
        ("달걀", 147, 0.8, 12.4, 10.0, 140),
        ("돼지고기(삼겹살)", 331, 0.0, 17.4, 28.4, 50),
        ("돼지고기(앞다리)", 171, 0.0, 20.0, 9.7, 58),
        ("소고기(등심)", 187, 0.0, 21.0, 11.0, 56),
        ("닭고기(가슴살)", 109, 0.0, 23.1, 1.2, 45),
        ("닭고기(다리)", 150, 0.0, 18.5, 8.0, 68),
        ("고등어", 183, 0.0, 20.2, 10.8, 70),
        ("갈치", 124, 0.0, 18.4, 5.2, 90),
        ("오징어", 82, 1.5, 17.6, 0.8, 300),
        ("새우", 85, 0.0, 18.0, 1.0, 180),
        ("쌀(백미,지은밥)", 149, 34.0, 2.6, 0.3, 0),
        ("떡(가래떡)", 229, 50.3, 4.3, 0.5, 228),
        ("당면", 332, 82.0, 0.1, 0.1, 3),
        ("라면(건면)", 457, 63.0, 9.4, 17.0, 1680),
        ("우유", 60, 4.7, 3.2, 3.2, 41),
        ("빵(식빵)", 269, 49.0, 8.5, 3.5, 520),
    ]

    id_map = {}
    for name, kcal, carb, pro, fat, sod in items:
        existing = db.query(FoodNutrient).filter(FoodNutrient.food_name == name).first()
        if existing:
            id_map[name] = existing.id
            continue
        fn = FoodNutrient(
            food_name=name, kcal_per_100g=kcal, carb_g_per_100g=carb,
            protein_g_per_100g=pro, fat_g_per_100g=fat, sodium_mg_per_100g=sod,
        )
        db.add(fn)
        db.flush()
        id_map[name] = fn.id
    return id_map


def seed_nutrient_mappings(db: Session, ing_map: dict, nut_map: dict):
    """재료 ↔ 영양DB 매핑"""
    mappings = [
        ("배추김치", "배추김치"),
        ("대파", "대파"),
        ("양파", "양파"),
        ("애호박", "애호박"),
        ("감자", "감자"),
        ("무", "무"),
        ("시금치", "시금치"),
        ("콩나물", "콩나물"),
        ("두부", "두부"),
        ("당근", "당근"),
        ("마늘", "마늘"),
        ("버섯", "버섯(표고)"),
        ("달걀", "달걀"),
        ("돼지고기", "돼지고기(앞다리)"),
        ("소고기", "소고기(등심)"),
        ("닭고기", "닭고기(가슴살)"),
        ("고등어", "고등어"),
        ("갈치", "갈치"),
        ("오징어", "오징어"),
        ("새우", "새우"),
        ("쌀", "쌀(백미,지은밥)"),
        ("떡", "떡(가래떡)"),
        ("당면", "당면"),
        ("라면", "라면(건면)"),
        ("우유", "우유"),
        ("빵", "빵(식빵)"),
    ]
    for ing_name, nut_name in mappings:
        if ing_name not in ing_map or nut_name not in nut_map:
            continue
        existing = db.query(IngredientNutrientMap).filter(
            IngredientNutrientMap.ingredient_id == ing_map[ing_name]
        ).first()
        if existing:
            continue
        db.add(IngredientNutrientMap(
            ingredient_id=ing_map[ing_name],
            food_nutrient_id=nut_map[nut_name],
            match_confidence=1.0,
            match_method=MatchMethod.MANUAL,
        ))
    db.flush()


def seed_recipes(db: Session, ing_map: dict):
    """30개 MVP 레시피"""
    recipes_data = [
        # ─── 아침 간편식 (6개) ───
        {
            "title": "달걀죽",
            "cuisine": "KOREAN", "tags": ["죽", "간편식"],
            "meal_types": ["BREAKFAST"], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "쌀을 물에 불린다"}, {"step": 2, "text": "냄비에 쌀과 물(3배)을 넣고 약불에 끓인다"}, {"step": 3, "text": "풀어둔 달걀을 넣고 저어 완성"}],
            "ingredients": [("쌀", 80, "g", 80), ("달걀", 1, "개", 60), ("소금", 1, "g", 1)],
        },
        {
            "title": "토스트 + 우유",
            "cuisine": "FREE", "tags": ["간편식", "양식"],
            "meal_types": ["BREAKFAST"], "difficulty": 1, "cook_time_min": 5, "servings": 1,
            "steps": [{"step": 1, "text": "식빵을 토스터에 굽는다"}, {"step": 2, "text": "우유와 함께 낸다"}],
            "ingredients": [("빵", 60, "g", 60), ("우유", 200, "ml", 200)],
        },
        {
            "title": "콩나물국밥",
            "cuisine": "KOREAN", "tags": ["국", "간편식"],
            "meal_types": ["BREAKFAST"], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "멸치육수를 끓인다"}, {"step": 2, "text": "콩나물, 대파를 넣고 끓인다"}, {"step": 3, "text": "밥을 넣어 완성"}],
            "ingredients": [("콩나물", 100, "g", 100), ("쌀", 150, "g", 150), ("대파", 20, "g", 20)],
        },
        {
            "title": "계란후라이 + 밥",
            "cuisine": "KOREAN", "tags": ["간편식"],
            "meal_types": ["BREAKFAST"], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "팬에 식용유를 두르고 달걀을 프라이한다"}, {"step": 2, "text": "밥과 함께 낸다"}],
            "ingredients": [("달걀", 2, "개", 120), ("쌀", 200, "g", 200), ("식용유", 5, "ml", 5)],
        },
        {
            "title": "시금치 된장국 + 밥",
            "cuisine": "KOREAN", "tags": ["국", "간편식"],
            "meal_types": ["BREAKFAST"], "difficulty": 1, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "멸치육수에 된장을 풀어 끓인다"}, {"step": 2, "text": "시금치, 두부를 넣어 완성"}],
            "ingredients": [("시금치", 50, "g", 50), ("된장", 15, "g", 15), ("두부", 50, "g", 50), ("쌀", 200, "g", 200)],
        },
        {
            "title": "누룽지",
            "cuisine": "KOREAN", "tags": ["죽", "간편식"],
            "meal_types": ["BREAKFAST"], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "누룽지에 물을 넣고 끓인다"}],
            "ingredients": [("쌀", 100, "g", 100)],
        },
        # ─── 한식 점심/저녁 (18개) ───
        {
            "title": "김치찌개",
            "cuisine": "KOREAN", "tags": ["찌개", "돼지고기"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "돼지고기를 볶는다"}, {"step": 2, "text": "김치, 물을 넣고 끓인다"}, {"step": 3, "text": "두부, 대파를 넣어 완성"}],
            "ingredients": [("돼지고기", 150, "g", 150), ("배추김치", 200, "g", 200), ("두부", 150, "g", 150), ("대파", 30, "g", 30)],
        },
        {
            "title": "된장찌개",
            "cuisine": "KOREAN", "tags": ["찌개"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "멸치육수에 된장을 풀어 끓인다"}, {"step": 2, "text": "애호박, 두부, 감자를 넣는다"}, {"step": 3, "text": "대파, 고추를 넣어 완성"}],
            "ingredients": [("된장", 30, "g", 30), ("애호박", 100, "g", 100), ("두부", 150, "g", 150), ("감자", 80, "g", 80), ("대파", 20, "g", 20)],
        },
        {
            "title": "소고기 미역국",
            "cuisine": "KOREAN", "tags": ["국", "소고기"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 40, "servings": 2,
            "steps": [{"step": 1, "text": "미역을 불린다"}, {"step": 2, "text": "소고기를 참기름에 볶는다"}, {"step": 3, "text": "물을 넣고 끓여 간장으로 간을 한다"}],
            "ingredients": [("소고기", 100, "g", 100), ("간장", 15, "ml", 17)],
        },
        {
            "title": "제육볶음",
            "cuisine": "KOREAN", "tags": ["볶음", "돼지고기"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "돼지고기에 고추장 양념을 버무린다"}, {"step": 2, "text": "양파, 대파와 함께 팬에 볶는다"}],
            "ingredients": [("돼지고기", 200, "g", 200), ("고추장", 30, "g", 30), ("양파", 100, "g", 100), ("대파", 30, "g", 30)],
        },
        {
            "title": "닭볶음탕",
            "cuisine": "KOREAN", "tags": ["찜/탕", "닭고기"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 40, "servings": 2,
            "steps": [{"step": 1, "text": "닭고기를 끓는 물에 데친다"}, {"step": 2, "text": "양념장(고추장+간장+고춧가루)에 감자, 당근과 함께 졸인다"}],
            "ingredients": [("닭고기", 300, "g", 300), ("감자", 150, "g", 150), ("당근", 80, "g", 80), ("양파", 100, "g", 100)],
        },
        {
            "title": "고등어 구이",
            "cuisine": "KOREAN", "tags": ["구이", "생선"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "고등어에 소금을 뿌려 10분 둔다"}, {"step": 2, "text": "팬 또는 그릴에 앞뒤로 굽는다"}],
            "ingredients": [("고등어", 300, "g", 300), ("소금", 3, "g", 3)],
        },
        {
            "title": "갈치 조림",
            "cuisine": "KOREAN", "tags": ["조림", "생선"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "냄비에 무를 깔고 갈치를 올린다"}, {"step": 2, "text": "양념장(간장+고춧가루+마늘)을 끼얹고 졸인다"}],
            "ingredients": [("갈치", 250, "g", 250), ("무", 150, "g", 150), ("간장", 30, "ml", 34), ("고춧가루", 10, "g", 10)],
        },
        {
            "title": "두부 조림",
            "cuisine": "KOREAN", "tags": ["조림"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "두부를 팬에 노릇하게 굽는다"}, {"step": 2, "text": "간장 양념을 끼얹고 조린다"}],
            "ingredients": [("두부", 300, "g", 300), ("간장", 30, "ml", 34), ("대파", 20, "g", 20)],
        },
        {
            "title": "오징어볶음",
            "cuisine": "KOREAN", "tags": ["볶음", "해산물"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "오징어를 손질해 먹기 좋게 썬다"}, {"step": 2, "text": "고추장 양념에 양파, 당근과 볶는다"}],
            "ingredients": [("오징어", 250, "g", 250), ("양파", 100, "g", 100), ("당근", 50, "g", 50), ("고추장", 20, "g", 20)],
        },
        {
            "title": "비빔밥",
            "cuisine": "KOREAN", "tags": ["밥", "나물"],
            "meal_types": ["LUNCH"], "difficulty": 2, "cook_time_min": 30, "servings": 1,
            "steps": [{"step": 1, "text": "시금치, 콩나물, 당근을 각각 데치거나 볶아 나물을 만든다"}, {"step": 2, "text": "밥 위에 나물, 고추장을 올려 비빈다"}],
            "ingredients": [("쌀", 200, "g", 200), ("시금치", 50, "g", 50), ("콩나물", 50, "g", 50), ("당근", 30, "g", 30), ("고추장", 15, "g", 15), ("달걀", 1, "개", 60)],
        },
        {
            "title": "불고기",
            "cuisine": "KOREAN", "tags": ["볶음", "소고기"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 25, "servings": 2,
            "steps": [{"step": 1, "text": "소고기를 간장 양념에 30분 재운다"}, {"step": 2, "text": "양파, 대파와 함께 팬에 볶는다"}],
            "ingredients": [("소고기", 200, "g", 200), ("양파", 100, "g", 100), ("대파", 30, "g", 30), ("간장", 30, "ml", 34)],
        },
        {
            "title": "잡채",
            "cuisine": "KOREAN", "tags": ["볶음", "면"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 30, "servings": 2,
            "steps": [{"step": 1, "text": "당면을 삶아 물기를 뺀다"}, {"step": 2, "text": "채소(시금치, 당근, 양파, 버섯)를 각각 볶는다"}, {"step": 3, "text": "모두 섞어 간장+참기름으로 버무린다"}],
            "ingredients": [("당면", 100, "g", 100), ("시금치", 50, "g", 50), ("당근", 50, "g", 50), ("양파", 80, "g", 80), ("버섯", 50, "g", 50)],
        },
        {
            "title": "콩나물국",
            "cuisine": "KOREAN", "tags": ["국"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "물을 끓여 콩나물을 넣는다"}, {"step": 2, "text": "대파, 마늘을 넣고 간장으로 간을 한다"}],
            "ingredients": [("콩나물", 150, "g", 150), ("대파", 20, "g", 20), ("마늘", 5, "g", 5)],
        },
        {
            "title": "감자조림",
            "cuisine": "KOREAN", "tags": ["조림"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "감자를 깍둑 썰어 간장+설탕+물에 조린다"}, {"step": 2, "text": "국물이 자작해지면 참기름을 뿌린다"}],
            "ingredients": [("감자", 300, "g", 300), ("간장", 30, "ml", 34), ("설탕", 15, "g", 15)],
        },
        {
            "title": "애호박 된장찌개",
            "cuisine": "KOREAN", "tags": ["찌개"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 20, "servings": 2,
            "steps": [{"step": 1, "text": "멸치육수에 된장을 풀고 애호박, 두부를 넣는다"}, {"step": 2, "text": "끓으면 고추, 대파를 넣어 완성"}],
            "ingredients": [("애호박", 150, "g", 150), ("된장", 25, "g", 25), ("두부", 100, "g", 100), ("대파", 15, "g", 15)],
        },
        # ─── 주말 자유 메뉴 (6개) ───
        {
            "title": "라면 + 달걀",
            "cuisine": "FREE", "tags": ["면", "간편식"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "물 550ml를 끓인다"}, {"step": 2, "text": "라면과 수프를 넣고 4분 끓인다"}, {"step": 3, "text": "달걀을 넣어 완성"}],
            "ingredients": [("라면", 120, "g", 120), ("달걀", 1, "개", 60), ("대파", 10, "g", 10)],
        },
        {
            "title": "떡볶이",
            "cuisine": "FREE", "tags": ["분식", "떡"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 15, "servings": 2,
            "steps": [{"step": 1, "text": "물에 고추장+설탕+간장을 풀어 양념을 만든다"}, {"step": 2, "text": "떡을 넣고 졸인다"}],
            "ingredients": [("떡", 300, "g", 300), ("고추장", 30, "g", 30), ("설탕", 15, "g", 15)],
        },
        {
            "title": "김치볶음밥",
            "cuisine": "FREE", "tags": ["볶음", "밥"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 10, "servings": 1,
            "steps": [{"step": 1, "text": "김치를 잘게 썰어 볶는다"}, {"step": 2, "text": "밥을 넣고 함께 볶는다"}, {"step": 3, "text": "달걀프라이를 올린다"}],
            "ingredients": [("배추김치", 150, "g", 150), ("쌀", 200, "g", 200), ("달걀", 1, "개", 60), ("식용유", 5, "ml", 5)],
        },
        {
            "title": "달걀말이",
            "cuisine": "KOREAN", "tags": ["볶음", "달걀"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 1, "cook_time_min": 10, "servings": 2,
            "steps": [{"step": 1, "text": "달걀에 대파, 당근을 넣고 푼다"}, {"step": 2, "text": "팬에 얇게 부어 돌돌 만다"}],
            "ingredients": [("달걀", 4, "개", 240), ("대파", 15, "g", 15), ("당근", 20, "g", 20)],
        },
        {
            "title": "새우볶음밥",
            "cuisine": "FREE", "tags": ["볶음", "밥", "해산물"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 15, "servings": 1,
            "steps": [{"step": 1, "text": "새우를 볶다가 달걀을 넣는다"}, {"step": 2, "text": "밥과 야채를 넣고 함께 볶는다"}],
            "ingredients": [("새우", 80, "g", 80), ("쌀", 200, "g", 200), ("달걀", 1, "개", 60), ("양파", 50, "g", 50)],
        },
        {
            "title": "소고기 무국",
            "cuisine": "KOREAN", "tags": ["국", "소고기"],
            "meal_types": ["LUNCH", "DINNER"], "difficulty": 2, "cook_time_min": 35, "servings": 2,
            "steps": [{"step": 1, "text": "소고기를 참기름에 볶는다"}, {"step": 2, "text": "무를 넣고 함께 볶다가 물을 넣는다"}, {"step": 3, "text": "간장으로 간을 맞추고 끓인다"}],
            "ingredients": [("소고기", 100, "g", 100), ("무", 200, "g", 200), ("대파", 20, "g", 20), ("간장", 15, "ml", 17)],
        },
    ]

    for rd in recipes_data:
        existing = db.query(Recipe).filter(Recipe.title == rd["title"]).first()
        if existing:
            continue
        recipe = Recipe(
            title=rd["title"],
            cuisine=CuisineType(rd["cuisine"]),
            tags=rd["tags"],
            meal_types=rd["meal_types"],
            difficulty=rd["difficulty"],
            cook_time_min=rd["cook_time_min"],
            servings=rd["servings"],
            steps=rd["steps"],
            source_type=SourceType.MANUAL,
        )
        db.add(recipe)
        db.flush()

        for ing_name, qty, unit, qty_g in rd["ingredients"]:
            if ing_name not in ing_map:
                continue
            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing_map[ing_name],
                qty=qty, unit=unit, qty_in_grams=qty_g,
            )
            db.add(ri)
    db.flush()


def run_seed(db: Session):
    """전체 시드 실행"""
    print("🌱 Seeding ingredients...")
    ing_map = seed_ingredients(db)
    print(f"   → {len(ing_map)} ingredients")

    print("🌱 Seeding nutrients...")
    nut_map = seed_nutrients(db)
    print(f"   → {len(nut_map)} nutrients")

    print("🌱 Seeding nutrient mappings...")
    seed_nutrient_mappings(db, ing_map, nut_map)

    print("🌱 Seeding recipes...")
    seed_recipes(db, ing_map)

    db.commit()
    print("✅ Seed complete!")
