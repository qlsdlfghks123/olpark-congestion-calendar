"""정상 8개월 교차 검증(한 달씩 시험 달로 제외)과 날씨 영향."""
import json
import sys

import pandas as pd

from olpark.analog import fit_analog
from olpark.baseline import baseline_at, fit_baseline, level_thresholds
from olpark.events import extract_events, show_window_mask
from olpark.forecast import forecast, to_blocks
from olpark.load import CLEAN_MONTHS


def _r(x, nd=3):
    return None if x is None else round(float(x), nd)


def block_scores(act: pd.Series, pred: pd.Series, show: pd.Series, err: pd.Series) -> dict:
    act, pred, show = act.astype(bool), pred.astype(bool), show.astype(bool)
    tp = int((act & pred).sum())
    return {
        "n_days": int(len(act)),
        "acc": _r((act == pred).mean()),
        "recall": _r(tp / act.sum()) if act.sum() else None,
        "precision": _r(tp / pred.sum()) if pred.sum() else None,
        "show_days_n": int(show.sum()),
        "show_days_acc": _r((act == pred)[show].mean()) if show.any() else None,
        "show_days_recall": _r((act & pred)[show].sum() / act[show].sum()) if act[show].sum() else None,
        "mae": _r(err.mean(), 1),
    }


def _month_frames(df: pd.DataFrame, test_month: int, train: list[int]):
    table = fit_baseline(df, train)
    analog = fit_analog(df, train)
    th = level_thresholds(df, train)
    test = df[df["clean"] & (df["dt"].dt.month == test_month)].copy()
    ev = extract_events(test)
    sched = ev.rename(columns={"show": "title"})[["date", "start_hour", "size", "title"]].assign(venue="")
    f = forecast(sched, test["dt"].min().date(), test["dt"].max().date(), table, analog, th)
    f = f.merge(test[["dt", "parking"]], on="dt", how="inner")
    # actual: same blocks rule applied to observed parking; titles come from the observed show windows
    win = show_window_mask(test).values
    obs = test[["dt", "parking"]].copy()
    obs["base"] = f.set_index("dt").reindex(obs["dt"])["base"].values
    obs["titles"] = [["show"] if w else [] for w in win]
    obs["assumed_start"] = False
    obs["baseline_month_fallback"] = None
    return f, obs, th, set(ev["date"])


def run_backtest_loo(df: pd.DataFrame, months: list[int] = CLEAN_MONTHS) -> dict:
    pred_blocks, act_blocks = [], []
    for m in months:
        train = [x for x in months if x != m]
        f, obs, th, show_dates = _month_frames(df, m, train)
        pb = to_blocks(f, th)
        bb = to_blocks(f.assign(base_only=f["base"]), th, value_col="base_only")
        ab = to_blocks(obs, th, value_col="parking")
        key = ["date", "block"]
        merged = (pb.merge(bb[key + ["pred_max", "level"]], on=key, suffixes=("", "_base"))
                  .merge(ab[key + ["pred_max", "level", "show_congestion"]], on=key, suffixes=("", "_act")))
        merged["show_day"] = merged["date"].isin(show_dates)
        pred_blocks.append(merged)
    allb = pd.concat(pred_blocks, ignore_index=True)
    busy = lambda s: s != "보통"  # noqa: E731
    out = {"months": list(months), "blocks": {}}
    for blk, g in allb.groupby("block", sort=False):
        act = busy(g["level_act"])
        out["blocks"][blk] = {
            "analog": block_scores(act, busy(g["level"]), g["show_day"], (g["pred_max"] - g["pred_max_act"]).abs()),
            "baseline": block_scores(act, busy(g["level_base"]), g["show_day"], (g["pred_max_base"] - g["pred_max_act"]).abs()),
        }
    a, p = allb["show_congestion_act"].astype(bool), allb["show_congestion"].astype(bool)
    tp = int((a & p).sum())
    out["flag"] = {"hit_rate": _r(tp / a.sum()) if a.sum() else None,
                   "false_alarm_rate": _r(1 - tp / p.sum()) if p.sum() else None,
                   "n_actual": int(a.sum()), "n_pred": int(p.sum())}
    return out


def weather_effect(df: pd.DataFrame, months: list[int]) -> dict:
    table = fit_baseline(df, months)
    d = df[df["clean"] & df["dt"].dt.month.isin(months) & ~show_window_mask(df).values].copy()
    d["base"] = [baseline_at(table, ts, h)[0] for ts, h in zip(d["dt"], d["holiday"])]
    d = d[d["base"] > 0]
    d["ratio"] = d["parking"] / d["base"]
    rain = d["rain"].fillna(0) > 0
    return {"rain_ratio": _r(d.loc[rain, "ratio"].median()) if rain.any() else None,
            "dry_ratio": _r(d.loc[~rain, "ratio"].median()),
            "n_rain": int(rain.sum()), "n_dry": int((~rain).sum())}


if __name__ == "__main__":
    from olpark.load import load_linked
    data = load_linked(sys.argv[1])
    res = run_backtest_loo(data)
    res["weather"] = weather_effect(data, CLEAN_MONTHS)
    print(json.dumps(res, ensure_ascii=False, indent=1))
