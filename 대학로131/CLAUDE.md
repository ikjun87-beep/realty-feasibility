# CLAUDE.md — 대학로 131 보고서 프로젝트 고정정보

## 프로젝트
대구 북구 대학로 131(= 산격동 1391-4 = GS25 산격점) 상가주택 **매입 → 리모델링 → 임대수익** 타당성 검토 보고서.

## 파일 구조 (`/home/jun/projects/대학로131_매입리모델링/`)
- `리포트_원본(PDF소스).html` — **SSOT. 수정은 여기서만.**
- `대학로131_매입리모델링수익_검토리포트.pdf` — 최종 산출물(파생물)
- `build_pdf.py` — SSOT HTML → PDF (WeasyPrint + keep-all 주입). **PDF 재생성은 이 스크립트로만.**
- `build_map.py` — CARTO 타일 합성 지도 생성기(현재 PDF엔 미사용, 사용자 제공 지도 사용 중)
- `지도_실제.png` — 슬라이드 3 지도 이미지(940×640)
- `디자인.md` — 디자인 표준(네이비/골드, 16:9, Pretendard). §7 "핀 좌표 추정 금지".
- `미리보기_N페이지.png` — 페이지 미리보기
- `JN.md` — 진행상태·다음할일

## 렌더 방법
```
<venv>/python build_pdf.py     # 스크래치패드 .venv 사용 (weasyprint/pymupdf 설치됨)
```
- Chrome/puppeteer는 이 환경에서 실행 불가(시스템 라이브러리 없음) → WeasyPrint 사용.
- 폰트: Pretendard(설치됨), 폴백 NanumGothic/Malgun. 둘 다 `~/.local/share/fonts`.

## 디자인 규격 (디자인.md 요약)
- 포맷: `@page size:297mm 167mm; margin:0` (16:9 가로 슬라이드), `.slide` = 297×167mm, `page-break-after:always`
- 색: --navy #1b2738 / --gold #b3873a / --gold-l #f3ecdc / --ink #21262d / --mut #656565 / --line #dfdfdf / --soft #f5f5f5
- 폰트 Pretendard 단일. box-shadow 0(깊이는 1px line + soft 배경). 숫자 tabular-nums.
- 컴포넌트: .shead(다크헤더+골드바) / .kpi / .card / .call(warn·ok·amber·gold) / table(2px navy head·gold 합계행) / ul.clean(골드 45°마커) / .facts / .tag / .chart(.brow 골드/네이비 막대) / .tl(타임라인) / .scen(시나리오)

## 관련 메모리
- `korean-address-geocoding` — 한국 도로명은 OSM/Nominatim 금지, VWorld/juso/Kakao + POI 교차검증
- `daehak131-project` — 프로젝트 핵심 사실
