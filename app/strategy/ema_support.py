"""
EMA21 / support-resistance interaction foundations
for Paper Trading Lab.

This module describes the relationship between price,
EMA21, and an existing support/resistance zone.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass

from .zones import PriceZone, price_in_zone


VALID_EMA_RELATIONSHIPS = {
    "ABOVE_EMA",
    "BELOW_EMA",
    "AT_EMA",
}

VALID_ZONE_RELATIONSHIPS = {
    "IN_SUPPORT_ZONE",
    "IN_RESISTANCE_ZONE",
    "OUTSIDE_ZONE",
}

VALID_INTERACTION_TYPES = {
    "SUPPORT_EMA_INTERACTION",
    "RESISTANCE_EMA_INTERACTION",
    "SUPPORT_ONLY",
    "RESISTANCE_ONLY",
    "EMA_ONLY",
    "NO_INTERACTION",
}


@dataclass(frozen=True)
class EMA21SupportContext:
    price: float
    ema21: float
    ema_relationship: str
    zone_relationship: str
    interaction_type: str
    zone_source: str | None

    def validate(self) -> None:
        if self.price <= 0:
            raise ValueError(
                "Price must be greater than zero"
            )

        if self.ema21 <= 0:
            raise ValueError(
                "EMA21 must be greater than zero"
            )

        if self.ema_relationship not in VALID_EMA_RELATIONSHIPS:
            raise ValueError(
                f"Unsupported EMA relationship: "
                f"{self.ema_relationship}"
            )

        if self.zone_relationship not in VALID_ZONE_RELATIONSHIPS:
            raise ValueError(
                f"Unsupported zone relationship: "
                f"{self.zone_relationship}"
            )

        if self.interaction_type not in VALID_INTERACTION_TYPES:
            raise ValueError(
                f"Unsupported interaction type: "
                f"{self.interaction_type}"
            )

        if (
            self.zone_relationship == "OUTSIDE_ZONE"
            and self.zone_source is not None
        ):
            raise ValueError(
                "Outside-zone context cannot contain a zone source"
            )

        if (
            self.zone_relationship != "OUTSIDE_ZONE"
            and not self.zone_source
        ):
            raise ValueError(
                "Zone source is required when price is inside a zone"
            )


def classify_ema_relationship(
    price: float,
    ema21: float,
) -> str:
    """
    Describe price location relative to EMA21.

    Exact equality is classified as AT_EMA.
    """

    if price <= 0:
        raise ValueError(
            "Price must be greater than zero"
        )

    if ema21 <= 0:
        raise ValueError(
            "EMA21 must be greater than zero"
        )

    if price > ema21:
        return "ABOVE_EMA"

    if price < ema21:
        return "BELOW_EMA"

    return "AT_EMA"


def classify_zone_relationship(
    price: float,
    zone: PriceZone | None,
) -> tuple[str, str | None]:
    """
    Describe whether price is inside an existing zone.

    The zone source is preserved for traceability.
    """

    if price <= 0:
        raise ValueError(
            "Price must be greater than zero"
        )

    if zone is None:
        return "OUTSIDE_ZONE", None

    zone.validate()

    if price_in_zone(price, zone):
        if zone.source.startswith("SUPPORT:"):
            return "IN_SUPPORT_ZONE", zone.source

        if zone.source.startswith("RESISTANCE:"):
            return "IN_RESISTANCE_ZONE", zone.source

        raise ValueError(
            "Zone source must identify SUPPORT or RESISTANCE"
        )

    return "OUTSIDE_ZONE", None


def classify_ema_zone_interaction(
    price: float,
    ema21: float,
    zone: PriceZone | None = None,
) -> EMA21SupportContext:
    """
    Combine EMA21 location with support/resistance-zone context.

    This is descriptive analysis only.
    """

    ema_relationship = classify_ema_relationship(
        price=price,
        ema21=ema21,
    )

    zone_relationship, zone_source = classify_zone_relationship(
        price=price,
        zone=zone,
    )

    if (
        zone_relationship == "IN_SUPPORT_ZONE"
        and ema_relationship == "AT_EMA"
    ):
        interaction_type = "SUPPORT_EMA_INTERACTION"

    elif (
        zone_relationship == "IN_RESISTANCE_ZONE"
        and ema_relationship == "AT_EMA"
    ):
        interaction_type = "RESISTANCE_EMA_INTERACTION"

    elif zone_relationship == "IN_SUPPORT_ZONE":
        interaction_type = "SUPPORT_ONLY"

    elif zone_relationship == "IN_RESISTANCE_ZONE":
        interaction_type = "RESISTANCE_ONLY"

    elif ema_relationship == "AT_EMA":
        interaction_type = "EMA_ONLY"

    else:
        interaction_type = "NO_INTERACTION"

    result = EMA21SupportContext(
        price=float(price),
        ema21=float(ema21),
        ema_relationship=ema_relationship,
        zone_relationship=zone_relationship,
        interaction_type=interaction_type,
        zone_source=zone_source,
    )

    result.validate()
    return result
