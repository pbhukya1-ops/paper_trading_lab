"""
Central data-quality gate for Paper Trading Lab.

Only validated, completed, chronologically ordered candles
may proceed to downstream analysis.
"""

from collections.abc import Sequence

from .candle import Candle
from .series import validate_candle_series
from .session_boundary import is_valid_intraday_candle
from .timeframes import get_timeframe


def validate_data_quality(candles: Sequence[Candle]) -> None:
    """
    Validate a candle series before downstream analysis.

    Raises ValueError when the data violates the project's
    structural, temporal, timeframe, or session contracts.
    """
    validate_candle_series(candles)

    timeframe = candles[0].timeframe
    spec = get_timeframe(timeframe)

    # Weekly candles have separate calendar semantics.
    if spec.is_weekly:
        return

    for index, candle in enumerate(candles):
        if not is_valid_intraday_candle(candle.timestamp, timeframe):
            raise ValueError(
                f"Invalid intraday candle boundary at index {index}: "
                f"{candle.timestamp} ({timeframe})"
            )
