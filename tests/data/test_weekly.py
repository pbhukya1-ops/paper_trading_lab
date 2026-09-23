from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.weekly import (
    is_structurally_complete_week,
    is_valid_weekly_open,
    weekly_interval,
    weekly_open_date,
)


IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")


def test_weekly_open_date_returns_monday():
    assert weekly_open_date(date(2026, 9, 16)).isoformat() == "2026-09-14"


def test_valid_weekly_open_is_monday_0915():
    timestamp = datetime(2026, 9, 14, 9, 15, tzinfo=IST)

    assert is_valid_weekly_open(timestamp) is True


def test_non_monday_weekly_open_is_invalid():
    timestamp = datetime(2026, 9, 15, 9, 15, tzinfo=IST)

    assert is_valid_weekly_open(timestamp) is False


def test_weekly_interval_ends_friday_1530():
    timestamp = datetime(2026, 9, 14, 9, 15, tzinfo=IST)

    start, close = weekly_interval(timestamp)

    assert start == timestamp
    assert close == datetime(2026, 9, 18, 15, 30, tzinfo=IST)


def test_weekly_interval_rejects_invalid_timestamp():
    timestamp = datetime(2026, 9, 15, 9, 15, tzinfo=IST)

    with pytest.raises(ValueError, match="Monday"):
        weekly_interval(timestamp)


def test_structurally_complete_week_before_close_is_false():
    start = datetime(2026, 9, 14, 9, 15, tzinfo=IST)
    as_of = datetime(2026, 9, 18, 15, 29, tzinfo=IST)

    assert is_structurally_complete_week(start, as_of) is False


def test_structurally_complete_week_at_close_is_true():
    start = datetime(2026, 9, 14, 9, 15, tzinfo=IST)
    as_of = datetime(2026, 9, 18, 15, 30, tzinfo=IST)

    assert is_structurally_complete_week(start, as_of) is True


def test_naive_as_of_is_rejected():
    start = datetime(2026, 9, 14, 9, 15, tzinfo=IST)
    as_of = datetime(2026, 9, 18, 15, 30)

    with pytest.raises(ValueError, match="timezone-aware"):
        is_structurally_complete_week(start, as_of)
