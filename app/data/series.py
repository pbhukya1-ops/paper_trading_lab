"""
Candle-series validation for Paper Trading Lab.

This layer validates the structure of a sequence of completed candles
before the data is passed to analysis, backtesting, or paper simulation.
"""

from collections.abc import Sequence

from .candle import Candle


def validate_candle_series(candles: Sequence[Candle]) -> None:
    """Fail closed if a candle series violates structural rules."""

    if not candles:
        raise ValueError("Candle series cannot be empty")

    expected_timeframe = candles[0].timeframe
    previous_timestamp = None
    seen_timestamps = set()

    for index, candle in enumerate(candles):
        candle.validate()

        if candle.timeframe != expected_timeframe:
            raise ValueError(
                f"Mixed timeframes detected at index {index}: "
                f"{candle.timeframe} != {expected_timeframe}"
            )

        if not candle.completed:
            raise ValueError(
                f"Incomplete candle detected at index {index}"
            )

        if candle.timestamp in seen_timestamps:
            raise ValueError(
                f"Duplicate candle timestamp: {candle.timestamp}"
            )

        seen_timestamps.add(candle.timestamp)

        if (
            previous_timestamp is not None
            and candle.timestamp <= previous_timestamp
        ):
            raise ValueError(
                "Candle timestamps must be strictly chronological"
            )

        previous_timestamp = candle.timestamp
