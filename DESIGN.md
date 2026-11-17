---
name: 올림픽공원 공연 혼잡 캘린더
description: 공연 때문에 붐비는 오후와 저녁을 수영장 강좌 시간표 위에 미리 보여 주는 게시판
colors:
  shell-navy: "#0f172a"
  shell-ink: "#f8fafc"
  shell-muted: "#cbd5e1"
  shell-mark: "#38bdf8"
  pool-blue: "#0369a1"
  pool-blue-deep: "#075985"
  pool-wash: "#e0f2fe"
  ground: "#f8fafc"
  tile: "#ffffff"
  tile-hover: "#f1f5f9"
  grout: "#e2e8f0"
  edge: "#cbd5e1"
  lane-idle: "#e8edf3"
  ink: "#020617"
  ink-secondary: "#334155"
  ink-muted: "#475569"
  ink-faint: "#64748b"
  rope-amber: "#d97706"
  rope-amber-wash: "#fef3c7"
  rope-amber-ink: "#92400e"
  rope-red: "#b91c1c"
  rope-red-wash: "#fee2e2"
  rope-red-ink: "#991b1b"
typography:
  headline:
    fontFamily: "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.45
  data:
    fontFamily: "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 650
    lineHeight: 1.55
    fontFeature: "tnum"
rounded:
  tile: "2px"
  control: "6px"
  panel: "8px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  2xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.pool-blue}"
    textColor: "{colors.tile}"
    rounded: "{rounded.control}"
    padding: "0 16px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.pool-blue-deep}"
    textColor: "{colors.tile}"
  button-secondary:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 16px"
    height: "40px"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.pool-blue}"
    rounded: "{rounded.control}"
    padding: "0 8px"
    height: "40px"
  input:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "42px"
  chip-busy:
    backgroundColor: "{colors.rope-amber-wash}"
    textColor: "{colors.rope-amber-ink}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  chip-very-busy:
    backgroundColor: "{colors.rope-red-wash}"
    textColor: "{colors.rope-red-ink}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  panel:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "20px"
  day-tile:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tile}"
    padding: "8px"
    height: "96px"
  month-switch-selected:
    backgroundColor: "{colors.shell-navy}"
    textColor: "{colors.shell-ink}"
    rounded: "{rounded.control}"
    height: "36px"
---

# Design System: 올림픽공원 공연 혼잡 캘린더

## Overview

**Creative North Star: "수영장 강습 시간표 게시판"**

수강생이 매주 보는 수영장 시간표와 레인의 세계를 빌린 업무용 화면입니다. 화면의 짜임은 흔한 달력과 표 그대로 두고, 세계는 네 가지만 빌려줍니다. 하나의 한글 글꼴(Pretendard)과 고정폭 숫자, 남색 머리띠와 타일 줄눈 격자, 레인 로프의 호박색과 빨강, 그리고 대표 동작 하나입니다. 대표 동작은 날짜 칸을 오후와 저녁 두 레인으로 나누고, 강좌를 고르면 그 수업 시간의 레인이 한 달 내내 파란 테두리로 켜지는 것입니다. 예보 데이터의 구조(날짜와 구간)가 곧 화면의 구조입니다.

밀도는 시간표 게시판처럼 촘촘하되, 색은 일을 할 때만 씁니다. 공연 때문에 평소보다 붐빌 때만 레인을 칠하고, 평소에도 붐비는 시간은 날짜 상세에서만 말로 알려 줍니다. 사용 장면은 출근 전 휴대폰과 낮의 사무실 PC라서 밝은 화면입니다. 흔한 AI 대시보드(같은 크기 카드 묶음, 큰 숫자 타일, 그라데이션 장식)와 한눈에 들어오지 않는 화면은 피하기로 사용자와 정했습니다.

**Key Characteristics:**
- 날짜 칸 하나에 레인 두 줄(위 오후 12~16시, 아래 저녁 17~22시)
- 색은 상태와 내 강좌에만, 장식에는 쓰지 않음
- 그림자 없는 평면, 경계는 1px 줄눈
- 숫자는 모두 고정폭 숫자로 정렬

## Colors

차가운 흰 바탕 위에 남색 머리띠, 수영장 파랑 하나, 레인 로프 두 색으로 끝나는 절제된 팔레트입니다.

### Primary
- **수영장 파랑** (pool-blue): 내 강좌 레인 테두리, 주 동작 단추(휴대폰 캘린더에 추가, CSV 내려받기), 포커스 링, 링크, 검색어 일치 부분. 화면마다 한두 군데만.
- **깊은 수영장 파랑** (pool-blue-deep): 주 단추와 링크의 누름 직전(hover) 상태, 내 수업 글자.
- **물빛** (pool-wash): 선택 후보 강조, 내 수업 안내 상자 바탕, 텍스트 선택 색.

### Secondary
- **레인 로프 호박색** (rope-amber): 공연으로 붐빔. 레인, 수준 표의 견본, 막대에만.
- **레인 로프 빨강** (rope-red): 공연으로 매우 붐빔. 호박색과 색각 이상 검사(ΔE 16 이상)를 통과한 쌍입니다.
- 두 색의 옅은 바탕과 짙은 글자(rope-*-wash, rope-*-ink)는 수준 표(chip) 안에서만 씁니다.

### Neutral
- **게시판 남색** (shell-navy): 상단 머리띠, 고른 달 단추, 선택한 날짜 칸 테두리, 툴팁 바탕.
- **바탕** (ground)과 **타일** (tile): 쪽 바탕과 판, 날짜 칸.
- **줄눈** (grout): 달력 격자 1px 간격, 판 테두리, 표의 가로줄.
- **빈 레인** (lane-idle): 칠하지 않은 레인.
- **잉크 네 단계** (ink, ink-secondary, ink-muted, ink-faint): 본문, 보조 글, 설명, 자리 표시 글과 비활성 날짜.

### Named Rules
**The Earned Color Rule.** 레인과 막대는 공연 때문에 평소보다 붐빌 때만 칠합니다. 원래 붐비는 시간에 색을 쓰면 달력이 매일 칠해져 아무것도 알려 주지 못합니다.

**The One Blue Rule.** 수영장 파랑은 '나'와 '주 동작'의 색입니다. 데이터 계열이나 장식에 쓰지 않습니다.

## Typography

**Body Font:** Pretendard Variable (Apple SD Gothic Neo, Malgun Gothic 대체). 저장소의 `site/fonts/`에서 직접 제공하고 유니코드 범위별로 나눠 필요한 글자만 내려받습니다.

**Character:** 한 가족으로 제목, 본문, 표, 숫자를 모두 처리하는 업무용 글꼴입니다. 개성은 글꼴이 아니라 시간표 같은 숫자 정렬에서 나옵니다.

### Hierarchy
- **Headline** (700, 1.5rem, 1.3): 쪽 제목. 모바일 1.3125rem.
- **Title** (700, 1.0625rem~1.25rem, 1.3): 판 제목, 달 이름(1.25rem).
- **Body** (400, 0.9375rem, 1.55): 설명과 상세. 설명 문단은 68ch 안쪽.
- **Label** (600, 0.8125rem): 입력 이름, 범례, 표 머리.
- **Data** (650, 0.875rem, 고정폭 숫자): 날짜 숫자, 시각, 대수, 회차.

### Named Rules
**The Timetable Numerals Rule.** 줄을 맞춰 읽는 숫자(날짜, 시각, 표의 수)는 고정폭 숫자로, 문장 속 큰 숫자는 기본 숫자로 씁니다.

## Layout

최대 너비 1280px, 좌우 여백 24px(모바일 16px). 수강생 화면은 데스크톱에서 두 단입니다. 왼쪽 340px 단에 내 강좌와 날짜 상세, 오른쪽 단에 달력과 다가오는 공연 혼잡 목록이 있습니다. 1023px 이하에서는 한 단으로 바뀌고 순서는 내 강좌, 달력, 날짜 상세, 다가오는 목록입니다. 판 사이 간격은 16~20px, 판 안 여백 20px(모바일 16px). 달력은 7열 격자이고 칸 높이는 96px(모바일 64px)입니다. 모바일 칸에서는 공연명을 숨기고 숫자와 레인만 남깁니다. 기관 화면은 조건 판, 묶음 표, 운영 방법이 위에서 아래로 쌓이고, 근거 화면은 데스크톱 두 단에서 검증과 한계만 전체 폭을 씁니다.

## Elevation & Depth

평면입니다. 판과 칸은 그림자 없이 1px 줄눈과 바탕색 차이로 나뉩니다. 그림자는 툴팁 하나에만 있습니다(0 4px 12px, 남색 18%).

### Named Rules
**The Grout Not Shadow Rule.** 구분은 줄눈(1px 선)과 바탕 단계로 합니다. 판에 그림자를 넣지 않습니다.

## Shapes

모서리는 쓰임에 따라 세 단계입니다. 타일과 레인은 거의 각진 2px, 단추와 입력은 6px, 판은 8px. 수준 표만 알약 모양입니다. 달력은 1px 간격의 격자로 줄눈을 그리고, 바깥만 6px로 둥글립니다.

## Components

### Buttons
- **Shape:** 6px 모서리, 높이 40px.
- **Primary:** 수영장 파랑 바탕에 흰 글자, 아이콘은 선 굵기 1.75의 직접 그린 SVG.
- **Hover / Focus:** hover는 깊은 수영장 파랑, 포커스는 2px 파랑 외곽선과 2px 간격. 전환 0.15초.
- **Secondary / Quiet:** 흰 바탕에 #cbd5e1 테두리, 또는 테두리 없는 파랑 글자 단추(보조 동작).

### Chips
- **Style:** 알약 모양, 0.75rem 굵은 글자, 앞에 10x4px 레인 견본. 보통은 회색, 붐빔은 호박색, 매우 붐빔은 빨강.
- **Tag:** 4px 모서리의 작은 이름표(공연 영향, 토요일 선택, 내 수업).

### Cards / Containers
- **Corner Style:** 8px.
- **Background:** 흰색 타일, 바탕은 #f8fafc.
- **Shadow Strategy:** 없음.
- **Border:** 1px 줄눈.
- **Internal Padding:** 20px(모바일 16px). 판 안에 판을 넣지 않고, 구역은 1px 가로줄로 나눕니다.

### Inputs / Fields
- **Style:** 흰 바탕, 1px #cbd5e1 테두리, 6px 모서리, 높이 42px, 검색 아이콘은 왼쪽 안쪽.
- **Focus:** 테두리와 2px 외곽선이 수영장 파랑으로.
- **Combobox:** 결과는 입력 아래에 펼쳐지는 목록(위아래 화살표, Enter, Esc), 일치 부분은 깊은 파랑 굵은 글자. 결과가 없으면 무엇을 바꾸면 되는지 문장으로 알립니다.

### Navigation
- 남색 머리띠 오른쪽의 글자 탭. 기본 #cbd5e1, hover 흰색, 현재 화면은 흰 굵은 글자와 아래 3px 하늘색 막대. 모바일에서는 서비스 이름 아래 한 줄로 내려오고 가로로 밀립니다.

### Day Tile (signature)
- 흰 칸, 위에 날짜 숫자(일요일과 공휴일은 #b91c1c), 아래 8px 레인 두 줄(위 오후, 아래 저녁), 맨 아래 한 줄 메모(공연 짧은 이름, 공휴일 이름, 또는 '내 수업 19:00').
- 공연 혼잡 레인은 호박색 또는 빨강. 내 강좌가 있는 날의 해당 레인은 2px 파랑 외곽선(토요일 선택 수업은 점선).
- 고른 날은 안쪽 2px 남색 테두리, 예보 기간 밖의 날은 바탕색으로 비활성.

## Do's and Don'ts

### Do:
- **Do** 새 화면도 날짜와 구간을 레인 두 줄로 보여 주는 문법을 그대로 씁니다.
- **Do** 수준은 색과 글자를 함께 씁니다(수준 표의 '붐빔', 칸의 접근성 이름). 색만으로 알리지 않습니다.
- **Do** 숫자 열은 오른쪽 정렬과 고정폭 숫자로 맞춥니다.
- **Do** 차트는 한 계열이면 수영장 파랑 하나, 비교는 채운 점(이 서비스)과 빈 점(평소 패턴)처럼 모양으로 구분합니다.

### Don't:
- **Don't** 판에 그림자, 그라데이션, 유리 효과를 넣지 않습니다.
- **Don't** 같은 크기 카드에 큰 숫자를 얹은 대시보드 타일을 만들지 않습니다. 요약 수치는 문장 속 굵은 숫자로 씁니다.
- **Don't** 제목 위에 작은 머리말 라벨을 달지 않고, 메타 정보를 가운뎃점으로 잇지 않습니다.
- **Don't** 레인 로프 두 색을 상태 말고 다른 데이터 계열에 쓰지 않습니다.
- **Don't** 이모지나 글자 기호를 아이콘 대신 쓰지 않습니다.
