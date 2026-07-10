#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
강화 화도면 내리 3필지(144-1, 140-1, 140-3) 지적 경계 취득 + 면적 계산 + SVG 렌더
사용법:  VWORLD_KEY=발급받은키  python3 fetch_parcels.py
- 외부 라이브러리 불필요(requests만 사용). shapely/matplotlib 없이 순수 파이썬으로 면적·SVG 처리.
"""
import os, sys, json, math, urllib.parse, urllib.request

KEY = os.environ.get("VWORLD_KEY", "").strip()
JIBUN = ["인천광역시 강화군 화도면 내리 144-1",
         "인천광역시 강화군 화도면 내리 140-1",
         "인천광역시 강화군 화도면 내리 140-3"]
OUT = os.path.dirname(os.path.abspath(__file__))

def http_get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def geocode(addr):
    """지번주소 -> (lon, lat)"""
    q = urllib.parse.urlencode({
        "service":"address","request":"getcoord","version":"2.0",
        "crs":"epsg:4326","address":addr,"type":"parcel","format":"json","key":KEY})
    d = http_get("https://api.vworld.kr/req/address?"+q)
    if d["response"]["status"] != "OK":
        raise RuntimeError(f"geocode 실패: {addr} -> {d['response'].get('error')}")
    p = d["response"]["result"]["point"]
    return float(p["x"]), float(p["y"])

def parcel_at(lon, lat):
    """좌표점이 속한 연속지적도 필지 폴리곤+속성 취득"""
    q = urllib.parse.urlencode({
        "service":"data","request":"GetFeature","data":"LP_PA_CBND_BUBUN",
        "key":KEY,"domain":"http://localhost","format":"json","crs":"EPSG:4326",
        "geomFilter":f"POINT({lon} {lat})","size":"5"})
    return http_get("https://api.vworld.kr/req/data?"+q)

def poly_rings(feat):
    g = feat["geometry"]; t = g["type"]
    return g["coordinates"] if t=="Polygon" else [r for poly in g["coordinates"] for r in poly]

def area_m2(ring, lat0):
    """경위도 링 -> 대략 면적(㎡). 국소 평면 근사(경도 축척 cos 보정)."""
    R=6378137.0; k=math.cos(math.radians(lat0))
    pts=[(math.radians(x)*R*k, math.radians(y)*R) for x,y in ring]
    s=0.0
    for i in range(len(pts)-1):
        s += pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1]
    return abs(s)/2.0

def main():
    if not KEY:
        sys.exit("VWORLD_KEY 환경변수가 비어있습니다.  예)  VWORLD_KEY=xxxx python3 fetch_parcels.py")
    feats=[]
    for addr in JIBUN:
        lon,lat = geocode(addr)
        d = parcel_at(lon,lat)
        fc = d["response"]["result"]["featureCollection"]["features"]
        if not fc:
            print(f"[경고] 필지 미조회: {addr}"); continue
        f=fc[0]; f["_addr"]=addr; feats.append(f)
        print(f"OK  {addr}  (lon={lon:.6f}, lat={lat:.6f})")
    if not feats: sys.exit("취득된 필지가 없습니다.")

    # 면적 계산
    all_x=[]; all_y=[]; total=0.0
    print("\n=== 필지별 면적 ===")
    for f in feats:
        ring = poly_rings(f)[0]
        lat0 = sum(p[1] for p in ring)/len(ring)
        a = area_m2(ring, lat0)
        pyeong = a/3.305785
        prop=f["properties"]
        print(f"- {f['_addr'].split()[-1]:8s} 지목:{prop.get('jimok','?'):3s} "
              f"면적≈{a:8.1f}㎡ ({pyeong:6.1f}평)  공시지가:{prop.get('pnilto','?')}")
        total+=a
        for x,y in ring: all_x.append(x); all_y.append(y)
    print(f"  합계 ≈ {total:.1f}㎡ ({total/3.305785:.1f}평)")

    # GeoJSON 저장
    gj={"type":"FeatureCollection","features":feats}
    with open(os.path.join(OUT,"parcels.geojson"),"w",encoding="utf-8") as fp:
        json.dump(gj,fp,ensure_ascii=False)

    # SVG 렌더(경계 형상 확인용)
    W=900;H=700;pad=40
    minx,maxx=min(all_x),max(all_x); miny,maxy=min(all_y),max(all_y)
    sx=(W-2*pad)/(maxx-minx); sy=(H-2*pad)/(maxy-miny); s=min(sx,sy)
    def T(x,y): return (pad+(x-minx)*s, H-(pad+(y-miny)*s))
    colors=["#4C78A8","#F58518","#54A24B"]
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" style="background:#fff;font-family:sans-serif">']
    for i,f in enumerate(feats):
        ring=poly_rings(f)[0]
        pts=" ".join(f"{T(x,y)[0]:.1f},{T(x,y)[1]:.1f}" for x,y in ring)
        cx=sum(T(x,y)[0] for x,y in ring)/len(ring); cy=sum(T(x,y)[1] for x,y in ring)/len(ring)
        svg.append(f'<polygon points="{pts}" fill="{colors[i%3]}33" stroke="{colors[i%3]}" stroke-width="2"/>')
        svg.append(f'<text x="{cx:.0f}" y="{cy:.0f}" font-size="14" text-anchor="middle">{f["_addr"].split()[-1]}</text>')
    svg.append("</svg>")
    with open(os.path.join(OUT,"parcels.svg"),"w",encoding="utf-8") as fp:
        fp.write("\n".join(svg))
    print(f"\n저장: {OUT}/parcels.geojson , parcels.svg")

if __name__=="__main__":
    main()
