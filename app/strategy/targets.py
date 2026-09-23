"""
Target and risk/reward geometry foundations for Paper Trading Lab.

This module describes price-distance and target geometry using
explicit reference, entry, stop, and target prices.

The calculations are mathematical/descriptive only.

This module does NOT:
- generate trade signals,
- recommend trades,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass


VALID_DIRECTIONS = {
    "LONG_GEOMETRY",
    "SHORT_GEOMETRY",
}


@dataclass(frozen=True)
class TargetGeometry:
    direction: str
    reference_price: float
    entry_price: float
    stop_price: float
    target_price: float
    risk_distance: float
    reward_distance: float
    reward_risk_ratio: float

    def validate(self) -> None:
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Unsupported direction: {self.direction}"
            )

        prices = {
            "reference_price": self.reference_price,
            "entry_price": self.entry_price,
            "stop_price": self.stop_price,
            "target_price": self.target_price,
        }

        for name, value in prices.items():
            if value <= 0:
                raise ValueError(
                    f"{name} must be greater than zero"
                )

        if self.risk_distance <= 0:
            raise ValueError(
                "Risk distance must be greater than zero"
            )

        if self.reward_distance <= 0:
            raise ValueError(
                "Reward distance must be greater than zero"
            )

        if self.reward_risk_ratio <= 0:
            raise ValueError(
                "Reward/risk ratio must be greater than zero"
            )

        if self.direction == "LONG_GEOMETRY":
            if self.stop_price >= self.entry_price:
                raise ValueError(
                    "Long geometry requires stop below entry"
                )

            if self.target_price <= self.entry_price:
                raise ValueError(
                    "Long geometry requires target above entry"
                )

        elif self.direction == "SHORT_GEOMETRY":
            if self.stop_price <= self.entry_price:
                raise ValueError(
                    "Short geometry requires stop above entry"
                )

            if self.target_price >= self.entry_price:
                raise ValueError(
                    "Short geometry requires target below entry"
                )


def calculate_target_geometry(
    reference_price: float,
    entry_price: float,
    stop_price: float,
    target_price: float,
    direction: str,
) -> TargetGeometry:
    """
    Calculate descriptive risk/reward geometry.

    LONG_GEOMETRY:
        stop < entry < target

    SHORT_GEOMETRY:
        target < entry < stop

    Reference price is retained as contextual information.
    It does not alter the mathematical RR calculation.
    """

    prices = {
        "reference_price": reference_price,
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
    }

    for name, value in prices.items():
        if value <= 0:
            raise ValueError(
                f"{name} must be greater than zero"
            )

    if direction == "LONG_GEOMETRY":
        if stop_price >= entry_price:
            raise ValueError(
                "Long geometry requires stop below entry"
            )

        if target_price <= entry_price:
            raise ValueError(
                "Long geometry requires target above entry"
            )

        risk_distance = entry_price - stop_price
        reward_distance = target_price - entry_price

    elif direction == "SHORT_GEOMETRY":
        if stop_price <= entry_price:
            raise ValueError(
                "Short geometry requires stop above entry"
            )

        if target_price >= entry_price:
            raise ValueError(
                "Short geometry requires target below entry"
            )

        risk_distance = stop_price - entry_price
        reward_distance = entry_price - target_price

    else:
        raise ValueError(
            f"Unsupported direction: {direction}"
        )

    if risk_distance <= 0:
        raise ValueError(
            "Risk distance must be greater than zero"
        )

    if reward_distance <= 0:
        raise ValueError(
            "Reward distance must be greater than zero"
        )

    reward_risk_ratio = reward_distance / risk_distance

    result = TargetGeometry(
        direction=direction,
        reference_price=float(reference_price),
        entry_price=float(entry_price),
        stop_price=float(stop_price),
        target_price=float(target_price),
        risk_distance=float(risk_distance),
        reward_distance=float(reward_distance),
        reward_risk_ratio=float(reward_risk_ratio),
    )

    result.validate()
    return result


def target_from_risk_multiple(
    entry_price: float,
    stop_price: float,
    risk_multiple: float,
    direction: str,
) -> float:
    """
    Calculate a mathematical target from a risk multiple.

    This is geometry only.

    LONG_GEOMETRY:
        target = entry + risk_distance * risk_multiple

    SHORT_GEOMETRY:
        target = entry - risk_distance * risk_multiple
    """

    if entry_price <= 0:
        raise ValueError(
            "Entry price must be greater than zero"
        )

    if stop_price <= 0:
        raise ValueError(
            "Stop price must be greater than zero"
        )

    if risk_multiple <= 0:
        raise ValueError(
            "Risk multiple must be greater than zero"
        )

    if direction == "LONG_GEOMETRY":
        if stop_price >= entry_price:
            raise ValueError(
                "Long geometry requires stop below entry"
            )

        risk_distance = entry_price - stop_price
        return float(
            entry_price + risk_distance * risk_multiple
        )

    if direction == "SHORT_GEOMETRY":
        if stop_price <= entry_price:
            raise ValueError(
                "Short geometry requires stop above entry"
            )

        risk_distance = stop_price - entry_price
        return float(
            entry_price - risk_distance * risk_multiple
        )

    raise ValueError(
        f"Unsupported direction: {direction}"
    )


def price_distance(
    price_a: float,
    price_b: float,
) -> float:
    """
    Return the absolute mathematical distance between two prices.
    """

    if price_a <= 0:
        raise ValueError(
            "price_a must be greater than zero"
        )

    if price_b <= 0:
        raise ValueError(
            "price_b must be greater than zero"
        )

    return abs(float(price_a) - float(price_b))
