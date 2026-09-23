from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.session import (
    MARKET_TIMEZONE,
    SESSION_END,
    SESSION_START,
    is_within_session,
    minutes_from_session_start,
    session_date,
    to_market_timezone,
)


IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")


def test_market_timezone_is_asia_kolkata():
    assert str(MARKET_TIMEZONE) == "Asia/Kolkata"


def test_session_start_and_end():
    assert SESSION_START.hour == 9
    assert SESSION_START.minute == 15
    assert SESSION_END.hour == 15
    assert SESSION_END.minute == 30


def test_timezone_conversion():
    timestamp = datetime(2026, 9, 1, 3, 45, tzinfo=UTC)

    converted = to_market_timezone(timestamp)

    assert converted.hour == 9
    assert converted.minute == 15
    assert str(converted.tzinfo) == "Asia/Kolkata"


def test_naive_timestamp_is_rejected():
    timestamp = datetime(2026, 9, 1, 9, 15)

    with pytest.raises(ValueError, match="timezone-aware"):
        to_market_timezone(timestamp)


def test_session_start_is_inside_session():
    timestamp = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    assert is_within_session(timestamp) is True


def test_session_end_is_inside_session_under_current_contract():
    timestamp = datetime(2026, 9, 1, 15, 30, tzinfo=IST)

    assert is_within_session(timestamp) is True


def test_before_session_is_outside():
    timestamp = datetime(2026, 9, 1, 9, 14, tzinfo=IST)

    assert is_within_session(timestamp) is False


def test_after_session_is_outside():
    timestamp = datetime(2026, 9, 1, 15, 31, tzinfo=IST)

    assert is_within_session(timestamp) is False


def test_session_date_uses_market_timezone():
    timestamp = datetime(2026, 8, 31, 20, 0, tzinfo=UTC)

    assert session_date(timestamp).isoformat() == "2026-09-01"


def test_minutes_from_session_start():
    timestamp = datetime(2026, 9, 1, 10, 15, tzinfo=IST)

    assert minutes_from_session_start(timestamp) == 60


def test_minutes_from_session_start_rejects_outside_session():
    timestamp = datetime(2026, 9, 1, 9, 14, tzinfo=IST)

    with pytest.raises(ValueError, match="outside"):
        minutes_from_session_start(timestamp)
