"""
Liquidity-sweep analysis foundations for Paper Trading Lab.

This module detects price sweeps of previously established
structural liquidity levels.

A sweep is a descriptive price-action event only.
It does not generate trading signals or place orders.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LiquiditySweep:
    """
    Describes a candle that penetrates a prior structural
    liquidity level and closes back on the opposite side.

    HIGH level:
        Price trades above the prior high and closes below it.

    LOW level:
        Price trades below the prior low and closes above it.
    """

    candle_index: int
    level_index: int
    level_price: float
    sweep_type: str
    wick_extreme: float
    close_price: float

    def validate(self) -> None:
        if self.candle_index < 0:
            raise ValueError("Candle index cannot be negative")

        if self.level_index < 0:
            raise ValueError("Liquidity level index cannot be negative")

        if self.level_price <= 0:
            raise ValueError(
                "Liquidity level price must be greater than zero"
            )

        if self.wick_extreme <= 0:
            raise ValueError(
                "Sweep wick extreme must be greater than zero"
            )

        if self.close_price <= 0:
            raise ValueError(
                "Sweep close price must be greater than zero"
            )

        if self.sweep_type not in {
            "BUY_SIDE_SWEEP",
            "SELL_SIDE_SWEEP",
        }:
            raise ValueError(
                f"Unsupported sweep type: {self.sweep_type}"
            )

        if self.level_index >= self.candle_index:
            raise ValueError(
                "Liquidity level must precede the sweep candle"
            )


def detect_liquidity_sweep(
    high: float,
    low: float,
    close: float,
    level_price: float,
    level_type: str,
    candle_index: int,
    level_index: int,
) -> LiquiditySweep | None:
    """
    Detect a sweep of one previously established structural level.

    HIGH / BUY-SIDE LIQUIDITY:
        high > level_price
        close < level_price

    LOW / SELL-SIDE LIQUIDITY:
        low < level_price
        close > level_price

    Exact-touch conditions do not qualify as sweeps.

    This function describes price behavior only.
    No trading signal is generated.
    """

    if high <= 0:
        raise ValueError("High must be greater than zero")

    if low <= 0:
        raise ValueError("Low must be greater than zero")

    if close <= 0:
        raise ValueError("Close must be greater than zero")

    if low > high:
        raise ValueError("Low cannot be greater than high")

    if close < low or close > high:
        raise ValueError(
            "Close must lie within the candle's high-low range"
        )

    if level_price <= 0:
        raise ValueError(
            "Liquidity level price must be greater than zero"
        )

    if candle_index < 0:
        raise ValueError("Candle index cannot be negative")

    if level_index < 0:
        raise ValueError("Liquidity level index cannot be negative")

    if level_index >= candle_index:
        raise ValueError(
            "Liquidity level must precede the sweep candle"
        )

    if level_type == "HIGH":
        if high > level_price and close < level_price:
            sweep = LiquiditySweep(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                sweep_type="BUY_SIDE_SWEEP",
                wick_extreme=float(high),
                close_price=float(close),
            )
            sweep.validate()
            return sweep

        return None

    if level_type == "LOW":
        if low < level_price and close > level_price:
            sweep = LiquiditySweep(
                candle_index=candle_index,
                level_index=level_index,
                level_price=float(level_price),
                sweep_type="SELL_SIDE_SWEEP",
                wick_extreme=float(low),
                close_price=float(close),
            )
            sweep.validate()
            return sweep

        return None

    raise ValueError(
        f"Unsupported liquidity level type: {level_type}"
    )


def detect_liquidity_sweeps(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    level_index: int,
    level_price: float,
    level_type: str,
) -> list[LiquiditySweep]:
    """
    Detect all sweeps of one previously established
    structural liquidity level.

    Results are returned in chronological order.

    No trading signal is generated.
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
        raise ValueError("Price input cannot be empty")

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
            "Liquidity level index cannot be negative"
        )

    if level_index >= len(highs):
        raise ValueError(
            "Liquidity level index is outside the price series"
        )

    if level_price <= 0:
        raise ValueError(
            "Liquidity level price must be greater than zero"
        )

    result: list[LiquiditySweep] = []

    for candle_index in range(level_index + 1, len(highs)):
        sweep = detect_liquidity_sweep(
            high=highs[candle_index],
            low=lows[candle_index],
            close=closes[candle_index],
            level_price=level_price,
            level_type=level_type,
            candle_index=candle_index,
            level_index=level_index,
        )

        if sweep is not None:
            result.append(sweep)

    return result
