"""
Canonical candle timestamp and interval contract.

The timestamp of a candle is its OPENING timestamp.

A candle labelled 09:15 represents the interval:
    [09:15, 09:20)

The closing boundary is exclusive.

This contract is intentionally independent of market-data fetching,
resampling, indicators, strategy logic, and order execution.
"""

from datetime import datetime, timedelta

from .timeframes import get_timeframe


def candle_interval(
    timestamp: datetime,
    timeframe: str,
) -> tuple[datetime, datetime]:
    """
    Return the [open, close) interval represented by a candle.

    Weekly candles are intentionally excluded until their calendar
    semantics are defined separately.
    """

    if timestamp.tzinfo is None:
        raise ValueError("Candle timestamp must be timezone-aware")

    spec = get_timeframe(timeframe)

    if spec.is_weekly:
        raise ValueError(
            "Weekly candle interval requires separate calendar semantics"
        )

    close_timestamp = timestamp + timedelta(minutes=spec.minutes)

    return timestamp, close_timestamp


def is_open_timestamp(timestamp: datetime) -> bool:
    """
    Explicitly document the project's timestamp convention.

    Every canonical candle timestamp represents its opening time.
    """
    return timestamp.tzinfo is not None
