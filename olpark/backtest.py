"""학습 월로 적합하고 시험 월로 예보 정확도를 잰다."""
import json
import sys

import pandas as pd

from olpark.baseline import baseline_at, fit_baseline, level_of, level_thresholds
from olpark.events import extract_events, show_window_mask
from olpark.forecast import forecast, is_show_congestion
from olpark.uplift import fit_uplift

TRAIN_MONTHS = [1, 2, 3, 4, 5, 6, 7]
TEST_MONTH = 10


def _scores(merged: pd.DataFrame, pred_col: str, flag_col: str) -> dict:
    show_days = merged["has_show"]
    actual_flag = merged["actual_flag"]
    pred_flag = merged[flag_col]
    tp = int((actual_flag & pred_flag).sum())
    return {
        "mae_all": round(float((merged[pred_col] - merged["parking"]).abs().mean()), 1),
        "mae_show_days": round(float((merged.loc[show_days, pred_col] - merged.loc[show_days, "parking"]).abs().mean()), 1),
        "hit_rate": round(tp / int(actual_flag.sum()), 3) if actual_flag.sum() else None,
        "false_alarm_rate": round(1 - tp / int(pred_flag.sum()), 3) if pred_flag.sum() else None,
        "n_actual": int(actual_flag.sum()),
        "n_pred": int(pred_flag.sum()),
    }


def run_backtest(df: pd.DataFrame, train_months=TRAIN_MONTHS, test_month=TEST_MONTH) -> dict:
    table = fit_baseline(df, train_months)
    profile = fit_uplift(df, table, train_months)
    th = level_thresholds(df, train_months)
    test = df[df["clean"] & (df["dt"].dt.month == test_month)].copy()
    ev = extract_events(test)
    sched = ev.rename(columns={"show": "title"})[["date", "start_hour", "size", "title"]].assign(venue="")
    start, end = test["dt"].min().date(), test["dt"].max().date()
    f = forecast(sched, start, end, table, profile, th)
    test["in_window"] = show_window_mask(test).values
    m = test.merge(f, on="dt", how="inner")
    m["actual_up"] = m["parking"] - m["base"]
    m["actual_flag"] = [bool(w) and is_show_congestion(level_of(p, th), u, b)
                        for w, p, u, b in zip(m["in_window"], m["parking"], m["actual_up"], m["base"])]
    m["has_show"] = m["dt"].dt.date.isin(set(ev["date"]))
    m["base_flag"] = False
    out = _scores(m, "pred", "show_congestion")
    out["baseline_only"] = _scores(m, "base", "base_flag")
    out["thresholds"] = th
    out["n_test_hours"] = int(len(m))
    out["n_test_events"] = int(len(ev))
    return out


def weather_effect(df: pd.DataFrame, months: list[int]) -> dict:
    table = fit_baseline(df, months)
    d = df[df["clean"] & df["dt"].dt.month.isin(months) & ~show_window_mask(df).values].copy()
    d["base"] = [baseline_at(table, ts, h)[0] for ts, h in zip(d["dt"], d["holiday"])]
    d = d[d["base"] > 0]
    d["ratio"] = d["parking"] / d["base"]
    rain = d["rain"].fillna(0) > 0
    return {"rain_ratio": round(float(d.loc[rain, "ratio"].median()), 3) if rain.any() else None,
            "dry_ratio": round(float(d.loc[~rain, "ratio"].median()), 3),
            "n_rain": int(rain.sum()), "n_dry": int((~rain).sum())}


if __name__ == "__main__":
    from olpark.load import load_linked
    data = load_linked(sys.argv[1])
    res = run_backtest(data)
    res["weather"] = weather_effect(data, TRAIN_MONTHS)
    print(json.dumps(res, ensure_ascii=False, indent=1))
