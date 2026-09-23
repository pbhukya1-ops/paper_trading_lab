"""
Liquidity analysis foundations for Paper Trading Lab.

This module converts confirmed structural highs and lows into
descriptive liquidity areas.

Liquidity labels are analytical interpretations of price structure.
They are not claims about directly observed resting orders and
do not generate trading signals.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LiquidityZone:
    center: float
    lower: float
    upper: float
    liquidity_type: str
    source: str

    def validate(self) -> None:
        if self.center <= 0:
            raise ValueError("Liquidity center must be greater than zero")

        if self.lower <= 0:
            raise ValueError("Liquidity lower bound must be greater than zero")

        if self.upper <= 0:
            raise ValueError("Liquidity upper bound must be greater than zero")

        if self.lower > self.center:
            raise ValueError(
                "Liquidity lower bound cannot exceed center"
            )

        if self.upper < self.center:
            raise ValueError(
                "Liquidity upper bound cannot be below center"
            )

        if self.liquidity_type not in {
            "BUY_SIDE_LIQUIDITY",
            "SELL_SIDE_LIQUIDITY",
        }:
            raise ValueError(
                f"Unsupported liquidity type: {self.liquidity_type}"
            )

        if not self.source:
            raise ValueError("Liquidity source cannot be empty")


def structural_level_to_liquidity(
    index: int,
    price: float,
    level_type: str,
    tolerance: float = 0.0,
) -> LiquidityZone:
    """
    Convert one confirmed structural level into a descriptive
    liquidity zone.

    HIGH → BUY_SIDE_LIQUIDITY
    LOW  → SELL_SIDE_LIQUIDITY

    No trading signal is generated.
    """
    if index < 0:
        raise ValueError("Structural level index cannot be negative")

    if price <= 0:
        raise ValueError(
            "Structural level price must be greater than zero"
        )

    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative")

    if level_type == "HIGH":
        liquidity_type = "BUY_SIDE_LIQUIDITY"
    elif level_type == "LOW":
        liquidity_type = "SELL_SIDE_LIQUIDITY"
    else:
        raise ValueError(
            f"Unsupported structural level type: {level_type}"
        )

    zone = LiquidityZone(
        center=float(price),
        lower=float(price - tolerance),
        upper=float(price + tolerance),
        liquidity_type=liquidity_type,
        source=f"{level_type}:{index}",
    )

    zone.validate()
    return zone


def structural_levels_to_liquidity(
    levels: list[tuple[int, float, str]],
    tolerance: float = 0.0,
) -> list[LiquidityZone]:
    """
    Convert confirmed structural levels into descriptive
    liquidity zones while preserving chronological order.

    No trading signal is generated.
    """
    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative")

    result: list[LiquidityZone] = []

    for index, price, level_type in levels:
        result.append(
            structural_level_to_liquidity(
                index=index,
                price=price,
                level_type=level_type,
                tolerance=tolerance,
            )
        )

    return result
