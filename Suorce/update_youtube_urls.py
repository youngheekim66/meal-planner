# -*- coding: utf-8 -*-
"""
YouTube URL 일괄 업데이트 스크립트
106개 레시피에 YouTube source_url을 등록합니다.
"""
import requests

API = "https://meal-planner-production-81ed.up.railway.app"

YOUTUBE_MAPPING = {
    1: "https://www.youtube.com/watch?v=xeOv8cZMg2I",
    2: "https://www.youtube.com/watch?v=3enx3GoMffU",
    3: "https://www.youtube.com/watch?v=SgbK5INDgA8",
    4: "https://www.youtube.com/watch?v=0BvCirgQNb8",
    5: "https://www.youtube.com/watch?v=JZBrbp2WHlY",
    6: "https://www.youtube.com/watch?v=GfJy8Xcb5kQ",
    7: "https://www.youtube.com/watch?v=lNdPbWepmPI",
    8: "https://www.youtube.com/watch?v=IvaYhpEBexc",
    9: "https://www.youtube.com/watch?v=sPCjieBk9KE",
    10: "https://www.youtube.com/watch?v=chnArCaEpqA",
    11: "https://www.youtube.com/watch?v=hs5sJd9zdO4",
    12: "https://www.youtube.com/watch?v=ZxIJB8zirnQ",
    13: "https://www.youtube.com/watch?v=E2csZYObCDU",
    14: "https://www.youtube.com/watch?v=VrpxGigN9fY",
    15: "https://www.youtube.com/watch?v=L8Y_vqv_ix8",
    16: "https://www.youtube.com/watch?v=IenRd9gBWSY",
    17: "https://www.youtube.com/watch?v=5q-T50K66a4",
    18: "https://www.youtube.com/watch?v=jJJfbAn6GBE",
    19: "https://www.youtube.com/watch?v=kAEaoDd5mxo",
    20: "https://www.youtube.com/watch?v=Wpm8h10wXBQ",
    21: "https://www.youtube.com/watch?v=Rcf_VUkoF88",
    22: "https://www.youtube.com/watch?v=yYn6jsPqmZE",
    23: "https://www.youtube.com/watch?v=yd1WYXyl5_w",
    24: "https://www.youtube.com/watch?v=MZrksU3hR0M",
    25: "https://www.youtube.com/watch?v=ugAqimryJ00",
    26: "https://www.youtube.com/watch?v=7S4vTqvQR04",
    27: "https://www.youtube.com/watch?v=FKTHO15QutU",
    28: "https://www.youtube.com/watch?v=O2QMCuYMnpo",
    29: "https://www.youtube.com/watch?v=wQRRMEqYPeg",
    30: "https://www.youtube.com/watch?v=sPCjieBk9KE",
    31: "https://www.youtube.com/watch?v=Qlj7xZharQ4",
    32: "https://www.youtube.com/watch?v=A8R6FE7YtaI",
    33: "https://www.youtube.com/watch?v=8HycHjpapTY",
    34: "https://www.youtube.com/watch?v=gUYeEasWU58",
    35: "https://www.youtube.com/watch?v=2ebjEWk4E4I",
    36: "https://www.youtube.com/watch?v=sPCjieBk9KE",
    37: "https://www.youtube.com/watch?v=W1x9BIgVQss",
    38: "https://www.youtube.com/watch?v=k6Pzfri444Y",
    39: "https://www.youtube.com/watch?v=-OWr6ra5Rak",
    40: "https://www.youtube.com/watch?v=uWlLewIaPOY",
    41: "https://www.youtube.com/watch?v=dj254ORKR30",
    42: "https://www.youtube.com/watch?v=9120oxxZE-Y",
    43: "https://www.youtube.com/watch?v=KOgNHxjHwqk",
    44: "https://www.youtube.com/watch?v=xiLqt4FUEzc",
    45: "https://www.youtube.com/watch?v=SNimRYX9YaQ",
    46: "https://www.youtube.com/watch?v=vG07DHeNH9c",
    47: "https://www.youtube.com/shorts/g-jfkK3hSpA",
    48: "https://www.youtube.com/watch?v=ZYaXo3TZzkk",
    49: "https://www.youtube.com/watch?v=sVVBjEwq3Rc",
    50: "https://www.youtube.com/watch?v=I_X_kOy86AE",
    51: "https://www.youtube.com/watch?v=Rcf_VUkoF88&t=16s",
    52: "https://www.youtube.com/watch?v=dzfpaJkr_Q4",
    53: "https://www.youtube.com/watch?v=w0D2v3ptfbU",
    54: "https://www.youtube.com/watch?v=d3wzIl-rVzs",
    55: "https://www.youtube.com/watch?v=TzFyIFBBrFo",
    56: "https://www.youtube.com/watch?v=xtMICg0KGtI",
    57: "https://www.youtube.com/watch?v=YPL9zdaftdI",
    58: "https://www.youtube.com/watch?v=ZyGsvmer55M&t=11s",
    59: "https://www.youtube.com/watch?v=7ROaS5ITuAU",
    60: "https://www.youtube.com/watch?v=EMTMscHNDjc&t=37s",
    61: "https://www.youtube.com/watch?v=mJX4glWXfQs",
    62: "https://www.youtube.com/watch?v=t70eGxX-3_Q",
    63: "https://www.youtube.com/watch?v=GA_h02yYfvk",
    64: "https://www.youtube.com/watch?v=yYn6jsPqmZE",
    65: "https://www.youtube.com/shorts/GA83m5gJbUQ",
    66: "https://www.youtube.com/watch?v=vJtHOiPqlvY",
    67: "https://www.youtube.com/shorts/mkoOAwm31s0",
    68: "https://www.youtube.com/watch?v=-2Ny2CXIG1w",
    69: "https://www.youtube.com/watch?v=jZ_o_QcMds0",
    70: "https://www.youtube.com/watch?v=HE6iGbyezug",
    71: "https://www.youtube.com/watch?v=xeOv8cZMg2I&t=54s",
    72: "https://www.youtube.com/watch?v=cMu0Ij8j3_0",
    73: "https://www.youtube.com/watch?v=KjioHP3yTO0",
    74: "https://www.youtube.com/watch?v=W6_bZgbX9rU",
    75: "https://www.youtube.com/watch?v=W9ndHRcq--c",
    76: "https://www.youtube.com/watch?v=5VLV3VpDLxQ",
    77: "https://www.youtube.com/watch?v=fJdZpi5lXb0",
    78: "https://www.youtube.com/watch?v=ovLHUP6wjmk",
    79: "https://www.youtube.com/watch?v=mjl4pFQeCxE",
    80: "https://www.youtube.com/watch?v=13YhMW5qdOI",
    81: "https://www.youtube.com/watch?v=gqrBngRMEPg",
    82: "https://www.youtube.com/watch?v=du9q1BldDHU",
    83: "https://www.youtube.com/watch?v=eeiqjyYgPew",
    84: "https://www.youtube.com/watch?v=xmj4VzjNo6s",
    85: "https://www.youtube.com/watch?v=tqpwhtw54mQ",
    86: "https://www.youtube.com/watch?v=I3NLQ20-BV4",
    87: "https://www.youtube.com/watch?v=nL41mkmg2Qg",
    88: "https://www.youtube.com/watch?v=W9wWVY7aCuk",
    89: "https://www.youtube.com/watch?v=t4Es8mwdYlE",
    90: "https://www.youtube.com/watch?v=8epUyIsYERc",
    91: "https://www.youtube.com/watch?v=mJX4glWXfQs&t=20s",
    92: "https://www.youtube.com/watch?v=0bjJPOA18eo",
    93: "https://www.youtube.com/watch?v=j7s9VRsrm9o",
    94: "https://www.youtube.com/watch?v=chnArCaEpqA",
    95: "https://www.youtube.com/watch?v=4meB2PHUnsE",
    96: "https://www.youtube.com/watch?v=mn8rlhOV5Gg",
    97: "https://www.youtube.com/watch?v=FmMTvUoY06o",
    98: "https://www.youtube.com/watch?v=eY-RvCkYnqQ",
    99: "https://www.youtube.com/watch?v=cDz2glT5JLA",
    100: "https://www.youtube.com/watch?v=ffuakdFmuh4",
    101: "https://www.youtube.com/watch?v=8HycHjpapTY",
    102: "https://www.youtube.com/watch?v=voO7XqucReo",
    103: "https://www.youtube.com/watch?v=nj-DjQFEZb0",
    104: "https://www.youtube.com/watch?v=vWb4uQDFnLY",
    105: "https://www.youtube.com/watch?v=kK1JtK16IvQ",
    129: "https://www.youtube.com/watch?v=-PHTqnbW3_k",
}

def update_source_urls():
    success = 0
    fail = 0
    for recipe_id, youtube_url in YOUTUBE_MAPPING.items():
        try:
            res = requests.patch(
                f"{API}/api/recipes/{recipe_id}",
                json={"youtube_url": youtube_url}
            )
            if res.status_code == 200:
                data = res.json()
                print(f"  [OK] {recipe_id}: {data.get('title', '?')} -> {youtube_url[:50]}...")
                success += 1
            else:
                print(f"  [FAIL] {recipe_id}: HTTP {res.status_code} - {res.text[:100]}")
                fail += 1
        except Exception as e:
            print(f"  [ERROR] {recipe_id}: {e}")
            fail += 1

    print(f"\n완료: 성공 {success}개, 실패 {fail}개")

if __name__ == "__main__":
    print(f"=== YouTube URL 일괄 업데이트 ({len(YOUTUBE_MAPPING)}개) ===")
    update_source_urls()