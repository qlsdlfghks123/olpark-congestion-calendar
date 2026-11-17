"""전체 파이프라인: python -m olpark.build --out site/data"""
import argparse
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from olpark.analog import fit_analog
from olpark.backtest import run_backtest_loo, weather_effect
from olpark.baseline import fit_baseline, level_thresholds
from olpark.calendar_kr import holidays_between
from olpark.export import (current_timetable, project_timetable, write_agency_csv, write_ics, write_json)
from olpark.forecast import forecast, to_blocks
from olpark.load import CLEAN_MONTHS, expand_sessions, load_courses, load_linked, load_schedule
from olpark.overlap import evidence_2025, overlaps

SOURCES = {
    "data": [
        {"name": "한국체육산업개발 올림픽공원 2025 차량입출차, 공연, 날씨정보 등 연계 데이터 (API_CPM_009)",
         "url": "https://www.data.go.kr/data/15164822/openapi.do"},
        {"name": "한국체육산업개발 올림픽수영장 강좌정보 (2026-05-11 기준 파일)",
         "url": "https://www.data.go.kr/data/15101610/fileData.do"},
        {"name": "올림픽공원 홈페이지 공연 일정안내 (앞으로의 공연)",
         "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301010100"},
    ],
    "limits": [
        "2025년 8~9월은 주차대수 수준이 다른 달의 약 1/4로 바뀌어 학습에서 제외했습니다.",
        "2025년 11월 8일 이후 값은 1씩 줄어드는 일련번호 형태라 사용하지 않았습니다.",
        "동2·남2·북2 주차장의 총 주차면 수가 공개되지 않아, 혼잡 수준은 2025년 시간대별 주차대수 분포의 백분위(상위 10%: 매우 붐빔, 상위 25%: 붐빔)로 정했습니다.",
        "강좌 시간표는 공개 파일의 최근 시간표가 예보 기간에도 이어진다고 가정했고, 공휴일에는 수업이 없다고 보았습니다.",
        "저녁(17~22시) 구간은 공연일 붐빔의 절반 정도만 미리 잡아냅니다. 검증 결과는 근거 화면에 있습니다.",
    ],
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site/data")
    ap.add_argument("--linked", default="data/raw/linked_2025.csv")
    ap.add_argument("--courses", default="data/raw/courses_pool.csv")
    ap.add_argument("--schedule", default="data/schedule.csv")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--months", default=",".join(map(str, CLEAN_MONTHS)))
    a = ap.parse_args(argv)
    months = [int(m) for m in a.months.split(",")]
    out = Path(a.out)
    (out / "ics").mkdir(parents=True, exist_ok=True)

    df = load_linked(a.linked)
    courses = load_courses(a.courses)
    sched = load_schedule(a.schedule)
    start = date.fromisoformat(a.start) if a.start else date.today() + timedelta(days=1)
    end = date.fromisoformat(a.end) if a.end else max(sched["date"])

    table, analog, th = fit_baseline(df, months), fit_analog(df, months), level_thresholds(df, months)
    s = sched[(sched["date"] >= start) & (sched["date"] <= end)]
    blocks = to_blocks(forecast(s, start, end, table, analog, th), th)
    write_json(out / "forecast.json", {"generated_at": pd.Timestamp.now(tz="Asia/Seoul").isoformat(timespec="minutes"),
                                       "period": {"start": str(start), "end": str(end)}, "thresholds": th,
                                       "holidays": holidays_between(start, end),
                                       "schedule": s.to_dict("records"), "blocks": blocks.to_dict("records")})

    tt = current_timetable(courses)
    write_json(out / "courses.json", [{"course_no": r.course_no, "name": r.name, "days": r.days,
                                       "optional_days": r.optional_days, "start": f"{r.start:%H:%M}",
                                       "end": f"{r.end:%H:%M}", "capacity": r.capacity, "group": r.group}
                                      for r in tt.itertuples(index=False)])
    ov = overlaps(expand_sessions(project_timetable(tt, start), start, end), blocks)
    write_json(out / "overlaps.json", ov.to_dict("records"))
    write_agency_csv(out / "agency_overlaps.csv", ov)
    for r in tt.itertuples(index=False):
        write_ics(out / "ics" / f"{r.course_no}.ics", r.name, ov[ov["course_no"] == r.course_no])

    metrics = run_backtest_loo(df, months) if len(months) >= 2 else {"skipped": "학습 월이 2개 미만"}
    metrics["weather"] = weather_effect(df, months)
    write_json(out / "metrics.json", metrics)
    write_json(out / "evidence_2025.json", evidence_2025(df, courses, months))
    write_json(out / "sources.json", SOURCES)


if __name__ == "__main__":
    main()
