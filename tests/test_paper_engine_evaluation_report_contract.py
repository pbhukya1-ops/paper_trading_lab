from dataclasses import FrozenInstanceError

import pytest

from app.evaluation import EvaluationReport, evaluate_trades
from app.paper_engine import PaperEngine
from tests.test_paper_engine_performance_snapshot_contract import complete_trade


def test_evaluation_report_is_available_and_zeroed_when_empty():
    engine = PaperEngine()

    report = engine.evaluation_report

    assert isinstance(report, EvaluationReport)
    assert report == evaluate_trades(())
    assert report.completed_trade_count == 0
    assert report.realized_pnl == 0.0


def test_evaluation_report_matches_completed_trade_history():
    engine = PaperEngine()
    complete_trade(engine, 108.0, 1)
    complete_trade(engine, 97.0, 2)
    complete_trade(engine, 100.0, 3)

    report = engine.evaluation_report

    assert report == evaluate_trades(engine.trade_history)
    assert report.completed_trade_count == 3
    assert report.winning_trade_count == 1
    assert report.losing_trade_count == 1
    assert report.breakeven_trade_count == 1
    assert report.realized_pnl == 50.0
    assert report.win_rate == pytest.approx(100.0 / 3.0)


def test_evaluation_report_is_immutable():
    engine = PaperEngine()

    with pytest.raises(AttributeError):
        engine.evaluation_report = evaluate_trades(())

    with pytest.raises(FrozenInstanceError):
        engine.evaluation_report.realized_pnl = 123.0


def test_evaluation_report_tracks_reset_trade_history():
    engine = PaperEngine()
    complete_trade(engine, 108.0, 1)

    engine.reset()

    assert engine.evaluation_report == evaluate_trades(())
    assert engine.evaluation_report.completed_trade_count == 0


def test_evaluation_report_does_not_change_performance_snapshot_contract():
    engine = PaperEngine()

    assert set(engine.performance_snapshot) == {
        "completed_trade_count",
        "winning_trade_count",
        "losing_trade_count",
        "breakeven_trade_count",
        "realized_pnl",
        "win_rate",
    }
