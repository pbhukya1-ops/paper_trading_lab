from datetime import datetime, timezone

import pytest

from app.paper_engine import PaperEngine
from app.position import Position
from app.strategy.targets import TargetGeometry


@pytest.fixture
def engine_class():
    return PaperEngine


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
    engine.open_position(
        make_position(),
        datetime(2026, 9, 28, 9, minute, tzinfo=timezone.utc),
    )

    return engine.close_position(
        exit_price=exit_price,
        exit_time=datetime(2026, 9, 28, 10, minute, tzinfo=timezone.utc),
    )


def test_win_rate_starts_at_zero(engine_class):
    engine = engine_class()

    assert engine.win_rate == 0.0


def test_one_winning_trade_has_100_percent_win_rate(engine_class):
    engine = engine_class()

    complete_trade(engine, 108.0, 1)

    assert engine.win_rate == 100.0


def test_one_losing_trade_has_zero_percent_win_rate(engine_class):
    engine = engine_class()

    complete_trade(engine, 97.0, 2)

    assert engine.win_rate == 0.0


def test_mixed_outcomes_calculate_win_rate(engine_class):
    engine = engine_class()

    complete_trade(engine, 108.0, 3)
    complete_trade(engine, 97.0, 4)
    complete_trade(engine, 100.0, 5)
    complete_trade(engine, 108.0, 6)

    assert engine.trade_outcomes == {
        "completed_trade_count": 4,
        "winning_trade_count": 2,
        "losing_trade_count": 1,
    }
    assert engine.win_rate == 50.0


def test_win_rate_is_percentage_not_fraction(engine_class):
    engine = engine_class()

    complete_trade(engine, 108.0, 7)
    complete_trade(engine, 108.0, 8)
    complete_trade(engine, 97.0, 9)

    assert engine.win_rate == pytest.approx(66.6666666667)


def test_win_rate_does_not_modify_engine_state(engine_class):
    engine = engine_class()

    complete_trade(engine, 108.0, 10)

    capital_before = engine.capital
    history_before = engine.trade_history
    outcomes_before = engine.trade_outcomes

    value = engine.win_rate

    assert value == 100.0
    assert engine.capital == capital_before
    assert engine.trade_history == history_before
    assert engine.trade_outcomes == outcomes_before


def test_win_rate_is_read_only(engine_class):
    engine = engine_class()

    with pytest.raises(AttributeError):
        engine.win_rate = 50.0


def test_win_rate_has_no_order_execution_api(engine_class):
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
