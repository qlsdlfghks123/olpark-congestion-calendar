from pathlib import Path
from pandas import Timestamp
from olpark.load import load_linked

FIXTURE = str(Path(__file__).parent / "fixtures" / "linked_small.csv")


def test_clean_flag_excludes_aug_sep_and_after_nov8():
    df = load_linked(FIXTURE)
    assert df.set_index("dt")["clean"].to_dict() == {
        Timestamp("2025-07-31 10:00"): True,
        Timestamp("2025-08-01 10:00"): False,
        Timestamp("2025-10-01 10:00"): True,
        Timestamp("2025-11-07 23:00"): False,
        Timestamp("2025-11-08 00:00"): False,
    }


def test_no_visitor_column():
    cols = load_linked(FIXTURE).columns
    assert "방문객" not in cols and "visitors" not in cols


def test_english_columns_and_types():
    df = load_linked(FIXTURE)
    for c in ["dt", "parking", "temp", "wind", "rain", "humidity", "holiday", "show", "audience", "clean"]:
        assert c in df.columns
    assert df["audience"].dtype.kind == "i"
    assert df["parking"].dtype.kind == "i"
