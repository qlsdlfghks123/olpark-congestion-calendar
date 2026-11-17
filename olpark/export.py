"""화면용 JSON, 강좌별 ICS, 기관용 CSV."""
import csv
import json
from datetime import date
from pathlib import Path

import pandas as pd

CURRENT_WINDOW_MONTHS = 4  # 파일의 마지막 개설월부터 4개월 이내에 개설된 강좌를 '현재 강좌'로 본다


def current_timetable(courses: pd.DataFrame) -> pd.DataFrame:
    from olpark.load import latest_timetable
    lt = latest_timetable(courses)
    from olpark.load import is_timed_class
    cutoff = courses["month"].max() - CURRENT_WINDOW_MONTHS
    keep = ((lt["month"] >= cutoff) | lt["period_end"].isna()) & pd.Series([is_timed_class(s, e) for s, e in zip(lt["start"], lt["end"])], index=lt.index)
    return lt[keep].reset_index(drop=True)


def project_timetable(timetable: pd.DataFrame, start: date) -> pd.DataFrame:
    """가장 최근 시간표가 예보 기간에도 이어진다고 가정한다."""
    p = timetable.copy()
    p["period_start"] = start
    p["period_end"] = None
    return p


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\;").replace(",", "\\,").replace("\n", "\\n")


def write_ics(path: Path, course_name: str, ov: pd.DataFrame) -> None:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//olpark-congestion-calendar//KO", "CALSCALE:GREGORIAN",
             f"X-WR-CALNAME:{_esc('올림픽공원 공연 혼잡 · ' + course_name)}", "X-WR-TIMEZONE:Asia/Seoul",
             "BEGIN:VTIMEZONE", "TZID:Asia/Seoul", "BEGIN:STANDARD", "DTSTART:19700101T000000",
             "TZOFFSETFROM:+0900", "TZOFFSETTO:+0900", "TZNAME:KST", "END:STANDARD", "END:VTIMEZONE"]
    for r in ov.itertuples(index=False):
        title = ", ".join(r.titles)
        lines += ["BEGIN:VEVENT", f"UID:{r.course_no}-{r.start_dt:%Y%m%dT%H%M}@olpark-congestion-calendar",
                  f"DTSTAMP:{pd.Timestamp.now(tz='UTC'):%Y%m%dT%H%M%SZ}",
                  f"DTSTART;TZID=Asia/Seoul:{r.start_dt:%Y%m%dT%H%M%S}", f"DTEND;TZID=Asia/Seoul:{r.end_dt:%Y%m%dT%H%M%S}",
                  f"SUMMARY:{_esc('올림픽공원 공연 혼잡 예상: ' + title)}",
                  f"DESCRIPTION:{_esc(f'{r.block} {r.level}, 평소보다 약 {round(r.excess)}대 많을 것으로 예상')}",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")


AGENCY_HEADER = ["강좌번호", "강좌명", "날짜", "시작", "종료", "정원", "토요일선택여부", "구간", "수준", "공연증가대수", "공연명"]


def write_agency_csv(path: Path, ov: pd.DataFrame) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(AGENCY_HEADER)
        for r in ov.itertuples(index=False):
            w.writerow([r.course_no, r.name, str(r.date), f"{r.start_dt:%H:%M}", f"{r.end_dt:%H:%M}", r.capacity,
                        "Y" if r.optional else "N", r.block, r.level, round(r.excess), " / ".join(r.titles)])


def _default(o):
    if isinstance(o, (date, pd.Timestamp)):
        return str(o)
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(type(o))


def _clean(o):
    if isinstance(o, float) and o != o:  # NaN
        return None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if hasattr(o, "item") and not isinstance(o, (str, bytes)):
        return _clean(o.item())
    return o


def write_json(path: Path, obj) -> None:
    text = json.dumps(_clean(obj), ensure_ascii=False, indent=1, default=_default, allow_nan=False)
    path.write_text(text, encoding="utf-8")
