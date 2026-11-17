"""공연이 없는 시간의 기준선과 혼잡 수준 경계."""
import pandas as pd

from olpark.calendar_kr import day_type

LEVELS = ("보통", "붐빔", "매우 붐빔")


def _with_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out["dt"].dt.month
    out["hour"] = out["dt"].dt.hour
    out["day_type"] = [day_type(d.date(), h) for d, h in zip(out["dt"], out["holiday"])]
    return out


def fit_baseline(df: pd.DataFrame, months: list[int]) -> pd.DataFrame:
    d = _with_keys(df)
    d = d[d["clean"] & d["month"].isin(months) & d["show"].isna()]
    return (d.groupby(["month", "day_type", "hour"])["parking"].median()
            .rename("base").reset_index())


def _nearest_month(target: int, available: list[int]) -> int:
    return min(available, key=lambda m: (min((m - target) % 12, (target - m) % 12), m))


def baseline_at(table: pd.DataFrame, ts: pd.Timestamp, holiday_name: str | None = None):
    dt_ = day_type(ts.date(), holiday_name)
    cell = table[(table["day_type"] == dt_) & (table["hour"] == ts.hour)]
    if cell.empty:
        return float("nan"), None
    months = sorted(cell["month"].unique().tolist())
    if ts.month in months:
        return float(cell.loc[cell["month"] == ts.month, "base"].item()), None
    m = _nearest_month(ts.month, months)
    return float(cell.loc[cell["month"] == m, "base"].item()), m


def level_thresholds(df: pd.DataFrame, months: list[int]) -> dict:
    d = df[df["clean"] & df["dt"].dt.month.isin(months)]["parking"]
    return {"p75": float(d.quantile(0.75)), "p90": float(d.quantile(0.9))}


def level_of(value: float, th: dict) -> str:
    if value >= th["p90"]:
        return "매우 붐빔"
    if value >= th["p75"]:
        return "붐빔"
    return "보통"
