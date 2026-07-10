#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""주변 필지까지 지적도 취득 -> 도로/구거 식별 -> 대상 3필지 강조 SVG 렌더 + 도로접함 리포트"""
import os, json, math, urllib.parse, urllib.request

KEY=os.environ.get("VWORLD_KEY","").strip()
OUT=os.path.dirname(os.path.abspath(__file__))
TARGET={"2871034021101440001":"144-1","2871034021101400001":"140-1","2871034021101400003":"140-3"}
# 대상필지 대략 중심(앞 단계 결과)
CLON,CLAT=126.41007,37.64542
D=0.0016  # 약 ±140m

def get(url):
    with urllib.request.urlopen(url,timeout=30) as r: return json.loads(r.read().decode())

def fetch_box():
    box=f"BOX({CLON-D},{CLAT-D},{CLON+D},{CLAT+D})"
    q=urllib.parse.urlencode({"service":"data","request":"GetFeature","data":"LP_PA_CBND_BUBUN",
        "key":KEY,"domain":"http://localhost","format":"json","crs":"EPSG:4326",
        "geomFilter":box,"size":"1000"})
    d=get("https://api.vworld.kr/req/data?"+q)
    return d["response"]["result"]["featureCollection"]["features"]

def rings(f):
    g=f["geometry"]
    return g["coordinates"] if g["type"]=="Polygon" else [p[0] for p in g["coordinates"]]

def jimok(jibun):
    for ch in jibun:
        if '가'<=ch<='힣': return ch  # 첫 한글 = 지목약자
    return "?"

def area_m2(ring,lat0):
    R=6378137.0;k=math.cos(math.radians(lat0))
    pts=[(math.radians(x)*R*k,math.radians(y)*R) for x,y in ring]
    s=sum(pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1] for i in range(len(pts)-1))
    return abs(s)/2

def shared_len(a,b,lat0):
    """두 링의 공유 경계 길이(m) 근사: a의 각 변이 b의 어떤 변과 겹치는지"""
    R=6378137.0;k=math.cos(math.radians(lat0))
    def M(x,y): return (math.radians(x)*R*k,math.radians(y)*R)
    def segs(r): return [(M(*r[i]),M(*r[i+1])) for i in range(len(r)-1)]
    def near(p,q,t=0.6): return abs(p[0]-q[0])<t and abs(p[1]-q[1])<t
    tot=0
    for (a1,a2) in segs(a):
        for (b1,b2) in segs(b):
            if (near(a1,b1) and near(a2,b2)) or (near(a1,b2) and near(a2,b1)):
                tot+=math.dist(a1,a2)
    return tot

feats=fetch_box()
print(f"주변 필지 {len(feats)}개 취득")
targets=[]; roads=[]
for f in feats:
    jb=f["properties"].get("jibun","")
    jm=jimok(jb)
    f["_jm"]=jm; f["_jb"]=jb
    if f["properties"].get("pnu") in TARGET: targets.append(f)
    if jm in ("도","천","구"): roads.append(f)  # 도로/하천/구거

# 도로접함 리포트
print("\n=== 대상 3필지 도로/구거 접함 ===")
for t in targets:
    tr=rings(t)[0]; lat0=sum(p[1] for p in tr)/len(tr)
    name=TARGET[t["properties"]["pnu"]]
    hits=[]
    for rd in roads:
        L=shared_len(tr,rings(rd)[0],lat0)
        if L>0.5: hits.append((rd["_jb"],round(L,1)))
    a=area_m2(tr,lat0)
    print(f"- {name} ({t['_jm']}, {a:.0f}㎡/{a/3.305785:.0f}평): "+("도로접함 "+", ".join(f"{j}={l}m" for j,l in hits) if hits else "★도로 직접접함 없음(맹지 가능성)"))

# SVG 렌더
allpts=[p for f in feats for p in rings(f)[0]]
xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
W,H,pad=1100,1000,30
s=min((W-2*pad)/(maxx-minx),(H-2*pad)/(maxy-miny))
def T(x,y): return (pad+(x-minx)*s, H-(pad+(y-miny)*s))
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" style="background:#f7f7f4;font-family:sans-serif">']
for f in feats:
    r=rings(f)[0]; pts=" ".join(f"{T(x,y)[0]:.1f},{T(x,y)[1]:.1f}" for x,y in r)
    pnu=f["properties"].get("pnu"); jm=f["_jm"]
    if pnu in TARGET: fill,stroke,sw="#ff6b35cc","#c1440e",3
    elif jm in("도","천","구"): fill,stroke,sw="#b7c9d966","#7a93a8",1
    else: fill,stroke,sw="#ffffff","#cccccc",1
    svg.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    cx=sum(T(x,y)[0] for x,y in r)/len(r); cy=sum(T(x,y)[1] for x,y in r)/len(r)
    if pnu in TARGET:
        svg.append(f'<text x="{cx:.0f}" y="{cy:.0f}" font-size="15" font-weight="bold" text-anchor="middle" fill="#7a1f00">{TARGET[pnu]}·{jm}</text>')
    elif jm in("도","천","구"):
        svg.append(f'<text x="{cx:.0f}" y="{cy:.0f}" font-size="10" text-anchor="middle" fill="#456">{jm}</text>')
svg.append('</svg>')
open(os.path.join(OUT,"neighbors.svg"),"w",encoding="utf-8").write("\n".join(svg))
print(f"\n저장: neighbors.svg")
