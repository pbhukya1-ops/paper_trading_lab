from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.candle import Candle


IST = ZoneInfo("Asia/Kolkata")


def make_candle(**overrides):
    values = {
        "timestamp": datetime(2026, 9, 1, 9, 15, tzinfo=IST),
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


def test_valid_candle_passes_validation():
    make_candle().validate()


def test_naive_timestamp_is_rejected():
    candle = make_candle(timestamp=datetime(2026, 9, 1, 9, 15))

    with pytest.raises(ValueError, match="timezone-aware"):
        candle.validate()


def test_invalid_timeframe_is_rejected():
    candle = make_candle(timeframe="1m")

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        candle.validate()


def test_high_below_open_is_rejected():
    candle = make_candle(high=99.0)

    with pytest.raises(ValueError, match="High is below"):
        candle.validate()


def test_low_above_close_is_rejected():
    candle = make_candle(low=104.0)

    with pytest.raises(ValueError, match="Low is above"):
        candle.validate()


def test_negative_volume_is_rejected():
    candle = make_candle(volume=-1.0)

    with pytest.raises(ValueError, match="Volume"):
        candle.validate()


def test_incomplete_candle_is_rejected():
    candle = make_candle(completed=False)

    with pytest.raises(ValueError, match="Incomplete"):
        candle.validate()


def test_candle_is_immutable():
    candle = make_candle()

    with pytest.raises(AttributeError):
        candle.close = 200.0
