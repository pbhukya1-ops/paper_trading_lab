"""
Session and timeframe-alignment contract.

This module defines deterministic session semantics for the paper-trading
research pipeline. It does not fetch broker data or place orders.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("Asia/Kolkata")
SESSION_START = time(9, 15)
SESSION_END = time(15, 30)


def to_market_timezone(timestamp: datetime) -> datetime:
    """Convert an aware timestamp to the canonical market timezone."""

    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    return timestamp.astimezone(MARKET_TIMEZONE)


def is_within_session(timestamp: datetime) -> bool:
    """Return True when the timestamp falls within the intraday session."""

    local = to_market_timezone(timestamp)
    current = local.time()

    return SESSION_START <= current <= SESSION_END


def session_date(timestamp: datetime):
    """Return the market-session calendar date."""

    return to_market_timezone(timestamp).date()


def minutes_from_session_start(timestamp: datetime) -> int:
    """
    Return elapsed whole minutes from the 09:15 session anchor.

    This is intended for intraday timeframe-alignment checks.
    """

    local = to_market_timezone(timestamp)

    if not is_within_session(local):
        raise ValueError("Timestamp is outside the defined market session")

    return (
        (local.hour * 60 + local.minute)
        - (SESSION_START.hour * 60 + SESSION_START.minute)
    )
