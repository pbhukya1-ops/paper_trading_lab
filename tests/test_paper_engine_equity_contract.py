from datetime import datetime

import pytest

from app.position import Position
from app.strategy.targets import TargetGeometry


@pytest.fixture
def engine_class():
    from app.paper_engine import PaperEngine
    return PaperEngine


def make_long_position():
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


def make_short_position():
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
        direction="SHORT_GEOMETRY",
        quantity=10.0,
        target_geometry=geometry,
    )


def test_equity_without_open_position_equals_capital(engine_class):
    engine = engine_class()

    assert engine.equity(100.0) == 100000.0


def test_long_equity_includes_unrealized_pnl(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.equity(108.0) == 100080.0
    assert engine.capital == 100000.0


def test_short_equity_includes_unrealized_pnl(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_short_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.equity(92.0) == 100080.0


def test_equity_reflects_negative_unrealized_pnl(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.equity(97.0) == 99970.0


def test_equity_after_close_uses_realized_capital(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )
    engine.close_position(
        exit_price=108.0,
        exit_time=datetime(2026, 1, 1, 11, 0),
    )

    assert engine.equity(108.0) == 100080.0


def test_equity_does_not_modify_capital(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    engine.equity(108.0)

    assert engine.capital == 100000.0


def test_equity_requires_positive_price(engine_class):
    engine = engine_class()

    with pytest.raises(ValueError, match="current_price"):
        engine.equity(0.0)


def test_equity_has_no_order_execution_api(engine_class):
    engine = engine_class()

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(engine)))
