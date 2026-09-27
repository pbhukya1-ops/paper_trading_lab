from datetime import datetime, timedelta

import pytest

from app.position import Position
from app.strategy.targets import TargetGeometry


@pytest.fixture
def trade_class():
    from app.trade import Trade
    return Trade


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


def test_long_trade_contract(trade_class):
    position = make_long_position()
    entry_time = datetime(2026, 1, 1, 10, 0)
    exit_time = datetime(2026, 1, 1, 11, 0)

    trade = trade_class(
        position=position,
        exit_price=108.0,
        entry_time=entry_time,
        exit_time=exit_time,
    )

    assert trade.position == position
    assert trade.exit_price == 108.0
    assert trade.entry_time == entry_time
    assert trade.exit_time == exit_time
    assert trade.realized_pnl == 80.0


def test_short_trade_contract(trade_class):
    position = make_short_position()
    entry_time = datetime(2026, 1, 1, 10, 0)
    exit_time = datetime(2026, 1, 1, 11, 0)

    trade = trade_class(
        position=position,
        exit_price=92.0,
        entry_time=entry_time,
        exit_time=exit_time,
    )

    assert trade.realized_pnl == 80.0


def test_trade_rejects_non_positive_exit_price(trade_class):
    with pytest.raises(ValueError, match="exit_price"):
        trade_class(
            position=make_long_position(),
            exit_price=0.0,
            entry_time=datetime(2026, 1, 1, 10, 0),
            exit_time=datetime(2026, 1, 1, 11, 0),
        )


def test_trade_rejects_exit_before_entry(trade_class):
    with pytest.raises(ValueError, match="exit_time"):
        trade_class(
            position=make_long_position(),
            exit_price=108.0,
            entry_time=datetime(2026, 1, 1, 11, 0),
            exit_time=datetime(2026, 1, 1, 10, 0),
        )


def test_trade_is_immutable(trade_class):
    trade = trade_class(
        position=make_long_position(),
        exit_price=108.0,
        entry_time=datetime(2026, 1, 1, 10, 0),
        exit_time=datetime(2026, 1, 1, 11, 0),
    )

    with pytest.raises(Exception):
        trade.exit_price = 109.0


def test_trade_has_no_order_execution_api(trade_class):
    trade = trade_class(
        position=make_long_position(),
        exit_price=108.0,
        entry_time=datetime(2026, 1, 1, 10, 0),
        exit_time=datetime(2026, 1, 1, 11, 0),
    )

    forbidden = {
        "place_order",
        "modify_order",
        "cancel_order",
        "execute_order",
        "submit_order",
    }
    assert forbidden.isdisjoint(set(dir(trade)))
