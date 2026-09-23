"""
Breakout analysis foundations for Paper Trading Lab.

This module detects descriptive price breaks through previously
established structural price levels.

A breakout is based only on observable OHLC price behavior.
Optional volume information can be supplied separately.

This module does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass


VALID_BREAKOUT_TYPES = {
    "BULLISH_BREAKOUT",
    "BEARISH_BREAKOUT",
    "NO_BREAKOUT",
    "INSUFFICIENT_DATA",
}

VALID_CONFIRMATION_TYPES = {
    "CLOSE_CONFIRMED",
    "WICK_ONLY",
    "NO_CONFIRMATION",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True)
class BreakoutEvent:
    """
    Descriptive price-break event.

    level_price:
        Previously established structural price level.

    candle_index:
        Candle where the interaction occurred.

    breakout_type:
        Direction of the observed price break.

    confirmation_type:
        Whether the candle close confirmed the break
        or only the wick crossed the level.
    """

    candle_index: int
    level_index: int
    level_price: float
    breakout_type: str
    confirmation_type: str
    wick_extreme: float
    close_price: float

    def validate(self) -> None:
        if self.candle_index < 0:
            raise ValueError(
                "Candle index cannot be negative"
            )

        if self.level_index < 0:
            raise ValueError(
                "Level index cannot be negative"
            )

        if self.level_index >= self.candle_index:
            raise ValueError(
                "Level index must precede breakout candle"
            )

        if self.level_price <= 0:
            raise ValueError(
                "Level price must be greater than zero"
            )

        if self.wick_extreme <= 0:
            raise ValueError(
                "Wick extreme must be greater than zero"
            )

        if self.close_price <= 0:
            raise ValueError(
                "Close price must be greater than zero"
            )

        if self.breakout_type not in VALID_BREAKOUT_TYPES:
            raise ValueError(
                f"Unsupported breakout type: "
                f"{self.breakout_type}"
            )

        if (
            self.confirmation_type
            not in VALID_CONFIRMATION_TYPES
        ):
            raise ValueError(
                f"Unsupported confirmation type: "
                f"{self.confirmation_type}"
            )


def detect_breakout(
    high: float,
    low: float,
    close: float,
    level_price: float,
    level_type: str,
    candle_index: int,
    level_index: int,
) -> BreakoutEvent:
    """
    Detect an interaction with a previously established level.

    For a HIGH/resistance level:

        close > level
            → BULLISH_BREAKOUT / CLOSE_CONFIRMED

        high > level and close <= level
            → BULLISH_BREAKOUT / WICK_ONLY

        otherwise
            → NO_BREAKOUT / NO_CONFIRMATION

    For a LOW/support level:

        close < level
            → BEARISH_BREAKOUT / CLOSE_CONFIRMED

        low < level and close >= level
            → BEARISH_BREAKOUT / WICK_ONLY

        otherwise
            → NO_BREAKOUT / NO_CONFIRMATION

    This function describes price behavior only.
    """

    if high <= 0:
        raise ValueError(
            "High must be greater than zero"
        )

    if low <= 0:
        raise ValueError(
            "Low must be greater than zero"
        )

    if low > high:
        raise ValueError(
            "Low cannot be greater than high"
        )

    if close < low or close > high:
        raise ValueError(
            "Close must lie within candle high-low range"
        )

    if level_price <= 0:
        raise ValueError(
            "Level price must be greater than zero"
        )

    if candle_index < 0:
        raise ValueError(
            "Candle index cannot be negative"
        )

    if level_index < 0:
        raise ValueError(
            "Level index cannot be negative"
        )

    if level_index >= candle_index:
        raise ValueError(
            "Level index must precede breakout candle"
        )

    if level_type == "HIGH":

        if close > level_price:
            result = BreakoutEvent(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                breakout_type="BULLISH_BREAKOUT",
                confirmation_type="CLOSE_CONFIRMED",
                wick_extreme=float(high),
                close_price=float(close),
            )

        elif high > level_price:
            result = BreakoutEvent(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                breakout_type="BULLISH_BREAKOUT",
                confirmation_type="WICK_ONLY",
                wick_extreme=float(high),
                close_price=float(close),
            )

        else:
            result = BreakoutEvent(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                breakout_type="NO_BREAKOUT",
                confirmation_type="NO_CONFIRMATION",
                wick_extreme=float(high),
                close_price=float(close),
            )

        result.validate()
        return result

    if level_type == "LOW":

        if close < level_price:
            result = BreakoutEvent(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                breakout_type="BEARISH_BREAKOUT",
                confirmation_type="CLOSE_CONFIRMED",
                wick_extreme=float(low),
                close_price=float(close),
            )

        elif low < level_price:
            result = BreakoutEvent(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                breakout_type="BEARISH_BREAKOUT",
                confirmation_type="WICK_ONLY",
                wick_extreme=float(low),
                close_price=float(close),
            )

        else:
            result = BreakoutEvent(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                breakout_type="NO_BREAKOUT",
                confirmation_type="NO_CONFIRMATION",
                wick_extreme=float(low),
                close_price=float(close),
            )

        result.validate()
        return result

    raise ValueError(
        f"Unsupported level type: {level_type}"
    )


def detect_breakouts(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    level_index: int,
    level_price: float,
    level_type: str,
) -> list[BreakoutEvent]:
    """
    Detect all later interactions with one structural level.

    Results are returned in chronological order.

    This function does not generate trading signals.
    """

    if not (
        len(highs)
        == len(lows)
        == len(closes)
    ):
        raise ValueError(
            "Highs, lows, and closes must have equal length"
        )

    if not highs:
        raise ValueError(
            "Price input cannot be empty"
        )

    if any(value <= 0 for value in highs):
        raise ValueError(
            "High values must be greater than zero"
        )

    if any(value <= 0 for value in lows):
        raise ValueError(
            "Low values must be greater than zero"
        )

    if any(value <= 0 for value in closes):
        raise ValueError(
            "Close values must be greater than zero"
        )

    if level_index < 0:
        raise ValueError(
            "Level index cannot be negative"
        )

    if level_index >= len(highs):
        raise ValueError(
            "Level index is outside the price series"
        )

    if level_price <= 0:
        raise ValueError(
            "Level price must be greater than zero"
        )

    result: list[BreakoutEvent] = []

    for candle_index in range(
        level_index + 1,
        len(highs),
    ):
        event = detect_breakout(
            high=highs[candle_index],
            low=lows[candle_index],
            close=closes[candle_index],
            level_price=level_price,
            level_type=level_type,
            candle_index=candle_index,
            level_index=level_index,
        )

        if event.breakout_type != "NO_BREAKOUT":
            result.append(event)

    return result
