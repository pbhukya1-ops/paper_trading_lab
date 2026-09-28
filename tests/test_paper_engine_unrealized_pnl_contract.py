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


def test_unrealized_pnl_is_zero_without_open_position(engine_class):
    engine = engine_class()

    assert engine.unrealized_pnl(100.0) == 0.0


def test_long_unrealized_pnl(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.unrealized_pnl(108.0) == 80.0


def test_short_unrealized_pnl(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_short_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.unrealized_pnl(92.0) == 80.0


def test_unrealized_pnl_can_be_negative(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.unrealized_pnl(97.0) == -30.0


def test_unrealized_pnl_does_not_change_realized_pnl(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert engine.unrealized_pnl(108.0) == 80.0
    assert engine.account_snapshot["realized_pnl"] == 0.0


def test_unrealized_pnl_does_not_modify_capital(engine_class):
    engine = engine_class()
    engine.open_position(
        position=make_long_position(),
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    engine.unrealized_pnl(108.0)

    assert engine.capital == 100000.0


def test_unrealized_pnl_requires_positive_price(engine_class):
    engine = engine_class()

    with pytest.raises(ValueError, match="current_price"):
        engine.unrealized_pnl(0.0)


def test_unrealized_pnl_is_read_only_api(engine_class):
    engine = engine_class()

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(engine)))
