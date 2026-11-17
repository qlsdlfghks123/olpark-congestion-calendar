from datetime import date

import pandas as pd
from olpark.forecast import forecast, is_show_congestion

# baseline: weekday Jan 100 at all hours
TABLE = pd.DataFrame({"month": 1, "day_type": "weekday", "hour": range(24), "base": 100.0})
PROFILE = pd.DataFrame({"size": ["L", "L"], "offset": [0, 1], "uplift": [300.0, 500.0], "n": [5, 5]})
TH = {"p75": 300.0, "p90": 600.0}


def _sched(rows):
    return pd.DataFrame(rows, columns=["date", "start_hour", "size", "title", "venue"])


def test_no_show_equals_baseline():
    f = forecast(_sched([]), date(2027, 1, 13), date(2027, 1, 13), TABLE, PROFILE, TH)
    assert len(f) == 24 and (f.pred == 100).all() and not f.show_congestion.any()


def test_two_shows_same_hour_add_up():
    s = _sched([(date(2027, 1, 13), 19, "L", "A", "KSPO DOME"), (date(2027, 1, 13), 19, "L", "B", "올림픽홀")])
    f = forecast(s, date(2027, 1, 13), date(2027, 1, 13), TABLE, PROFILE, TH).set_index("dt")
    assert f.loc[pd.Timestamp("2027-01-13 19:00"), "uplift"] == 600
    assert f.loc[pd.Timestamp("2027-01-13 20:00"), "titles"] == ["A", "B"]


def test_level_and_flag():
    s = _sched([(date(2027, 1, 13), 19, "L", "A", "KSPO DOME")])
    f = forecast(s, date(2027, 1, 13), date(2027, 1, 13), TABLE, PROFILE, TH).set_index("dt")
    r = f.loc[pd.Timestamp("2027-01-13 20:00")]
    assert r.pred == 600 and r.level == "매우 붐빔" and r.show_congestion


def test_fallback_month_recorded():
    f = forecast(_sched([]), date(2026, 12, 9), date(2026, 12, 9), TABLE, PROFILE, TH)
    assert (f.baseline_month_fallback == 1).all()


def test_assumed_start_propagates():
    s = _sched([(date(2027, 1, 13), 19, "L", "A", "KSPO DOME")])
    s["start_time_assumed"] = True
    f = forecast(s, date(2027, 1, 13), date(2027, 1, 13), TABLE, PROFILE, TH).set_index("dt")
    assert f.loc[pd.Timestamp("2027-01-13 19:00"), "assumed_start"] and not f.loc[pd.Timestamp("2027-01-13 10:00"), "assumed_start"]


def test_show_congestion_rule():
    assert is_show_congestion("붐빔", 300, 1000) is True
    assert is_show_congestion("붐빔", 200, 1000) is False
    assert is_show_congestion("보통", 900, 100) is False
