"""공연 규모·시작 시각 기준 시간대별 주차 증가분 프로필."""
import pandas as pd

from olpark.baseline import baseline_at
from olpark.events import OFFSETS, extract_events, size_of  # noqa: F401 (re-export)

MIN_SAMPLES = 3
_SMALLER = {"L": "M", "M": "S", "S": None}


def fit_uplift(df: pd.DataFrame, table: pd.DataFrame, months: list[int]) -> pd.DataFrame:
    d = df[df["clean"] & df["dt"].dt.month.isin(months)]
    ev = extract_events(d)
    single = ev.groupby("date").filter(lambda g: len(g) == 1)
    lookup = d.set_index("dt")
    rows = []
    for e in single.itertuples(index=False):
        for off in OFFSETS:
            h = e.start_hour + off
            if not 0 <= h <= 23:
                continue
            ts = pd.Timestamp(e.date) + pd.Timedelta(hours=h)
            if ts not in lookup.index:
                continue
            r = lookup.loc[ts]
            base, _ = baseline_at(table, ts, r["holiday"])
            if pd.isna(base):
                continue
            rows.append({"size": e.size, "offset": off, "uplift": float(r["parking"]) - base})
    raw = pd.DataFrame(rows, columns=["size", "offset", "uplift"])
    return (raw.groupby(["size", "offset"])["uplift"].agg(["median", "size"])
            .rename(columns={"median": "uplift", "size": "n"}).reset_index())


def uplift_for(profile: pd.DataFrame, size: str, offset: int) -> float:
    if offset not in OFFSETS:
        return 0.0
    s = size
    while s is not None:
        cell = profile[(profile["size"] == s) & (profile["offset"] == offset) & (profile["n"] >= MIN_SAMPLES)]
        if not cell.empty:
            return float(cell["uplift"].item())
        s = _SMALLER[s]
    return 0.0
