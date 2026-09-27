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


def test_account_snapshot_initial_state(engine_class):
    engine = engine_class()

    snapshot = engine.account_snapshot

    assert snapshot["starting_capital"] == 100000.0
    assert snapshot["capital"] == 100000.0
    assert snapshot["open_position_count"] == 0
    assert snapshot["completed_trade_count"] == 0
    assert snapshot["realized_pnl"] == 0.0


def test_account_snapshot_updates_after_completed_trade(engine_class):
    engine = engine_class()
    position = make_long_position()

    engine.open_position(
        position=position,
        entry_time=datetime(2026, 1, 1, 10, 0),
    )

    engine.close_position(
        exit_price=108.0,
        exit_time=datetime(2026, 1, 1, 11, 0),
    )

    snapshot = engine.account_snapshot

    assert snapshot["starting_capital"] == 100000.0
    assert snapshot["capital"] == 100080.0
    assert snapshot["open_position_count"] == 0
    assert snapshot["completed_trade_count"] == 1
    assert snapshot["realized_pnl"] == 80.0


def test_account_snapshot_is_read_only(engine_class):
    engine = engine_class()

    with pytest.raises(AttributeError):
        engine.account_snapshot = {}


def test_account_snapshot_returns_fresh_mapping(engine_class):
    engine = engine_class()

    first = engine.account_snapshot
    first["capital"] = -1.0

    second = engine.account_snapshot

    assert second["capital"] == 100000.0


def test_account_snapshot_has_no_order_execution_api(engine_class):
    engine = engine_class()

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(engine)))
