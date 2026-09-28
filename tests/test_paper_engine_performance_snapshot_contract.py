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
    engine.open_position(
        make_position(),
        datetime(
            2026,
            9,
            28,
            9,
            minute,
            tzinfo=timezone.utc,
        ),
    )
    return engine.close_position(
        exit_price=exit_price,
        exit_time=datetime(
            2026,
            9,
            28,
            10,
            minute,
            tzinfo=timezone.utc,
        ),
    )


def test_performance_snapshot_exists():
    engine = PaperEngine()

    snapshot = engine.performance_snapshot

    assert isinstance(snapshot, dict)


def test_empty_performance_snapshot_is_zeroed():
    engine = PaperEngine()

    snapshot = engine.performance_snapshot

    assert snapshot["completed_trade_count"] == 0
    assert snapshot["winning_trade_count"] == 0
    assert snapshot["losing_trade_count"] == 0
    assert snapshot["breakeven_trade_count"] == 0
    assert snapshot["realized_pnl"] == 0.0
    assert snapshot["win_rate"] == 0.0


def test_performance_snapshot_matches_completed_trade_history():
    engine = PaperEngine()

    complete_trade(engine, 108.0, 1)
    complete_trade(engine, 97.0, 2)
    complete_trade(engine, 100.0, 3)

    snapshot = engine.performance_snapshot

    assert snapshot["completed_trade_count"] == 3
    assert snapshot["winning_trade_count"] == 1
    assert snapshot["losing_trade_count"] == 1
    assert snapshot["breakeven_trade_count"] == 1
    assert snapshot["realized_pnl"] == 50.0
    assert snapshot["win_rate"] == pytest.approx(33.3333333333)


def test_performance_snapshot_is_read_only():
    engine = PaperEngine()

    with pytest.raises(AttributeError):
        engine.performance_snapshot = {}


def test_performance_snapshot_returns_fresh_mapping():
    engine = PaperEngine()

    first = engine.performance_snapshot
    first["realized_pnl"] = -999.0

    second = engine.performance_snapshot

    assert second["realized_pnl"] == 0.0


def test_performance_snapshot_has_no_order_execution_api():
    engine = PaperEngine()

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(engine)))
