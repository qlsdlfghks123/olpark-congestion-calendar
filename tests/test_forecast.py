from datetime import date

import pandas as pd
from olpark.forecast import forecast, is_show_congestion, to_blocks

# baseline: weekday Jan 1000 at all hours
TABLE = pd.DataFrame({"month": 1, "day_type": "weekday", "hour": range(24), "base": 1000.0})
ANALOG = pd.DataFrame({"size": ["L", "L"], "wk": ["wd", "wd"], "offset": [0, 1], "park": [1600.0, 2500.0], "n": [5, 5]})
TH = {"p75": 1500.0, "p90": 2400.0}
D = date(2027, 1, 13)  # Wednesday


def _sched(rows):
    return pd.DataFrame(rows, columns=["date", "start_hour", "size", "title", "venue"])


def test_no_show_equals_baseline():
    f = forecast(_sched([]), D, D, TABLE, ANALOG, TH)
    assert len(f) == 24 and (f.pred == 1000).all()


def test_two_shows_same_hour_add_excess():
    s = _sched([(D, 19, "L", "A", "KSPO DOME"), (D, 19, "L", "B", "올림픽홀")])
    f = forecast(s, D, D, TABLE, ANALOG, TH).set_index("dt")
    assert f.loc[pd.Timestamp("2027-01-13 19:00"), "pred"] == 1000 + 600 + 600
    assert f.loc[pd.Timestamp("2027-01-13 20:00"), "titles"] == ["A", "B"]


def test_analog_below_base_does_not_lower_prediction():
    low = ANALOG.assign(park=[500.0, 500.0])
    f = forecast(_sched([(D, 19, "L", "A", "")]), D, D, TABLE, low, TH)
    assert (f.pred == 1000).all()


def test_fallback_month_recorded():
    f = forecast(_sched([]), date(2026, 12, 9), date(2026, 12, 9), TABLE, ANALOG, TH)
    assert (f.baseline_month_fallback == 1).all()


def test_assumed_start_propagates():
    s = _sched([(D, 19, "L", "A", "KSPO DOME")])
    s["start_time_assumed"] = True
    f = forecast(s, D, D, TABLE, ANALOG, TH).set_index("dt")
    assert f.loc[pd.Timestamp("2027-01-13 19:00"), "assumed_start"]
    assert not f.loc[pd.Timestamp("2027-01-13 10:00"), "assumed_start"]


def test_blocks_evening_flagged_afternoon_not():
    f = forecast(_sched([(D, 19, "L", "A", "KSPO DOME")]), D, D, TABLE, ANALOG, TH)
    b = to_blocks(f, TH).set_index("block")
    assert list(b.index) == ["오후", "저녁"]
    ev = b.loc["저녁"]
    assert ev.pred_max == 2500 and ev.base_max == 1000 and ev.level == "매우 붐빔" and ev.show_congestion
    assert ev.titles == ["A"]
    assert not b.loc["오후"].show_congestion and b.loc["오후"].titles == ["A"]  # 15-16h are inside the -4..+3 window


def test_busy_block_without_show_is_not_show_congestion():
    busy = TABLE.assign(base=2000.0)
    b = to_blocks(forecast(_sched([]), D, D, busy, ANALOG, TH), TH).set_index("block")
    assert b.loc["오후"].level == "붐빔" and not b.loc["오후"].show_congestion


def test_show_congestion_rule():
    assert is_show_congestion("붐빔", 300, 1000) is True
    assert is_show_congestion("붐빔", 200, 1000) is False
    assert is_show_congestion("보통", 900, 100) is False
