from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.session_boundary import (
    is_valid_intraday_candle,
    is_valid_intraday_open,
)


IST = ZoneInfo("Asia/Kolkata")


def ts(hour, minute):
    return datetime(2026, 9, 1, hour, minute, tzinfo=IST)


def test_0915_is_valid_open():
    assert is_valid_intraday_open(ts(9, 15)) is True


def test_1530_is_not_a_new_intraday_open():
    assert is_valid_intraday_open(ts(15, 30)) is False


def test_final_5m_candle_is_valid():
    assert is_valid_intraday_candle(ts(15, 25), "5m") is True


def test_1530_5m_candle_is_invalid():
    assert is_valid_intraday_candle(ts(15, 30), "5m") is False


def test_1520_15m_candle_is_invalid_because_it_crosses_session_end():
    assert is_valid_intraday_candle(ts(15, 20), "15m") is False


def test_weekly_requires_separate_semantics():
    with pytest.raises(ValueError, match="Weekly"):
        is_valid_intraday_candle(ts(9, 15), "1W")


def test_naive_timestamp_is_rejected():
    timestamp = datetime(2026, 9, 1, 9, 15)

    with pytest.raises(ValueError, match="timezone-aware"):
        is_valid_intraday_open(timestamp)
