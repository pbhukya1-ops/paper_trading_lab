"""
Fair Value Gap (FVG) analysis foundations for Paper Trading Lab.

This module detects three-candle price-imbalance structures.

FVG detection is descriptive market analysis only.
It does not generate trading signals or place orders.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FairValueGap:
    lower: float
    upper: float
    gap_type: str
    first_candle_index: int
    middle_candle_index: int
    third_candle_index: int

    def validate(self) -> None:
        if self.lower <= 0:
            raise ValueError("FVG lower bound must be greater than zero")

        if self.upper <= 0:
            raise ValueError("FVG upper bound must be greater than zero")

        if self.lower >= self.upper:
            raise ValueError(
                "FVG lower bound must be strictly below upper bound"
            )

        if self.gap_type not in {"BULLISH_FVG", "BEARISH_FVG"}:
            raise ValueError(
                f"Unsupported FVG type: {self.gap_type}"
            )

        if self.first_candle_index < 0:
            raise ValueError(
                "First candle index cannot be negative"
            )

        if self.middle_candle_index <= self.first_candle_index:
            raise ValueError(
                "Middle candle index must follow first candle index"
            )

        if self.third_candle_index <= self.middle_candle_index:
            raise ValueError(
                "Third candle index must follow middle candle index"
            )


def detect_fvg(
    highs: list[float],
    lows: list[float],
    index: int,
) -> FairValueGap | None:
    """
    Detect a three-candle FVG ending at `index`.

    Bullish FVG:
        low[index] > high[index - 2]

    Bearish FVG:
        high[index] < low[index - 2]

    The middle candle is the displacement candle.

    No trading signal is generated.
    """
    if len(highs) != len(lows):
        raise ValueError("Highs and lows must have equal length")

    if not highs:
        raise ValueError("Price input cannot be empty")

    if any(value <= 0 for value in highs):
        raise ValueError("High values must be greater than zero")

    if any(value <= 0 for value in lows):
        raise ValueError("Low values must be greater than zero")

    if index < 0:
        raise ValueError("Index cannot be negative")

    if index >= len(highs):
        raise ValueError("Index is outside the price series")

    if index < 2:
        return None

    first_high = float(highs[index - 2])
    first_low = float(lows[index - 2])
    third_high = float(highs[index])
    third_low = float(lows[index])

    if third_low > first_high:
        gap = FairValueGap(
            lower=first_high,
            upper=third_low,
            gap_type="BULLISH_FVG",
            first_candle_index=index - 2,
            middle_candle_index=index - 1,
            third_candle_index=index,
        )
        gap.validate()
        return gap

    if third_high < first_low:
        gap = FairValueGap(
            lower=third_high,
            upper=first_low,
            gap_type="BEARISH_FVG",
            first_candle_index=index - 2,
            middle_candle_index=index - 1,
            third_candle_index=index,
        )
        gap.validate()
        return gap

    return None


def detect_all_fvgs(
    highs: list[float],
    lows: list[float],
) -> list[FairValueGap]:
    """
    Detect all FVGs in chronological order.

    No trading signal is generated.
    """
    if len(highs) != len(lows):
        raise ValueError("Highs and lows must have equal length")

    if not highs:
        raise ValueError("Price input cannot be empty")

    result: list[FairValueGap] = []

    for index in range(2, len(highs)):
        gap = detect_fvg(
            highs=highs,
            lows=lows,
            index=index,
        )

        if gap is not None:
            result.append(gap)

    return result
