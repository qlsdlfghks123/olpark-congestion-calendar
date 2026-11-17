"""디자인 목업용 데이터 스냅샷.

빌드 산출물(site/data/*.json)에서 목업 한 화면(달 하나, 강좌 하나)에 필요한 값만 뽑아
snapshot.js로 저장한다. 값은 가공하지 않고 그대로 옮긴다. 서비스 코드와 무관한 디자인 전용 파일.

    python -m olpark.build --out site/data
    python design/preview/make_snapshot.py 2026-12 1013091
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "site" / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main(month: str, course_no: str) -> None:
    fc, courses, overlaps = load("forecast.json"), load("courses.json"), load("overlaps.json")
    course = next(c for c in courses if c["course_no"] == course_no)
    mine = [o for o in overlaps if o["course_no"] == course_no]

    blocks = {}
    for b in fc["blocks"]:
        blocks.setdefault(b["date"], {})[b["block"]] = {
            "level": b["level"],
            "flag": b["show_congestion"],
            "pred": b["pred_max"],
            "base": b["base_max"],
            "titles": b["titles"],
            "fallback": b.get("baseline_month_fallback"),
            "assumed": b.get("assumed_start", False),
        }
    sched = {}
    for s in fc["schedule"]:
        sched.setdefault(s["date"], []).append(
            {"time": s["start_time"], "assumed": s["start_time_assumed"], "venue": s["venue"],
             "size": s["size"], "title": s["title"]})

    flagged_days = sorted({b["date"] for b in fc["blocks"] if b["show_congestion"]})
    snap = {
        "generated_at": fc["generated_at"],
        "period": fc["period"],
        "thresholds": fc["thresholds"],
        "holidays": {h["date"]: h["name"] for h in fc.get("holidays", [])},
        "month": month,
        "course": course,
        "mine": {o["date"]: {"start": o["start_dt"][11:16], "end": o["end_dt"][11:16], "block": o["block"],
                             "level": o["level"], "optional": o["optional"]} for o in mine},
        "blocks": {d: v for d, v in blocks.items()},
        "schedule": sched,
        "flagged_days": flagged_days,
    }
    out = Path(__file__).with_name("snapshot.js")
    out.write_text("window.SNAP = " + json.dumps(snap, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"wrote {out.name}: {len(blocks)} days, {len(mine)} overlaps for {course['name']}")


if __name__ == "__main__":
    main(*(sys.argv[1:3] if len(sys.argv) >= 3 else ("2026-12", "1013091")))
