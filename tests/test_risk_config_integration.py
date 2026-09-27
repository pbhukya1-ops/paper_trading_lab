from app.risk.risk_manager import RiskManager, RiskParameters
from config import MAX_OPEN_POSITIONS, MAX_RISK_PER_TRADE


def test_config_values_create_matching_risk_parameters():
    parameters = RiskParameters(
        max_risk_per_trade=MAX_RISK_PER_TRADE,
        max_open_positions=MAX_OPEN_POSITIONS,
    )

    assert parameters.max_risk_per_trade == MAX_RISK_PER_TRADE
    assert parameters.max_open_positions == MAX_OPEN_POSITIONS


def test_config_values_can_initialize_risk_manager():
    manager = RiskManager(
        RiskParameters(
            max_risk_per_trade=MAX_RISK_PER_TRADE,
            max_open_positions=MAX_OPEN_POSITIONS,
        )
    )

    assert manager.parameters.max_risk_per_trade == 0.01
    assert manager.parameters.max_open_positions == 1

def test_risk_manager_from_config_uses_project_configuration():
    manager = RiskManager.from_config()

    assert manager.parameters.max_risk_per_trade == MAX_RISK_PER_TRADE
    assert manager.parameters.max_open_positions == MAX_OPEN_POSITIONS
