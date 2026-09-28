from datetime import datetime, timezone

import pytest

from app.paper_engine import PaperEngine
from app.position import Position
from app.strategy.targets import TargetGeometry


@pytest.fixture
def engine_class():
    return PaperEngine


def make_position(direction="LONG_GEOMETRY"):
    if direction == "LONG_GEOMETRY":
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
    else:
        geometry = TargetGeometry(
            direction="SHORT_GEOMETRY",
            reference_price=100.0,
            entry_price=100.0,
            stop_price=105.0,
            target_price=90.0,
            risk_distance=5.0,
            reward_distance=10.0,
            reward_risk_ratio=2.0,
        )

    return Position(
        direction=direction,
        quantity=10.0,
        target_geometry=geometry,
    )


def complete_trade(engine, exit_price):
    engine.open_position(
        make_position(),
        datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc),
    )
    return engine.close_position(
        exit_price=exit_price,
        exit_time=datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc),
    )


def test_trade_outcomes_start_at_zero(engine_class):
    engine = engine_class()

    assert engine.trade_outcomes == {
        "completed_trade_count": 0,
        "winning_trade_count": 0,
        "losing_trade_count": 0,
    }


def test_winning_trade_is_counted(engine_class):
    engine = engine_class()

    trade = complete_trade(engine, 108.0)

    assert trade.realized_pnl == 80.0
    assert engine.trade_outcomes == {
        "completed_trade_count": 1,
        "winning_trade_count": 1,
        "losing_trade_count": 0,
    }


def test_losing_trade_is_counted(engine_class):
    engine = engine_class()

    trade = complete_trade(engine, 97.0)

    assert trade.realized_pnl == -30.0
    assert engine.trade_outcomes == {
        "completed_trade_count": 1,
        "winning_trade_count": 0,
        "losing_trade_count": 1,
    }


def test_breakeven_trade_is_not_win_or_loss(engine_class):
    engine = engine_class()

    trade = complete_trade(engine, 100.0)

    assert trade.realized_pnl == 0.0
    assert engine.trade_outcomes == {
        "completed_trade_count": 1,
        "winning_trade_count": 0,
        "losing_trade_count": 0,
    }


def test_multiple_trade_outcomes_are_counted(engine_class):
    engine = engine_class()

    complete_trade(engine, 108.0)
    complete_trade(engine, 97.0)
    complete_trade(engine, 100.0)

    assert engine.trade_outcomes == {
        "completed_trade_count": 3,
        "winning_trade_count": 1,
        "losing_trade_count": 1,
    }


def test_trade_outcomes_does_not_modify_capital_or_history(engine_class):
    engine = engine_class()

    complete_trade(engine, 108.0)

    capital_before = engine.capital
    history_before = engine.trade_history

    outcomes = engine.trade_outcomes

    assert engine.capital == capital_before
    assert engine.trade_history == history_before
    assert outcomes["completed_trade_count"] == len(engine.trade_history)


def test_trade_outcomes_returns_a_fresh_mapping(engine_class):
    engine = engine_class()

    first = engine.trade_outcomes
    first["winning_trade_count"] = 999

    second = engine.trade_outcomes

    assert second["winning_trade_count"] == 0


def test_trade_outcomes_has_no_order_execution_api(engine_class):
    public_names = {
        name for name in dir(engine_class) if not name.startswith("_")
    }

    forbidden = {
        "place_order",
        "submit_order",
        "execute_order",
        "create_order",
        "send_order",
    }

    assert public_names.isdisjoint(forbidden)
