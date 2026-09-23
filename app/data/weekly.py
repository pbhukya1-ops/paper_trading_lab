"""
Weekly candle calendar contract.

Structural convention for the research pipeline:

    Weekly OPEN  = Monday 09:15 Asia/Kolkata
    Weekly CLOSE = Friday 15:30 Asia/Kolkata

This module does not fetch market data and does not determine exchange
holidays. Holiday-aware completeness will be handled by a later
exchange-calendar layer.
"""

from datetime import date, datetime, time, timedelta

from .session import MARKET_TIMEZONE


WEEKLY_OPEN_TIME = time(9, 15)
WEEKLY_CLOSE_TIME = time(15, 30)


def weekly_open_date(day: date) -> date:
    """Return the Monday belonging to the calendar week containing day."""
    return day - timedelta(days=day.weekday())


def is_valid_weekly_open(timestamp: datetime) -> bool:
    """
    Return True when timestamp is the canonical weekly opening timestamp.

    Canonical weekly opening:
        Monday 09:15 Asia/Kolkata
    """

    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    local = timestamp.astimezone(MARKET_TIMEZONE)

    return (
        local.weekday() == 0
        and local.time() == WEEKLY_OPEN_TIME
    )


def weekly_interval(timestamp: datetime) -> tuple[datetime, datetime]:
    """
    Return the structural weekly [open, close) interval.

    The input must be the canonical Monday 09:15 weekly timestamp.
    """

    if not is_valid_weekly_open(timestamp):
        raise ValueError(
            "Weekly timestamp must be Monday 09:15 Asia/Kolkata"
        )

    local = timestamp.astimezone(MARKET_TIMEZONE)

    days_to_friday = 4 - local.weekday()
    friday = local.date() + timedelta(days=days_to_friday)

    close = datetime.combine(
        friday,
        WEEKLY_CLOSE_TIME,
        tzinfo=MARKET_TIMEZONE,
    )

    return local, close


def is_structurally_complete_week(
    timestamp: datetime,
    as_of: datetime,
) -> bool:
    """
    Return True when the structural weekly close has passed.

    This is NOT holiday-aware. Exchange-calendar validation is intentionally
    deferred to a later layer.
    """

    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")

    start, close = weekly_interval(timestamp)

    current = as_of.astimezone(MARKET_TIMEZONE)

    return current >= close
