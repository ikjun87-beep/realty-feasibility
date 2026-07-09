#!/usr/bin/env python3
"""한국 주소 → 정확 좌표 확정 (Kakao Local REST API).

왜 이 방식인가:
  대학로131에서 OSM/Nominatim이 '도로 중심선' 좌표를 반환해 핀이 틀렸다.
  Kakao는 지번/도로명을 '필지' 기준으로 해석하고, POI(장소) 검색으로 교차검증 가능.
  → 좌표를 눈으로 맞추는 시행착오(토큰 소모) 대신 API로 1회 확정한다.

사용:
  export KAKAO_REST_KEY=<발급키>   # developers.kakao.com → 앱 → REST API 키
  python geocode.py "경기도 화성시 향남읍 장짐리 228-1"
  python geocode.py "경기도 화성시 향남읍 장짐리 228-1" --poi "향남산업단지"  # 교차검증

출력: JSON {address_in, matched(지번/도로명), lat, lon, source, cross}
"""
import os, sys, json, urllib.parse, urllib.request

def _load_key():
    k = os.environ.get("KAKAO_REST_KEY", "").strip()
    if k:
        return k
    # 셸 env는 호출 간 유지되지 않으므로 로컬 키파일(gitignore) 폴백
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, ".kakao_key"), os.path.expanduser("~/.config/realty/kakao_key")):
        if os.path.exists(p):
            return open(p).read().strip()
    return ""

KEY = _load_key()
BASE = "https://dapi.kakao.com/v2/local"

def _get(path, params):
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"KakaoAK {KEY}"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def geocode(addr):
    """주소 → 좌표. 지번/도로명 모두 반환값에 담아 검증 가능하게."""
    d = _get("search/address.json", {"query": addr, "analyze_type": "similar", "size": 5})
    docs = d.get("documents", [])
    if not docs:
        return None
    top = docs[0]
    # x=경도(lon), y=위도(lat)  (WGS84)
    out = {
        "lat": float(top["y"]), "lon": float(top["x"]),
        "matched_jibun": (top.get("address") or {}).get("address_name"),
        "matched_road": (top.get("road_address") or {}).get("address_name"),
        "region": (top.get("address") or {}).get("region_3depth_name"),
        "candidates": len(docs), "source": "kakao/address",
    }
    return out

def poi(name, x=None, y=None):
    """상호(POI) 검색으로 좌표 교차검증. 좌표 주면 근접순 정렬."""
    p = {"query": name, "size": 3}
    if x and y:
        p.update({"x": x, "y": y, "radius": 20000, "sort": "distance"})
    d = _get("search/keyword.json", p)
    return [{"name": r["place_name"], "lat": float(r["y"]), "lon": float(r["x"]),
             "addr": r.get("road_address_name") or r.get("address_name")}
            for r in d.get("documents", [])]

if __name__ == "__main__":
    if not KEY:
        print("ERROR: 환경변수 KAKAO_REST_KEY 미설정. developers.kakao.com에서 REST API 키 발급 후\n"
              "  export KAKAO_REST_KEY=<키>", file=sys.stderr)
        sys.exit(2)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    addr = args[0] if args else "경기도 화성시 향남읍 장짐리 228-1"
    poi_name = None
    if "--poi" in sys.argv:
        poi_name = sys.argv[sys.argv.index("--poi") + 1]
    res = geocode(addr)
    if not res:
        print(json.dumps({"address_in": addr, "error": "no match"}, ensure_ascii=False))
        sys.exit(1)
    res["address_in"] = addr
    if poi_name:
        res["cross"] = poi(poi_name, res["lon"], res["lat"])
    print(json.dumps(res, ensure_ascii=False, indent=2))
