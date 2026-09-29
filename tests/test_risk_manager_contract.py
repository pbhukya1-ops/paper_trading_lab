import pytest

from app.risk.risk_manager import (
    RiskManager,
    RiskParameters,
)


def test_risk_parameters_store_valid_configuration():
    params = RiskParameters(
        max_risk_per_trade=0.01,
        max_open_positions=1,
    )

    assert params.max_risk_per_trade == 0.01
    assert params.max_open_positions == 1


def test_risk_budget_is_percentage_of_capital():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    assert manager.calculate_risk_budget(100000.0) == pytest.approx(1000.0)


def test_position_size_uses_risk_budget_divided_by_risk_distance():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    # Capital = 100,000
    # Risk budget = 1,000
    # Entry = 100, Stop = 95
    # Risk distance = 5
    # Position size = 1,000 / 5 = 200
    assert manager.calculate_position_size(
        capital=100000.0,
        entry_price=100.0,
        stop_price=95.0,
    ) == pytest.approx(200.0)


def test_zero_risk_distance_is_rejected():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    with pytest.raises(ValueError, match="risk distance"):
        manager.calculate_position_size(
            capital=100000.0,
            entry_price=100.0,
            stop_price=100.0,
        )


def test_short_position_size_uses_risk_budget_divided_by_risk_distance():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    # Capital = 100,000
    # Risk budget = 1,000
    # Entry = 100, Stop = 105
    # Risk distance = 5
    # Position size = 1,000 / 5 = 200
    assert manager.calculate_position_size(
        capital=100000.0,
        entry_price=100.0,
        stop_price=105.0,
        direction="SHORT_GEOMETRY",
    ) == pytest.approx(200.0)


def test_short_wrong_side_stop_is_rejected():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    with pytest.raises(ValueError, match="Short geometry requires stop above entry"):
        manager.calculate_position_size(
            capital=100000.0,
            entry_price=100.0,
            stop_price=95.0,
            direction="SHORT_GEOMETRY",
        )


def test_invalid_position_size_direction_is_rejected():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    with pytest.raises(ValueError, match="Unsupported direction"):
        manager.calculate_position_size(
            capital=100000.0,
            entry_price=100.0,
            stop_price=95.0,
            direction="INVALID",
        )


def test_negative_risk_distance_is_rejected_for_long_geometry():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    with pytest.raises(ValueError):
        manager.calculate_position_size(
            capital=100000.0,
            entry_price=100.0,
            stop_price=105.0,
        )


def test_zero_or_negative_capital_is_rejected():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    with pytest.raises(ValueError):
        manager.calculate_risk_budget(0.0)

    with pytest.raises(ValueError):
        manager.calculate_risk_budget(-100.0)


def test_invalid_risk_percentage_is_rejected():
    with pytest.raises(ValueError):
        RiskParameters(
            max_risk_per_trade=0.0,
            max_open_positions=1,
        )

    with pytest.raises(ValueError):
        RiskParameters(
            max_risk_per_trade=1.0,
            max_open_positions=1,
        )


def test_invalid_max_open_positions_is_rejected():
    with pytest.raises(ValueError):
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=0,
        )


def test_open_position_limit_is_enforced():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    assert manager.can_open_position(0) is True
    assert manager.can_open_position(1) is False


def test_position_size_is_descriptive_and_does_not_place_orders():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=0.01,
            max_open_positions=1,
        )
    )

    size = manager.calculate_position_size(
        capital=100000.0,
        entry_price=100.0,
        stop_price=95.0,
    )

    assert size == pytest.approx(200.0)
