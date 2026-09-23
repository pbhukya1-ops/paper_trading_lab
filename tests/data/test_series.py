from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.data.candle import Candle
from app.data.series import validate_candle_series


IST = ZoneInfo("Asia/Kolkata")


def make_candle(timestamp, **overrides):
    values = {
        "timestamp": timestamp,
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 103.0,
        "volume": 1000.0,
        "timeframe": "5m",
        "completed": True,
    }
    values.update(overrides)
    return Candle(**values)


def test_valid_series_passes():
    start = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=5)),
        make_candle(start + timedelta(minutes=10)),
    ]

    validate_candle_series(candles)


def test_empty_series_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_candle_series([])


def test_duplicate_timestamp_is_rejected():
    timestamp = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(timestamp),
        make_candle(timestamp),
    ]

    with pytest.raises(ValueError, match="Duplicate"):
        validate_candle_series(candles)


def test_out_of_order_series_is_rejected():
    start = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=10)),
        make_candle(start + timedelta(minutes=5)),
    ]

    with pytest.raises(ValueError, match="chronological"):
        validate_candle_series(candles)


def test_mixed_timeframes_are_rejected():
    start = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(start, timeframe="5m"),
        make_candle(start + timedelta(minutes=5), timeframe="10m"),
    ]

    with pytest.raises(ValueError, match="Mixed timeframes"):
        validate_candle_series(candles)


def test_incomplete_candle_is_rejected():
    start = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(start),
        make_candle(
            start + timedelta(minutes=5),
            completed=False,
        ),
    ]

    with pytest.raises(ValueError, match="Incomplete"):
        validate_candle_series(candles)
