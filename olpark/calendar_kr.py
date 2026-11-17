"""날짜 유형 판정: 평일 / 토요일 / 일요일·공휴일."""
from datetime import date

import holidays

_KR = holidays.KR(years=range(2024, 2029))


def _is_named(holiday_name) -> bool:
    return isinstance(holiday_name, str) and holiday_name.strip() != ""


def day_type(d: date, holiday_name: str | None = None) -> str:
    if _is_named(holiday_name) or d in _KR or d.weekday() == 6:
        return "sun_hol"
    if d.weekday() == 5:
        return "sat"
    return "weekday"
