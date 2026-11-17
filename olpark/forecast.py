"""공연 일정 → 시간별 예보 → 오후·저녁 구간 판정."""
from datetime import date

import pandas as pd

from olpark.analog import analog_for, wk_of
from olpark.baseline import baseline_at, level_of
from olpark.events import OFFSETS

MIN_UPLIFT = 200.0
MIN_UPLIFT_RATIO = 0.25
BLOCKS = {"오후": (12, 16), "저녁": (17, 22)}


def is_show_congestion(level: str, uplift: float, base: float) -> bool:
    return bool(level != "보통" and uplift >= max(MIN_UPLIFT, MIN_UPLIFT_RATIO * base))


def forecast(schedule: pd.DataFrame, start: date, end: date, table: pd.DataFrame,
             analog: pd.DataFrame, th: dict) -> pd.DataFrame:
    sched = schedule.copy()
    if "start_time_assumed" not in sched.columns:
        sched["start_time_assumed"] = False
    by_date = {d: g for d, g in sched.groupby("date")} if len(sched) else {}
    rows = []
    for ts in pd.date_range(pd.Timestamp(start), pd.Timestamp(end) + pd.Timedelta(hours=23), freq="h"):
        base, fb = baseline_at(table, ts)
        excess, titles, assumed = 0.0, [], False
        events = by_date.get(ts.date())
        if events is not None:
            wk = wk_of(ts.date())
            for e in events.itertuples(index=False):
                off = ts.hour - int(e.start_hour)
                if off not in OFFSETS:
                    continue
                titles.append(e.title)
                assumed = assumed or bool(e.start_time_assumed)
                a = analog_for(analog, e.size, wk, off)
                if a is not None and not pd.isna(base):
                    excess += max(0.0, a - base)
        rows.append({"dt": ts, "base": base, "pred": base + excess, "titles": titles,
                     "assumed_start": assumed, "baseline_month_fallback": fb})
    return pd.DataFrame(rows)


def to_blocks(hourly: pd.DataFrame, th: dict, value_col: str = "pred") -> pd.DataFrame:
    h = hourly.copy()
    h["date"] = h["dt"].dt.date
    h["hour"] = h["dt"].dt.hour
    rows = []
    for d, g in h.groupby("date"):
        for name, (lo, hi) in BLOCKS.items():
            b = g[g["hour"].between(lo, hi)]
            if b.empty:
                continue
            pmax, bmax = float(b[value_col].max()), float(b["base"].max())
            titles = list(dict.fromkeys(t for ts in b["titles"] for t in ts))
            lvl = level_of(pmax, th)
            fb = b["baseline_month_fallback"].dropna()
            rows.append({"date": d, "block": name, "pred_max": pmax, "base_max": bmax, "level": lvl,
                         "show_congestion": bool(titles) and is_show_congestion(lvl, pmax - bmax, bmax),
                         "titles": titles, "assumed_start": bool(b["assumed_start"].any()),
                         "baseline_month_fallback": int(fb.iloc[0]) if len(fb) else None})
    return pd.DataFrame(rows, columns=["date", "block", "pred_max", "base_max", "level", "show_congestion",
                                       "titles", "assumed_start", "baseline_month_fallback"])
