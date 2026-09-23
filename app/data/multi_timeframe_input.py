"""
Multi-timeframe raw-input contract for Paper Trading Lab.

This module stores validated candle sequences for the supported
timeframes.

It does NOT:
- resample candles,
- align candles across timeframes,
- calculate indicators,
- generate trading signals,
- place orders,
- connect to brokers.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .candle import Candle
from .quality_gate import validate_data_quality
from .timeframes import validate_timeframe


@dataclass(frozen=True)
class MultiTimeframeInput:
    """
    Validated raw candle input across one or more supported timeframes.

    The mapping keys are timeframe names and the values are candle
    sequences belonging to those exact timeframes.
    """

    candles_by_timeframe: Mapping[str, Sequence[Candle]]

    def validate(self) -> None:
        if not self.candles_by_timeframe:
            raise ValueError("Multi-timeframe input cannot be empty")

        for timeframe, candles in self.candles_by_timeframe.items():
            validate_timeframe(timeframe)

            if not candles:
                raise ValueError(
                    f"Candle series cannot be empty for timeframe: {timeframe}"
                )

            validate_data_quality(candles)

            actual_timeframe = candles[0].timeframe
            if actual_timeframe != timeframe:
                raise ValueError(
                    f"Timeframe key {timeframe} does not match "
                    f"candle timeframe {actual_timeframe}"
                )
