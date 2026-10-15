import json
from dataclasses import asdict

import pytest

from app.evaluation import EvaluationReport, evaluate_trades


def make_report():
    return evaluate_trades(())


def test_export_function_returns_all_report_fields():
    from app.evaluation import evaluation_report_to_dict

    report = make_report()
    payload = evaluation_report_to_dict(report)

    assert payload == asdict(report)
    assert payload is not report.__dict__


def test_export_function_rejects_wrong_input_type():
    from app.evaluation import evaluation_report_to_dict

    with pytest.raises(TypeError):
        evaluation_report_to_dict({"realized_pnl": 0.0})


def test_report_fields_are_exportable_as_json():
    report = make_report()
    payload = asdict(report)
    encoded = json.dumps(payload, sort_keys=True)
    decoded = json.loads(encoded)

    assert isinstance(decoded, dict)
    assert decoded["completed_trade_count"] == 0
    assert decoded["realized_pnl"] == 0.0


def test_export_preserves_all_report_fields():
    report = make_report()
    payload = asdict(report)

    assert set(payload) == {
        "completed_trade_count",
        "winning_trade_count",
        "losing_trade_count",
        "breakeven_trade_count",
        "realized_pnl",
        "win_rate",
        "gross_profit",
        "gross_loss",
        "profit_factor",
        "average_realized_pnl",
    }


def test_export_does_not_mutate_immutable_report():
    report = make_report()
    payload = asdict(report)
    payload["realized_pnl"] = 999.0

    assert report.realized_pnl == 0.0


def test_export_payload_rejects_non_finite_json_values():
    payload = asdict(make_report())
    payload["realized_pnl"] = float("nan")

    with pytest.raises(ValueError):
        json.dumps(payload, allow_nan=False)
