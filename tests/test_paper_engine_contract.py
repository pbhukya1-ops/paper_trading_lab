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
