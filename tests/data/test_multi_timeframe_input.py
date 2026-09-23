from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.candle import Candle
from app.data.multi_timeframe_input import MultiTimeframeInput


IST = ZoneInfo("Asia/Kolkata")


def make_candle(timeframe="5m", minute=15, close=100.0):
    return Candle(
        timestamp=datetime(2026, 9, 21, 9, minute, tzinfo=IST),
        open=99.0,
        high=101.0,
        low=98.0,
        close=close,
        volume=1000.0,
        timeframe=timeframe,
        completed=True,
    )


def test_valid_single_timeframe_input():
    candles = [
        make_candle("5m", 15),
        make_candle("5m", 20),
    ]

    result = MultiTimeframeInput(
        candles_by_timeframe={"5m": candles}
    )

    result.validate()


def test_valid_multiple_timeframe_input():
    result = MultiTimeframeInput(
        candles_by_timeframe={
            "5m": [
                make_candle("5m", 15),
                make_candle("5m", 20),
            ],
            "10m": [
                make_candle("10m", 15),
                make_candle("10m", 25),
            ],
        }
    )

    result.validate()


def test_rejects_empty_input():
    result = MultiTimeframeInput(candles_by_timeframe={})

    with pytest.raises(ValueError, match="cannot be empty"):
        result.validate()


def test_rejects_unsupported_timeframe_key():
    result = MultiTimeframeInput(
        candles_by_timeframe={
            "1m": [make_candle("1m", 15)]
        }
    )

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        result.validate()


def test_rejects_empty_series():
    result = MultiTimeframeInput(
        candles_by_timeframe={
            "5m": []
        }
    )

    with pytest.raises(ValueError, match="Candle series cannot be empty"):
        result.validate()


def test_rejects_key_and_candle_timeframe_mismatch():
    result = MultiTimeframeInput(
        candles_by_timeframe={
            "5m": [make_candle("10m", 15)]
        }
    )

    with pytest.raises(ValueError, match="Timeframe key 5m does not match"):
        result.validate()


def test_rejects_invalid_candle_series():
    candles = [
        make_candle("5m", 15),
        make_candle("5m", 20),
        make_candle("5m", 20),
    ]

    result = MultiTimeframeInput(
        candles_by_timeframe={"5m": candles}
    )

    with pytest.raises(ValueError, match="Duplicate candle timestamp"):
        result.validate()


def test_rejects_intraday_candle_starting_at_session_end():
    candle = Candle(
        timestamp=datetime(2026, 9, 21, 15, 30, tzinfo=IST),
        open=99.0,
        high=101.0,
        low=98.0,
        close=100.0,
        volume=1000.0,
        timeframe="5m",
        completed=True,
    )

    result = MultiTimeframeInput(
        candles_by_timeframe={
            "5m": [candle]
        }
    )

    with pytest.raises(ValueError, match="Invalid intraday candle boundary"):
        result.validate()
