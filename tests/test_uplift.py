import pandas as pd
from olpark.uplift import extract_events, fit_uplift, uplift_for, size_of
from olpark.baseline import fit_baseline
from tests.helpers import make_df


def test_event_start_and_size():
    df = make_df([(f"2025-01-20 {h}:00", 500, "공연A", 12000 if h == 20 else 0) for h in range(19, 24)])
    ev = extract_events(df)
    assert len(ev) == 1
    assert ev.iloc[0].start_hour == 19 and ev.iloc[0].audience == 12000 and ev.iloc[0]["size"] == "M"


def test_size_bins():
    assert [size_of(x) for x in (0, 4999, 5000, 14999, 15000)] == ["S", "S", "M", "M", "L"]


def _training_df():
    rows = []
    # three Mondays in Jan without show: 18-20h base 100
    for d in ("2025-01-06", "2025-01-13", "2025-01-20"):
        for h in range(14, 24):
            rows.append((f"{d} {h}:00", 100, None, 0))
    for d in ("2025-01-07", "2025-01-14", "2025-01-21"):
        for h in range(14, 24):
            rows.append((f"{d} {h}:00", 100, None, 0))
    # L shows on Mondays; extra cars 17-21h, show name tagged 19-23h only (as in real data)
    for d in ("2025-02-17", "2025-02-03", "2025-02-10"):
        for h in range(14, 24):
            show = "공연L" + d if h >= 19 else None
            rows.append((f"{d} {h}:00", 100 + (400 if 17 <= h <= 21 else 0), show, 20000 if show else 0))
    return make_df(rows)


def test_uplift_positive_before_start_for_large():
    df = _training_df()
    t = fit_baseline(df, [1, 2])
    prof = fit_uplift(df, t, [1, 2])
    assert uplift_for(prof, "L", -2) == 400 and uplift_for(prof, "L", 0) == 400 and uplift_for(prof, "L", 3) == 0


def test_uplift_offset_window():
    df = _training_df()
    prof = fit_uplift(df, fit_baseline(df, [1, 2]), [1, 2])
    assert uplift_for(prof, "L", 4) == 0 and uplift_for(prof, "L", -5) == 0


def test_sparse_cell_falls_back_to_smaller_size():
    prof = pd.DataFrame({"size": ["S"], "offset": [0], "uplift": [50.0], "n": [5]})
    assert uplift_for(prof, "L", 0) == 50.0
    assert uplift_for(prof, "M", 1) == 0
