from datetime import date
from olpark.calendar_kr import day_type


def test_day_type():
    assert day_type(date(2025, 7, 30)) == "weekday"
    assert day_type(date(2025, 8, 2)) == "sat"
    assert day_type(date(2025, 8, 3)) == "sun_hol"
    assert day_type(date(2025, 8, 15)) == "sun_hol"
    assert day_type(date(2025, 6, 4), "임시공휴일") == "sun_hol"
