"""
Canonical timeframe definitions for Paper Trading Lab.

This module defines the project's supported timeframe vocabulary.
It does not fetch data or perform resampling.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeframeSpec:
    name: str
    minutes: int | None
    is_weekly: bool = False


TIMEFRAMES = {
    "5m": TimeframeSpec("5m", 5),
    "10m": TimeframeSpec("10m", 10),
    "15m": TimeframeSpec("15m", 15),
    "30m": TimeframeSpec("30m", 30),
    "1W": TimeframeSpec("1W", None, is_weekly=True),
}


def get_timeframe(name: str) -> TimeframeSpec:
    """Return the canonical specification for a supported timeframe."""

    try:
        return TIMEFRAMES[name]
    except KeyError:
        raise ValueError(f"Unsupported timeframe: {name}") from None


def validate_timeframe(name: str) -> None:
    """Fail closed when an unsupported timeframe is requested."""

    get_timeframe(name)
