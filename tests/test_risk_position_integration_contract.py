import pytest

from app.position import Position
from app.risk.risk_manager import RiskManager, RiskParameters
from app.strategy.targets import TargetGeometry


@pytest.mark.parametrize(
    "direction,entry_price,stop_price,target_price",
    [
        ("LONG_GEOMETRY", 100.0, 95.0, 110.0),
        ("SHORT_GEOMETRY", 100.0, 105.0, 90.0),
    ],
)
def test_risk_sized_quantity_constructs_matching_position(
    direction,
    entry_price,
    stop_price,
    target_price,
):
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    quantity = manager.calculate_position_size(
        capital=100000.0,
        entry_price=entry_price,
        stop_price=stop_price,
        direction=direction,
    )

    geometry = TargetGeometry(
        direction=direction,
        reference_price=entry_price,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    position = Position(
        direction=direction,
        quantity=quantity,
        target_geometry=geometry,
    )

    assert quantity == pytest.approx(200.0)
    assert position.direction == direction
    assert position.quantity == pytest.approx(200.0)
    assert position.target_geometry == geometry
