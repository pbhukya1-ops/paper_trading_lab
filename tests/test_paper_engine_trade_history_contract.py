from datetime import datetime

import pytest

from app.position import Position
from app.strategy.targets import TargetGeometry


@pytest.fixture
def engine_class():
    from app.paper_engine import PaperEngine
    return PaperEngine


def make_long_position(quantity=10.0):
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
        quantity=quantity,
        target_geometry=geometry,
    )


def test_engine_starts_with_empty_trade_history(engine_class):
    engine = engine_class()

    assert engine.trade_history == ()


def test_close_adds_completed_trade_to_history(engine_class):
    engine = engine_class()
    position = make_long_position()

    engine.open_position(
        position=position,
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    trade = engine.close_position(
        exit_price=108.0,
        exit_time=datetime(2026, 1, 1, 11, 0),
    )

    assert engine.trade_history == (trade,)


def test_trade_history_preserves_completion_order(engine_class):
    engine = engine_class()

    first_position = make_long_position(quantity=10.0)
    engine.open_position(
        position=first_position,
        entry_time=datetime(2026, 1, 1, 10, 0),
    )
    first_trade = engine.close_position(
        exit_price=108.0,
        exit_time=datetime(2026, 1, 1, 11, 0),
    )

    second_position = make_long_position(quantity=5.0)
    engine.open_position(
        position=second_position,
        entry_time=datetime(2026, 1, 2, 10, 0),
    )
    second_trade = engine.close_position(
        exit_price=106.0,
        exit_time=datetime(2026, 1, 2, 11, 0),
    )

    assert engine.trade_history == (first_trade, second_trade)


def test_trade_history_is_not_mutable(engine_class):
    engine = engine_class()

    with pytest.raises(AttributeError):
        engine.trade_history = ()


def test_trade_history_has_no_order_execution_api(engine_class):
    engine = engine_class()

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(engine)))
