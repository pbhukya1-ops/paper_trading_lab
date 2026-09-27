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


def test_engine_starts_without_open_position(engine_class):
    engine = engine_class()
    assert engine.current_position is None


def test_engine_can_open_and_store_position(engine_class):
    engine = engine_class()
    position = make_long_position()

    result = engine.open_position(
        position=position,
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    assert result == position
    assert engine.current_position == position


def test_engine_rejects_second_open_position(engine_class):
    engine = engine_class()
    position = make_long_position()

    engine.open_position(
        position=position,
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(ValueError, match="open position"):
        engine.open_position(
            position=position,
            entry_time=datetime(2026, 1, 1, 11, 0),
        )


def test_engine_close_returns_trade(engine_class):
    engine = engine_class()
    position = make_long_position()
    entry_time = datetime(2026, 1, 1, 10, 0)
    exit_time = datetime(2026, 1, 1, 11, 0)

    engine.open_position(position=position, entry_time=entry_time)
    trade = engine.close_position(
        exit_price=108.0,
        exit_time=exit_time,
    )

    assert trade.position == position
    assert trade.exit_price == 108.0
    assert trade.entry_time == entry_time
    assert trade.exit_time == exit_time
    assert trade.realized_pnl == 80.0
    assert engine.current_position is None


def test_engine_rejects_close_without_open_position(engine_class):
    engine = engine_class()

    with pytest.raises(ValueError, match="No open position"):
        engine.close_position(
            exit_price=108.0,
            exit_time=datetime(2026, 1, 1, 11, 0),
        )


def test_engine_is_paper_only(engine_class):
    engine = engine_class()
    assert engine.paper_only is True
    assert not hasattr(engine, "place_order")
    assert not hasattr(engine, "submit_order")
    assert not hasattr(engine, "cancel_order")
