"""
Intraday session-boundary contract.

Candle timestamps represent OPEN timestamps.

Therefore:
    session start = 09:15 inclusive
    session end   = 15:30 exclusive

A candle may start at 15:25, but a new intraday candle may NOT
start at 15:30.

This module does not fetch data, resample candles, or perform
strategy/execution logic.
"""

from datetime import datetime

from .session import MARKET_TIMEZONE, SESSION_START, SESSION_END
from .timeframes import get_timeframe


def is_valid_intraday_open(timestamp: datetime) -> bool:
    """
    Return True when an intraday candle OPEN timestamp is inside
    the defined session.

    Session interval:
        [09:15, 15:30)
    """

    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    local = timestamp.astimezone(MARKET_TIMEZONE)
    current = local.time()

    return SESSION_START <= current < SESSION_END


def is_valid_intraday_candle(
    timestamp: datetime,
    timeframe: str,
) -> bool:
    """
    Validate that a candle's opening timestamp is inside the session
    and that the complete candle does not extend beyond 15:30.
    """

    spec = get_timeframe(timeframe)

    if spec.is_weekly:
        raise ValueError(
            "Weekly candles require separate calendar/session semantics"
        )

    if not is_valid_intraday_open(timestamp):
        return False

    local = timestamp.astimezone(MARKET_TIMEZONE)

    elapsed_minutes = (
        local.hour * 60
        + local.minute
        - (SESSION_START.hour * 60 + SESSION_START.minute)
    )

    return elapsed_minutes + spec.minutes <= (
        SESSION_END.hour * 60 + SESSION_END.minute
        - (SESSION_START.hour * 60 + SESSION_START.minute)
    )
