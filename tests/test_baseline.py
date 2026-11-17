import pandas as pd
from pandas import Timestamp
from olpark.baseline import fit_baseline, baseline_at, level_thresholds, level_of
from tests.helpers import make_df

# 2025-01-02, 09, 16, 23 are ordinary Thursdays
DF = make_df([
    ("2025-01-02 19:00", 100, None, 0),
    ("2025-01-09 19:00", 120, None, 0),
    ("2025-01-16 19:00", 140, None, 0),
    ("2025-01-23 19:00", 900, "공연A", 10000),
])


def test_baseline_ignores_show_hours():
    t = fit_baseline(DF, [1])
    assert t.query("month==1 and day_type=='weekday' and hour==19").base.item() == 120


def test_fallback_for_december():
    t = fit_baseline(DF, [1])
    v, used = baseline_at(t, Timestamp("2026-12-09 19:00"))
    assert used == 1 and v == 120


def test_same_month_has_no_fallback():
    t = fit_baseline(DF, [1])
    assert baseline_at(t, Timestamp("2027-01-11 19:00")) == (120, None)


def test_missing_cell_uses_all_month_median():
    df = pd.concat([DF, make_df([("2025-02-03 19:00", 200, None, 0)])])
    t = fit_baseline(df, [1, 2])
    v, used = baseline_at(t, Timestamp("2026-03-09 19:00"))   # March missing -> Feb (nearest)
    assert used == 2 and v == 200


def test_levels():
    th = {"p75": 1000, "p90": 2000}
    assert [level_of(x, th) for x in (999, 1000, 2000)] == ["보통", "붐빔", "매우 붐빔"]


def test_thresholds_only_training_months_and_clean():
    df = make_df([(f"2025-01-{d:02d} 10:00", d * 10, None, 0) for d in range(1, 21)])
    df.loc[df.index[-1], "clean"] = False
    th = level_thresholds(df, [1])
    assert th["p90"] == df[df.clean].parking.quantile(0.9)


def test_baseline_excludes_pre_show_hours_on_show_day():
    # show tagged from 19h; 17h on the same day is inside the -4..+3 window and must not enter the baseline
    df = make_df([
        ("2025-01-06 17:00", 100, None, 0),
        ("2025-01-20 17:00", 900, None, 0),
        ("2025-01-20 19:00", 900, "공연A", 10000),
    ])
    t = fit_baseline(df, [1])
    assert t.query("day_type=='weekday' and hour==17").base.item() == 100
