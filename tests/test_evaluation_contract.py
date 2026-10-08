from datetime import datetime, timezone

import pytest

from app.evaluation import EvaluationReport, evaluate_trades
from app.position import Position
from app.strategy.targets import TargetGeometry
from app.trade import Trade


def make_trade(direction, exit_price):
    geometry = TargetGeometry(
        direction=direction,
        reference_price=100.0,
        entry_price=100.0,
        stop_price=95.0 if direction == "LONG_GEOMETRY" else 105.0,
        target_price=110.0 if direction == "LONG_GEOMETRY" else 90.0,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    position = Position(
        direction=direction,
        quantity=10.0,
        target_geometry=geometry,
    )

    return Trade(
        position=position,
        exit_price=exit_price,
        entry_time=datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc),
        exit_time=datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc),
    )


def test_empty_evaluation_is_zeroed():
    report = evaluate_trades(())

    assert isinstance(report, EvaluationReport)
    assert report.completed_trade_count == 0
    assert report.winning_trade_count == 0
    assert report.losing_trade_count == 0
    assert report.breakeven_trade_count == 0
    assert report.realized_pnl == 0.0
    assert report.win_rate == 0.0
    assert report.gross_profit == 0.0
    assert report.gross_loss == 0.0
    assert report.profit_factor == 0.0
    assert report.average_realized_pnl == 0.0


def test_mixed_long_and_short_trades_are_evaluated():
    trades = (
        make_trade("LONG_GEOMETRY", 108.0),   # +80
        make_trade("LONG_GEOMETRY", 97.0),    # -30
        make_trade("LONG_GEOMETRY", 100.0),   # 0
        make_trade("SHORT_GEOMETRY", 92.0),   # +80
    )

    report = evaluate_trades(trades)

    assert report.completed_trade_count == 4
    assert report.winning_trade_count == 2
    assert report.losing_trade_count == 1
    assert report.breakeven_trade_count == 1
    assert report.realized_pnl == pytest.approx(130.0)
    assert report.win_rate == pytest.approx(50.0)
    assert report.gross_profit == pytest.approx(160.0)
    assert report.gross_loss == pytest.approx(30.0)
    assert report.profit_factor == pytest.approx(160.0 / 30.0)
    assert report.average_realized_pnl == pytest.approx(32.5)


def test_all_winning_trades_have_zero_profit_factor_without_losses():
    report = evaluate_trades(
        (
            make_trade("LONG_GEOMETRY", 108.0),
            make_trade("SHORT_GEOMETRY", 92.0),
        )
    )

    assert report.gross_profit == pytest.approx(160.0)
    assert report.gross_loss == 0.0
    assert report.profit_factor == 0.0


def test_report_is_immutable():
    report = evaluate_trades((make_trade("LONG_GEOMETRY", 108.0),))

    with pytest.raises((AttributeError, TypeError)):
        report.realized_pnl = -999.0


def test_invalid_trade_input_is_rejected():
    with pytest.raises(TypeError, match="Trade"):
        evaluate_trades((object(),))


def test_input_trade_history_is_not_modified():
    trades = (
        make_trade("LONG_GEOMETRY", 108.0),
        make_trade("LONG_GEOMETRY", 97.0),
    )
    before = trades

    evaluate_trades(trades)

    assert trades == before


def test_report_contains_no_order_execution_api():
    report = evaluate_trades(())

    forbidden = {
        "place_order",
        "submit_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    }

    assert forbidden.isdisjoint(set(dir(report)))
