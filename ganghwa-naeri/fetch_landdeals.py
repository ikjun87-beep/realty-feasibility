#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
강화군(LAWD 28710) 토지 실거래가 취득 → 화도면·계획관리·전(田)/대(垈) 필터 → 평단가 통계
data.go.kr '국토교통부_토지 매매 신고 정보'(RTMSDataSvcLandTrade) 사용.
사용법:  DATAGO_KEY='서비스키(Decoding)' python3 fetch_landdeals.py [개월수]
"""
import os, sys, json, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from collections import defaultdict

KEY = os.environ.get("DATAGO_KEY", "").strip()
LAWD = "28710"          # 인천 강화군
MONTHS = int(sys.argv[1]) if len(sys.argv) > 1 else 24
BASE_YM = 202607        # 조회 시작(최근)에서 과거로. 필요시 조정.
EUP = "화도면"
END = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"

def ym_list(n, base=BASE_YM):
    y, m = base//100, base%100; out=[]
    for _ in range(n):
        out.append(f"{y}{m:02d}")
        m-=1
        if m==0: y-=1; m=12
    return out

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")  # data.go.kr WAF가 기본 UA 차단 → 필수

def fetch(ym):
    q = urllib.parse.urlencode({"serviceKey":KEY,"LAWD_CD":LAWD,"DEAL_YMD":ym,
                                "pageNo":"1","numOfRows":"500"}, safe="%")
    req = urllib.request.Request(END+"?"+q, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")

def txt(item, tag):
    e = item.find(tag); return e.text.strip() if e is not None and e.text else ""

def main():
    if not KEY: sys.exit("DATAGO_KEY 환경변수가 비어있습니다. data.go.kr 서비스키(Decoding) 필요.")
    deals=[]
    for ym in ym_list(MONTHS):
        time.sleep(0.5)
        try: body = fetch(ym)
        except Exception as e: print(f"[{ym}] 오류 {e}"); continue
        if "<resultCode>" in body and "<resultCode>00</resultCode>" not in body and "<resultCode>000</resultCode>" not in body:
            # 인증 오류 등
            print(f"[{ym}] API 응답: {body[:200]}"); continue
        try: root = ET.fromstring(body)
        except ET.ParseError: print(f"[{ym}] XML 파싱 실패: {body[:150]}"); continue
        for it in root.iter("item"):
            umd = txt(it,"umdNm") or txt(it,"법정동")
            if EUP not in umd and EUP.replace("면","") not in umd: continue
            try:
                amt = int(txt(it,"dealAmount").replace(",","")) * 10000  # 만원→원
                area = float(txt(it,"dealArea"))
            except: continue
            if area<=0: continue
            deals.append({"ym":ym,"umd":umd,"jimok":txt(it,"landCd") or txt(it,"jimok"),
                          "use":txt(it,"landUse") or txt(it,"지역"),"area":area,
                          "amt":amt,"ppm":amt/area,"pyeong_price":amt/(area/3.305785)})
    print(f"\n화도면 토지 실거래: {len(deals)}건 (최근 {MONTHS}개월)")
    if not deals:
        print("→ 거래 없음/키 미승인. 국토부 실거래가 공개시스템 수동확인 권장."); return
    # 통계
    pp=sorted(d["pyeong_price"] for d in deals)
    n=len(pp); med=pp[n//2]
    print(f"평단가: 최저 {pp[0]:,.0f} · 중앙 {med:,.0f} · 최고 {pp[-1]:,.0f} 원/평")
    print(f"평균 {sum(pp)/n:,.0f} 원/평")
    by=defaultdict(list)
    for d in deals: by[d["use"] or "미상"].append(d["pyeong_price"])
    print("\n용도지역별 평단가(원/평, 건수):")
    for u,v in sorted(by.items(), key=lambda x:-len(x[1])):
        print(f"  {u:12s} 중앙 {sorted(v)[len(v)//2]:>10,.0f}  ({len(v)}건)")
    json.dump(deals, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"landdeals.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n저장: landdeals.json")

if __name__=="__main__": main()
