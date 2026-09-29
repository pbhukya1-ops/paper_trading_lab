from datetime import datetime

import pytest

from app.paper_simulation import PaperSimulationRequest
from app.strategy.analysis_context import StrategyAnalysisContext
from app.strategy.mtf_context import MTFPriceActionContext
from app.strategy.regime import MarketRegime
from app.strategy.targets import TargetGeometry
from app.strategy.trend_quality import TrendQuality


def make_analysis_context():
    mtf_context = MTFPriceActionContext(
        timeframe="5m",
        timeframe_regime="BULLISH",
        higher_timeframe=None,
        higher_regime=None,
        relationship="NO_HIGHER_TIMEFRAME",
    )

    market_regime = MarketRegime(
        structure_regime="BULLISH",
        market_regime="TRENDING_BULLISH",
    )

    trend_quality = TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="NORMAL_TREND",
        confirmation_count=2,
    )

    context = StrategyAnalysisContext(
        timeframe="5m",
        mtf_context=mtf_context,
        market_regime=market_regime,
        trend_quality=trend_quality,
    )
    context.validate()
    return context


@pytest.mark.parametrize(
    "direction,entry_price,stop_price,target_price",
    [
        ("LONG_GEOMETRY", 100.0, 95.0, 110.0),
        ("SHORT_GEOMETRY", 100.0, 105.0, 90.0),
    ],
)
def test_simulation_request_accepts_explicit_geometry(
    direction,
    entry_price,
    stop_price,
    target_price,
):
    geometry = TargetGeometry(
        direction=direction,
        reference_price=entry_price,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    request = PaperSimulationRequest(
        analysis_context=make_analysis_context(),
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        entry_time=datetime(2026, 1, 1, 10, 0),
        target_geometry=geometry,
    )

    assert request.direction == direction
    assert request.entry_price == entry_price
    assert request.stop_price == stop_price
    assert request.target_price == target_price
    assert request.target_geometry == geometry
    assert isinstance(request.entry_time, datetime)


def test_simulation_request_rejects_direction_geometry_mismatch():
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

    with pytest.raises(
        ValueError,
        match="direction must match target_geometry direction",
    ):
        PaperSimulationRequest(
            analysis_context=make_analysis_context(),
            direction="SHORT_GEOMETRY",
            entry_price=100.0,
            stop_price=95.0,
            target_price=110.0,
            entry_time=datetime(2026, 1, 1, 10, 0),
            target_geometry=geometry,
        )


def test_simulation_request_rejects_price_geometry_mismatch():
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

    with pytest.raises(
        ValueError,
        match="entry_price must match target_geometry entry_price",
    ):
        PaperSimulationRequest(
            analysis_context=make_analysis_context(),
            direction="LONG_GEOMETRY",
            entry_price=101.0,
            stop_price=95.0,
            target_price=110.0,
            entry_time=datetime(2026, 1, 1, 10, 0),
            target_geometry=geometry,
        )


def test_simulation_request_is_immutable():
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

    request = PaperSimulationRequest(
        analysis_context=make_analysis_context(),
        direction="LONG_GEOMETRY",
        entry_price=100.0,
        stop_price=95.0,
        target_price=110.0,
        entry_time=datetime(2026, 1, 1, 10, 0),
        target_geometry=geometry,
    )

    with pytest.raises(AttributeError):
        request.direction = "SHORT_GEOMETRY"


@pytest.mark.parametrize(
    "direction,entry_price,stop_price,target_price",
    [
        ("LONG_GEOMETRY", 100.0, 95.0, 110.0),
        ("SHORT_GEOMETRY", 100.0, 105.0, 90.0),
    ],
)
def test_open_paper_simulation_creates_risk_sized_position(
    direction,
    entry_price,
    stop_price,
    target_price,
):
    from app.paper_engine import PaperEngine
    from app.paper_simulation import open_paper_simulation

    geometry = TargetGeometry(
        direction=direction,
        reference_price=entry_price,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    request = PaperSimulationRequest(
        analysis_context=make_analysis_context(),
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        entry_time=datetime(2026, 1, 1, 10, 0),
        target_geometry=geometry,
    )

    engine = PaperEngine()

    position = open_paper_simulation(engine, request)

    expected_quantity = engine.risk_manager.calculate_position_size(
        capital=engine.capital,
        entry_price=entry_price,
        stop_price=stop_price,
        direction=direction,
    )

    assert position == engine.current_position
    assert position.direction == direction
    assert position.quantity == pytest.approx(expected_quantity)
    assert position.target_geometry == geometry
    assert engine.open_position_count == 1


def test_open_paper_simulation_does_not_add_order_api():
    from app.paper_engine import PaperEngine
    from app.paper_simulation import open_paper_simulation

    assert not hasattr(PaperEngine(), "place_order")
    assert not hasattr(PaperEngine(), "submit_order")
    assert not hasattr(PaperEngine(), "execute_order")
    assert callable(open_paper_simulation)

@pytest.mark.parametrize(
    "direction,entry_price,stop_price,target_price,exit_price,expected_pnl",
    [
        ("LONG_GEOMETRY", 100.0, 95.0, 110.0, 108.0, 1600.0),
        ("SHORT_GEOMETRY", 100.0, 105.0, 90.0, 92.0, 1600.0),
    ],
)
def test_open_paper_simulation_closes_with_correct_realized_pnl(
    direction,
    entry_price,
    stop_price,
    target_price,
    exit_price,
    expected_pnl,
):
    from app.paper_engine import PaperEngine
    from app.paper_simulation import open_paper_simulation

    entry_time = datetime(2026, 1, 2, 10, 0, 0)
    exit_time = datetime(2026, 1, 2, 10, 15, 0)

    geometry = TargetGeometry(
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
    )

    request = PaperSimulationRequest(
        analysis_context=make_analysis_context(),
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        entry_time=entry_time,
        target_geometry=geometry,
    )

    engine = PaperEngine()

    position = open_paper_simulation(engine, request)

    trade = engine.close_position(
        exit_price=exit_price,
        exit_time=exit_time,
    )

    assert position == trade.position
    assert trade.realized_pnl == pytest.approx(expected_pnl)
    assert engine.current_position is None
    assert engine.open_position_count == 0
    assert engine.account_snapshot["realized_pnl"] == pytest.approx(expected_pnl)

@pytest.mark.parametrize(
    "direction,entry_price,stop_price,target_price,exit_price,expected_pnl",
    [
        ("LONG_GEOMETRY", 100.0, 95.0, 110.0, 108.0, 1600.0),
        ("SHORT_GEOMETRY", 100.0, 105.0, 90.0, 92.0, 1600.0),
    ],
)
def test_open_paper_simulation_closes_with_correct_realized_pnl(
    direction,
    entry_price,
    stop_price,
    target_price,
    exit_price,
    expected_pnl,
):
    from app.paper_engine import PaperEngine
    from app.paper_simulation import open_paper_simulation

    entry_time = datetime(2026, 1, 2, 10, 0, 0)
    exit_time = datetime(2026, 1, 2, 10, 15, 0)

    geometry = TargetGeometry(
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        reference_price=entry_price,
        risk_distance=abs(entry_price - stop_price),
        reward_distance=abs(target_price - entry_price),
        reward_risk_ratio=2.0,
    )

    request = PaperSimulationRequest(
        analysis_context=make_analysis_context(),
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        entry_time=entry_time,
        target_geometry=geometry,
    )

    engine = PaperEngine()

    position = open_paper_simulation(engine, request)

    trade = engine.close_position(
        exit_price=exit_price,
        exit_time=exit_time,
    )

    assert position == trade.position
    assert trade.realized_pnl == pytest.approx(expected_pnl)
    assert engine.current_position is None
    assert engine.open_position_count == 0
    assert engine.account_snapshot["realized_pnl"] == pytest.approx(expected_pnl)
