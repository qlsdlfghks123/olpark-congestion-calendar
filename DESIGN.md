---
name: 올림픽공원 공연 혼잡 캘린더
description: 날짜마다 12~23시 시간축 막대 위에 공연 혼잡 구간과 내 수업 시각을 함께 놓는 시민용 데이터 달력
colors:
  navy: "#111d32"
  navy-hover: "#22314d"
  navy-wash: "#edf0f5"
  ground: "#f7f8fa"
  surface: "#ffffff"
  line: "#e3e8ef"
  line-soft: "#eef1f5"
  control: "#aeb8c6"
  ink: "#172033"
  ink-2: "#3d4a5f"
  muted: "#5b6b82"
  on-navy: "#ffffff"
  on-navy-muted: "#aeb9cb"
  idle: "#e3e8ef"
  signal: "#e87329"
  signal-strong: "#9a3412"
  signal-ink: "#af4d0f"
  signal-wash: "#fef4ec"
  signal-wash-hover: "#fce9da"
  holiday: "#c53340"
  danger-wash: "#fdecee"
typography:
  display:
    fontFamily: "Pretendard Variable, Pretendard, -apple-system, BlinkMacSystemFont, Apple SD Gothic Neo, Malgun Gothic, system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.03em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  title:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  title-s:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.55
  body-s:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.38
  micro:
    fontFamily: "Pretendard Variable, Pretendard, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.6
rounded:
  mark: "2px"
  ctl: "8px"
  sheet: "12px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  section: "28px"
  gutter: "32px"
  gutter-tablet: "24px"
  gutter-phone: "16px"
components:
  button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    typography: "{typography.body}"
    rounded: "{rounded.ctl}"
    padding: "0 16px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.navy-hover}"
    textColor: "{colors.on-navy}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body-s}"
    rounded: "{rounded.ctl}"
    padding: "0 16px"
    height: "44px"
  button-secondary-hover:
    backgroundColor: "{colors.ground}"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.navy}"
    rounded: "{rounded.ctl}"
    padding: "0 10px"
    height: "36px"
  button-quiet-hover:
    backgroundColor: "{colors.navy-wash}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.ctl}"
    padding: "0 12px"
    height: "44px"
  segmented-active:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    height: "40px"
  sheet:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.sheet}"
  shell:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    height: "60px"
  day-cell:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    padding: "10px 12px 11px"
    height: "114px"
  day-cell-flag:
    backgroundColor: "{colors.signal-wash}"
  day-strip-seg:
    backgroundColor: "{colors.idle}"
    rounded: "{rounded.mark}"
    height: "8px"
  day-strip-seg-busy:
    backgroundColor: "{colors.signal}"
  day-strip-seg-very-busy:
    backgroundColor: "{colors.signal-strong}"
  tooltip:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    typography: "{typography.label}"
    rounded: "{rounded.ctl}"
    padding: "8px 10px"
---

# Design System: 올림픽공원 공연 혼잡 캘린더

## Overview

**Creative North Star: "시청 데이터 지면 (The Civic Data Broadsheet)"**

공공 데이터 플랫폼의 정확함과 잘 짜인 편집 지면의 절제를 합친 체계다. 남색 머리띠 아래 서늘한 회색 바탕이 깔리고, 그 위에 흰 작업 판 하나가 놓인다. 판 안은 카드로 쪼개지 않고 1px 선으로만 나뉜다. 모든 정보는 숫자와 시간축으로 말하며, 장식은 없다.

이 체계의 중심은 하루 시간축 막대다. 12시부터 23시까지를 실제 비율로 그린 짧은 막대가 오후(5시간)와 저녁(6시간) 두 구간으로 갈리고, 공연 혼잡은 주황으로, 내 수업 시각은 남색 눈금으로 같은 축 위에 찍힌다. 같은 막대가 달력 칸, 날짜 상세 도표, 다가오는 목록, 기관 표의 묶음 줄에 크기만 바꿔 반복된다. 화면이 달라도 읽는 법은 하나다.

색은 뜻을 가진다. 남색은 틀과 주 동작, 선택, 내 수업이고, 주황은 오직 '공연으로 붐빔'이다. 이 둘이 한 칸에서 만나는 순간이 이 제품이 전하려는 단 하나의 사실이다.

**Key Characteristics:**
- 남색 머리띠, 회색 바탕, 흰 판 하나, 1px 선으로 나뉜 내부
- 주황은 혼잡 데이터 전용, 동작과 링크는 남색
- 숫자는 모두 고정폭(tabular-nums), 글꼴은 Pretendard 하나
- 하루 시간축 막대와 내 수업 눈금이 모든 화면에 같은 문법으로 반복
- 그림자는 떠 있는 층(콤보박스 목록, 툴팁, 건너뛰기 링크)에만

## Colors

차가운 남색과 회색 위에 데이터 신호인 주황 하나만 뜨거운, 절제된 공공 지면의 팔레트다.

### Primary
- **밤 남색 (Civic Night Navy)** (`navy`): 머리띠 바탕, 주 단추, 선택된 달 단추, 선택된 날의 안쪽 테두리와 숫자 배지, 오늘의 원 테두리, 내 수업 눈금, 링크, 포커스 링, 툴팁 바탕. 이 화면에서 '틀'과 '나'를 뜻하는 색이다.
- **밤 남색 눌림 (Navy Hover)** (`navy-hover`): 주 단추와 링크의 hover.
- **남색 물빛 (Navy Wash)** (`navy-wash`): 조용한 단추 hover, 콤보박스 선택 항목, 다가오는 목록의 현재 날짜 줄, 내 수업 안내 상자 바탕.

### Secondary
- **공연 주황 (Concert Signal Orange)** (`signal`): '공연으로 붐빔' 구간 막대, 근거 화면 막대 차트, 수준 견본.
- **매우 붐빔 적갈 (Deep Rust)** (`signal-strong`): '매우 붐빔' 구간. 같은 색상의 명도 단계로, 색상을 바꾸지 않는다.
- **주황 글자 (Signal Ink)** (`signal-ink`): 혼잡 수준을 글자로 쓸 때. 흰 판과 주황 물빛 위에서 4.5:1을 넘기기 위해 `signal`보다 어둡게 잡았다.
- **주황 물빛 (Signal Wash)** (`signal-wash`, hover `signal-wash-hover`): 혼잡한 날 달력 칸 전체 바탕.

### Tertiary
- **휴일 적색 (Holiday Red)** (`holiday`): 일요일과 공휴일 날짜 숫자, 요일 머리의 '일', 공휴일 이름. 다른 용도로 쓰지 않는다.

### Neutral
- **바탕 회색 (Ground)** (`ground`): 페이지 바탕, 달력 앞뒤 빈 칸, 지난 날, 표 머리, 보조 단추 hover.
- **흰 판 (Surface)** (`surface`): 작업 판 하나와 입력, 보조 단추, 날짜 칸.
- **선 (Line)** (`line`): 판 테두리, 단과 구획 사이, 달력 가로선, 표 머리 밑줄.
- **옅은 선 (Line Soft)** (`line-soft`): 달력 세로선, 목록과 표의 줄 사이.
- **조작 테두리 (Control)** (`control`): 입력, 보조 단추, 달 분할 단추의 테두리.
- **잉크 (Ink)** (`ink`), **둘째 잉크 (Ink 2)** (`ink-2`), **흐린 글자 (Muted)** (`muted`): 본문, 보조 문장, 설명과 각주. 흐린 글자는 바탕 회색 위 4.5:1을 위해 방향 계약의 #64748b보다 어둡게 확정했다.
- **빈 구간 (Idle)** (`idle`): 붐비지 않는 시간 구간 막대.
- **남색 위 글자** (`on-navy`, `on-navy-muted`): 머리띠와 툴팁 안의 글자, 비활성 탭.
- **오류 물빛** (`danger-wash`): 오류 상자 바탕.

### Named Rules
**The 주황은 데이터 Rule.** 주황 계열(`signal`, `signal-strong`, `signal-ink`, `signal-wash`)은 '공연으로 붐빔'이라는 뜻에만 쓴다. 단추, 링크, 포커스, 선택, 강조 장식에는 절대 쓰지 않는다. 주황이 보이면 그곳은 붐빈다.

**The 남색은 나 Rule.** 내 수업과 내 선택(선택한 날, 선택한 달, 내 수업 라벨과 눈금)은 남색으로만 그린다. 그래서 '주황 위의 남색 눈금'이 곧 '겹침'으로 읽힌다.

**The 휴일 숫자 Rule.** 휴일 적색은 날짜 숫자와 공휴일 이름에만 쓴다. 칸 바탕이나 막대에 번지지 않는다.

## Typography

**Display Font:** Pretendard Variable (Pretendard, Apple SD Gothic Neo, Malgun Gothic, system-ui 대체)
**Body Font:** 같은 Pretendard Variable

**Character:** 한 글꼴의 무게와 크기만으로 위계를 만든다. 큰 제목은 자간을 당긴 굵은 숫자로 지면 같은 무게를 갖고, 나머지는 단정한 공공 문서체로 물러선다.

### Hierarchy
- **Display** (700, 2rem, 1.15, -0.03em): 페이지 제목과 달 제목('2026년 11월'). 휴대폰에서 1.5rem.
- **Headline** (700, 1.5rem, 1.3, -0.02em): 날짜 상세의 날짜 제목.
- **Title** (700, 1.125rem, -0.01em): 구획 제목(다가오는 공연 혼잡, 표 제목, 근거 절 제목).
- **Title S** (650~700, 1rem): 오른쪽 단 머리, 머리띠 브랜드, 날짜 칸 숫자.
- **Body** (400, 0.9375rem, 1.55): 본문, 요약문, 주 단추 글자. 설명 문단은 68~72ch를 넘지 않는다.
- **Body S** (400~650, 0.875rem): 표, 목록, 보조 단추, 수치 줄.
- **Label** (600, 0.8125rem): 필드 이름, 요일, 범례, 칸 안 공연명과 내 수업 시각.
- **Micro** (500~600, 0.75rem): 축 눈금 시각, 공휴일 이름, 각주, 작은 이름표.

### Named Rules
**The 고정폭 숫자 Rule.** 날짜, 시각, 횟수, 비율처럼 비교되는 숫자는 모두 `font-variant-numeric: tabular-nums`로 쓴다. 열이 흔들리면 데이터 지면이 아니다.

**The 무게로 위계 Rule.** 위계는 크기 8단계(32/24/18/16/15/14/13/12)와 무게(400/500/600/650/700)로만 만든다. 대문자 변환, 넓은 자간, 색 강조로 위계를 만들지 않는다.

## Layout

페이지는 남색 머리띠(높이 60px) 아래 바탕 회색 위에 흰 판 하나를 놓고, 좌우 여백(`gutter`)을 데스크톱 32px, 태블릿 24px, 휴대폰 16px로 줄인다. 판 안 구획은 24~28px 안쪽 여백과 1px 선으로 나누며, 구획 사이 큰 간격은 40px까지만 쓴다.

수강생 화면은 판을 달력 단(가변)과 오른쪽 단 두 칸으로 나눈다. 1280px 이상에서 오른쪽 단 400px, 1024~1279px에서 360px로 줄고 날짜 칸 안쪽 여백이 8px로 줄며 공연명은 한 줄, 내 수업은 짧은 눈금 견본으로 바뀐다. 1023px 이하에서는 한 단으로 풀어 강좌 찾기, 달력, 내 강좌 요약과 .ics, 날짜 상세, 다가오는 목록 순으로 세운다. 640px 이하 휴대폰에서는 날짜 칸을 66px 높이로 줄이고 숫자와 시간축 막대만 남기며, 모든 누를 곳을 44px 이상으로 키운다.

달력은 7열 격자로, 칸 높이 114px에 다섯 주가 1440x900 첫 화면 안에 들어간다. 다가오는 목록과 기관 표는 같은 고정 열 폭 격자를 쓰고, 좁아지면 열을 줄 단위로 접는다. 한국어 줄바꿈은 `word-break: keep-all`.

## Elevation & Depth

평면 체계다. 깊이는 바탕 회색과 흰 판의 명도 차, 그리고 1px 선으로만 만든다. 그림자는 문서 흐름 위에 실제로 떠 있는 층 셋(콤보박스 결과 목록, 근거 차트 툴팁, 건너뛰기 링크)에만 쓰는 단 하나의 값이다.

### Shadow Vocabulary
- **떠 있는 층 (Pop)** (`box-shadow: 0 12px 28px -12px rgba(17, 29, 50, .28), 0 1px 3px rgba(17, 29, 50, .08)`): 콤보박스 결과 목록, 툴팁, 건너뛰기 링크. 판, 칸, 단추, 상자에는 쓰지 않는다.

### Named Rules
**The 한 장의 판 Rule.** 흰 판은 화면마다 하나다. 판 안을 카드로 다시 쪼개거나 그림자로 띄우지 않고, 선과 여백으로만 나눈다.

## Shapes

모서리는 세 단계뿐이다. 데이터 표지(막대 구간, 견본)는 2px로 거의 각지게, 조작부(단추, 입력, 달 분할, 알림 상자, 툴팁)는 8px, 작업 판은 12px. 막대가 커지는 날짜 상세 도표(20px 높이)에서만 구간 모서리가 4px로 비례해 커진다. 수준 견본은 알약이 아니라 12x6px 작은 사각 견본에 글자를 붙인다. 원은 오늘 표시와 근거 화면의 점 그림 표지에만 쓴다.

## Components

### Buttons
공공 서식처럼 단정하고 분명하다.
- **Shape:** 8px 모서리, 최소 높이 44px.
- **Primary:** 남색 바탕, 흰 글자, 0.9375rem 650. 화면마다 주 동작 하나(.ics 받기, CSV 받기, 조회).
- **Secondary:** 흰 바탕, 조작 테두리, 잉크 글자, 0.875rem 650. hover 시 바탕 회색.
- **Quiet:** 테두리 없는 남색 글자, 높이 36px(휴대폰 44px). hover 시 남색 물빛.
- **Hover / Focus:** 배경과 테두리 색만 0.15초 바뀐다. 포커스는 남색 2px 외곽선, 남색 바탕 위에서는 흰 외곽선.

### Segmented Month Switcher
- 조작 테두리로 묶인 한 줄 단추 묶음, 안쪽 구분선은 `line`. 눌린 달은 남색 바탕 흰 글자. 휴대폰에서 폭 100% 균등 분할.

### Level Chip and Tag
- **수준 글자:** 알약 없이 12x6px 견본 + 0.8125rem 650 글자. 붐빔은 주황 견본, 매우 붐빔은 적갈 견본, 글자는 `signal-ink`.
- **이름표:** 1px 선 테두리, 4px 모서리, 0.75rem 600 글자의 작은 흰 표지.

### Cards / Containers
- **Corner Style:** 판 12px.
- **Background:** 흰 판 하나, 바깥은 바탕 회색.
- **Shadow Strategy:** 없음(Elevation 참조).
- **Border:** 1px `line`.
- **Internal Padding:** 구획마다 24~28px, 휴대폰 16~20px.

### Inputs / Fields
- **Style:** 흰 바탕, 1px 조작 테두리, 8px 모서리, 높이 44px, 필드 이름은 0.8125rem 600 `ink-2`로 입력 위에.
- **Hover:** 테두리가 흐린 글자 색으로.
- **Focus:** 남색 2px 외곽선(간격 0)과 남색 테두리.
- **Combobox:** 왼쪽 돋보기, 오른쪽 지우기 단추, 결과 목록은 떠 있는 층 그림자와 4px 안쪽 여백, 일치한 글자는 밑줄 친 굵은 남색.
- **Error:** 오류 물빛 상자에 짙은 적색 글자.

### Navigation
- 남색 머리띠 60px 안에 브랜드, 세 탭, 오른쪽 예보 기간. 탭은 `on-navy-muted` 글자, 현재 탭은 흰 글자 650과 바닥 2px 흰 밑줄. 휴대폰에서는 브랜드 아래 44px 높이의 가로 스크롤 탭 줄.

### 하루 시간축 막대 (Signature)
이 체계의 서명이다. 12~23시 실제 시간축 위에 오후(5시간, 폭 45.45%)와 저녁(6시간) 두 구간을 2px 간격으로 놓는다.
- **구간:** 빈 구간 `idle`, 붐빔 `signal`, 매우 붐빔 `signal-strong`. 달력 칸에서 높이 8px(휴대폰 7px), 범례 52px 폭, 기관 묶음 줄 72px 폭, 날짜 상세 도표 20px 높이에 축 시각 라벨.
- **내 수업 눈금:** 수업 시각 위치에 남색 세로 눈금. 수업만 있는 날은 옅게(불투명도 0.42, 폭 3px), 혼잡 구간과 겹치는 날은 진하게(불투명도 1, 폭 5px, 막대 위아래로 5px 넘침)와 흰 1.5px 테두리. 토요일 선택 수업은 속이 빈 눈금.
- **동작:** 사용자가 강좌를 고르는 순간에만 눈금이 날짜 순서로 찍혀 들어온다(날짜당 16ms 지연, 0.5초, `cubic-bezier(.16, 1, .3, 1)`, 세로 0.2배에서 펼침). 줄임 동작 설정에서는 꺼진다.

### Calendar Day Cell
- 흰 칸, 위에 날짜 숫자(1rem 650 고정폭), 그 아래 공연명 한두 줄, 바닥에 내 수업 시각과 시간축 막대. 혼잡한 날은 칸 전체 `signal-wash`.
- **선택된 날:** 칸 안쪽 2px 남색 테두리 + 숫자를 남색 채운 배지(6px 모서리)로. 포커스 링과 구별되기 위해 둘 다 필요하다.
- **오늘:** 숫자를 남색 1.5px 테두리의 원으로.
- **지난 날, 앞뒤 빈 칸:** 바탕 회색, 흐린 숫자.

### Data Table (기관)
- 0.875rem 표, 머리는 바탕 회색 위 0.8125rem 650으로 상단에 고정, 줄 사이 옅은 선, 숫자 열 오른쪽 정렬 고정폭. 묶음 줄은 흰 바탕에 굵은 시간대 제목과 시간축 막대(72px), 블록 정보를 한 줄로.

### Evidence Charts (근거)
- 가로 막대는 주황 16px, 오른쪽 끝만 3px 둥글게, hover 시 적갈. 비교 점 그림은 기준(속 빈 흐린 원)과 우리 예보(남색 점). 툴팁은 남색 바탕 흰 글자에 떠 있는 층 그림자.

## Do's and Don'ts

### Do:
- **Do** 공연 혼잡을 표시할 때는 언제나 12~23시 시간축 막대의 오후/저녁 두 구간으로 그린다. 새 화면도 같은 막대를 크기만 바꿔 쓴다.
- **Do** 내 수업과 겹치는 날은 주황 구간 위 진한 남색 눈금(흰 테두리)으로, 겹치지 않는 수업일은 옅은 눈금으로 구분한다.
- **Do** 판 안 구획은 1px `line`과 `line-soft`로만 나누고 흰 판은 한 장으로 둔다.
- **Do** 비교되는 숫자는 모두 고정폭 숫자로 쓴다.
- **Do** 누를 곳은 휴대폰에서 44px 이상, 포커스는 남색 2px 외곽선으로 보이게 한다.
- **Do** 수준은 작은 사각 견본과 글자로 쓴다.

### Don't:
- **Don't** 주황 계열을 단추, 링크, 선택, 포커스, 장식 강조에 쓴다.
- **Don't** 날짜 아래 점, 알약 배지, 카드 위젯 묶음 같은 흔한 SaaS 달력 문법으로 혼잡을 표시한다.
- **Don't** 판이나 칸, 단추에 그림자를 준다. 그림자는 떠 있는 층에만.
- **Don't** 그라데이션을 쓴다.
- **Don't** 제목 위 눈썹 라벨이나 대문자 소제목을 단다.
- **Don't** 두 번째 글꼴을 들인다.
- **Don't** 휴일 적색을 날짜 숫자와 공휴일 이름 밖에서 쓴다.
