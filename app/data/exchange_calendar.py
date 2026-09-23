"""
Exchange calendar abstraction for Paper Trading Lab.

This module defines the market-session calendar contract.
It is intentionally independent of any broker API.
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("Asia/Kolkata")

SESSION_START = time(9, 15)
SESSION_END = time(15, 30)


def to_market_timezone(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    return timestamp.astimezone(MARKET_TIMEZONE)


def is_trading_day(day: date) -> bool:
    """
    Initial calendar rule:
    Monday-Friday are trading days.

    Exchange holidays are intentionally not handled here yet.
    """
    return day.weekday() < 5


def is_market_open(timestamp: datetime) -> bool:
    """
    Return True only when timestamp is inside the defined
    intraday market session.
    """
    local = to_market_timezone(timestamp)

    if not is_trading_day(local.date()):
        return False

    return SESSION_START <= local.time() < SESSION_END


def next_trading_day(day: date) -> date:
    candidate = day + timedelta(days=1)

    while not is_trading_day(candidate):
        candidate += timedelta(days=1)

    return candidate
