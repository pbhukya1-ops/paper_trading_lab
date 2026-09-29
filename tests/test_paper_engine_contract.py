import pytest

from config import STARTING_CAPITAL


@pytest.fixture
def paper_engine_class():
    from app.paper_engine import PaperEngine
    return PaperEngine


def test_engine_uses_project_starting_capital(paper_engine_class):
    engine = paper_engine_class()

    assert engine.starting_capital == STARTING_CAPITAL
    assert engine.capital == STARTING_CAPITAL


def test_engine_creates_risk_manager_from_project_config(paper_engine_class):
    engine = paper_engine_class()

    assert engine.risk_manager.parameters.max_risk_per_trade > 0
    assert engine.risk_manager.parameters.max_open_positions > 0


def test_engine_position_size_uses_risk_manager(paper_engine_class):
    engine = paper_engine_class()

    size = engine.calculate_position_size(
        entry_price=100.0,
        stop_price=95.0,
    )

    expected = engine.risk_manager.calculate_position_size(
        capital=STARTING_CAPITAL,
        entry_price=100.0,
        stop_price=95.0,
    )

    assert size == expected


def test_engine_position_size_supports_short_geometry(paper_engine_class):
    engine = paper_engine_class()

    size = engine.calculate_position_size(
        entry_price=100.0,
        stop_price=105.0,
        direction="SHORT_GEOMETRY",
    )

    expected = engine.risk_manager.calculate_position_size(
        capital=STARTING_CAPITAL,
        entry_price=100.0,
        stop_price=105.0,
        direction="SHORT_GEOMETRY",
    )

    assert size == expected
    assert size == pytest.approx(200.0)


def test_engine_short_position_lifecycle_updates_capital_and_history(
    paper_engine_class,
):
    from datetime import datetime

    from app.position import Position
    from app.strategy.targets import TargetGeometry

    engine = paper_engine_class()

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
    position = Position(
        direction="SHORT_GEOMETRY",
        quantity=10.0,
        target_geometry=geometry,
    )

    entry_time = datetime(2026, 1, 1, 10, 0)
    exit_time = datetime(2026, 1, 1, 11, 0)

    opened = engine.open_position(position, entry_time)

    assert opened == position
    assert engine.current_position == position
    assert engine.open_position_count == 1
    assert engine.unrealized_pnl(92.0) == pytest.approx(80.0)
    assert engine.equity(92.0) == pytest.approx(
        STARTING_CAPITAL + 80.0
    )

    trade = engine.close_position(
        exit_price=92.0,
        exit_time=exit_time,
    )

    assert trade.position == position
    assert trade.realized_pnl == pytest.approx(80.0)
    assert engine.current_position is None
    assert engine.open_position_count == 0
    assert engine.capital == pytest.approx(STARTING_CAPITAL + 80.0)
    assert engine.account_snapshot["realized_pnl"] == pytest.approx(80.0)
    assert engine.account_snapshot["completed_trade_count"] == 1
    assert len(engine.trade_history) == 1


def test_engine_respects_open_position_limit(paper_engine_class):
    engine = paper_engine_class()

    assert engine.can_open_position() is True

    engine.open_position_count = engine.risk_manager.parameters.max_open_positions

    assert engine.can_open_position() is False


def test_engine_is_paper_only(paper_engine_class):
    engine = paper_engine_class()

    assert engine.paper_only is True
    assert not hasattr(engine, 'place_order')
    assert not hasattr(engine, 'submit_order')
    assert not hasattr(engine, 'execute_order')
