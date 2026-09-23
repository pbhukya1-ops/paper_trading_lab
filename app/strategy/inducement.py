"""
Inducement analysis foundations for Paper Trading Lab.

This module identifies a descriptive intermediate structural
level that may attract a liquidity interaction before a later
structural move.

Inducement is inferred only from observable price structure.
It is not a claim about hidden orders or trader intent.

This module does not generate trading signals or place orders.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class InducementLevel:
    """
    Describes an intermediate structural level between two
    confirmed structural reference levels.

    HIGH:
        Intermediate swing high between a prior structural low
        and a later structural high.

    LOW:
        Intermediate swing low between a prior structural high
        and a later structural low.
    """

    index: int
    price: float
    inducement_type: str
    reference_index: int
    target_index: int

    def validate(self) -> None:
        if self.index < 0:
            raise ValueError("Inducement index cannot be negative")

        if self.reference_index < 0:
            raise ValueError(
                "Reference index cannot be negative"
            )

        if self.target_index < 0:
            raise ValueError(
                "Target index cannot be negative"
            )

        if self.price <= 0:
            raise ValueError(
                "Inducement price must be greater than zero"
            )

        if self.inducement_type not in {
            "HIGH_INDUCEMENT",
            "LOW_INDUCEMENT",
        }:
            raise ValueError(
                f"Unsupported inducement type: "
                f"{self.inducement_type}"
            )

        if not (
            self.reference_index
            < self.index
            < self.target_index
        ):
            raise ValueError(
                "Inducement index must lie strictly between "
                "reference and target indices"
            )


def detect_inducement(
    prices: list[float],
    reference_index: int,
    inducement_index: int,
    target_index: int,
    inducement_type: str,
) -> InducementLevel:
    """
    Validate and describe one structural inducement level.

    HIGH_INDUCEMENT:
        The intermediate price is interpreted as an
        intermediate structural high.

    LOW_INDUCEMENT:
        The intermediate price is interpreted as an
        intermediate structural low.

    This function does not infer hidden liquidity or trader intent.
    It only records the supplied observable structural relationship.
    """

    if not prices:
        raise ValueError("Price input cannot be empty")

    if any(value <= 0 for value in prices):
        raise ValueError(
            "Price values must be greater than zero"
        )

    if reference_index < 0:
        raise ValueError(
            "Reference index cannot be negative"
        )

    if inducement_index < 0:
        raise ValueError(
            "Inducement index cannot be negative"
        )

    if target_index < 0:
        raise ValueError(
            "Target index cannot be negative"
        )

    if reference_index >= len(prices):
        raise ValueError(
            "Reference index is outside the price series"
        )

    if inducement_index >= len(prices):
        raise ValueError(
            "Inducement index is outside the price series"
        )

    if target_index >= len(prices):
        raise ValueError(
            "Target index is outside the price series"
        )

    if not (
        reference_index
        < inducement_index
        < target_index
    ):
        raise ValueError(
            "Indices must satisfy "
            "reference < inducement < target"
        )

    if inducement_type not in {
        "HIGH_INDUCEMENT",
        "LOW_INDUCEMENT",
    }:
        raise ValueError(
            f"Unsupported inducement type: {inducement_type}"
        )

    level = InducementLevel(
        index=inducement_index,
        price=float(prices[inducement_index]),
        inducement_type=inducement_type,
        reference_index=reference_index,
        target_index=target_index,
    )

    level.validate()
    return level


def detect_inducements(
    prices: list[float],
    reference_index: int,
    target_index: int,
    inducement_type: str,
) -> list[InducementLevel]:
    """
    Describe all intermediate price levels between a reference
    index and a target index.

    Results are returned in chronological order.

    This is a structural description only.
    No trading signal is generated.
    """

    if not prices:
        raise ValueError("Price input cannot be empty")

    if any(value <= 0 for value in prices):
        raise ValueError(
            "Price values must be greater than zero"
        )

    if reference_index < 0:
        raise ValueError(
            "Reference index cannot be negative"
        )

    if target_index < 0:
        raise ValueError(
            "Target index cannot be negative"
        )

    if reference_index >= len(prices):
        raise ValueError(
            "Reference index is outside the price series"
        )

    if target_index >= len(prices):
        raise ValueError(
            "Target index is outside the price series"
        )

    if reference_index >= target_index:
        raise ValueError(
            "Reference index must precede target index"
        )

    if inducement_type not in {
        "HIGH_INDUCEMENT",
        "LOW_INDUCEMENT",
    }:
        raise ValueError(
            f"Unsupported inducement type: {inducement_type}"
        )

    result: list[InducementLevel] = []

    for index in range(reference_index + 1, target_index):
        result.append(
            detect_inducement(
                prices=prices,
                reference_index=reference_index,
                inducement_index=index,
                target_index=target_index,
                inducement_type=inducement_type,
            )
        )

    return result
