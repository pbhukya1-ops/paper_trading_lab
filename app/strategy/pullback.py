"""
Pullback and retest analysis foundations for Paper Trading Lab.

This module describes observable price movement after a breakout
or structural move and identifies a subsequent return toward
the referenced price level.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass


VALID_MOVE_TYPES = {
    "BULLISH_MOVE",
    "BEARISH_MOVE",
}

VALID_RETEST_TYPES = {
    "BULLISH_RETEST",
    "BEARISH_RETEST",
    "NO_RETEST",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True)
class PullbackRetestContext:
    move_type: str
    reference_index: int
    move_index: int
    retest_index: int | None
    reference_price: float
    retest_price: float | None
    retest_type: str

    def validate(self) -> None:
        if self.move_type not in VALID_MOVE_TYPES:
            raise ValueError(
                f"Unsupported move type: {self.move_type}"
            )

        if self.reference_index < 0:
            raise ValueError(
                "Reference index cannot be negative"
            )

        if self.move_index <= self.reference_index:
            raise ValueError(
                "Move index must follow reference index"
            )

        if self.retest_index is not None:
            if self.retest_index <= self.move_index:
                raise ValueError(
                    "Retest index must follow move index"
                )

        if self.reference_price <= 0:
            raise ValueError(
                "Reference price must be greater than zero"
            )

        if self.retest_price is not None:
            if self.retest_price <= 0:
                raise ValueError(
                    "Retest price must be greater than zero"
                )

        if self.retest_type not in VALID_RETEST_TYPES:
            raise ValueError(
                f"Unsupported retest type: {self.retest_type}"
            )

        if self.retest_type == "NO_RETEST":
            if self.retest_index is not None:
                raise ValueError(
                    "NO_RETEST cannot contain a retest index"
                )
            if self.retest_price is not None:
                raise ValueError(
                    "NO_RETEST cannot contain a retest price"
                )

        if self.retest_type in {
            "BULLISH_RETEST",
            "BEARISH_RETEST",
        }:
            if self.retest_index is None:
                raise ValueError(
                    "Confirmed retest requires retest index"
                )
            if self.retest_price is None:
                raise ValueError(
                    "Confirmed retest requires retest price"
                )


def detect_pullback_retest(
    reference_price: float,
    move_extreme: float,
    retest_price: float,
    move_type: str,
    reference_index: int,
    move_index: int,
    retest_index: int,
    tolerance: float = 0.0,
) -> PullbackRetestContext:
    """
    Detect a descriptive return toward a reference price.

    Bullish move:
        move_extreme > reference_price
        retest_price <= move_extreme
        retest_price is within tolerance of reference_price

    Bearish move:
        move_extreme < reference_price
        retest_price >= move_extreme
        retest_price is within tolerance of reference_price

    A retest means price has returned to the configured
    reference area. It does not imply support, resistance,
    continuation, or reversal.

    This function does not generate a trading signal.
    """

    if reference_price <= 0:
        raise ValueError(
            "Reference price must be greater than zero"
        )

    if move_extreme <= 0:
        raise ValueError(
            "Move extreme must be greater than zero"
        )

    if retest_price <= 0:
        raise ValueError(
            "Retest price must be greater than zero"
        )

    if tolerance < 0:
        raise ValueError(
            "Tolerance cannot be negative"
        )

    if reference_index < 0:
        raise ValueError(
            "Reference index cannot be negative"
        )

    if move_index <= reference_index:
        raise ValueError(
            "Move index must follow reference index"
        )

    if retest_index <= move_index:
        raise ValueError(
            "Retest index must follow move index"
        )

    if move_type not in VALID_MOVE_TYPES:
        raise ValueError(
            f"Unsupported move type: {move_type}"
        )

    distance = abs(retest_price - reference_price)

    if move_type == "BULLISH_MOVE":
        if move_extreme <= reference_price:
            raise ValueError(
                "Bullish move extreme must exceed reference price"
            )

        if retest_price > move_extreme:
            raise ValueError(
                "Bullish retest price cannot exceed move extreme"
            )

        if distance <= tolerance:
            retest_type = "BULLISH_RETEST"
        else:
            retest_type = "NO_RETEST"

    else:
        if move_extreme >= reference_price:
            raise ValueError(
                "Bearish move extreme must be below reference price"
            )

        if retest_price < move_extreme:
            raise ValueError(
                "Bearish retest price cannot be below move extreme"
            )

        if distance <= tolerance:
            retest_type = "BEARISH_RETEST"
        else:
            retest_type = "NO_RETEST"

    result = PullbackRetestContext(
        move_type=move_type,
        reference_index=reference_index,
        move_index=move_index,
        retest_index=(
            retest_index
            if retest_type != "NO_RETEST"
            else None
        ),
        reference_price=float(reference_price),
        retest_price=(
            float(retest_price)
            if retest_type != "NO_RETEST"
            else None
        ),
        retest_type=retest_type,
    )

    result.validate()
    return result


def classify_retest_distance(
    reference_price: float,
    current_price: float,
    tolerance: float,
) -> str:
    """
    Classify whether current price is within a configured
    distance of a reference price.

    This is a geometric price-location test only.
    """

    if reference_price <= 0:
        raise ValueError(
            "Reference price must be greater than zero"
        )

    if current_price <= 0:
        raise ValueError(
            "Current price must be greater than zero"
        )

    if tolerance < 0:
        raise ValueError(
            "Tolerance cannot be negative"
        )

    if abs(current_price - reference_price) <= tolerance:
        return "WITHIN_RETEST_AREA"

    return "OUTSIDE_RETEST_AREA"
