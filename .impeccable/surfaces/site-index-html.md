---
version: 1
slug: "site-index-html"
primary_target: "site/index.html"
related_targets: ["site/agency.html","site/evidence.html"]
---

## Scope

올림픽공원 공연 혼잡 캘린더 정적 사이트 세 화면: site/index.html(수강생 캘린더, 주 화면), site/agency.html(기관 겹침 목록), site/evidence.html(근거와 검증). 모드: Operate(evidence는 Operate 안의 읽기 화면). 공용 site/app.css, site/app.js.

## Audience and job

주 사용자는 올림픽수영장 수강생. 내 강좌를 고르고, 공연 때문에 주차장이 붐비는 날과 내 수업이 겹치는지 한눈에 본 뒤 .ics로 휴대폰 캘린더에 넣는다. 기관 직원은 기간을 정해 겹치는 회차 목록을 보고 CSV를 내려받는다. 심사위원은 근거 화면에서 2025년 실데이터 검증 수치를 확인한다. 사용 장면: 출근 전 휴대폰, 낮 사무실 PC, 밝은 실내. 그래서 밝은 화면.

## Direction contract

THESIS: 달력의 날짜 칸 하나를 수영장 레인 두 줄(오후 12~16시, 저녁 17~22시)로 나눈 시간표 게시판. 흔한 SaaS 달력(날짜 숫자 아래 점이나 배지, 카드에 담긴 위젯 묶음)을 거부한다. 예보 데이터의 구조(날짜 x 구간)가 곧 화면의 구조다.

OWN-WORLD: 수영장 타일과 레인 로프. 남색 #0F172A 상단 띠(게시판 머리), 바탕 #F8FAFC, 타일 흰색에 줄눈 #E2E8F0 1px 격자, 수영장 파랑 #0369A1은 내 강좌와 주 동작에만. 혼잡은 레인 로프 색: 붐빔은 호박색 #D97706, 매우 붐빔은 짙은 빨강 #B91C1C(색각 검사 통과 쌍), 공연 영향이 아닐 때는 칠하지 않는다. 일요일과 공휴일 날짜 숫자는 한국 달력 관례대로 붉게. 글꼴은 Pretendard 하나, 숫자는 고정폭 숫자(tnum). 모서리는 타일 2px, 컨트롤 6px, 그림자 없음, 그라데이션 없음.

STORY: 수강생은 첫 화면에서 이번 달 어느 날 저녁이 공연으로 붐비는지 색으로 바로 읽고, 강좌를 고르면 내 수업 레인이 달력 전체에서 파랗게 짚이며 겹치는 날이 몇 번인지 알게 되고, .ics를 받아 간다. 기관은 같은 데이터를 표와 CSV로 받는다. 심사위원은 예보가 얼마나 맞았는지 숫자로 확인한다.

FIRST VIEWPORT: 데스크톱 1280: 남색 머리띠(서비스 이름 왼쪽, 세 화면 이동 탭 오른쪽). 아래 두 단. 왼쪽 340px 단: 강좌 검색 입력(주 동작, 맨 위), 선택한 강좌 요약과 .ics 버튼, 날짜 상세(기본값은 가장 가까운 공연 혼잡일). 오른쪽 단: 월 고르기와 범례, 7열 타일 달력이 화면 높이를 채우고, 그 아래 다가오는 공연 혼잡 목록(날짜별 한 줄). 목록을 오른쪽 단으로 옮긴 이유: 공연명이 길어 넓은 폭이 필요하고, 왼쪽 단만 길어지는 불균형을 없애기 위해(1차 점검). 모바일 375: 머리띠, 검색, 달력, 상세, 다가오는 목록 순으로 쌓인다.

FORM: 수영장 강습 시간표 게시판. 내 후보 목록 1순위(배정은 5번 88 서울올림픽 디자인 방식이었으나 사용자가 추천안을 선택). seed:6df9c824f101379a. 시그니처 동작: 강좌를 고르면 그 수업 시간의 레인이 모든 날짜 칸에서 파란 테두리로 켜지고, 겹치는 날의 레인은 파란 표식으로 채워진다.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Memorable moment

강좌 선택 순간 달력 위에 내 레인이 가로로 켜지는 것.

## Constraints

기존 기능 유지(검색, 월 이동, 날짜 상세, .ics, 기관 기간 필터, 토요일 선택 제외, CSV, 더 보기, 근거 표, 출처와 한계). 정적 HTML/CSS/JS, 빌드 도구 없음. data/*.json 형식 변경 없음. 이모지, em-dash, 가운뎃점 나열, 상단 소제목 라벨 금지.

## Unresolved

없음.
