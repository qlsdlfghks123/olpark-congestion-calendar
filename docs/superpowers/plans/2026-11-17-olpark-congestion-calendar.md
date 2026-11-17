# 올림픽공원 공연 혼잡 캘린더 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 2025년 올림픽공원 주차 데이터로 공연 혼잡을 예보하고, 올림픽수영장 강좌와 겹치는 날짜를 시민용 캘린더와 기관용 목록으로 보여주는 정적 웹 시제품과 기획서용 실측 수치를 만든다.

**Architecture:** Python 파이프라인(`olpark/`)이 데이터 정제, 기준선, 공연 효과, 예보, 강좌 겹침을 계산해 `site/data/`에 JSON·ICS·CSV를 미리 생성한다. 화면은 프레임워크 없는 정적 HTML/JS(`site/`)이고 GitHub Pages로 배포하며, 일정 CSV가 바뀌면 GitHub Actions가 파이프라인을 다시 돌린다.

**Tech Stack:** Python 3.11+, pandas, holidays(KR), pytest, 바닐라 HTML/CSS/JS, GitHub Pages, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-11-17-olpark-congestion-calendar-design.md`

## Global Constraints

- 학습·통계에 쓰는 정상 기간은 2025년 1~7월과 10월뿐이다. 8~9월은 제외, 2025-11-08 00:00 이후는 사용 금지.
- `방문객` 컬럼은 쓰지 않는다(대부분 주차대수×3).
- 혼잡 수준: 정상 기간 전체 시간대 주차대수 분포의 90백분위 이상 = `매우 붐빔`, 75~90백분위 = `붐빔`, 그 외 = `보통`.
- '공연 혼잡' 판정: 수준이 `붐빔` 이상 **그리고** 공연 증가분 ≥ max(200대, 기준선의 25%). (설계 문서의 "기준 이상"을 이 값으로 고정한 것은 계획 작성자의 판단이며 기획서에 기준으로 명시한다.)
- 공연 규모 구간: 공연관람객수 < 5,000 = `S`, 5,000 이상 15,000 미만 = `M`, 15,000 이상 = `L`. 0이거나 비어 있으면 `S`.
- 검증: 학습 1~7월, 시험 10월.
- 개인정보를 받거나 저장하는 코드는 만들지 않는다.
- 화면과 기획서의 모든 수치는 `site/data/metrics.json`과 `site/data/evidence_2025.json`에서만 가져온다.
- 모든 화면에 데이터 출처(한국체육산업개발 연계 데이터 API_CPM_009, 올림픽수영장 강좌정보, 올림픽공원 홈페이지 일정안내)와 한계를 표시한다.
- 문구 규칙: 이모지 금지, em-dash 금지, "AI 기반 혁신" 같은 근거 없는 수식어 금지.

## Review Focus

1. 기준선 표에 없는 월(8·9·11·12월)의 미래 날짜 예보: 달력상 가장 가까운 정상 월의 값을 쓰고(12월→1월, 11월→10월, 8월→7월, 9월→10월) 결과에 `baseline_month_fallback`을 남긴다. Task 3 테스트로 고정.
2. 강좌 `요일`의 괄호 표기 `(토)`: 선택 수업으로 세션을 만들되 `optional=True`로 표시하고 화면에 "토요일(선택)"로 보여준다. Task 2 테스트로 고정.
3. 강좌 종료일 `9999-12-31`: 무기한이 아니라 예보 기간 끝에서 자른다. Task 2 테스트로 고정.
4. 같은 날 두 공연(다른 공연장)이 겹치는 경우: 증가분을 시간대별로 더한다. Task 4 테스트로 고정.
5. 일정 CSV의 시작 시각이 비어 있는 공연: 19:00으로 가정하고 `start_time_assumed=True`를 남겨 화면에 "시작 시각 미정(19시 가정)"으로 표시한다. Task 6 테스트로 고정.

---

## File Structure

```
olpark/
  olpark/__init__.py
  olpark/load.py        # 원천 데이터 읽기·정제 (연계 데이터, 강좌정보)
  olpark/calendar_kr.py # 날짜 유형(평일/토/일·휴일) 판정
  olpark/baseline.py    # 기준선, 혼잡 수준 경계값
  olpark/uplift.py      # 공연 이벤트 추출, 규모 구간, 증가분 프로필
  olpark/forecast.py    # 일정 → 시간대별 예보, 공연 혼잡 판정
  olpark/backtest.py    # 10월 검증 지표
  olpark/overlap.py     # 강좌 세션 × 예보/실측 겹침
  olpark/export.py      # JSON, ICS, CSV 생성
  olpark/build.py       # 전체 파이프라인 진입점 (python -m olpark.build)
  data/raw/linked_2025.csv          # 연계 데이터 정리본 (커밋)
  data/raw/courses_pool.csv         # 강좌정보 원본, cp949 (커밋)
  data/schedule.csv                 # 앞으로의 공연 일정 (기관이 교체하는 파일)
  site/index.html  site/agency.html  site/evidence.html  site/app.css  site/app.js
  site/data/       # build 산출물 (Actions가 생성, 커밋하지 않음)
  tests/           # 모듈별 test_*.py, tests/fixtures/
  .github/workflows/build.yml
  requirements.txt  README.md
```

---

### Task 1: 프로젝트 골격과 연계 데이터 정제

**Files:**
- Create: `requirements.txt`(pandas, holidays, pytest), `olpark/__init__.py`, `olpark/load.py`, `olpark/calendar_kr.py`, `tests/test_load.py`, `tests/test_calendar_kr.py`, `data/raw/linked_2025.csv`(작업 공간의 `/home/claude/work/linked_2025.csv` 복사)

**Interfaces:**
- Produces: `load_linked(path: str) -> pd.DataFrame` 컬럼 `dt`(datetime64), `parking`(int), `temp`, `wind`, `rain`, `humidity`(float, 결측 NaN), `holiday`(str|None), `show`(str|None), `audience`(int, 결측 0), `clean`(bool)
- Produces: `day_type(d: date, holiday_name: str|None = None) -> str` 반환값 `"weekday" | "sat" | "sun_hol"`. `holiday_name`이 없으면 `holidays.KR`로 판정.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_clean_flag_excludes_aug_sep_and_after_nov8(tmp_path):
    df = load_linked(FIXTURE)  # tests/fixtures/linked_small.csv: 2025-07-31 10시, 2025-08-01 10시, 2025-10-01 10시, 2025-11-07 23시, 2025-11-08 00시
    assert df.set_index("dt")["clean"].to_dict() == {
        Timestamp("2025-07-31 10:00"): True, Timestamp("2025-08-01 10:00"): False,
        Timestamp("2025-10-01 10:00"): True, Timestamp("2025-11-07 23:00"): False,
        Timestamp("2025-11-08 00:00"): False}

def test_no_visitor_column():
    assert "방문객" not in load_linked(FIXTURE).columns and "visitors" not in load_linked(FIXTURE).columns

def test_day_type():
    assert day_type(date(2025,7,30)) == "weekday"
    assert day_type(date(2025,8,2)) == "sat"
    assert day_type(date(2025,8,3)) == "sun_hol"
    assert day_type(date(2025,8,15)) == "sun_hol"          # 광복절
    assert day_type(date(2025,6,4), "임시공휴일") == "sun_hol"
```

(11월은 정상 기간이 아니므로 11월 행은 모두 `clean=False`다. 정상 기간은 Global Constraints대로 1~7월, 10월.)

- [ ] **Step 2: 실패 확인** — Run: `pytest tests/test_load.py tests/test_calendar_kr.py -v` / Expected: FAIL (모듈 없음)
- [ ] **Step 3: `load_linked`, `day_type` 구현** — 원본 CSV 컬럼명(`주차대수` 등)을 영문 컬럼으로 바꾼다.
- [ ] **Step 4: 통과 확인** — 같은 명령, Expected: PASS
- [ ] **Step 5: 실데이터 점검** — Run: `python -c "from olpark.load import load_linked; d=load_linked('data/raw/linked_2025.csv'); print(len(d), d.clean.sum())"` / Expected: `7803`과 5,000~5,800 사이 값
- [ ] **Step 6: Commit** — `git add -A && git commit -m "feat: load and clean 2025 linked parking data"`

---

### Task 2: 강좌정보 읽기와 세션 전개

**Files:**
- Create: `olpark/load.py`에 함수 추가, `tests/test_courses.py`, `tests/fixtures/courses_small.csv`(cp949), `data/raw/courses_pool.csv`(사용자 PC `contest` 폴더의 `한국체육산업개발주식회사_올림픽수영장 강좌정보_20260511.csv`를 스테이징해 복사)

**Interfaces:**
- Produces: `load_courses(path: str) -> pd.DataFrame` 컬럼 `course_no`(str, 강좌번호), `sub_no`(str), `month`(Period[M], 시작월), `name`(str, 공백 정리), `start`(time), `end`(time), `capacity`(int), `days`(list[int], 월=0), `optional_days`(list[int]), `group`(str, 강습반), `fee`(int), `period_start`(date), `period_end`(date|None, 9999-12-31은 None)
- Produces: `expand_sessions(courses: pd.DataFrame, start: date, end: date) -> pd.DataFrame` 컬럼 `course_no`, `name`, `date`, `start_dt`, `end_dt`, `capacity`, `optional`(bool). 각 강좌 행은 `period_start`~(`period_end` 또는 `end`) 범위와 해당 `month` 안에서만 세션을 만든다. 단, `period_end`가 None인 행은 `month` 제한 없이 `end`까지 이어진다.
- Produces: `latest_timetable(courses: pd.DataFrame) -> pd.DataFrame` — `course_no`별 가장 최근 `month` 행 하나씩.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_parse_days_with_optional_saturday():
    c = load_courses(FIXTURE)
    row = c[c.course_no == "1027444"].iloc[0]          # 요일 "월,수,금,(토)"
    assert row.days == [0, 2, 4] and row.optional_days == [5]

def test_open_ended_period_is_clipped():
    s = expand_sessions(load_courses(FIXTURE), date(2026,12,1), date(2026,12,31))
    assert s.date.max() <= date(2026,12,31)            # 9999-12-31 행이 12월 말에서 잘림

def test_optional_saturday_sessions_flagged():
    s = expand_sessions(load_courses(FIXTURE), date(2025,9,1), date(2025,9,30))
    sat = s[(s.course_no == "1027444") & (pd.to_datetime(s.date).dt.dayofweek == 5)]
    assert len(sat) > 0 and sat.optional.all()

def test_cp949_name_is_trimmed():
    assert load_courses(FIXTURE).name.str.endswith(" ").sum() == 0
```

- [ ] **Step 2: 실패 확인** — `pytest tests/test_courses.py -v` / FAIL
- [ ] **Step 3: 구현** — 요일 문자열은 `,`로 나누고 괄호가 있으면 `optional_days`로 보낸다. `시작일자` 컬럼은 `"YYYY-MM-DD~YYYY-MM-DD"` 범위 문자열이다.
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: 실데이터 점검** — `load_courses('data/raw/courses_pool.csv')` 행 수 7133, 2025년 `month` 행 2019
- [ ] **Step 6: Commit** — `feat: load swimming pool courses and expand sessions`

---

### Task 3: 기준선과 혼잡 수준 경계

**Files:**
- Create: `olpark/baseline.py`, `tests/test_baseline.py`

**Interfaces:**
- Consumes: `load_linked`, `day_type`
- Produces: `fit_baseline(df: pd.DataFrame, months: list[int]) -> pd.DataFrame` — `clean`이고 `show`가 없는 행만으로 (`month`, `day_type`, `hour`)별 `parking` 중앙값. 컬럼 `month`, `day_type`, `hour`, `base`.
- Produces: `baseline_at(table: pd.DataFrame, ts: pd.Timestamp, holiday_name: str|None=None) -> tuple[float, int|None]` — 값과 대체에 쓴 월(대체 없으면 None). 대체 순서: 같은 월 → Review Focus 1의 대응표(1월↔12월, 10월↔11월, 7월↔8월, 10월↔9월; 표에 없는 월은 달력상 가장 가까운 학습 월) → 같은 (`day_type`, `hour`)의 전체 학습 월 중앙값.
- Produces: `level_thresholds(df: pd.DataFrame, months: list[int]) -> dict` — `{"p75": float, "p90": float}` (학습 월의 clean 행 전체)
- Produces: `level_of(value: float, th: dict) -> str` — `"매우 붐빔" | "붐빔" | "보통"`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_baseline_ignores_show_hours(): ...   # 픽스처: 같은 (월,평일,19시)에 공연 없는 값 100,120,140과 공연 있는 값 900 → base == 120
def test_fallback_for_december():
    v, used = baseline_at(TABLE_JAN_ONLY, Timestamp("2026-12-09 19:00"))
    assert used == 1 and v == TABLE_JAN_ONLY.query("month==1 and day_type=='weekday' and hour==19").base.item()
def test_levels():
    th = {"p75": 1000, "p90": 2000}
    assert [level_of(x, th) for x in (999, 1000, 2000)] == ["보통", "붐빔", "매우 붐빔"]
```

- [ ] **Step 2: 실패 확인** — FAIL
- [ ] **Step 3: 구현**
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: Commit** — `feat: baseline table and congestion level thresholds`

---

### Task 4: 공연 이벤트와 증가분 프로필

**Files:**
- Create: `olpark/uplift.py`, `tests/test_uplift.py`

**Interfaces:**
- Consumes: `fit_baseline`, `baseline_at`
- Produces: `extract_events(df: pd.DataFrame) -> pd.DataFrame` — (`date`, `show`)마다 한 행. `start_hour` = 그 날 그 공연명이 붙은 가장 이른 시각, `audience` = 그 날 최대 `audience`, `size` = Global Constraints의 구간.
- Produces: `fit_uplift(df, table, months: list[int]) -> pd.DataFrame` — 학습 월의 공연일에 대해 `offset` = 시각 − `start_hour`, 범위 −4…+3. 공연이 하나뿐인 날만 써서 (`size`, `offset`)별 (실측 − 기준선) 중앙값. 컬럼 `size`, `offset`, `uplift`. 표본이 3개 미만인 칸은 바로 작은 규모 구간 값으로 대체(L→M→S), S도 없으면 0.
- Produces: `uplift_for(profile, size: str, offset: int) -> float` — 범위 밖 offset은 0.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_event_start_and_size(): ...          # 픽스처: 공연명 19~23시, audience 최대 12000 → start_hour 19, size "M"
def test_zero_audience_is_small(): ...        # audience 0 → "S"
def test_uplift_offset_window():
    assert uplift_for(PROFILE, "L", 4) == 0 and uplift_for(PROFILE, "L", -5) == 0
def test_sparse_cell_falls_back_to_smaller_size(): ...
```

- [ ] **Step 2: 실패 확인** — FAIL
- [ ] **Step 3: 구현**
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: 실데이터 점검** — 1~7월로 적합한 `L` 프로필에서 offset −2…0의 uplift가 양수인지 출력해 확인(음수면 작업을 멈추고 보고)
- [ ] **Step 6: Commit** — `feat: show events and uplift profile by size`

---

### Task 5: 예보, 공연 혼잡 판정, 10월 검증

**Files:**
- Create: `olpark/forecast.py`, `olpark/backtest.py`, `tests/test_forecast.py`, `tests/test_backtest.py`

**Interfaces:**
- Consumes: Task 3, Task 4의 함수들
- Produces: `forecast(schedule: pd.DataFrame, start: date, end: date, table, profile, th) -> pd.DataFrame` — `schedule` 컬럼 `date`, `start_hour`, `size`, `title`, `venue`. 결과는 기간의 모든 시각 한 행씩: `dt`, `base`, `uplift`(같은 시각 여러 공연은 합산), `pred`=`base`+`uplift`, `level`, `show_congestion`(bool, Global Constraints 규칙), `titles`(list[str]), `assumed_start`(bool, 기여한 공연 중 시작 시각을 가정한 것이 있으면 True. `schedule`에 `start_time_assumed` 컬럼이 없으면 False), `baseline_month_fallback`(int|None).
- Produces: `weather_effect(df, months) -> dict` — 정상 기간 공연 없는 시각에서 (실측/기준선) 비율의 중앙값을 강수 있음/없음으로 나눠 `{"rain_ratio", "dry_ratio", "n_rain", "n_dry"}`. 예보에는 쓰지 않고 `metrics.json`에만 넣는다(설계 문서: 날씨는 영향 크기만 보고).
- Produces: `is_show_congestion(level: str, uplift: float, base: float) -> bool`
- Produces: `run_backtest(df, train_months=[1..7], test_month=10) -> dict` — 키 `mae_all`, `mae_show_days`, `hit_rate`(실측 공연 혼잡 시각 중 예보도 공연 혼잡인 비율), `false_alarm_rate`(예보 공연 혼잡 시각 중 실측은 아닌 비율), `n_actual`, `n_pred`. 실측 판정은 실측값과 같은 기준선으로 계산한 실측 증가분을 쓴다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_two_shows_same_hour_add_up(): ...        # 두 공연 같은 날 19시 시작 → uplift == 두 프로필 값의 합
def test_show_congestion_rule():
    assert is_show_congestion("붐빔", 300, 1000) is True
    assert is_show_congestion("붐빔", 200, 1000) is False   # max(200, 250)=250 미만
    assert is_show_congestion("보통", 900, 100) is False
def test_backtest_keys():
    assert set(run_backtest(FIXTURE_DF)) >= {"mae_all","mae_show_days","hit_rate","false_alarm_rate","n_actual","n_pred"}
```

- [ ] **Step 2: 실패 확인** — FAIL
- [ ] **Step 3: 구현**
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: 실데이터 검증 실행** — `python -m olpark.backtest data/raw/linked_2025.csv`로 지표 출력. 단순 기준선(공연 무시)의 `mae_show_days`도 함께 출력해 비교. 공연 반영 예보가 기준선보다 나쁘면 멈추고 보고한다.
- [ ] **Step 6: Commit** — `feat: forecast and October backtest`

---

### Task 6: 일정 입력, 강좌 겹침, 2025년 실측 근거

**Files:**
- Create: `olpark/overlap.py`, `tests/test_overlap.py`, `data/schedule.csv`
- Modify: `olpark/load.py` (`load_schedule` 추가)

**Interfaces:**
- Produces: `load_schedule(path: str) -> pd.DataFrame` — 입력 컬럼 `date,start_time,venue,title,expected_audience,source`. `start_time` 비면 19:00과 `start_time_assumed=True`. 여러 날 공연은 날짜별 한 행. `size`는 `expected_audience`로 판정, 비면 공연장 기본값(KSPO DOME=`L`, 티켓링크 라이브 아레나·핸드볼경기장=`M`, 그 외=`S`).
- Produces: `overlaps(sessions: pd.DataFrame, hourly: pd.DataFrame) -> pd.DataFrame` — 세션 시간대와 한 시각이라도 겹치는 `show_congestion` 시각이 있으면 한 행. 컬럼 `course_no`, `name`, `date`, `start_dt`, `end_dt`, `capacity`, `optional`, `max_level`, `max_uplift`, `titles`.
- Produces: `evidence_2025(df, courses) -> dict` — 정상 기간 실측 기준. 키 `n_sessions_overlapped`, `capacity_sum`, `n_show_congestion_hours`, `by_month`(월별 세션 수), `top_events`(겹친 세션이 많은 공연 상위 5개: `title`, `date`, `sessions`).

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_missing_start_time_assumed_19():
    s = load_schedule(FIXTURE_SCHEDULE)
    row = s[s.title == "시각미정공연"].iloc[0]
    assert row.start_hour == 19 and row.start_time_assumed
def test_multi_day_show_expands(): ...            # 2026-12-24~26 → 3행
def test_session_overlap_boundary():               # 세션 19:00~19:50, 혼잡 시각 19시 → 겹침 / 혼잡 시각 20시만 → 안 겹침
    ...
```

- [ ] **Step 2: 실패 확인** — FAIL
- [ ] **Step 3: 구현**
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: `data/schedule.csv` 작성** — 올림픽공원 홈페이지 일정안내(`https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301010100`)와 각 공연 상세 페이지에서 2026-12-01~2027-02-28 공연의 날짜, 시작 시각, 공연장, 제목을 옮긴다. `source` 열에 상세 페이지 URL. 시작 시각을 못 찾으면 비워 둔다.
- [ ] **Step 6: Commit** — `feat: schedule input, course overlap, 2025 evidence`

---

### Task 7: 산출물 생성 (JSON, ICS, CSV)과 빌드 진입점

**Files:**
- Create: `olpark/export.py`, `olpark/build.py`, `tests/test_export.py`

**Interfaces:**
- Consumes: Task 1~6 전부
- Produces: `python -m olpark.build --out site/data` 가 아래 파일을 만든다.
  - `forecast.json`: `{"generated_at", "period":{"start","end"}, "thresholds":{"p75","p90"}, "hours":[{"dt","pred","base","uplift","level","show_congestion","titles","assumed_start"}]}`
  - `courses.json`: `latest_timetable` 기준 `[{"course_no","name","days","optional_days","start","end","capacity","group"}]`
  - `overlaps.json`: 예보 기간의 `overlaps` 결과 전체
  - `agency_overlaps.csv`: 같은 내용, UTF-8 BOM, 한글 헤더(강좌번호, 강좌명, 날짜, 시작, 종료, 정원, 토요일선택여부, 최고수준, 공연증가대수, 공연명)
  - `ics/<course_no>.ics`: 그 강좌의 겹침 날짜마다 VEVENT 하나(SUMMARY "올림픽공원 공연 혼잡 예상: <공연명>", 시작·종료는 세션 시각, Asia/Seoul)
  - `metrics.json`: `run_backtest` 결과 + 기준선 비교값 + `weather_effect` 결과
  - `evidence_2025.json`: `evidence_2025` 결과
  - `sources.json`: 데이터 출처 3종과 한계 문구(8~9월 제외, 11월 8일 이후 미사용, 총 주차면 수 미공개)
- Produces: 예보 기간 기본값은 빌드 날짜의 다음 날부터 `schedule.csv` 마지막 날짜까지.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
def test_ics_is_valid_and_kst(tmp_path): ...       # 생성 파일이 BEGIN:VCALENDAR로 시작, DTSTART;TZID=Asia/Seoul 포함
def test_agency_csv_has_bom_and_korean_header(tmp_path): ...
def test_build_writes_all_files(tmp_path):
    main(["--out", str(tmp_path), "--linked", FIX_LINKED, "--courses", FIX_COURSES, "--schedule", FIX_SCHEDULE])
    assert {p.name for p in tmp_path.iterdir()} >= {"forecast.json","courses.json","overlaps.json","agency_overlaps.csv","metrics.json","evidence_2025.json","sources.json","ics"}
```

- [ ] **Step 2: 실패 확인** — FAIL
- [ ] **Step 3: 구현** — ICS는 표준 형식을 직접 문자열로 쓴다(외부 라이브러리 추가 없음).
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: 실데이터 빌드** — `python -m olpark.build --out site/data` 실행 후 `metrics.json`, `evidence_2025.json` 내용을 출력해 사용자에게 보고
- [ ] **Step 6: Commit** — `feat: build pipeline and exports` (`site/data/`는 `.gitignore`)

---

### Task 8: 정적 웹 3개 화면

**Files:**
- Create: `site/index.html`, `site/agency.html`, `site/evidence.html`, `site/app.css`, `site/app.js`, `tests/test_site_smoke.py`

**Interfaces:**
- Consumes: Task 7의 JSON 파일 구조
- Produces:
  - `index.html`(시민용): 월 달력. 날짜 칸은 그날 최고 수준 색(보통/붐빔/매우 붐빔)과 공연명. 날짜 클릭 시 0~23시 막대(예보값, 기준선 점선, 공연 증가분 구분). 상단 강좌 검색(이름 일부 입력) → 선택 시 그 강좌의 겹침 날짜에 테두리 강조, `.ics` 구독 링크. 시작 시각 가정 공연은 "시작 시각 미정(19시 가정)".
  - `agency.html`(기관용): 기간 선택, 겹침 목록 표(정원 합계 포함), CSV 내려받기 링크, 일정 CSV 교체 방법 안내 3줄.
  - `evidence.html`(근거): 2025년 실측 수치, 월별 막대, 상위 공연 5개, 10월 검증 지표와 기준선 비교, 데이터 출처와 한계.
  - 세 화면 공통 하단에 `sources.json` 내용.
- 모바일 폭 375px에서 가로 스크롤이 생기지 않는다.

- [ ] **Step 1: 실패하는 스모크 테스트 작성** — `test_pages_reference_existing_data_files`: 각 HTML/JS가 참조하는 `data/` 경로가 Task 7 산출물 목록에 있는지 검사. `test_no_emoji_or_em_dash`: `site/` 텍스트 파일에 이모지 범위 문자와 `—`가 없는지 검사.
- [ ] **Step 2: 실패 확인** — FAIL
- [ ] **Step 3: 구현**
- [ ] **Step 4: 통과 확인** — PASS
- [ ] **Step 5: 화면 확인** — 빌드 결과를 단일 HTML로 묶어 아티팩트로 미리보기하거나 배포 후 내장 브라우저로 375px·데스크톱 두 폭에서 확인
- [ ] **Step 6: Commit** — `feat: citizen, agency and evidence pages`

---

### Task 9: GitHub 저장소, Actions, Pages 배포

**Files:**
- Create: `.github/workflows/build.yml`, `README.md`, `.gitignore`

**Interfaces:**
- Produces: `main` 브랜치에 push되거나 `data/schedule.csv`가 바뀌면 `pip install -r requirements.txt` → `pytest` → `python -m olpark.build --out site/data` → `site/`를 GitHub Pages로 배포. 테스트 실패 시 배포하지 않는다.
- README: 기관 담당자용 운영 방법(일정 CSV 형식과 교체 절차), 로컬 실행 방법, 데이터 출처.

- [ ] **Step 1: 사용자에게 공개 저장소 `olpark-congestion-calendar` 생성 요청** → `mcp__claude-code-remote__add_repo`로 push 권한 연결
- [ ] **Step 2: workflow 작성 후 push**
- [ ] **Step 3: 확인** — Actions 실행 성공, Pages 주소에서 세 화면이 열리고 `data/forecast.json` 응답 200
- [ ] **Step 4: Commit** — `ci: build and deploy to GitHub Pages`

---

## 이후 단계 (이 계획 범위 밖)

시제품 주소와 `metrics.json`, `evidence_2025.json`이 나오면 기획서(공고 양식, DOCX)를 쓰고, 작업을 보지 않은 검토자가 근거 없는 주장과 AI 문체를 확인한 뒤 12월 1일 18시 전에 제출한다.

---

## Revision 1 (2026-11-17, 사용자 승인): 예보 방식과 출력 단위 변경

Task 5 검증에서 '기준선 + 증가분' 방식이 공연일에 기준선보다 나빠 중단 조건에 걸렸다. 8개월 교차 검증 결과에 따라 아래로 바꾼다. Task 1~4 산출물은 그대로 쓰되 `olpark/uplift.py`는 삭제한다(`events.py`는 유지).

- **예보 방식:** '과거 비슷한 공연일 참고'. `olpark/analog.py`
  - `fit_analog(df, months) -> DataFrame[size, wk, offset, park, n]`: 학습 월의 공연이 하나뿐인 날에서 (규모, `wk`=`"wd"|"we"`, offset −4…+3)별 실제 주차대수 중앙값. `wk`는 `day_type`이 weekday면 `"wd"`, 아니면 `"we"`.
  - `analog_for(profile, size, wk, offset) -> float | None`: `n >= 3`인 칸만 사용, 없으면 같은 `wk`에서 작은 규모로 대체(L→M→S), 그래도 없으면 None.
- **forecast.py:** `forecast(schedule, start, end, table, analog, th)` 시간별 결과 컬럼 `dt, base, pred, titles, assumed_start, baseline_month_fallback`. `pred = base + Σ max(0, analog_i − base)`(같은 시각 여러 공연은 초과분을 합산).
  - `to_blocks(hourly, th) -> DataFrame[date, block, pred_max, base_max, level, show_congestion, titles, assumed_start, baseline_month_fallback]`. 구간은 `오후`=12~16시, `저녁`=17~22시. `level = level_of(pred_max)`, `show_congestion = is_show_congestion(level, pred_max − base_max, base_max) and titles`.
- **기준선 대체 월 동점 처리:** 거리가 같으면 대상 월보다 앞선 달을 쓴다(예: 10월 시험 시 1월·7월 동점 → 7월).
- **backtest.py:** `run_backtest_loo(df) -> dict` 정상 8개월을 한 달씩 시험 달로 빼는 교차 검증. 구간별(`오후`, `저녁`) × 방식별(`analog`, `baseline`)로 `n_days, acc, recall, precision, show_days_n, show_days_acc, show_days_recall, mae`. 분류 기준은 구간 최고값이 '붐빔' 이상인가. 별도로 `show_congestion` 판정의 `hit_rate, false_alarm_rate, n_actual, n_pred`. `weather_effect`는 유지.
- **Task 6:** 강좌 세션이 `show_congestion` 구간과 시간이 겹치면 겹침. `evidence_2025`는 정상 기간 실측값으로 같은 `to_blocks` 규칙을 적용해 계산.
- **Task 7:** `forecast.json`은 시간별 대신 `blocks` 배열(`date, block, level, pred_max, base_max, show_congestion, titles, assumed_start`)을 담는다. `metrics.json`은 `run_backtest_loo` 결과.
- **Task 8:** 시민용 화면의 날짜 상세는 시간별 막대 대신 오후·저녁 두 구간 카드. 근거 화면에 교차 검증 표와 저녁 예보의 한계 문구.
