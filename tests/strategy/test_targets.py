import pytest

from app.strategy.targets import (
    TargetGeometry,
    VALID_DIRECTIONS,
    calculate_target_geometry,
    price_distance,
    target_from_risk_multiple,
)


def test_valid_directions():
    assert VALID_DIRECTIONS == {
        "LONG_GEOMETRY",
        "SHORT_GEOMETRY",
    }


def test_long_target_geometry():
    result = calculate_target_geometry(
        reference_price=100.0,
        entry_price=102.0,
        stop_price=98.0,
        target_price=110.0,
        direction="LONG_GEOMETRY",
    )

    assert result.direction == "LONG_GEOMETRY"
    assert result.reference_price == 100.0
    assert result.entry_price == 102.0
    assert result.stop_price == 98.0
    assert result.target_price == 110.0
    assert result.risk_distance == 4.0
    assert result.reward_distance == 8.0
    assert result.reward_risk_ratio == 2.0


def test_short_target_geometry():
    result = calculate_target_geometry(
        reference_price=100.0,
        entry_price=98.0,
        stop_price=102.0,
        target_price=90.0,
        direction="SHORT_GEOMETRY",
    )

    assert result.direction == "SHORT_GEOMETRY"
    assert result.reference_price == 100.0
    assert result.entry_price == 98.0
    assert result.stop_price == 102.0
    assert result.target_price == 90.0
    assert result.risk_distance == 4.0
    assert result.reward_distance == 8.0
    assert result.reward_risk_ratio == 2.0


def test_reference_price_does_not_change_rr():
    first = calculate_target_geometry(
        reference_price=50.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        direction="LONG_GEOMETRY",
    )

    second = calculate_target_geometry(
        reference_price=999.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        direction="LONG_GEOMETRY",
    )

    assert first.reward_risk_ratio == second.reward_risk_ratio
    assert first.risk_distance == second.risk_distance
    assert first.reward_distance == second.reward_distance


def test_long_risk_multiple_target():
    assert (
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=95.0,
            risk_multiple=2.0,
            direction="LONG_GEOMETRY",
        )
        == 110.0
    )


def test_short_risk_multiple_target():
    assert (
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=105.0,
            risk_multiple=2.0,
            direction="SHORT_GEOMETRY",
        )
        == 90.0
    )


def test_one_risk_multiple_reaches_equal_distance():
    assert (
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=95.0,
            risk_multiple=1.0,
            direction="LONG_GEOMETRY",
        )
        == 105.0
    )

    assert (
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=105.0,
            risk_multiple=1.0,
            direction="SHORT_GEOMETRY",
        )
        == 95.0
    )


@pytest.mark.parametrize(
    "price_a,price_b,expected",
    [
        (100.0, 90.0, 10.0),
        (90.0, 100.0, 10.0),
        (100.0, 100.0, 0.0),
        (100.25, 99.75, 0.5),
    ],
)
def test_price_distance(price_a, price_b, expected):
    assert price_distance(price_a, price_b) == expected


def test_target_geometry_is_frozen():
    result = calculate_target_geometry(
        reference_price=100.0,
        entry_price=102.0,
        stop_price=98.0,
        target_price=110.0,
        direction="LONG_GEOMETRY",
    )

    with pytest.raises(AttributeError):
        result.target_price = 111.0


@pytest.mark.parametrize(
    "direction",
    [
        "INVALID",
        "",
        "LONG",
        "SHORT",
    ],
)
def test_invalid_direction(direction):
    with pytest.raises(ValueError, match="Unsupported direction"):
        calculate_target_geometry(
            reference_price=100.0,
            entry_price=102.0,
            stop_price=98.0,
            target_price=110.0,
            direction=direction,
        )


def test_long_requires_stop_below_entry():
    with pytest.raises(ValueError, match="Long geometry requires stop below entry"):
        calculate_target_geometry(
            reference_price=100.0,
            entry_price=100.0,
            stop_price=100.0,
            target_price=110.0,
            direction="LONG_GEOMETRY",
        )


def test_long_requires_target_above_entry():
    with pytest.raises(ValueError, match="Long geometry requires target above entry"):
        calculate_target_geometry(
            reference_price=100.0,
            entry_price=100.0,
            stop_price=95.0,
            target_price=100.0,
            direction="LONG_GEOMETRY",
        )


def test_short_requires_stop_above_entry():
    with pytest.raises(ValueError, match="Short geometry requires stop above entry"):
        calculate_target_geometry(
            reference_price=100.0,
            entry_price=100.0,
            stop_price=100.0,
            target_price=90.0,
            direction="SHORT_GEOMETRY",
        )


def test_short_requires_target_below_entry():
    with pytest.raises(ValueError, match="Short geometry requires target below entry"):
        calculate_target_geometry(
            reference_price=100.0,
            entry_price=100.0,
            stop_price=105.0,
            target_price=100.0,
            direction="SHORT_GEOMETRY",
        )


@pytest.mark.parametrize(
    "reference_price,entry_price,stop_price,target_price",
    [
        (0.0, 102.0, 98.0, 110.0),
        (100.0, 0.0, 98.0, 110.0),
        (100.0, 102.0, 0.0, 110.0),
        (100.0, 102.0, 98.0, 0.0),
    ],
)
def test_target_geometry_rejects_nonpositive_prices(
    reference_price,
    entry_price,
    stop_price,
    target_price,
):
    with pytest.raises(ValueError):
        calculate_target_geometry(
            reference_price=reference_price,
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            direction="LONG_GEOMETRY",
        )


@pytest.mark.parametrize(
    "entry_price,stop_price,risk_multiple",
    [
        (0.0, 95.0, 2.0),
        (100.0, 0.0, 2.0),
        (100.0, 95.0, 0.0),
        (100.0, 95.0, -1.0),
    ],
)
def test_risk_multiple_rejects_invalid_numeric_inputs(
    entry_price,
    stop_price,
    risk_multiple,
):
    with pytest.raises(ValueError):
        target_from_risk_multiple(
            entry_price=entry_price,
            stop_price=stop_price,
            risk_multiple=risk_multiple,
            direction="LONG_GEOMETRY",
        )


def test_long_risk_multiple_requires_stop_below_entry():
    with pytest.raises(ValueError, match="Long geometry requires stop below entry"):
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=100.0,
            risk_multiple=2.0,
            direction="LONG_GEOMETRY",
        )


def test_short_risk_multiple_requires_stop_above_entry():
    with pytest.raises(ValueError, match="Short geometry requires stop above entry"):
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=100.0,
            risk_multiple=2.0,
            direction="SHORT_GEOMETRY",
        )


def test_risk_multiple_rejects_invalid_direction():
    with pytest.raises(ValueError, match="Unsupported direction"):
        target_from_risk_multiple(
            entry_price=100.0,
            stop_price=95.0,
            risk_multiple=2.0,
            direction="INVALID",
        )


@pytest.mark.parametrize(
    "price_a,price_b",
    [
        (0.0, 100.0),
        (100.0, 0.0),
        (-1.0, 100.0),
        (100.0, -1.0),
    ],
)
def test_price_distance_rejects_nonpositive_prices(price_a, price_b):
    with pytest.raises(ValueError):
        price_distance(price_a, price_b)


def test_target_geometry_validation_rejects_invalid_risk_distance():
    context = TargetGeometry(
        direction="LONG_GEOMETRY",
        reference_price=100.0,
        entry_price=102.0,
        stop_price=98.0,
        target_price=110.0,
        risk_distance=0.0,
        reward_distance=8.0,
        reward_risk_ratio=2.0,
    )

    with pytest.raises(ValueError, match="Risk distance"):
        context.validate()


def test_target_geometry_validation_rejects_invalid_reward_distance():
    context = TargetGeometry(
        direction="LONG_GEOMETRY",
        reference_price=100.0,
        entry_price=102.0,
        stop_price=98.0,
        target_price=110.0,
        risk_distance=4.0,
        reward_distance=0.0,
        reward_risk_ratio=2.0,
    )

    with pytest.raises(ValueError, match="Reward distance"):
        context.validate()


def test_target_geometry_validation_rejects_invalid_rr():
    context = TargetGeometry(
        direction="LONG_GEOMETRY",
        reference_price=100.0,
        entry_price=102.0,
        stop_price=98.0,
        target_price=110.0,
        risk_distance=4.0,
        reward_distance=8.0,
        reward_risk_ratio=0.0,
    )

    with pytest.raises(ValueError, match="Reward/risk ratio"):
        context.validate()
