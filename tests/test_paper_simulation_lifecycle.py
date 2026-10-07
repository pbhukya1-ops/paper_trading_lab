from datetime import datetime, timedelta

import pytest

from config import assert_paper_only
from app.paper_engine import PaperEngine
from app.paper_simulation import (
    PaperSimulationRequest,
    open_paper_simulation,
)
from app.strategy.analysis_context import StrategyAnalysisContext
from app.strategy.mtf_context import MTFPriceActionContext
from app.strategy.regime import MarketRegime
from app.strategy.targets import TargetGeometry
from app.strategy.trend_quality import TrendQuality


def make_context():
    return StrategyAnalysisContext(
        timeframe="5m",
        mtf_context=MTFPriceActionContext(
            timeframe="5m",
            timeframe_regime="BULLISH",
            higher_timeframe=None,
            higher_regime=None,
            relationship="NO_HIGHER_TIMEFRAME",
        ),
        market_regime=MarketRegime(
            structure_regime="BULLISH",
            market_regime="TRENDING_BULLISH",
        ),
        trend_quality=TrendQuality(
            market_regime="TRENDING_BULLISH",
            trend_quality="NORMAL_TREND",
            confirmation_count=2,
        ),
    )


@pytest.mark.parametrize(
    "direction,entry_price,stop_price,target_price,exit_price,expected_pnl",
    [
        ("LONG_GEOMETRY", 100.0, 95.0, 110.0, 108.0, 1600.0),
        ("SHORT_GEOMETRY", 100.0, 105.0, 90.0, 92.0, 1600.0),
    ],
)
def test_end_to_end_paper_simulation_lifecycle(
    direction,
    entry_price,
    stop_price,
    target_price,
    exit_price,
    expected_pnl,
):
    assert_paper_only()

    context = make_context()

    geometry = TargetGeometry(
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        reference_price=entry_price,
        risk_distance=5.0,
        reward_distance=10.0,
        reward_risk_ratio=2.0,
    )

    entry_time = datetime(2026, 10, 7, 10, 0, 0)
    exit_time = entry_time + timedelta(minutes=5)

    request = PaperSimulationRequest(
        analysis_context=context,
        direction=direction,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        entry_time=entry_time,
        target_geometry=geometry,
    )

    engine = PaperEngine()
    position = open_paper_simulation(engine, request)

    assert engine.paper_only is True
    assert engine.current_position == position
    assert engine.open_position_count == 1
    assert position.direction == direction
    assert position.quantity == pytest.approx(200.0)
    assert position.target_geometry == geometry

    trade = engine.close_position(
        exit_price=exit_price,
        exit_time=exit_time,
    )

    assert trade.position == position
    assert trade.realized_pnl == pytest.approx(expected_pnl)
    assert engine.current_position is None
    assert engine.open_position_count == 0
    assert len(engine.trade_history) == 1
    assert engine.account_snapshot["realized_pnl"] == pytest.approx(
        expected_pnl
    )


def test_paper_simulation_lifecycle_is_paper_only():
    assert_paper_only()

    engine = PaperEngine()

    assert engine.paper_only is True
    assert not hasattr(engine, "place_order")
    assert not hasattr(engine, "submit_order")
    assert not hasattr(engine, "execute_order")
