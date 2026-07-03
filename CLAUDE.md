# CLAUDE.md

## 프로젝트 목적
부동산 개발 현장별 **분양성·사업성 검토보고서**를 HTML(SSOT)→PDF 발표자료로 제작하는 저작 저장소.
루트 `분양성보고서-표준기준서.md`가 전 보고서 공통 표준(목차·섹션·디자인·품질게이트)이다.

## 폴더 구조
- `분양성보고서-표준기준서.md` — **공통 표준(STANDARD)**. 새 보고서는 이 표준 목차·§4 필수 체크리스트·§12 품질게이트를 따른다.
- `cashflow-report/` — 양산 물금 공동주택 **사업수지(현금흐름)** 통합보고서. 최신·완성본. cashflow-tool 엔진값 × 디자인.
  - `PRD_사업수지통합보고서.md`(로드맵·Phase) · `engine_result_양산.json`(엔진 진실값) · `양산_사업수지_보고서.html/.pdf`(11장) · `양산_사업수지_경영요약_1p.*`(임원 1p) · `양산_사업수지_ppt_프롬프트.txt`
- `dangha-parking/` — 당하동 주차전용건축물 **분양성** 검토(report 12장 + deck 13장). `README.md`에 산출물 안내.
- `ktower-geomdan/` — The K Tower 검단 **적정분양가·사업성** 검토(report + deck + `PRD.md`).
- 현장 폴더 공통 산출물: `report.html`/`deck.html`(SSOT) · `*.pdf`(파생) · `map_locator.*`(위치도) · `cover_art.html`→`cover_render*.png`(표지 배경)

## 기술·구조
- **HTML = SSOT, PDF = 파생물.** 발표형은 16:9 가로 슬라이드(297×167mm), `@page size` + 슬라이드마다 `page-break-after`.
- 렌더: **puppeteer-core 헤드리스 + 로컬 Chrome**. `render*.mjs`가 `.slide` 요소→PNG, HTML→PDF(`page.pdf({preferCSSPageSize:true})`) 생성.
  ⚠ 렌더 스크립트·`node_modules`·`package.json`은 머신 고유 경로라 **`.gitignore`(로컬 전용)** — 새 클론엔 없음(재작성 필요).
- 디자인 규율("다방"): **Pretendard 단일 패밀리**, **box-shadow:0**(깊이는 1px 헤어라인+배경톤으로), 3계층 색 = **골드 `#b3873a` / 그래파이트 네이비 `#1b2738` / 그레이**, 표지=쿨 네이비·마무리=웜 톤. (표준기준서 §9 폼·§7 지도 표준 준수)
- 빌드·테스트 프레임워크 없음(정적 HTML).

## 주요 명령 (WSL, 이 머신)
- 슬라이드 PNG 렌더: `cd <현장폴더> && LD_LIBRARY_PATH=<chromelibs> node render.mjs`
- PDF 생성: `node render_pdf.mjs <입력.html> <출력.pdf>`
- ⚠ Chrome 공유 라이브러리 없으면 `libnspr4.so` 오류 → 메모리 `render-chrome-no-sudo` 절차로 `chromelibs` 재구성(apt-get download + dpkg-deb -x, sudo 불필요).
- 구글 드라이브(G:)는 WSL 미마운트 → PowerShell(`powershell.exe`) 경유해 접근/복사.

## 규칙·주의
- **수정은 HTML에서만.** PDF 단독 수정 금지 — 항상 HTML 고치고 재렌더.
- 표준기준서 준수: 목차 **MECE**(내용 중복 0), 신뢰도 라벨링(DRAFT/추정/`[확인필요]`), §12 품질게이트 통과, **지도 핀은 실주소 지오코딩**(좌표 추정 금지).
- **사업수지: 엔진 산출값이 권위값.** 항등식 `사업이익 = 총수입 − 지출(VAT포함) = CF 누적시재`가 잔차 0·멱등일 때만 신뢰. **가부(go/no-go) 미판정 · 투자권유 아님** — 지표만 제시.
- 미확보 수치는 **창작 금지** → `[확인필요]` 태그.
- 커밋: **main 직접**(저장소 관행). 메시지 끝에 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. 한글 파일명 사용.

---
**세션 시작 시 `JN.md`를 먼저 읽고 이어서 작업할 것.**
