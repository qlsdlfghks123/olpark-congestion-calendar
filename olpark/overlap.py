"""강좌 세션 × 공연 혼잡 구간 겹침, 2025년 실측 근거."""
import pandas as pd

from olpark.baseline import baseline_at, fit_baseline, level_thresholds
from olpark.events import OFFSETS, extract_events
from olpark.forecast import BLOCKS, to_blocks
from olpark.load import CLEAN_MONTHS, expand_sessions

OVERLAP_COLS = ["course_no", "name", "date", "start_dt", "end_dt", "capacity", "optional",
                "block", "level", "excess", "titles", "assumed_start"]


def overlaps(sessions: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    flagged = blocks[blocks["show_congestion"]]
    by_date = {d: g for d, g in flagged.groupby("date")}
    rows = []
    for s in sessions.itertuples(index=False):
        g = by_date.get(s.date)
        if g is None:
            continue
        for b in g.itertuples(index=False):
            lo, hi = BLOCKS[b.block]
            b_start = pd.Timestamp(s.date) + pd.Timedelta(hours=lo)
            b_end = pd.Timestamp(s.date) + pd.Timedelta(hours=hi + 1)
            if s.start_dt < b_end and s.end_dt > b_start:
                rows.append({"course_no": s.course_no, "name": s.name, "date": s.date, "start_dt": s.start_dt,
                             "end_dt": s.end_dt, "capacity": s.capacity, "optional": s.optional, "block": b.block,
                             "level": b.level, "excess": b.pred_max - b.base_max, "titles": b.titles,
                             "assumed_start": b.assumed_start})
                break  # 한 세션은 한 번만 센다
    return pd.DataFrame(rows, columns=OVERLAP_COLS)


def observed_hourly(df: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    h = df[["dt", "parking", "holiday"]].copy()
    h["base"] = [baseline_at(table, ts, hol)[0] for ts, hol in zip(h["dt"], h["holiday"])]
    titles = {ts: [] for ts in h["dt"]}
    for e in extract_events(df).itertuples(index=False):
        for off in OFFSETS:
            ts = pd.Timestamp(e.date) + pd.Timedelta(hours=e.start_hour + off)
            if ts in titles and e.show not in titles[ts]:
                titles[ts].append(e.show)
    h["titles"] = [titles[ts] for ts in h["dt"]]
    h["assumed_start"] = False
    h["baseline_month_fallback"] = None
    return h.drop(columns=["holiday"])


def evidence_2025(df: pd.DataFrame, courses: pd.DataFrame, months: list[int] = CLEAN_MONTHS) -> dict:
    clean = df[df["clean"] & df["dt"].dt.month.isin(months)]
    table = fit_baseline(df, months)
    th = level_thresholds(df, months)
    blocks = to_blocks(observed_hourly(clean, table), th, value_col="parking")
    sessions = expand_sessions(courses, clean["dt"].min().date(), clean["dt"].max().date())
    sessions = sessions[pd.to_datetime(sessions["date"]).dt.month.isin(months)]
    ov = overlaps(sessions, blocks)
    top = (ov.explode("titles").groupby(["titles", "date"]).size().rename("sessions").reset_index()
           .sort_values("sessions", ascending=False).head(5))
    return {
        "months": list(months),
        "n_sessions_total": int(len(sessions)),
        "n_sessions_overlapped": int(len(ov)),
        "n_sessions_overlapped_optional": int(ov["optional"].sum()),
        "capacity_sum": int(ov["capacity"].sum()),
        "n_blocks": int(len(blocks)),
        "n_show_congestion_blocks": int(blocks["show_congestion"].sum()),
        "by_month": {int(k): int(v) for k, v in pd.to_datetime(ov["date"]).dt.month.value_counts().sort_index().items()},
        "by_block": {k: int(v) for k, v in ov["block"].value_counts().items()},
        "top_events": [{"title": r.titles, "date": str(r.date), "sessions": int(r.sessions)} for r in top.itertuples()],
        "thresholds": th,
    }
