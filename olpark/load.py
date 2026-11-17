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
    df["holiday"] = pd.Series([_none_if_blank(v) for v in df["holiday"]], index=df.index, dtype=object)
    df["show"] = pd.Series([_none_if_blank(v) for v in df["show"]], index=df.index, dtype=object)
    df["clean"] = df["dt"].dt.month.isin(CLEAN_MONTHS) & (df["dt"] < CUTOFF)
    return df.sort_values("dt").reset_index(drop=True)


# ---------- 강좌정보 ----------
import holidays as _holidays  # noqa: E402

_KR_HOLIDAYS = _holidays.KR(years=range(2024, 2029))
_DAY = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}


def parse_days(text: str) -> tuple[list[int], list[int]]:
    """'월,수,금,(토)' -> ([0,2,4],[5]). 괄호로 감싼 요일은 선택 수업, '금(방)'처럼 뒤에 붙은 괄호 표기는 무시."""
    days, optional = [], []
    for tok in str(text).split(","):
        tok = tok.strip()
        if not tok:
            continue
        if tok.startswith("(") and len(tok) >= 2 and tok[1] in _DAY:
            optional.append(_DAY[tok[1]])
        elif tok[0] in _DAY:
            days.append(_DAY[tok[0]])
    return sorted(set(days)), sorted(set(optional) - set(days))


def _parse_time(s: str):
    return pd.to_datetime(s.strip(), format="%H:%M").time()


def load_courses(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path, encoding="cp949", dtype=str).fillna("")
    out = pd.DataFrame()
    out["course_no"] = raw["강좌번호"].str.strip()
    out["sub_no"] = raw["강좌서브번호"].str.strip()
    out["month"] = pd.to_datetime(raw["시작월"]).dt.to_period("M")
    out["name"] = raw["강좌명"].str.strip().str.replace(r"\s+", " ", regex=True)
    se = raw["시작종료시간"].str.split("~", expand=True)
    out["start"] = se[0].map(_parse_time)
    out["end"] = se[1].map(_parse_time)
    out["capacity"] = pd.to_numeric(raw["정원"], errors="coerce").fillna(0).astype(int)
    parsed = raw["요일"].map(parse_days)
    out["days"] = parsed.map(lambda p: p[0])
    out["optional_days"] = parsed.map(lambda p: p[1])
    out["group"] = raw["강습반"].str.strip()
    out["fee"] = pd.to_numeric(raw["강좌금액"], errors="coerce").fillna(0).astype(int)
    per = raw["시작일자"].str.split("~", expand=True)
    out["period_start"] = pd.to_datetime(per[0]).dt.date
    end = per[1].str.strip()
    out["period_end"] = [None if e.startswith("9999") else pd.to_datetime(e).date() for e in end]
    return out


MAX_CLASS_MINUTES = 180  # 이보다 길면 시간제 수업이 아니라 자유이용권(헬스 등)으로 본다


def is_timed_class(start, end) -> bool:
    minutes = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
    return 0 < minutes <= MAX_CLASS_MINUTES


def expand_sessions(courses: pd.DataFrame, start, end) -> pd.DataFrame:
    rows = []
    for c in courses.itertuples(index=False):
        if not is_timed_class(c.start, c.end):
            continue
        lo = max(start, c.period_start)
        if c.period_end is None:
            hi = end
        else:
            month_end = (c.month.to_timestamp(how="end")).date()
            hi = min(end, c.period_end, month_end)
            lo = max(lo, c.month.to_timestamp().date())
        if lo > hi:
            continue
        for d in pd.date_range(lo, hi, freq="D"):
            wd = d.dayofweek
            if d.date() in _KR_HOLIDAYS:
                continue
            if wd in c.days or wd in c.optional_days:
                rows.append({
                    "course_no": c.course_no, "name": c.name, "date": d.date(),
                    "start_dt": pd.Timestamp.combine(d.date(), c.start),
                    "end_dt": pd.Timestamp.combine(d.date(), c.end),
                    "capacity": c.capacity, "optional": wd in c.optional_days,
                })
    cols = ["course_no", "name", "date", "start_dt", "end_dt", "capacity", "optional"]
    return (pd.DataFrame(rows, columns=cols)
            .drop_duplicates(["course_no", "start_dt"]).reset_index(drop=True))


def latest_timetable(courses: pd.DataFrame) -> pd.DataFrame:
    return (courses.sort_values(["course_no", "month", "sub_no"])
            .groupby("course_no", as_index=False).tail(1).reset_index(drop=True))


# ---------- 앞으로의 공연 일정 ----------
VENUE_DEFAULT_SIZE = {"KSPO DOME": "L", "티켓링크 라이브 아레나": "M", "핸드볼경기장": "M"}
ASSUMED_START = "19:00"


def load_schedule(path: str) -> pd.DataFrame:
    from olpark.events import size_of
    raw = pd.read_csv(path, dtype=str).fillna("")
    rows = []
    for r in raw.itertuples(index=False):
        if "~" in r.date:
            a, b = (x.strip() for x in r.date.split("~"))
            dates = [d.date() for d in pd.date_range(a, b, freq="D")]
        else:
            dates = [pd.to_datetime(r.date.strip()).date()]
        assumed = r.start_time.strip() == ""
        hh = int((ASSUMED_START if assumed else r.start_time.strip()).split(":")[0])
        aud = pd.to_numeric(r.expected_audience, errors="coerce")
        size = size_of(aud) if pd.notna(aud) else VENUE_DEFAULT_SIZE.get(r.venue.strip(), "S")
        for d in dates:
            rows.append({"date": d, "start_hour": hh, "start_time": "" if assumed else r.start_time.strip(),
                         "start_time_assumed": assumed, "venue": r.venue.strip(), "title": r.title.strip(),
                         "size": size, "source": r.source.strip()})
    return pd.DataFrame(rows)
