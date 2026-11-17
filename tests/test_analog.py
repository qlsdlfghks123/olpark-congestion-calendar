import pandas as pd
from olpark.analog import fit_analog, analog_for
from tests.helpers import make_df


def _df():
    rows = []
    # three single-show Saturdays (L) in Feb 2025: 1, 8, 15 — parking 2000 at start (19h)
    for d in ("2025-02-01", "2025-02-08", "2025-02-15"):
        for h in range(12, 24):
            show = "공연" + d if h >= 19 else None
            rows.append((f"{d} {h}:00", 2000 if h == 19 else 500, show, 20000 if show else 0))
    return make_df(rows)


def test_fit_analog_median_by_size_wk_offset():
    prof = fit_analog(_df(), [2])
    cell = prof[(prof["size"] == "L") & (prof.wk == "we") & (prof.offset == 0)]
    assert cell.park.item() == 2000 and cell.n.item() == 3


def test_analog_for_falls_back_to_smaller_size_same_wk():
    prof = pd.DataFrame({"size": ["M"], "wk": ["we"], "offset": [0], "park": [1500.0], "n": [4]})
    assert analog_for(prof, "L", "we", 0) == 1500.0
    assert analog_for(prof, "L", "wd", 0) is None


def test_analog_for_ignores_sparse_cells():
    prof = pd.DataFrame({"size": ["L"], "wk": ["we"], "offset": [0], "park": [3000.0], "n": [2]})
    assert analog_for(prof, "L", "we", 0) is None


def test_analog_for_outside_window_is_none():
    prof = fit_analog(_df(), [2])
    assert analog_for(prof, "L", "we", 4) is None
