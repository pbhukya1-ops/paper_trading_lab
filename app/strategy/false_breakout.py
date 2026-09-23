"""
False-breakout / breakout-failure analysis foundations
for Paper Trading Lab.

This module describes observable price behavior in which price
first breaks a previously established structural level and then
closes back through that same level.

A false breakout is a descriptive price-action classification.
It does not establish trader intent or hidden order-book activity.

This module does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass


VALID_FAILURE_TYPES = {
    "BULLISH_BREAKOUT_FAILURE",
    "BEARISH_BREAKOUT_FAILURE",
    "NO_FAILURE",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True)
class FalseBreakoutContext:
    level_index: int
    failure_candle_index: int
    level_price: float
    breakout_type: str
    failure_type: str
    breakout_extreme: float
    failure_close: float

    def validate(self) -> None:
        if self.level_index < 0:
            raise ValueError(
                "Level index cannot be negative"
            )

        if self.failure_candle_index <= self.level_index:
            raise ValueError(
                "Failure candle must follow level index"
            )

        if self.level_price <= 0:
            raise ValueError(
                "Level price must be greater than zero"
            )

        if self.breakout_extreme <= 0:
            raise ValueError(
                "Breakout extreme must be greater than zero"
            )

        if self.failure_close <= 0:
            raise ValueError(
                "Failure close must be greater than zero"
            )

        if self.breakout_type not in {
            "BULLISH_BREAKOUT",
            "BEARISH_BREAKOUT",
        }:
            raise ValueError(
                f"Unsupported breakout type: {self.breakout_type}"
            )

        if self.failure_type not in VALID_FAILURE_TYPES:
            raise ValueError(
                f"Unsupported failure type: {self.failure_type}"
            )

        if self.failure_type == "BULLISH_BREAKOUT_FAILURE":
            if self.breakout_type != "BULLISH_BREAKOUT":
                raise ValueError(
                    "Bullish breakout failure requires "
                    "BULLISH_BREAKOUT"
                )

        if self.failure_type == "BEARISH_BREAKOUT_FAILURE":
            if self.breakout_type != "BEARISH_BREAKOUT":
                raise ValueError(
                    "Bearish breakout failure requires "
                    "BEARISH_BREAKOUT"
                )


def detect_false_breakout(
    breakout_extreme: float,
    failure_close: float,
    level_price: float,
    breakout_type: str,
    level_index: int,
    failure_candle_index: int,
) -> FalseBreakoutContext:
    """
    Detect whether a prior breakout subsequently failed.

    Bullish breakout:
        breakout_extreme > level_price
        failure_close < level_price

        -> BULLISH_BREAKOUT_FAILURE

    Bearish breakout:
        breakout_extreme < level_price
        failure_close > level_price

        -> BEARISH_BREAKOUT_FAILURE

    Equality with the level is not classified as a failure because
    the failure close must cross back through the level.

    This function describes price behavior only.
    """

    if breakout_extreme <= 0:
        raise ValueError(
            "Breakout extreme must be greater than zero"
        )

    if failure_close <= 0:
        raise ValueError(
            "Failure close must be greater than zero"
        )

    if level_price <= 0:
        raise ValueError(
            "Level price must be greater than zero"
        )

    if level_index < 0:
        raise ValueError(
            "Level index cannot be negative"
        )

    if failure_candle_index <= level_index:
        raise ValueError(
            "Failure candle must follow level index"
        )

    if breakout_type == "BULLISH_BREAKOUT":
        if breakout_extreme <= level_price:
            raise ValueError(
                "Bullish breakout extreme must exceed level"
            )

        if failure_close < level_price:
            failure_type = "BULLISH_BREAKOUT_FAILURE"
        else:
            failure_type = "NO_FAILURE"

    elif breakout_type == "BEARISH_BREAKOUT":
        if breakout_extreme >= level_price:
            raise ValueError(
                "Bearish breakout extreme must be below level"
            )

        if failure_close > level_price:
            failure_type = "BEARISH_BREAKOUT_FAILURE"
        else:
            failure_type = "NO_FAILURE"

    else:
        raise ValueError(
            f"Unsupported breakout type: {breakout_type}"
        )

    result = FalseBreakoutContext(
        level_index=level_index,
        failure_candle_index=failure_candle_index,
        level_price=float(level_price),
        breakout_type=breakout_type,
        failure_type=failure_type,
        breakout_extreme=float(breakout_extreme),
        failure_close=float(failure_close),
    )

    result.validate()
    return result


def classify_level_reclaim(
    price: float,
    level_price: float,
    breakout_type: str,
) -> str:
    """
    Classify whether price has reclaimed a broken level.

    This is a price-location test only.

    For a bullish breakout:
        price < level -> BELOW_BROKEN_LEVEL
        price >= level -> ABOVE_OR_AT_LEVEL

    For a bearish breakout:
        price > level -> ABOVE_BROKEN_LEVEL
        price <= level -> BELOW_OR_AT_LEVEL
    """

    if price <= 0:
        raise ValueError(
            "Price must be greater than zero"
        )

    if level_price <= 0:
        raise ValueError(
            "Level price must be greater than zero"
        )

    if breakout_type == "BULLISH_BREAKOUT":
        if price < level_price:
            return "BELOW_BROKEN_LEVEL"
        return "ABOVE_OR_AT_LEVEL"

    if breakout_type == "BEARISH_BREAKOUT":
        if price > level_price:
            return "ABOVE_BROKEN_LEVEL"
        return "BELOW_OR_AT_LEVEL"

    raise ValueError(
        f"Unsupported breakout type: {breakout_type}"
    )
