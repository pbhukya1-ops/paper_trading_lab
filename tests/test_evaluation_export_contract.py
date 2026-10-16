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


def test_strict_json_serializer_returns_valid_json():
    from app.evaluation import evaluation_report_to_json

    report = make_report()
    encoded = evaluation_report_to_json(report)
    decoded = json.loads(encoded)

    assert isinstance(encoded, str)
    assert decoded == asdict(report)


@pytest.mark.parametrize("non_finite", [float("nan"), float("inf"), float("-inf")])
def test_strict_json_serializer_rejects_non_finite_values(non_finite):
    from app.evaluation import evaluation_report_to_json

    report = EvaluationReport(
        completed_trade_count=0,
        winning_trade_count=0,
        losing_trade_count=0,
        breakeven_trade_count=0,
        realized_pnl=non_finite,
        win_rate=0.0,
        gross_profit=0.0,
        gross_loss=0.0,
        profit_factor=0.0,
        average_realized_pnl=0.0,
    )

    with pytest.raises(ValueError):
        evaluation_report_to_json(report)


def test_strict_json_serializer_rejects_wrong_input_type():
    from app.evaluation import evaluation_report_to_json

    with pytest.raises(TypeError):
        evaluation_report_to_json({"realized_pnl": 0.0})


def test_export_schema_has_exact_field_names_and_types():
    from app.evaluation import evaluation_report_to_dict

    payload = evaluation_report_to_dict(make_report())

    expected_types = {
        "completed_trade_count": int,
        "winning_trade_count": int,
        "losing_trade_count": int,
        "breakeven_trade_count": int,
        "realized_pnl": float,
        "win_rate": float,
        "gross_profit": float,
        "gross_loss": float,
        "profit_factor": float,
        "average_realized_pnl": float,
    }

    assert set(payload) == set(expected_types)
    for field, expected_type in expected_types.items():
        assert type(payload[field]) is expected_type, field


def test_json_export_has_exact_schema_after_round_trip():
    from app.evaluation import evaluation_report_to_json

    decoded = json.loads(evaluation_report_to_json(make_report()))

    assert set(decoded) == {
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
    assert type(decoded["completed_trade_count"]) is int
    for field in (
        "realized_pnl",
        "win_rate",
        "gross_profit",
        "gross_loss",
        "profit_factor",
        "average_realized_pnl",
    ):
        assert type(decoded[field]) is float, field
