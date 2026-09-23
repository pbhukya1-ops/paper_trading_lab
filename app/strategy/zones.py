"""
Support/resistance zone foundations for Paper Trading Lab.

Zones are analytical price areas derived from confirmed
structural levels. They do not generate trading signals.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceZone:
    center: float
    lower: float
    upper: float
    source: str

    def validate(self) -> None:
        if self.center <= 0:
            raise ValueError("Zone center must be greater than zero")

        if self.lower <= 0:
            raise ValueError("Zone lower bound must be greater than zero")

        if self.upper <= 0:
            raise ValueError("Zone upper bound must be greater than zero")

        if self.lower > self.center:
            raise ValueError("Zone lower bound cannot exceed center")

        if self.upper < self.center:
            raise ValueError("Zone upper bound cannot be below center")

        if not self.source:
            raise ValueError("Zone source cannot be empty")


def make_price_zone(
    center: float,
    tolerance: float,
    source: str,
) -> PriceZone:
    """
    Create a symmetric price zone around a structural level.
    """
    if center <= 0:
        raise ValueError("Center must be greater than zero")

    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative")

    if not source:
        raise ValueError("Zone source cannot be empty")

    zone = PriceZone(
        center=float(center),
        lower=float(center - tolerance),
        upper=float(center + tolerance),
        source=source,
    )

    zone.validate()
    return zone


def structural_levels_to_zones(
    levels: list[tuple[int, float, str]],
    tolerance: float,
) -> list[PriceZone]:
    """
    Convert confirmed structural levels into support/resistance zones.

    HIGH structural levels become RESISTANCE zones.
    LOW structural levels become SUPPORT zones.

    The function preserves the chronological order of the
    supplied structural levels and does not generate signals.
    """
    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative")

    zones: list[PriceZone] = []

    for index, price, level_type in levels:
        if index < 0:
            raise ValueError("Structural level index cannot be negative")

        if price <= 0:
            raise ValueError("Structural level price must be greater than zero")

        if level_type == "HIGH":
            source = f"RESISTANCE:{index}"
        elif level_type == "LOW":
            source = f"SUPPORT:{index}"
        else:
            raise ValueError(
                f"Unsupported structural level type: {level_type}"
            )

        zone = make_price_zone(
            center=float(price),
            tolerance=float(tolerance),
            source=source,
        )

        zones.append(zone)

    return zones


def price_in_zone(price: float, zone: PriceZone) -> bool:
    """
    Return True when a positive price lies within the zone boundaries.

    Boundaries are inclusive:
        lower <= price <= upper

    This is an analytical interaction check only.
    It does not generate a trading signal.
    """
    if price <= 0:
        raise ValueError("Price must be greater than zero")

    zone.validate()

    return zone.lower <= float(price) <= zone.upper


def cluster_price_zones(zones: list[PriceZone]) -> list[PriceZone]:
    """
    Merge overlapping or touching price zones.

    Zones are sorted by lower boundary for deterministic clustering.
    A cluster is formed when the next zone's lower boundary is
    less than or equal to the current cluster's upper boundary.

    The merged center is the midpoint of the merged boundaries.

    This is an analytical normalization step only.
    It does not generate trading signals.
    """
    if not zones:
        return []

    for zone in zones:
        zone.validate()

    ordered = sorted(
        zones,
        key=lambda zone: (zone.lower, zone.upper, zone.center),
    )

    clusters: list[PriceZone] = []

    current_lower = ordered[0].lower
    current_upper = ordered[0].upper
    current_sources = [ordered[0].source]

    for zone in ordered[1:]:
        if zone.lower <= current_upper:
            current_upper = max(current_upper, zone.upper)
            current_sources.append(zone.source)
            continue

        clusters.append(
            PriceZone(
                center=(current_lower + current_upper) / 2.0,
                lower=current_lower,
                upper=current_upper,
                source="|".join(current_sources),
            )
        )

        current_lower = zone.lower
        current_upper = zone.upper
        current_sources = [zone.source]

    clusters.append(
        PriceZone(
            center=(current_lower + current_upper) / 2.0,
            lower=current_lower,
            upper=current_upper,
            source="|".join(current_sources),
        )
    )

    return clusters
