# CLAUDE.md

## 프로젝트 목적
부동산 개발 현장별 **분양성·사업성 검토보고서**를 HTML(SSOT)→PDF 발표자료로 제작하는 저작 저장소.
루트 `분양성보고서-표준기준서.md`가 전 보고서 공통 표준(목차·섹션·디자인·품질게이트)이다.

## 폴더 구조
- `분양성보고서-표준기준서.md` — **공통 표준(STANDARD)**. 새 보고서는 이 표준 목차·§4 필수 체크리스트·§12 품질게이트를 따른다.
- `cashflow-report/` — 양산 물금 공동주택 **사업수지(현금흐름)** 통합보고서. 최신·완성본. cashflow-tool 엔진값 × 디자인.
  - `PRD_사업수지통합보고서.md`(로드맵·Phase) · `engine_result_양산.json`(엔진 진실값) · `양산_사업수지_보고서.html/.pdf`(11장) · `양산_사업수지_경영요약_1p.*`(임원 1p) · `양산_사업수지_ppt_프롬프트.txt`
- `화성향남장짐/` — 화성 향남 장짐지구 공동주택 **분양성·사업성** 검토(deck 13장, **진행중**). 자체 `JN.md`·`CLAUDE.md` 보유(현장 정본 — **단위 천원·개조식·요인비교법** 등 확정 규칙 포함). **카카오맵**(`map_*_kakao.html` + `render_kakao.mjs`), `fetch_infra.py`(Kakao Local 반경 실측), `geocode.py`(좌표 확정). ⚠ `_원자료/추출_핵심팩트.md`는 일부 stale — JN.md 우선.
- `ganghwa-naeri/` — 강화 내리 3필지 **지적검토 + 전원주택 가설계/3D**. 파이썬 빌드(`build_report.py`·`fetch_landdeals.py`·`fetch_parcels.py`·`neighbors_map.py`) → `index.html`/`house.html`.
- `dangha-parking/` — 당하동 주차전용건축물 **분양성** 검토(report 12장 + deck 13장). `README.md`에 산출물 안내.
- `ktower-geomdan/` — The K Tower 검단 **적정분양가·사업성** 검토(report + deck + `PRD.md`).
- `대학로131/` — **(참고)** 대구 북구 대학로 131(= 산격동 1391-4) **매입·리모델링·수익 검토** 보고서의 `JN.md`·`CLAUDE.md` 사본. 실제 산출물(HTML SSOT·PDF·지도·build 스크립트)은 형제 폴더 `../대학로131_매입리모델링/`에 있음. 표지·표기 톤(정보전달 목적, 이모지·책임회피 문구 금지)과 위치 지오코딩 교훈 참고용.
- 현장 폴더 공통 산출물: `report.html`/`deck.html`(SSOT) · `*.pdf`(파생) · `map_locator.*`(위치도) · `cover_art.html`→`cover_render*.png`(표지 배경)

## 기술·구조
- **HTML = SSOT, PDF = 파생물.** 발표형은 16:9 가로 슬라이드(297×167mm), `@page size` + 슬라이드마다 `page-break-after`.
- 렌더: **puppeteer-core 헤드리스 + 로컬 Chrome**. `render*.mjs`가 `.slide` 요소→PNG, HTML→PDF(`page.pdf({preferCSSPageSize:true})`) 생성.
  ⚠ 렌더 스크립트·`node_modules`·`package.json`은 머신 고유 경로라 **`.gitignore`(로컬 전용)** — 새 클론엔 없음(재작성 필요).
- 디자인 규율("다방"): **Pretendard 단일 패밀리**, **box-shadow:0**(깊이는 1px 헤어라인+배경톤으로). **색은 라이트 시스템(2026-07-12~)** = **네이비 `#13243f`(구조·타이틀) + 스카이 `#3b86d1`(데이터/정보 액센트) + 골드 `#b3873a`(절제된 브랜드 액센트)**, 화이트 배경. **표지·본문·마무리 전부 라이트**(구 "표지 쿨네이비·마무리 웜" 다크 대비는 폐기). 강조색은 슬라이드당 1~2개. **확정 토큰·헤더 규칙은 루트 `디자인_색감_가이드.md` 참조**(표준기준서 §9 폼·§7 지도 표준과 함께 준수).
- 빌드·테스트 프레임워크 없음(정적 HTML).

## API 키 (카카오)
- **정본은 `화성향남장짐/.env`** — `KAKAO_REST_KEY`(Local API: 지오코딩·POI 반경) · `KAKAO_JS_KEY`(지도 SDK 렌더). **둘은 같은 앱의 서로 다른 키.**
- 점파일 `.kakao_key`·`.kakao_js_key`는 기존 스크립트(`geocode.py`·`fetch_infra.py`·`render_kakao.mjs`)용 **파생물**이며 직접 편집하지 않는다.
- ⚠ **점파일에만 두지 말 것** — `backup-secrets.sh`가 `.env`·`*.jks`만 걷어가서 2026-07-25 새 PC 이전 때 키가 통째로 소실됐다. 키 투입·검증·백업은 `bash ~/projects/easygroup-hq/scripts/set-kakao-keys.sh <REST키> [JS키]` 한 줄로.
- JS 키는 **JavaScript SDK 도메인에 `http://localhost:8766` 등록**이 되어야 실제 지도가 뜬다. 상세는 지식창고 `참조/카카오맵-API.md`.

## 주요 명령 (WSL, 이 머신)
- 슬라이드 PNG 렌더: `cd <현장폴더> && LD_LIBRARY_PATH=<chromelibs> node render.mjs`
- PDF 생성: `node render_pdf.mjs <입력.html> <출력.pdf>`
- ⚠ Chrome 공유 라이브러리 없으면 `libnspr4.so` 오류 → 메모리 `render-chrome-no-sudo` 절차로 `chromelibs` 재구성(apt-get download + dpkg-deb -x, sudo 불필요).
- 구글 드라이브(G:)는 WSL 미마운트 → PowerShell(`powershell.exe`) 경유해 접근/복사.

## 규칙·주의
- **수정은 HTML에서만.** PDF 단독 수정 금지 — 항상 HTML 고치고 재렌더.
- 표준기준서 준수: 목차 **MECE**(내용 중복 0), 신뢰도 라벨링(DRAFT/추정/`[확인필요]`), §12 품질게이트 통과, **지도 핀은 실주소 지오코딩**(좌표 추정 금지).
- **사업수지: 엔진 산출값이 권위값.** 항등식 `사업이익 = 총수입 − 지출(VAT포함) = CF 누적시재`가 잔차 0·멱등일 때만 신뢰.
  - ⚠ **잔차 0은 필요조건일 뿐 충분조건이 아님**(2026-07-17 향남장짐에서 실증). 원본 엑셀의 **셀 수식 자체가 틀리면** 항등식은 그대로 통과한다. 실제 사례: `현금흐름표!N101 = 사업수지표!AL88` **하드링크**라 "현금흐름표 일치"는 **같은 오류셀을 재인용하는 순환논리**(검증력 0)였고, 부호 오류(`CE89 = CC89 + CD89`) 하나가 사업이익을 **+120억 부풀림**. → **검증은 셀 수식 단위로**, 패널 내 **동일 항등식이 전 행에서 지켜지는지**(공유수식 비교) 확인할 것. 원본을 "일치하니 검증됐다"고 쓰지 말 것. **가부(go/no-go) 미판정 · 투자권유 아님** — 지표만 제시.
- 미확보 수치는 **창작 금지** → `[확인필요]` 태그.
- 커밋: **main 직접**(저장소 관행). 메시지 끝에 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. 한글 파일명 사용.

---
**세션 시작 시 `JN.md`를 먼저 읽고 이어서 작업할 것.**
