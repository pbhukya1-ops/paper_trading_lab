import pytest

from app.strategy.zones import (
    PriceZone,
    cluster_price_zones,
    make_price_zone,
    price_in_zone,
    structural_levels_to_zones,
)


def test_price_zone_validates_valid_zone():
    zone = PriceZone(
        center=100.0,
        lower=95.0,
        upper=105.0,
        source="SUPPORT:1",
    )

    zone.validate()


def test_price_zone_rejects_non_positive_center():
    zone = PriceZone(
        center=0.0,
        lower=1.0,
        upper=2.0,
        source="SUPPORT:1",
    )

    with pytest.raises(ValueError, match="center.*greater than zero"):
        zone.validate()


def test_price_zone_rejects_non_positive_lower():
    zone = PriceZone(
        center=100.0,
        lower=0.0,
        upper=105.0,
        source="SUPPORT:1",
    )

    with pytest.raises(ValueError, match="lower bound.*greater than zero"):
        zone.validate()


def test_price_zone_rejects_non_positive_upper():
    zone = PriceZone(
        center=100.0,
        lower=95.0,
        upper=0.0,
        source="SUPPORT:1",
    )

    with pytest.raises(ValueError, match="upper bound.*greater than zero"):
        zone.validate()


def test_price_zone_rejects_lower_above_center():
    zone = PriceZone(
        center=100.0,
        lower=101.0,
        upper=105.0,
        source="SUPPORT:1",
    )

    with pytest.raises(ValueError, match="lower bound cannot exceed center"):
        zone.validate()


def test_price_zone_rejects_upper_below_center():
    zone = PriceZone(
        center=100.0,
        lower=95.0,
        upper=99.0,
        source="SUPPORT:1",
    )

    with pytest.raises(ValueError, match="upper bound cannot be below center"):
        zone.validate()


def test_price_zone_rejects_empty_source():
    zone = PriceZone(
        center=100.0,
        lower=95.0,
        upper=105.0,
        source="",
    )

    with pytest.raises(ValueError, match="source cannot be empty"):
        zone.validate()


def test_make_price_zone_creates_symmetric_zone():
    zone = make_price_zone(
        center=100.0,
        tolerance=5.0,
        source="SUPPORT:1",
    )

    assert zone.center == 100.0
    assert zone.lower == 95.0
    assert zone.upper == 105.0
    assert zone.source == "SUPPORT:1"


def test_make_price_zone_accepts_zero_tolerance():
    zone = make_price_zone(
        center=100.0,
        tolerance=0.0,
        source="RESISTANCE:2",
    )

    assert zone.center == 100.0
    assert zone.lower == 100.0
    assert zone.upper == 100.0


def test_make_price_zone_rejects_negative_tolerance():
    with pytest.raises(ValueError, match="Tolerance cannot be negative"):
        make_price_zone(
            center=100.0,
            tolerance=-1.0,
            source="SUPPORT:1",
        )


def test_make_price_zone_rejects_non_positive_center():
    with pytest.raises(ValueError, match="Center must be greater than zero"):
        make_price_zone(
            center=0.0,
            tolerance=1.0,
            source="SUPPORT:1",
        )


def test_make_price_zone_rejects_empty_source():
    with pytest.raises(ValueError, match="source cannot be empty"):
        make_price_zone(
            center=100.0,
            tolerance=1.0,
            source="",
        )


def test_structural_high_becomes_resistance_zone():
    result = structural_levels_to_zones(
        [(3, 120.0, "HIGH")],
        tolerance=2.0,
    )

    assert result == [
        PriceZone(
            center=120.0,
            lower=118.0,
            upper=122.0,
            source="RESISTANCE:3",
        )
    ]


def test_structural_low_becomes_support_zone():
    result = structural_levels_to_zones(
        [(4, 90.0, "LOW")],
        tolerance=3.0,
    )

    assert result == [
        PriceZone(
            center=90.0,
            lower=87.0,
            upper=93.0,
            source="SUPPORT:4",
        )
    ]


def test_structural_levels_preserve_order():
    levels = [
        (0, 100.0, "LOW"),
        (1, 120.0, "HIGH"),
        (2, 105.0, "LOW"),
    ]

    result = structural_levels_to_zones(
        levels,
        tolerance=1.0,
    )

    assert [zone.source for zone in result] == [
        "SUPPORT:0",
        "RESISTANCE:1",
        "SUPPORT:2",
    ]


def test_structural_levels_reject_negative_index():
    with pytest.raises(ValueError, match="index cannot be negative"):
        structural_levels_to_zones(
            [(-1, 100.0, "LOW")],
            tolerance=1.0,
        )


def test_structural_levels_reject_non_positive_price():
    with pytest.raises(ValueError, match="price must be greater than zero"):
        structural_levels_to_zones(
            [(1, 0.0, "HIGH")],
            tolerance=1.0,
        )


def test_structural_levels_reject_unknown_type():
    with pytest.raises(ValueError, match="Unsupported structural level type"):
        structural_levels_to_zones(
            [(1, 100.0, "MIDDLE")],
            tolerance=1.0,
        )


def test_structural_levels_reject_negative_tolerance():
    with pytest.raises(ValueError, match="Tolerance cannot be negative"):
        structural_levels_to_zones(
            [(1, 100.0, "HIGH")],
            tolerance=-1.0,
        )


def test_price_in_zone_includes_lower_boundary():
    zone = make_price_zone(100.0, 5.0, "SUPPORT:1")

    assert price_in_zone(95.0, zone) is True


def test_price_in_zone_includes_upper_boundary():
    zone = make_price_zone(100.0, 5.0, "SUPPORT:1")

    assert price_in_zone(105.0, zone) is True


def test_price_in_zone_includes_center():
    zone = make_price_zone(100.0, 5.0, "SUPPORT:1")

    assert price_in_zone(100.0, zone) is True


def test_price_in_zone_rejects_price_outside_zone():
    zone = make_price_zone(100.0, 5.0, "SUPPORT:1")

    assert price_in_zone(94.99, zone) is False
    assert price_in_zone(105.01, zone) is False


def test_price_in_zone_rejects_non_positive_price():
    zone = make_price_zone(100.0, 5.0, "SUPPORT:1")

    with pytest.raises(ValueError, match="Price must be greater than zero"):
        price_in_zone(0.0, zone)


def test_cluster_overlapping_zones():
    zones = [
        PriceZone(100.0, 95.0, 105.0, "SUPPORT:1"),
        PriceZone(108.0, 103.0, 113.0, "RESISTANCE:2"),
    ]

    result = cluster_price_zones(zones)

    assert result == [
        PriceZone(
            center=104.0,
            lower=95.0,
            upper=113.0,
            source="SUPPORT:1|RESISTANCE:2",
        )
    ]


def test_cluster_touching_zones():
    zones = [
        PriceZone(100.0, 95.0, 105.0, "SUPPORT:1"),
        PriceZone(110.0, 105.0, 115.0, "RESISTANCE:2"),
    ]

    result = cluster_price_zones(zones)

    assert result == [
        PriceZone(
            center=105.0,
            lower=95.0,
            upper=115.0,
            source="SUPPORT:1|RESISTANCE:2",
        )
    ]


def test_cluster_separate_zones_remain_separate():
    zones = [
        PriceZone(100.0, 95.0, 105.0, "SUPPORT:1"),
        PriceZone(120.0, 115.0, 125.0, "RESISTANCE:2"),
    ]

    result = cluster_price_zones(zones)

    assert result == [
        PriceZone(100.0, 95.0, 105.0, "SUPPORT:1"),
        PriceZone(120.0, 115.0, 125.0, "RESISTANCE:2"),
    ]


def test_cluster_is_order_independent():
    zones = [
        PriceZone(120.0, 115.0, 125.0, "RESISTANCE:2"),
        PriceZone(100.0, 95.0, 105.0, "SUPPORT:1"),
    ]

    result = cluster_price_zones(zones)

    assert result == [
        PriceZone(100.0, 95.0, 105.0, "SUPPORT:1"),
        PriceZone(120.0, 115.0, 125.0, "RESISTANCE:2"),
    ]


def test_cluster_empty_input_returns_empty_list():
    assert cluster_price_zones([]) == []


def test_cluster_validates_input_zones():
    invalid_zone = PriceZone(
        center=100.0,
        lower=101.0,
        upper=105.0,
        source="SUPPORT:1",
    )

    with pytest.raises(ValueError, match="lower bound cannot exceed center"):
        cluster_price_zones([invalid_zone])
