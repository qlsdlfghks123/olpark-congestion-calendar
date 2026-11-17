"""'과거 비슷한 공연일 참고' 예보: 규모·평일/주말·시작 기준 시각별 실제 주차대수 중앙값."""
import pandas as pd

from olpark.calendar_kr import day_type
from olpark.events import OFFSETS, extract_events

MIN_SAMPLES = 3
_SMALLER = {"L": "M", "M": "S", "S": None}


def wk_of(d, holiday_name=None) -> str:
    return "wd" if day_type(d, holiday_name) == "weekday" else "we"


def fit_analog(df: pd.DataFrame, months: list[int]) -> pd.DataFrame:
    d = df[df["clean"] & df["dt"].dt.month.isin(months)]
    ev = extract_events(d)
    single = ev.groupby("date").filter(lambda g: len(g) == 1)
    lookup = d.set_index("dt")
    rows = []
    for e in single.itertuples(index=False):
        for off in OFFSETS:
            ts = pd.Timestamp(e.date) + pd.Timedelta(hours=e.start_hour + off)
            if ts.date() != e.date or ts not in lookup.index:
                continue
            r = lookup.loc[ts]
            rows.append({"size": e.size, "wk": wk_of(e.date, r["holiday"]), "offset": off, "park": float(r["parking"])})
    raw = pd.DataFrame(rows, columns=["size", "wk", "offset", "park"])
    return (raw.groupby(["size", "wk", "offset"])["park"].agg(park="median", n="count").reset_index())


def analog_for(profile: pd.DataFrame, size: str, wk: str, offset: int) -> float | None:
    if offset not in OFFSETS:
        return None
    s = size
    while s is not None:
        cell = profile[(profile["size"] == s) & (profile["wk"] == wk)
                       & (profile["offset"] == offset) & (profile["n"] >= MIN_SAMPLES)]
        if not cell.empty:
            return float(cell["park"].item())
        s = _SMALLER[s]
    return None
