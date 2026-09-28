import pytest

from app.paper_engine import PaperEngine
from app.position import Position
from app.strategy.targets import TargetGeometry


def make_position() -> Position:
    geometry = TargetGeometry(
        direction="LONG_GEOMETRY",
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )
    return Position(
        direction="LONG_GEOMETRY",
        quantity=10.0,
        target_geometry=geometry,
    )


def complete_trade(engine: PaperEngine, exit_price: float, minute: int):
    from datetime import datetime, timedelta

    entry_time = datetime(2026, 1, 1, 9, 15)
    exit_time = entry_time + timedelta(minutes=minute)

    engine.open_position(make_position(), entry_time)
    return engine.close_position(exit_price, exit_time)


def test_profit_factor_exists():
    engine = PaperEngine()

    assert isinstance(engine.profit_factor, float)


def test_empty_profit_factor_is_zero():
    engine = PaperEngine()

    assert engine.profit_factor == 0.0


def test_profit_factor_uses_gross_profit_and_gross_loss():
    engine = PaperEngine()

    complete_trade(engine, 108.0, 1)  # +80
    complete_trade(engine, 97.0, 2)   # -30
    complete_trade(engine, 100.0, 3)  # 0

    assert engine.profit_factor == pytest.approx(80.0 / 30.0)


def test_profit_factor_ignores_breakeven_trades():
    engine = PaperEngine()

    complete_trade(engine, 108.0, 1)  # +80
    complete_trade(engine, 100.0, 2)  # 0

    assert engine.profit_factor == 0.0


def test_profit_factor_is_zero_when_no_losses_exist():
    engine = PaperEngine()

    complete_trade(engine, 108.0, 1)
    complete_trade(engine, 105.0, 2)

    assert engine.profit_factor == 0.0


def test_profit_factor_is_read_only():
    engine = PaperEngine()

    with pytest.raises(AttributeError):
        engine.profit_factor = 2.0


def test_profit_factor_has_no_order_execution_api():
    engine = PaperEngine()

    forbidden = {
        "place_order",
        "submit_order",
        "execute_order",
        "create_order",
    }

    assert not any(hasattr(engine, name) for name in forbidden)
