from datetime import date
from olpark.calendar_kr import day_type


def test_day_type():
    assert day_type(date(2025, 7, 30)) == "weekday"
    assert day_type(date(2025, 8, 2)) == "sat"
    assert day_type(date(2025, 8, 3)) == "sun_hol"
    assert day_type(date(2025, 8, 15)) == "sun_hol"
    assert day_type(date(2025, 6, 4), "임시공휴일") == "sun_hol"


def test_missing_holiday_value_is_not_a_holiday():
    assert day_type(date(2025, 7, 30), float("nan")) == "weekday"
    assert day_type(date(2025, 7, 30), "") == "weekday"


def test_holidays_between_lists_named_days_in_range():
    from olpark.calendar_kr import holidays_between
    got = holidays_between(date(2026, 12, 20), date(2027, 1, 31))
    assert [h["date"] for h in got] == ["2026-12-25", "2027-01-01"]
    assert all(isinstance(h["name"], str) and h["name"] for h in got)
