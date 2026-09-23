from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.data.candle import Candle
from app.data.quality_gate import validate_data_quality


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


def test_valid_intraday_data_passes_quality_gate():
    start = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=5)),
        make_candle(start + timedelta(minutes=10)),
    ]

    validate_data_quality(candles)


def test_candle_crossing_session_end_fails_quality_gate():
    timestamp = datetime(2026, 9, 1, 15, 27, tzinfo=IST)

    candles = [make_candle(timestamp)]

    with pytest.raises(ValueError, match="Invalid intraday candle boundary"):
        validate_data_quality(candles)


def test_duplicate_candle_fails_quality_gate():
    timestamp = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(timestamp),
        make_candle(timestamp),
    ]

    with pytest.raises(ValueError, match="Duplicate"):
        validate_data_quality(candles)


def test_mixed_timeframes_fail_quality_gate():
    start = datetime(2026, 9, 1, 9, 15, tzinfo=IST)

    candles = [
        make_candle(start, timeframe="5m"),
        make_candle(
            start + timedelta(minutes=5),
            timeframe="10m",
        ),
    ]

    with pytest.raises(ValueError, match="Mixed timeframes"):
        validate_data_quality(candles)


def test_weekly_data_uses_weekly_semantics():
    start = datetime(2026, 9, 7, 9, 15, tzinfo=IST)

    candle = make_candle(
        start,
        timeframe="1W",
    )

    validate_data_quality([candle])
