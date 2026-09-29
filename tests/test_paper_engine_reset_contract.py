from datetime import datetime

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


def complete_trade(engine: PaperEngine, exit_price: float) -> None:
    entry_time = datetime(2026, 1, 1, 9, 15)
    exit_time = datetime(2026, 1, 1, 10, 15)

    engine.open_position(make_position(), entry_time)
    engine.close_position(exit_price, exit_time)


def test_reset_exists_and_returns_none():
    engine = PaperEngine()
    assert engine.reset() is None


def test_reset_restores_initial_account_state():
    engine = PaperEngine()
    complete_trade(engine, 108.0)

    engine.reset()

    assert engine.capital == engine.starting_capital
    assert engine.open_position_count == 0
    assert engine.current_position is None
    assert engine.trade_history == ()
    assert engine.drawdown == 0.0


def test_reset_clears_all_completed_trade_metrics():
    engine = PaperEngine()
    complete_trade(engine, 108.0)
    complete_trade(engine, 97.0)

    engine.reset()

    assert engine.trade_outcomes == {
        "completed_trade_count": 0,
        "winning_trade_count": 0,
        "losing_trade_count": 0,
    }
    assert engine.win_rate == 0.0
    assert engine.profit_factor == 0.0
    assert engine.performance_snapshot == {
        "completed_trade_count": 0,
        "winning_trade_count": 0,
        "losing_trade_count": 0,
        "breakeven_trade_count": 0,
        "realized_pnl": 0.0,
        "win_rate": 0.0,
    }


def test_reset_clears_open_position_state():
    engine = PaperEngine()
    engine.open_position(
        position=make_position(),
        entry_time=datetime(2026, 1, 1, 9, 15),
    )

    engine.reset()

    assert engine.current_position is None
    assert engine.open_position_count == 0
    assert engine.unrealized_pnl(100.0) == 0.0


def test_reset_preserves_starting_capital_and_risk_manager():
    engine = PaperEngine()
    risk_manager = engine.risk_manager

    complete_trade(engine, 108.0)
    engine.reset()

    assert engine.starting_capital == 100000.0
    assert engine.risk_manager is risk_manager


def test_reset_preserves_paper_only_boundary():
    engine = PaperEngine()

    engine.reset()

    assert engine.paper_only is True

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
        "create_order",
    }
    assert forbidden.isdisjoint(set(dir(engine)))
