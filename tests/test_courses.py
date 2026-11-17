from datetime import date
from pathlib import Path

import pandas as pd
from olpark.load import load_courses, expand_sessions, latest_timetable, parse_days

FIXTURE = str(Path(__file__).parent / "fixtures" / "courses_small.csv")


def test_parse_days_with_optional_saturday():
    c = load_courses(FIXTURE)
    row = c[c.course_no == "1027444"].iloc[0]
    assert row.days == [0, 2, 4] and row.optional_days == [5]


def test_parse_days_ignores_suffix_like_bang():
    assert parse_days("월,화,수,목,금(방)") == ([0, 1, 2, 3, 4], [])


def test_open_ended_period_is_clipped():
    s = expand_sessions(load_courses(FIXTURE), date(2026, 12, 1), date(2026, 12, 31))
    assert len(s) > 0
    assert s.date.max() <= date(2026, 12, 31)


def test_optional_saturday_sessions_flagged():
    s = expand_sessions(load_courses(FIXTURE), date(2025, 9, 1), date(2025, 9, 30))
    mine = s[s.course_no == "1027444"]
    sat = mine[pd.to_datetime(mine.date).dt.dayofweek == 5]
    assert len(sat) == 4 and sat.optional.all()
    assert not mine[pd.to_datetime(mine.date).dt.dayofweek != 5].optional.any()


def test_closed_month_row_stays_in_its_month():
    s = expand_sessions(load_courses(FIXTURE), date(2025, 8, 1), date(2025, 10, 31))
    mine = s[s.course_no == "1027444"]
    assert pd.to_datetime(mine.date).dt.month.unique().tolist() == [9]


def test_session_times():
    s = expand_sessions(load_courses(FIXTURE), date(2025, 9, 1), date(2025, 9, 1))
    r = s[s.course_no == "1027444"].iloc[0]
    assert r.start_dt == pd.Timestamp("2025-09-01 19:00") and r.end_dt == pd.Timestamp("2025-09-01 19:50")


def test_cp949_name_is_trimmed():
    assert load_courses(FIXTURE).name.str.endswith(" ").sum() == 0


def test_latest_timetable_one_row_per_course():
    t = latest_timetable(load_courses(FIXTURE))
    assert t.course_no.is_unique


def test_no_duplicate_sessions_when_rows_overlap():
    c = load_courses(FIXTURE)
    dup = pd.concat([c, c[c.course_no == "15714"]])
    s = expand_sessions(dup, date(2026, 1, 1), date(2026, 1, 31))
    assert not s.duplicated(["course_no", "start_dt"]).any()


def test_public_holidays_have_no_sessions():
    c = pd.DataFrame([{"course_no": "9", "sub_no": "1", "month": pd.Period("2025-10", "M"), "name": "평일 수영",
                       "start": pd.Timestamp("19:00").time(), "end": pd.Timestamp("19:50").time(), "capacity": 10,
                       "days": [0, 1, 2, 3, 4], "optional_days": [], "group": "", "fee": 0,
                       "period_start": date(2025, 10, 1), "period_end": date(2025, 10, 31)}])
    days = set(expand_sessions(c, date(2025, 10, 1), date(2025, 10, 10)).date)
    assert date(2025, 10, 3) not in days and date(2025, 10, 9) not in days   # 개천절, 한글날
    assert date(2025, 10, 2) in days and date(2025, 10, 10) in days


def test_all_day_passes_and_broken_times_make_no_sessions():
    base = {"sub_no": "1", "capacity": 800, "days": [0, 1, 2, 3, 4, 5, 6], "optional_days": [], "group": "", "fee": 0,
            "month": pd.Period("2025-10", "M"), "period_start": date(2025, 10, 1), "period_end": date(2025, 10, 31)}
    c = pd.DataFrame([
        {**base, "course_no": "pass", "name": "헬스 (월~일)", "start": pd.Timestamp("06:00").time(), "end": pd.Timestamp("21:50").time()},
        {**base, "course_no": "wrap", "name": "11시 서킷핏", "start": pd.Timestamp("11:00").time(), "end": pd.Timestamp("10:50").time()},
        {**base, "course_no": "ok", "name": "수영", "start": pd.Timestamp("19:00").time(), "end": pd.Timestamp("19:50").time()},
    ])
    s = expand_sessions(c, date(2025, 10, 13), date(2025, 10, 13))
    assert set(s.course_no) == {"ok"}
