# -*- coding: utf-8 -*-
"""
잡채 레시피 등록 스크립트 (v3)
============================================
ingredients 형식을 테스트하고 잡채 레시피를 등록합니다.
실행: python add_japchae_recipe.py
============================================
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

API_BASE = "https://meal-planner-production-81ed.up.railway.app"

def test_ingredient_format(label, ingredients):
    data = {
        "title": f"재료테스트_{label}",
        "cuisine": "KOREAN",
        "servings": 2,
        "ingredients": ingredients
    }
    r = requests.post(f"{API_BASE}/api/recipes/", json=data)
    status = "OK" if r.status_code == 200 else "FAIL"
    print(f"  [{status}] {label}: HTTP {r.status_code} - {r.text[:200]}")
    return r.status_code == 200

print("[STEP 1] ingredients 형식 테스트")
print("="*50)

# 형식 A: name_std 사용
fmt_a = test_ingredient_format("name_std", [
    {"name_std": "당면", "qty": 500, "unit": "g"}
])

# 형식 B: ingredient_id 사용 (기존 재료 ID)
fmt_b = test_ingredient_format("ingredient_id", [
    {"ingredient_id": 27, "qty": 80, "unit": "g"}
])

# 형식 C: ingredient dict 사용
fmt_c = test_ingredient_format("ingredient_dict", [
    {"ingredient": {"name_std": "당면"}, "qty": 500, "unit": "g"}
])

# 형식 D: name + qty_in_grams
fmt_d = test_ingredient_format("name+qty_in_grams", [
    {"name": "당면", "qty": 500, "unit": "g", "qty_in_grams": 500}
])

# 형식 E: name_std + note
fmt_e = test_ingredient_format("name_std+note", [
    {"name_std": "당면", "qty": 500, "unit": "g", "note": None}
])

# 형식 F: ingredient_name
fmt_f = test_ingredient_format("ingredient_name", [
    {"ingredient_name": "당면", "qty": 500, "unit": "g"}
])

print()
print("="*50)
print("[STEP 2] 잡채 레시피 등록 (ingredients 제외)")
print("="*50)

# ingredients 없이 전체 레시피 등록
recipe_data = {
    "title": "불지 않는 잡채",
    "cuisine": "KOREAN",
    "tags": ["볶음", "명절", "잡채", "당면"],
    "meal_types": ["LUNCH", "DINNER"],
    "difficulty": 2,
    "cook_time_min": 40,
    "servings": 20,
    "source_type": "YOUTUBE",
    "source_url": "https://www.youtube.com/watch?v=-PHTqnbW3_k",
    "thumbnail_url": "https://i.ytimg.com/vi/-PHTqnbW3_k/maxresdefault.jpg",
    "steps": [
        {"step": 1, "text": "양념장 만들기: 냄비에 양조간장 150ml, 굴소스 5스푼, 흑설탕 3스푼, 조청 3스푼, 다진마늘 2스푼, 후추가루 반스푼, 맛술 5스푼, 물 200ml를 넣고 끓인다"},
        {"step": 2, "text": "끓어오르면 약불로 줄여 4분간 더 끓인 후 불을 끄고 식힌다"},
        {"step": 3, "text": "양파 2개, 당근 1개, 파프리카 1개를 채썰고, 표고버섯 4개를 썰고, 부추 100g은 7cm로 자르고, 사각어묵 6장을 채썬다"},
        {"step": 4, "text": "팬에 식용유 2스푼을 두르고 당근과 양파를 강불에서 볶는다"},
        {"step": 5, "text": "양파가 반투명해지면 어묵과 표고버섯을 넣고 양념장 대여섯 스푼 넣어 강불에서 볶는다"},
        {"step": 6, "text": "불을 끄고 부추와 파프리카를 넣어 잔열로 익힌다"},
        {"step": 7, "text": "물 2.5L를 끓인 다음 양조간장 6스푼, 식용유 4스푼을 넣고 당면 500g을 9분간 삶는다"},
        {"step": 8, "text": "삶은 당면을 체에 밭쳐 물기를 빼고 참기름 5스푼을 뿌려 장갑 끼고 비벼 코팅한다 (불지 않는 비법!)"},
        {"step": 9, "text": "당면 위에 볶은 채소와 남은 양념장을 넣고 통깨를 뿌린 후 골고루 버무리면 완성"}
    ]
}

response = requests.post(
    f"{API_BASE}/api/recipes/",
    json=recipe_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"  [OK] 등록 성공!")
    print(f"  레시피 ID: {result.get('id')}")
    print(f"  제목: {result.get('title')}")
    print(f"  칼로리: {result.get('kcal_per_serving')} kcal/인분")
    print(f"  출처: {result.get('source_url')}")
    print()
    print("  --> 식단 플래너 레시피 탭에서 '잡채' 검색해보세요!")
else:
    print(f"  [FAIL] 등록 실패 (HTTP {response.status_code})")
    print(f"  응답: {response.text}")

print()
print("="*50)
print("[DONE] 완료! 위 결과를 클로드에게 공유해주세요.")
