#!/usr/bin/env python3
"""사업지(장짐리 228-1) 반경 내 생활 인프라 실측 — Kakao Local API 카테고리 검색.
결과: infra.json  (창작 금지: 전부 API 실측값)
사용:  python3 fetch_infra.py
"""
import os, json, time, math, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(HERE, ".kakao_key"), encoding="utf-8").read().strip()
BASE = "https://dapi.kakao.com/v2/local"
SITE = (37.139655, 126.911075)   # 장짐리 228-1 (확정 좌표)

# Kakao 카테고리 그룹 코드
CATS = {
    "SC4": "학교",      "AC5": "학원",     "HP8": "병원",     "PM9": "약국",
    "MT1": "대형마트",  "CS2": "편의점",   "BK9": "은행",     "SW8": "지하철역",
    "CT1": "문화시설",  "AT4": "관광명소", "PO3": "공공기관", "OL7": "주유소",
    "FD6": "음식점",    "CE7": "카페",     "PK6": "주차장",   "AD5": "숙박",
}
RADII = [1000, 3000]   # m

def get(path, params):
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"KakaoAK {KEY}"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def haversine(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

out = {"site": {"lat": SITE[0], "lon": SITE[1]}, "radius_counts": {}, "nearest": {}}

for code, label in CATS.items():
    out["radius_counts"][label] = {}
    for rad in RADII:
        # total_count = 반경 내 전체 건수 (페이지네이션 없이 메타에서 획득)
        d = get("search/category.json", {
            "category_group_code": code, "x": SITE[1], "y": SITE[0],
            "radius": rad, "size": 1, "sort": "distance",
        })
        out["radius_counts"][label][f"{rad}m"] = d["meta"]["total_count"]
        time.sleep(0.05)

    # 가장 가까운 3곳 (거리 포함) — 3km 기준
    d = get("search/category.json", {
        "category_group_code": code, "x": SITE[1], "y": SITE[0],
        "radius": 5000, "size": 5, "sort": "distance",
    })
    near = []
    for doc in d["documents"]:
        dist = int(doc.get("distance") or haversine(SITE, (float(doc["y"]), float(doc["x"]))))
        near.append({"name": doc["place_name"], "dist_m": dist,
                     "cat": doc.get("category_name", "").split(">")[-1].strip()})
    out["nearest"][label] = near
    time.sleep(0.05)

json.dump(out, open(os.path.join(HERE, "infra.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("=== 반경별 시설 수 (Kakao Local 실측) ===")
print(f"{'카테고리':<10}{'1km':>7}{'3km':>7}")
for label in CATS.values():
    c = out["radius_counts"][label]
    print(f"{label:<10}{c['1000m']:>7}{c['3000m']:>7}")
print("\n=== 최근접 시설 ===")
for label in ["학교", "병원", "대형마트", "지하철역", "문화시설", "관광명소"]:
    n = out["nearest"][label]
    if n:
        print(f"{label:<8} " + " · ".join(f"{x['name']}({x['dist_m']}m)" for x in n[:3]))
print("\n저장: infra.json")
