from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.exchange_calendar import (
    is_market_open,
    is_trading_day,
    next_trading_day,
)


IST = ZoneInfo("Asia/Kolkata")


def test_weekday_is_trading_day_under_initial_calendar_rule():
    assert is_trading_day(date(2026, 9, 21)) is True


def test_saturday_is_not_trading_day():
    assert is_trading_day(date(2026, 9, 19)) is False


def test_market_open_during_session():
    timestamp = datetime(2026, 9, 21, 10, 0, tzinfo=IST)

    assert is_market_open(timestamp) is True


def test_market_closed_at_session_end():
    timestamp = datetime(2026, 9, 21, 15, 30, tzinfo=IST)

    assert is_market_open(timestamp) is False


def test_market_closed_on_weekend():
    timestamp = datetime(2026, 9, 19, 10, 0, tzinfo=IST)

    assert is_market_open(timestamp) is False


def test_next_trading_day_skips_weekend():
    assert next_trading_day(date(2026, 9, 18)).isoformat() == "2026-09-21"


def test_naive_market_timestamp_is_rejected():
    timestamp = datetime(2026, 9, 21, 10, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        is_market_open(timestamp)
