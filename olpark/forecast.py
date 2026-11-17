"""공연 일정 → 시간대별 주차 예보와 '공연 혼잡' 판정."""
from datetime import date

import pandas as pd

from olpark.baseline import baseline_at, level_of
from olpark.uplift import OFFSETS, uplift_for

MIN_UPLIFT = 200.0
MIN_UPLIFT_RATIO = 0.25


def is_show_congestion(level: str, uplift: float, base: float) -> bool:
    return bool(level != "보통" and uplift >= max(MIN_UPLIFT, MIN_UPLIFT_RATIO * base))


def forecast(schedule: pd.DataFrame, start: date, end: date, table: pd.DataFrame,
             profile: pd.DataFrame, th: dict) -> pd.DataFrame:
    sched = schedule.copy()
    if "start_time_assumed" not in sched.columns:
        sched["start_time_assumed"] = False
    by_date = {d: g for d, g in sched.groupby("date")} if len(sched) else {}
    rows = []
    for ts in pd.date_range(pd.Timestamp(start), pd.Timestamp(end) + pd.Timedelta(hours=23), freq="h"):
        base, fb = baseline_at(table, ts)
        up, titles, assumed = 0.0, [], False
        for e in by_date.get(ts.date(), pd.DataFrame()).itertuples(index=False):
            off = ts.hour - int(e.start_hour)
            if off in OFFSETS:
                up += uplift_for(profile, e.size, off)
                titles.append(e.title)
                assumed = assumed or bool(e.start_time_assumed)
        pred = max(0.0, base + up)
        lvl = level_of(pred, th)
        rows.append({"dt": ts, "base": base, "uplift": up, "pred": pred, "level": lvl,
                     "show_congestion": is_show_congestion(lvl, up, base), "titles": titles,
                     "assumed_start": assumed, "baseline_month_fallback": fb})
    return pd.DataFrame(rows)
