import pytest

from app.strategy.targets import TargetGeometry


@pytest.fixture
def position_class():
    from app.position import Position
    return Position


def test_long_position_contract(position_class):
    geometry = TargetGeometry(
        direction='LONG_GEOMETRY',
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    position = position_class(
        direction='LONG_GEOMETRY',
        quantity=10.0,
        target_geometry=geometry,
    )

    assert position.direction == 'LONG_GEOMETRY'
    assert position.quantity == 10.0
    assert position.target_geometry == geometry


def test_short_position_contract(position_class):
    geometry = TargetGeometry(
        direction='SHORT_GEOMETRY',
        reference_price=100.0,
        entry_price=100.0,
        stop_price=105.0,
        target_price=90.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    position = position_class(
        direction='SHORT_GEOMETRY',
        quantity=10.0,
        target_geometry=geometry,
    )

    assert position.direction == 'SHORT_GEOMETRY'
    assert position.quantity == 10.0
    assert position.target_geometry == geometry


def test_position_rejects_non_positive_quantity(position_class):
    geometry = TargetGeometry(
        direction='LONG_GEOMETRY',
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    with pytest.raises(ValueError, match='quantity'):
        position_class(
            direction='LONG_GEOMETRY',
            quantity=0.0,
            target_geometry=geometry,
        )


def test_position_rejects_direction_mismatch(position_class):
    geometry = TargetGeometry(
        direction='LONG_GEOMETRY',
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    with pytest.raises(ValueError, match='direction'):
        position_class(
            direction='SHORT_GEOMETRY',
            quantity=10.0,
            target_geometry=geometry,
        )


def test_position_is_immutable(position_class):
    geometry = TargetGeometry(
        direction='LONG_GEOMETRY',
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    position = position_class(
        direction='LONG_GEOMETRY',
        quantity=10.0,
        target_geometry=geometry,
    )

    with pytest.raises((AttributeError, TypeError)):
        position.quantity = 20.0


def test_position_has_no_order_execution_api(position_class):
    geometry = TargetGeometry(
        direction='LONG_GEOMETRY',
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    position = position_class(
        direction='LONG_GEOMETRY',
        quantity=10.0,
        target_geometry=geometry,
    )

    assert not hasattr(position, 'place_order')
    assert not hasattr(position, 'submit_order')
    assert not hasattr(position, 'execute_order')
