---
version: 1
slug: "site-index-html"
primary_target: "site/index.html"
related_targets: ["site/agency.html","site/evidence.html"]
---

## Scope

올림픽공원 공연 혼잡 캘린더 정적 사이트 세 화면: site/index.html(수강생 캘린더, 주 화면), site/agency.html(기관 겹침 목록), site/evidence.html(근거와 검증). 모드: Operate(evidence는 Operate 안의 읽기 화면). 공용 site/app.css, site/app.js. 2026-11-17 사용자 요청으로 기존 '수영장 시간표 게시판' 세계를 교체하는 재설계. 승인된 목업: design/preview/mockup-calendar-1440.png, 원본 design/preview/calendar.html.

## Audience and job

주 사용자는 올림픽수영장 수강생. 내 강좌를 고르고, 공연 때문에 주차장이 붐비는 날과 내 수업이 겹치는지 한눈에 본 뒤 .ics로 휴대폰 캘린더에 넣는다. 기관 직원은 기간을 정해 겹치는 회차 목록을 보고 CSV를 내려받는다. 심사위원은 근거 화면에서 2025년 실데이터 검증 수치를 확인한다. 사용 장면: 출근 전 휴대폰, 낮 사무실 PC, 밝은 실내. 그래서 밝은 화면.

## Direction contract

THESIS: 날짜 칸마다 12~23시 실제 시간축 막대를 놓아 공연 혼잡 구간(주황)과 내 수업 시각(남색 눈금)이 한 축에서 만나게 한다. 겹침은 주황 위의 진한 남색 눈금. 흔한 SaaS 달력(날짜 아래 점, 알약 배지, 카드 위젯 묶음)과 이전의 추상 레인 두 줄을 거부한다.

OWN-WORLD: Civic Data x Premium Editorial. 남색 #111D32 머리띠와 주 동작, 바탕 #F7F8FA, 흰 작업 판 하나(모서리 12px), 선 #E3E8EF. 주황 #E87329는 '공연으로 붐빔' 뜻으로만, 매우 붐빔 #9A3412(같은 색상의 명도 단계). 일요일과 공휴일 숫자 #C53340. Pretendard 하나, 숫자는 고정폭, 글자 단계 32/24/18/16/15/14/13/12. 그림자, 그라데이션, 카드 묶음, 눈썹 라벨 없음.

STORY: 수강생은 달 제목 아래 한 문장으로 이번 달 붐빌 날과 내 수업이 겹치는 날 수를 읽고, 주황 칸과 진한 눈금으로 그날을 찾고, 오른쪽 단에서 그날의 시간축 도표와 수치, 공연 목록을 본 뒤 .ics를 받는다. 기관은 같은 막대 문법의 표와 CSV를, 심사위원은 근거 수치를 본다.

FIRST VIEWPORT: 1440x900. 남색 머리띠 60px(브랜드, 세 탭, 오른쪽 예보 기간). 흰 판 = 달력 단(가변) + 오른쪽 400px 단. 달력 단: 32px 달 제목과 요약문, 오른쪽 달 분할 단추, 범례 한 줄, 7열 달력(칸 약 114px) 다섯 주가 900px 안에. 오른쪽 단 위: 내 강좌(콤보박스, 겹침 n회, 달별 겹치는 날, .ics 주 단추). 아래: 날짜 상세(24px 날짜, 요약문, 20px 시간축 도표와 내 수업 라벨, 구간 수치 두 열, 내 수업 안내, 이날 공연, 각주). 달력 아래: 다가오는 공연 혼잡 표형 목록.

FORM: 사용자가 고정한 방향. seed: none (pinned) "Civic Data Platform × Premium Editorial Interface", 팔레트 Primary #111D32, Background #F7F8FA, Surface #FFFFFF, Accent #E87329, Text #172033/#64748B, Border #E3E8EF, 글꼴 Pretendard. 시그니처: 하루 시간축 막대와 내 수업 눈금.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Memorable moment

강좌를 고르면 수업이 있는 날마다 그 시각에 눈금이 찍히고, 공연 혼잡과 겹치는 날만 진한 남색 눈금이 주황 막대 위에 선다.

## Constraints

기존 기능 유지(검색 콤보박스, ?course 주소와 저장, 달 이동, 날짜 상세, .ics, 겹치는 날 바로가기, 다가오는 목록과 모두 보기, 기관 기간 필터, 토요일 선택 제외, 묶음 표, 더 보기, CSV, 근거 차트와 표, 출처와 한계). 정적 HTML/CSS/JS, 빌드 도구와 새 의존성 없음. data/*.json 형식 변경 없음. 이모지, em-dash, 가운뎃점 나열, 상단 눈썹 라벨 금지. 주황은 단추와 링크에 쓰지 않는다.

## Unresolved

예상 관객 수는 데이터에 값이 없어 공연장 기준 규모로 대신 표시. 실제 수치는 파이프라인 변경이 필요한 별도 작업.
