import pandas as pd
from olpark.backtest import run_backtest_loo, weather_effect, block_scores
from tests.helpers import make_df


def _df():
    rows = []
    for m in (1, 2, 3):
        for day in pd.date_range(f"2025-{m:02d}-03", periods=21, freq="D"):
            for h in range(24):
                show = "S" + str(day.date()) if (day.day_of_week == 5 and h >= 19) else None
                rows.append((str(day + pd.Timedelta(hours=h)), 100 + (900 if show else 0), show, 20000 if show else 0))
    df = make_df(rows)
    df["rain"] = [1.0 if i % 10 == 0 else float("nan") for i in range(len(df))]
    return df


def test_block_scores_counts():
    act = pd.Series([True, True, False, False])
    pred = pd.Series([True, False, True, False])
    s = block_scores(act, pred, show=pd.Series([True, True, False, False]),
                     err=pd.Series([10.0, 20.0, 30.0, 40.0]))
    assert s == {"n_days": 4, "acc": 0.5, "recall": 0.5, "precision": 0.5,
                 "show_days_n": 2, "show_days_acc": 0.5, "show_days_recall": 0.5, "mae": 25.0}


def test_loo_structure():
    r = run_backtest_loo(_df(), months=[1, 2, 3])
    assert r["months"] == [1, 2, 3]
    for blk in ("오후", "저녁"):
        assert set(r["blocks"][blk]) == {"analog", "baseline"}
    assert set(r["flag"]) >= {"hit_rate", "false_alarm_rate", "n_actual", "n_pred"}


def test_weather_effect_keys():
    assert set(weather_effect(_df(), [1])) == {"rain_ratio", "dry_ratio", "n_rain", "n_dry"}
