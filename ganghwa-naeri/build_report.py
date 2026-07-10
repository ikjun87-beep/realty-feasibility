#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""map_data.json + parcels.geojson -> 인터랙티브 검토 리포트 index.html 생성"""
import json, math, os
OUT=os.path.dirname(os.path.abspath(__file__))
md=json.load(open(os.path.join(OUT,"map_data.json"),encoding="utf-8"))["parcels"]

# 투영: 경위도 -> 로컬미터 -> SVG(1000x900, y뒤집기)
allc=[c for p in md for c in p["ring"]]
minx=min(c[0] for c in allc); maxx=max(c[0] for c in allc)
miny=min(c[1] for c in allc); maxy=max(c[1] for c in allc)
lat0=(miny+maxy)/2; R=6378137; k=math.cos(math.radians(lat0))
def m(x,y): return ((x-minx)*math.radians(1)*R*k,(y-miny)*math.radians(1)*R)
Wm=m(maxx,miny)[0]; Hm=m(minx,maxy)[1]
PAD=24; VW=1000; sc=(VW-2*PAD)/Wm; VH=Hm*sc+2*PAD
def to_svg(x,y):
    mx,my=m(x,y); return (PAD+mx*sc, VH-PAD-my*sc)
def area_m2(ring):
    pts=[m(x,y) for x,y in ring]
    s=sum(pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1] for i in range(len(pts)-1))
    return abs(s)/2
JIMOK_FULL={"대":"대지","묘":"묘지","전":"전","답":"답","임":"임야","도":"도로","구":"구거","천":"하천","과":"과수원","목":"목장","잡":"잡종지","임야":"임야"}
parcels=[]
for p in md:
    ring=p["ring"]
    pts=[to_svg(x,y) for x,y in ring]
    a=area_m2(ring)
    parcels.append({"pts":[[round(x,1),round(y,1)] for x,y in pts],"cls":p["cls"],
        "label":p["label"],"jibun":p["jibun"],"jimok":p["jimok"],
        "jimokFull":JIMOK_FULL.get(p["jimok"],p["jimok"]),"area":round(a),"pyeong":round(a/3.305785,1)})

# 대상 3필지 요약
tg={x["label"]:x for x in parcels if x["cls"]=="target"}
total_p=sum(tg[l]["pyeong"] for l in tg)
GOSI={"144-1":133100,"140-1":46700,"140-3":70700}
for l in tg: tg[l]["gosi"]=GOSI.get(l,0); tg[l]["gosiTot"]=round(tg[l]["area"]*GOSI.get(l,0))
gosi_total=sum(tg[l]["gosiTot"] for l in tg)

# 대상 3필지의 도로 접함 프론티지 세그먼트(SVG좌표) 계산
def msegs(ring): return [(m(*ring[i]),m(*ring[i+1])) for i in range(len(ring)-1)]
def near(p,q,t=0.7): return abs(p[0]-q[0])<t and abs(p[1]-q[1])<t
road_rings=[p["ring"] for p in md if p["cls"]=="road"]
frontage=[]  # [{"label","x1","y1","x2","y2","len"}]
for p in md:
    if p["cls"]!="target": continue
    for (a1,a2) in msegs(p["ring"]):
        for rr in road_rings:
            hit=False
            for (b1,b2) in msegs(rr):
                if (near(a1,b1) and near(a2,b2)) or (near(a1,b2) and near(a2,b1)): hit=True;break
            if hit:
                # 원래 경위도 세그먼트를 다시 SVG로
                idx=msegs(p["ring"]).index((a1,a2))
                (x1,y1),(x2,y2)=p["ring"][idx],p["ring"][idx+1]
                s1=to_svg(x1,y1);s2=to_svg(x2,y2)
                frontage.append({"label":p["label"],"x1":round(s1[0],1),"y1":round(s1[1],1),
                    "x2":round(s2[0],1),"y2":round(s2[1],1),"len":round(math.dist(a1,a2),1)})
                break

# ===== 3획지 면적균등 분할(래스터 기반) =====
def mrings():
    return [[m(x,y) for x,y in p["ring"]] for p in md if p["cls"]=="target"]
def pip(px,py,ring):
    inside=False;n=len(ring);j=n-1
    for i in range(n):
        xi,yi=ring[i];xj,yj=ring[j]
        if ((yi>py)!=(yj>py)) and (px < (xj-xi)*(py-yi)/((yj-yi) or 1e-9)+xi): inside=not inside
        j=i
    return inside
def msvg(mx,my): return (round(PAD+mx*sc,1), round(VH-PAD-my*sc,1))
def compute_split():
    rings=mrings()
    xs=[q[0] for r in rings for q in r]; ys=[q[1] for r in rings for q in r]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    cell=0.5; nx=int((x1-x0)/cell)+1; ny=int((y1-y0)/cell)+1
    grid=[[False]*nx for _ in range(ny)]
    rowcnt=[0]*ny
    for iy in range(ny):
        py=y0+(iy+0.5)*cell
        for ix in range(nx):
            px=x0+(ix+0.5)*cell
            if any(pip(px,py,r) for r in rings):
                grid[iy][ix]=True; rowcnt[iy]+=1
    total=sum(rowcnt); a3=total/3
    # y컷: 남(y0)→북 누적 1/3,2/3
    cum=0; yA=yB=None
    for iy in range(ny):
        cum+=rowcnt[iy]
        if yA is None and cum>=a3: yA=y0+(iy+1)*cell
        if yB is None and cum>=2*a3: yB=y0+(iy+1)*cell; break
    cellA=cell*cell*3.305785  # per cell 평 아님, 면적㎡
    def band_area(lo,hi):
        c=sum(rowcnt[iy] for iy in range(ny) if lo<=y0+(iy+0.5)*cell<hi)
        return c*cell*cell
    lots=[("A",y0,yA),("B",yA,yB),("C",yB,y1+cell)]
    bx=[x0+(ix+0.5)*cell for iy in range(ny) if y0+(iy+0.5)*cell<y0+4
        for ix in range(nx) if grid[iy][ix]]
    dx=sorted(bx)[len(bx)//2] if bx else (x0+x1)/2
    def xspan(yv):
        iy=min(ny-1,max(0,int((yv-y0)/cell)))
        row=[x0+(ix+0.5)*cell for ix in range(nx) if grid[iy][ix]]
        return (min(row),max(row)) if row else (x0,x1)
    # 타깃 전용 확대 좌표계 (560x460, 여백 26)
    VWv,VHv,pd=560,460,26
    S=min((VWv-2*pd)/((x1-x0) or 1),(VHv-2*pd)/((y1-y0) or 1))
    def t(mx,my): return [round(pd+(mx-x0)*S,1), round(VHv-pd-(my-y0)*S,1)]
    out={"viewBox":f"0 0 {VWv} {VHv}","cutlines":[],"lots":[],"driveway":[],"parcels":[],"frontage":[]}
    for p in md:
        if p["cls"]!="target": continue
        ring=[t(*m(x,y)) for x,y in p["ring"]]
        out["parcels"].append({"pts":ring,"label":p.get("label",""),"jimok":p.get("jimok","")})
    for yv in (yA,yB):
        a,b=xspan(yv-cell); out["cutlines"].append(t(a,yv)+t(b,yv))
    out["driveway"]=[t(dx-2,y0),t(dx+2,y0),t(dx+2,y1),t(dx-2,y1)]
    for name,lo,hi in lots:
        ar=band_area(lo,hi); c=t(dx,(lo+hi)/2)
        out["lots"].append({"label":name,"area":round(ar),"pyeong":round(ar/3.305785,1),"cx":c[0],"cy":c[1]})
    # 도로 프론티지(대상↔도로 공유변)을 타깃좌표로
    for seg in []:
        pass
    return out
try: split=compute_split()
except Exception as e: split=None; print("split 계산 실패:",e)

DATA={"viewBox":f"0 0 {round(VW)} {round(VH)}","parcels":parcels,"frontage":frontage,"split":split,
      "summary":{"totalPyeong":round(total_p,1),"totalM2":round(sum(tg[l]['area'] for l in tg)),
                 "gosiTotal":gosi_total,"scaleBar_m":50,"scaleBar_px":round(50*sc,1)}}

tpl=open(os.path.join(OUT,"_template.html"),encoding="utf-8").read()
html=tpl.replace("/*__DATA__*/","const DATA="+json.dumps(DATA,ensure_ascii=False)+";")
open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(html)
print("index.html 생성. 대상합계 %.1f평 / 공시총액 %s원 / frontage세그 %d개"%(total_p,format(gosi_total,","),len(frontage)))
