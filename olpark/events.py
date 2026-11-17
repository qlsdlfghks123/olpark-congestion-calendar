"""공연 이벤트 추출과 규모 구간 (기준선과 증가분 모두 사용)."""
import pandas as pd

OFFSETS = range(-4, 4)  # 공연 시작 4시간 전 ~ 3시간 뒤


def size_of(audience: float) -> str:
    if audience >= 15000:
        return "L"
    if audience >= 5000:
        return "M"
    return "S"


def extract_events(df: pd.DataFrame) -> pd.DataFrame:
    s = df[df["show"].notna()].copy()
    s["date"] = s["dt"].dt.date
    ev = (s.groupby(["date", "show"])
          .agg(start_hour=("dt", lambda x: int(x.min().hour)), audience=("audience", "max"))
          .reset_index())
    ev["audience"] = ev["audience"].astype(int)
    ev["size"] = ev["audience"].map(size_of)
    return ev


def show_window_mask(df: pd.DataFrame) -> pd.Series:
    """공연명이 붙은 시각 또는 같은 날 공연 시작 -4..+3시간 안의 시각이면 True."""
    mask = df["show"].notna().copy()
    ev = extract_events(df)
    if ev.empty:
        return mask
    dates = df["dt"].dt.date
    hours = df["dt"].dt.hour
    for e in ev.itertuples(index=False):
        lo, hi = e.start_hour + min(OFFSETS), e.start_hour + max(OFFSETS)
        mask |= (dates == e.date) & hours.between(lo, hi)
    return mask
