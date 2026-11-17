import pandas as pd


def make_df(rows):
    """rows: list of (dt_str, parking, show, audience). Returns a load_linked-shaped frame."""
    df = pd.DataFrame(rows, columns=["dt", "parking", "show", "audience"])
    df["dt"] = pd.to_datetime(df["dt"])
    for c in ["temp", "wind", "rain", "humidity"]:
        df[c] = float("nan")
    df["holiday"] = None
    df["clean"] = True
    return df
