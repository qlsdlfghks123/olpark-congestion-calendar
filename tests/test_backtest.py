import pandas as pd
from olpark.backtest import run_backtest, weather_effect
from tests.helpers import make_df


def _df():
    rows = []
    for m in (1, 10):
        for day in pd.date_range(f"2025-{m:02d}-06", periods=14, freq="D"):
            for h in range(24):
                show = "S" + str(day.date()) if (day.dayofweek == 5 and h >= 19) else None
                park = 100 + (900 if show else 0)
                rows.append((day + pd.Timedelta(hours=h), park, show, 20000 if show else 0))
    df = make_df([(str(a), b, c, d) for a, b, c, d in rows])
    df["rain"] = [1.0 if i % 10 == 0 else float("nan") for i in range(len(df))]
    return df


def test_backtest_keys():
    r = run_backtest(_df(), train_months=[1], test_month=10)
    assert set(r) >= {"mae_all", "mae_show_days", "hit_rate", "false_alarm_rate", "n_actual", "n_pred", "baseline_only"}


def test_weather_effect_keys():
    assert set(weather_effect(_df(), [1])) == {"rain_ratio", "dry_ratio", "n_rain", "n_dry"}
