from datetime import datetime, timezone

import pytest

from app.paper_engine import PaperEngine
from app.position import Position
from app.strategy.targets import TargetGeometry


def make_position():
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


def complete_trade(engine, exit_price, minute):
    entry_time = datetime(
        2026, 9, 28, 9, minute, tzinfo=timezone.utc
    )
    exit_time = datetime(
        2026, 9, 28, 10, minute, tzinfo=timezone.utc
    )
    engine.open_position(make_position(), entry_time)
    return engine.close_position(exit_price, exit_time)


def test_drawdown_exists(engine_class=PaperEngine):
    engine = engine_class()
    assert engine.drawdown == 0.0


def test_drawdown_is_zero_at_a_new_peak(engine_class=PaperEngine):
    engine = engine_class()

    complete_trade(engine, 108.0, 1)

    assert engine.capital == pytest.approx(100080.0)
    assert engine.drawdown == pytest.approx(0.0)


def test_drawdown_is_peak_capital_minus_current_capital(
    engine_class=PaperEngine,
):
    engine = engine_class()

    complete_trade(engine, 108.0, 1)
    complete_trade(engine, 97.0, 2)

    assert engine.capital == pytest.approx(100050.0)
    assert engine.drawdown == pytest.approx(30.0)


def test_drawdown_updates_when_a_new_peak_is_reached(
    engine_class=PaperEngine,
):
    engine = engine_class()

    complete_trade(engine, 108.0, 1)
    complete_trade(engine, 97.0, 2)
    complete_trade(engine, 110.0, 3)

    assert engine.capital == pytest.approx(100150.0)
    assert engine.drawdown == pytest.approx(0.0)


def test_drawdown_does_not_use_unrealized_pnl(engine_class=PaperEngine):
    engine = engine_class()

    complete_trade(engine, 108.0, 1)

    engine.open_position(
        make_position(),
        datetime(2026, 9, 28, 11, 1, tzinfo=timezone.utc),
    )

    assert engine.capital == pytest.approx(100080.0)
    assert engine.unrealized_pnl(110.0) == pytest.approx(100.0)
    assert engine.drawdown == pytest.approx(0.0)


def test_drawdown_is_read_only(engine_class=PaperEngine):
    engine = engine_class()

    with pytest.raises(AttributeError):
        engine.drawdown = 10.0


def test_drawdown_has_no_order_execution_api(engine_class=PaperEngine):
    engine = engine_class()

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(engine)))
