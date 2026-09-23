import pytest

from app.strategy.liquidity import (
    LiquidityZone,
    structural_level_to_liquidity,
    structural_levels_to_liquidity,
)


def test_liquidity_zone_validates_valid_buy_side_zone():
    zone = LiquidityZone(
        center=100.0,
        lower=95.0,
        upper=105.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:3",
    )

    zone.validate()


def test_liquidity_zone_validates_valid_sell_side_zone():
    zone = LiquidityZone(
        center=100.0,
        lower=95.0,
        upper=105.0,
        liquidity_type="SELL_SIDE_LIQUIDITY",
        source="LOW:3",
    )

    zone.validate()


def test_liquidity_zone_rejects_non_positive_center():
    zone = LiquidityZone(
        center=0.0,
        lower=1.0,
        upper=2.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:1",
    )

    with pytest.raises(ValueError, match="center.*greater than zero"):
        zone.validate()


def test_liquidity_zone_rejects_non_positive_lower():
    zone = LiquidityZone(
        center=100.0,
        lower=0.0,
        upper=105.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:1",
    )

    with pytest.raises(ValueError, match="lower bound.*greater than zero"):
        zone.validate()


def test_liquidity_zone_rejects_non_positive_upper():
    zone = LiquidityZone(
        center=100.0,
        lower=95.0,
        upper=0.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:1",
    )

    with pytest.raises(ValueError, match="upper bound.*greater than zero"):
        zone.validate()


def test_liquidity_zone_rejects_lower_above_center():
    zone = LiquidityZone(
        center=100.0,
        lower=101.0,
        upper=105.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:1",
    )

    with pytest.raises(ValueError, match="lower bound cannot exceed center"):
        zone.validate()


def test_liquidity_zone_rejects_upper_below_center():
    zone = LiquidityZone(
        center=100.0,
        lower=95.0,
        upper=99.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:1",
    )

    with pytest.raises(ValueError, match="upper bound cannot be below center"):
        zone.validate()


def test_liquidity_zone_rejects_unsupported_type():
    zone = LiquidityZone(
        center=100.0,
        lower=95.0,
        upper=105.0,
        liquidity_type="UNKNOWN",
        source="HIGH:1",
    )

    with pytest.raises(ValueError, match="Unsupported liquidity type"):
        zone.validate()


def test_liquidity_zone_rejects_empty_source():
    zone = LiquidityZone(
        center=100.0,
        lower=95.0,
        upper=105.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="",
    )

    with pytest.raises(ValueError, match="source cannot be empty"):
        zone.validate()


def test_high_structural_level_becomes_buy_side_liquidity():
    result = structural_level_to_liquidity(
        index=5,
        price=120.0,
        level_type="HIGH",
        tolerance=2.0,
    )

    assert result == LiquidityZone(
        center=120.0,
        lower=118.0,
        upper=122.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:5",
    )


def test_low_structural_level_becomes_sell_side_liquidity():
    result = structural_level_to_liquidity(
        index=7,
        price=90.0,
        level_type="LOW",
        tolerance=3.0,
    )

    assert result == LiquidityZone(
        center=90.0,
        lower=87.0,
        upper=93.0,
        liquidity_type="SELL_SIDE_LIQUIDITY",
        source="LOW:7",
    )


def test_default_tolerance_creates_point_zone():
    result = structural_level_to_liquidity(
        index=2,
        price=100.0,
        level_type="HIGH",
    )

    assert result == LiquidityZone(
        center=100.0,
        lower=100.0,
        upper=100.0,
        liquidity_type="BUY_SIDE_LIQUIDITY",
        source="HIGH:2",
    )


def test_structural_level_rejects_negative_index():
    with pytest.raises(ValueError, match="index cannot be negative"):
        structural_level_to_liquidity(
            index=-1,
            price=100.0,
            level_type="HIGH",
        )


def test_structural_level_rejects_non_positive_price():
    with pytest.raises(
        ValueError,
        match="price must be greater than zero",
    ):
        structural_level_to_liquidity(
            index=1,
            price=0.0,
            level_type="HIGH",
        )


def test_structural_level_rejects_negative_tolerance():
    with pytest.raises(ValueError, match="Tolerance cannot be negative"):
        structural_level_to_liquidity(
            index=1,
            price=100.0,
            level_type="HIGH",
            tolerance=-1.0,
        )


def test_structural_level_rejects_unknown_level_type():
    with pytest.raises(
        ValueError,
        match="Unsupported structural level type",
    ):
        structural_level_to_liquidity(
            index=1,
            price=100.0,
            level_type="MIDDLE",
        )


def test_structural_levels_to_liquidity_preserves_order():
    levels = [
        (0, 100.0, "LOW"),
        (1, 120.0, "HIGH"),
        (2, 105.0, "LOW"),
    ]

    result = structural_levels_to_liquidity(
        levels,
        tolerance=1.0,
    )

    assert result == [
        LiquidityZone(
            center=100.0,
            lower=99.0,
            upper=101.0,
            liquidity_type="SELL_SIDE_LIQUIDITY",
            source="LOW:0",
        ),
        LiquidityZone(
            center=120.0,
            lower=119.0,
            upper=121.0,
            liquidity_type="BUY_SIDE_LIQUIDITY",
            source="HIGH:1",
        ),
        LiquidityZone(
            center=105.0,
            lower=104.0,
            upper=106.0,
            liquidity_type="SELL_SIDE_LIQUIDITY",
            source="LOW:2",
        ),
    ]


def test_structural_levels_to_liquidity_accepts_empty_input():
    assert structural_levels_to_liquidity([]) == []


def test_structural_levels_to_liquidity_rejects_negative_tolerance():
    with pytest.raises(ValueError, match="Tolerance cannot be negative"):
        structural_levels_to_liquidity(
            [(1, 100.0, "HIGH")],
            tolerance=-1.0,
        )
