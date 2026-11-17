"""원천 데이터 읽기와 정제."""
import pandas as pd

CLEAN_MONTHS = [1, 2, 3, 4, 5, 6, 7, 10]
CUTOFF = pd.Timestamp("2025-11-08 00:00")

_RENAME = {
    "주차대수": "parking", "기온": "temp", "풍향": "wind", "강수량": "rain",
    "습도": "humidity", "휴일": "holiday", "공연명": "show", "공연관람객수": "audience",
}


def _none_if_blank(v):
    if pd.isna(v) or str(v).strip() == "":
        return None
    return str(v).strip()


def load_linked(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    df = raw.rename(columns=_RENAME)[["dt", *_RENAME.values()]].copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df["parking"] = pd.to_numeric(df["parking"], errors="coerce").fillna(0).astype(int)
    for c in ["temp", "wind", "rain", "humidity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["audience"] = pd.to_numeric(df["audience"], errors="coerce").fillna(0).astype(int)
    df["holiday"] = df["holiday"].map(_none_if_blank)
    df["show"] = df["show"].map(_none_if_blank)
    df["clean"] = df["dt"].dt.month.isin(CLEAN_MONTHS) & (df["dt"] < CUTOFF)
    return df.sort_values("dt").reset_index(drop=True)
