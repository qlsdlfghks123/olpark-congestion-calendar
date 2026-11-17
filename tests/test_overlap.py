from datetime import date
from pathlib import Path

import pandas as pd
from olpark.load import load_schedule
from olpark.overlap import overlaps, observed_hourly, evidence_2025
from tests.helpers import make_df

FIX = Path(__file__).parent / "fixtures"


def test_missing_start_time_assumed_19():
    s = load_schedule(str(FIX / "schedule_small.csv"))
    row = s[s.title == "시각미정공연"].iloc[0]
    assert row.start_hour == 19 and row.start_time_assumed


def test_multi_day_show_expands():
    s = load_schedule(str(FIX / "schedule_small.csv"))
    assert sorted(s[s.title == "범위공연"].date) == [date(2026, 12, 24), date(2026, 12, 25), date(2026, 12, 26)]


def test_size_from_audience_then_venue_default():
    s = load_schedule(str(FIX / "schedule_small.csv")).drop_duplicates("title").set_index("title")["size"]
    assert s["관객수공연"] == "L" and s["시각미정공연"] == "L" and s["범위공연"] == "S"


def _blocks(flag_evening=True):
    return pd.DataFrame([
        {"date": date(2026, 12, 24), "block": "오후", "pred_max": 1000.0, "base_max": 1000.0, "level": "보통",
         "show_congestion": False, "titles": [], "assumed_start": False, "baseline_month_fallback": 1},
        {"date": date(2026, 12, 24), "block": "저녁", "pred_max": 3000.0, "base_max": 1000.0, "level": "매우 붐빔",
         "show_congestion": flag_evening, "titles": ["범위공연"], "assumed_start": False, "baseline_month_fallback": 1},
    ])


def _sessions(start, end):
    return pd.DataFrame([{"course_no": "1", "name": "수영", "date": date(2026, 12, 24),
                          "start_dt": pd.Timestamp(f"2026-12-24 {start}"), "end_dt": pd.Timestamp(f"2026-12-24 {end}"),
                          "capacity": 20, "optional": False}])


def test_session_overlap_boundary():
    assert len(overlaps(_sessions("19:00", "19:50"), _blocks())) == 1
    assert len(overlaps(_sessions("16:00", "16:50"), _blocks())) == 0      # afternoon block not flagged
    assert len(overlaps(_sessions("16:30", "17:20"), _blocks())) == 1      # crosses into evening
    assert len(overlaps(_sessions("23:00", "23:50"), _blocks())) == 0      # evening block ends at 23:00


def test_unflagged_block_never_overlaps():
    assert len(overlaps(_sessions("19:00", "19:50"), _blocks(flag_evening=False))) == 0


def test_overlap_columns():
    o = overlaps(_sessions("19:00", "19:50"), _blocks()).iloc[0]
    assert o.block == "저녁" and o.level == "매우 붐빔" and o.excess == 2000 and o.titles == ["범위공연"]


def test_observed_hourly_titles_cover_show_window():
    df = make_df([(f"2025-01-23 {h}:00", 500, "공연A" if h >= 19 else None, 0) for h in range(12, 24)])
    table = pd.DataFrame({"month": 1, "day_type": "weekday", "hour": range(24), "base": 400.0})
    h = observed_hourly(df, table).set_index("dt")
    assert h.loc[pd.Timestamp("2025-01-23 15:00"), "titles"] == ["공연A"]
    assert h.loc[pd.Timestamp("2025-01-23 14:00"), "titles"] == []
    assert h.loc[pd.Timestamp("2025-01-23 19:00"), "base"] == 400.0


def test_evidence_keys():
    rows = []
    for day in pd.date_range("2025-01-06", periods=28, freq="D"):
        for hh in range(24):
            show = "S" + str(day.date()) if (day.dayofweek == 5 and hh >= 18) else None
            rows.append((str(day + pd.Timedelta(hours=hh)), 300 + (3000 if show else 0), show, 20000 if show else 0))
    courses = pd.DataFrame([{"course_no": "1", "sub_no": "1", "month": pd.Period("2025-01", "M"), "name": "토요 수영",
                             "start": pd.Timestamp("19:00").time(), "end": pd.Timestamp("19:50").time(), "capacity": 10,
                             "days": [5], "optional_days": [], "group": "", "fee": 0,
                             "period_start": date(2025, 1, 1), "period_end": date(2025, 1, 31)}])
    ev = evidence_2025(make_df(rows), courses, months=[1])
    assert set(ev) >= {"n_sessions_overlapped", "n_sessions_total", "capacity_sum", "n_show_congestion_blocks",
                       "n_blocks", "by_month", "top_events"}
    assert ev["n_sessions_overlapped"] == 3 and ev["capacity_sum"] == 30  # Jan 11, 18, 25
