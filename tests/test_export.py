import json
from datetime import date
from pathlib import Path

import pandas as pd
from olpark.export import current_timetable, project_timetable, write_ics, write_agency_csv
from olpark.build import main

FIX = Path(__file__).parent / "fixtures"


def _courses():
    base = {"sub_no": "1", "start": pd.Timestamp("19:00").time(), "end": pd.Timestamp("19:50").time(), "capacity": 10,
            "days": [5], "optional_days": [], "group": "", "fee": 0}
    return pd.DataFrame([
        {**base, "course_no": "old", "name": "옛 강좌", "month": pd.Period("2024-01", "M"),
         "period_start": date(2024, 1, 1), "period_end": date(2024, 1, 31)},
        {**base, "course_no": "new", "name": "현재 강좌", "month": pd.Period("2026-05", "M"),
         "period_start": date(2026, 5, 1), "period_end": date(2026, 5, 31)},
        {**base, "course_no": "open", "name": "무기한 강좌", "month": pd.Period("2026-01", "M"),
         "period_start": date(2026, 1, 1), "period_end": None},
    ])


def test_current_timetable_drops_old_courses():
    assert set(current_timetable(_courses()).course_no) == {"new", "open"}


def test_project_timetable_runs_into_future():
    p = project_timetable(current_timetable(_courses()), date(2026, 12, 1))
    assert (p.period_start == date(2026, 12, 1)).all() and p.period_end.isna().all()


def _ov():
    return pd.DataFrame([{"course_no": "new", "name": "현재 강좌", "date": date(2026, 12, 5),
                          "start_dt": pd.Timestamp("2026-12-05 19:00"), "end_dt": pd.Timestamp("2026-12-05 19:50"),
                          "capacity": 10, "optional": True, "block": "저녁", "level": "매우 붐빔", "excess": 1500.0,
                          "titles": ["A, B; C"], "assumed_start": False}])


def test_ics_is_valid_and_kst(tmp_path):
    p = tmp_path / "new.ics"
    write_ics(p, "현재 강좌", _ov())
    t = p.read_bytes().decode("utf-8")
    assert t.startswith("BEGIN:VCALENDAR\r\n") and t.rstrip().endswith("END:VCALENDAR")
    assert "DTSTART;TZID=Asia/Seoul:20261205T190000" in t
    assert r"A\, B\; C" in t


def test_agency_csv_has_bom_and_korean_header(tmp_path):
    p = tmp_path / "a.csv"
    write_agency_csv(p, _ov())
    raw = p.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    header = raw.decode("utf-8-sig").splitlines()[0]
    assert header == "강좌번호,강좌명,날짜,시작,종료,정원,토요일선택여부,구간,수준,공연증가대수,공연명"


def test_build_writes_all_files(tmp_path):
    main(["--out", str(tmp_path), "--linked", str(FIX / "linked_build.csv"), "--courses", str(FIX / "courses_small.csv"),
          "--schedule", str(FIX / "schedule_small.csv"), "--start", "2026-12-20", "--end", "2027-01-31",
          "--months", "1"])
    names = {p.name for p in tmp_path.iterdir()}
    assert names >= {"forecast.json", "courses.json", "overlaps.json", "agency_overlaps.csv", "metrics.json",
                     "evidence_2025.json", "sources.json", "ics"}
    fc = json.loads((tmp_path / "forecast.json").read_text(encoding="utf-8"))
    assert fc["period"] == {"start": "2026-12-20", "end": "2027-01-31"} and len(fc["blocks"]) == 2 * 43
