# -*- coding: utf-8 -*-
"""
테스트/중복 레시피 정리 스크립트
============================================
DELETE API 추가 후 실행하세요.
실행: python cleanup_recipes.py
============================================
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

API_BASE = "https://meal-planner-production-81ed.up.railway.app"

# 삭제할 레시피 ID 목록
# - 110~121: 테스트 레시피 (재료 형식 테스트 등)
# - 122: 잡채 중복 1
# - 123~128: 테스트 레시피
# - 129: 잡채 중복 2 (이것만 남기거나, 이것도 삭제)
DELETE_IDS = [110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128]

# 129번(불지 않는 잡채)은 유지할지 삭제할지 선택
# 삭제하려면 아래 주석을 해제하세요:
# DELETE_IDS.append(129)

def main():
    print("[CLEANUP] 테스트/중복 레시피 정리 시작")
    print(f"  서버: {API_BASE}")
    print(f"  삭제 대상: {len(DELETE_IDS)}개 (ID: {DELETE_IDS[0]}~{DELETE_IDS[-1]})")
    print()

    success = 0
    fail = 0

    for recipe_id in DELETE_IDS:
        try:
            # soft delete 사용 (hard delete는 /hard/{id})
            r = requests.delete(f"{API_BASE}/api/recipes/{recipe_id}")

            if r.status_code == 200:
                data = r.json()
                print(f"  [OK] ID {recipe_id}: {data.get('message', 'deleted')}")
                success += 1
            elif r.status_code == 404:
                print(f"  [SKIP] ID {recipe_id}: 이미 없음")
            else:
                print(f"  [FAIL] ID {recipe_id}: HTTP {r.status_code} - {r.text[:100]}")
                fail += 1
        except Exception as e:
            print(f"  [ERROR] ID {recipe_id}: {e}")
            fail += 1

    print()
    print("="*50)
    print(f"[DONE] 완료! 성공: {success}개, 실패: {fail}개")
    print()

    # 남은 레시피 확인
    print("[CHECK] 현재 레시피 목록 확인...")
    try:
        r = requests.get(f"{API_BASE}/api/recipes/?limit=100&offset=90")
        recipes = r.json()
        # ID 100 이상만 표시
        high_id = [r for r in recipes if r['id'] >= 100]
        if high_id:
            print(f"  ID 100 이상 레시피:")
            for recipe in high_id:
                print(f"    ID {recipe['id']}: {recipe['title']}")
        else:
            print("  ID 100 이상 레시피 없음 (정리 완료!)")
    except Exception as e:
        print(f"  확인 실패: {e}")

if __name__ == "__main__":
    main()
