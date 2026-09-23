"""
Intraday timeframe boundary validation.

This module checks whether timestamps align to the 09:15 market-session
anchor for supported intraday timeframes.

It does not resample or fetch market data.
"""

from datetime import datetime

from .session import minutes_from_session_start
from .timeframes import get_timeframe


def is_valid_intraday_boundary(
    timestamp: datetime,
    timeframe: str,
) -> bool:
    """
    Return True when timestamp is aligned to the session anchor.

    Weekly candles are intentionally excluded because their boundary
    semantics are different from intraday candles.
    """

    spec = get_timeframe(timeframe)

    if spec.is_weekly:
        raise ValueError(
            "Weekly timeframe requires separate calendar/session semantics"
        )

    elapsed = minutes_from_session_start(timestamp)

    return elapsed % spec.minutes == 0


def validate_intraday_boundary(
    timestamp: datetime,
    timeframe: str,
) -> None:
    """Fail closed when an intraday timestamp is misaligned."""

    if not is_valid_intraday_boundary(timestamp, timeframe):
        raise ValueError(
            f"Timestamp {timestamp} is not aligned to {timeframe} "
            "from the 09:15 session anchor"
        )
