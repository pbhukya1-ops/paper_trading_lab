from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.data.candle import Candle
from app.strategy.evidence_request import (
    BreakoutEvidenceRequest,
    EvidenceRequest,
)
from app.strategy.evidence_analyzer import (
    analyze_multi_timeframe_with_evidence,
)


IST = ZoneInfo("Asia/Kolkata")


def make_candles(timeframe: str, step_minutes: int) -> list[Candle]:
    highs = [
        100.0, 105.0, 110.0, 104.0, 103.0,
        120.0, 114.0, 113.0, 130.0, 124.0, 123.0,
    ]
    lows = [
        95.0, 94.0, 90.0, 96.0, 97.0,
        95.0, 99.0, 100.0, 98.0, 104.0, 105.0,
    ]

    candles = []

    for index, (high, low) in enumerate(zip(highs, lows)):
        close = (high + low) / 2.0
        open_price = close - 0.5

        timestamp = datetime(
            2026, 9, 21, 9, 15, tzinfo=IST
        ) + timedelta(minutes=index * step_minutes)

        candles.append(
            Candle(
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=1000.0 + index * 100.0,
                timeframe=timeframe,
                completed=True,
            )
        )

    return candles


def test_evidence_analyzer_preserves_baseline_analysis():
    candles = {
        "5m": make_candles("5m", 5),
        "10m": make_candles("10m", 10),
    }

    results = analyze_multi_timeframe_with_evidence(candles, {})

    assert set(results) == {"5m", "10m"}

    assert results["5m"].analysis_context.breakout is None
    assert results["10m"].analysis_context.breakout is None

    assert (
        results["5m"].analysis_context.market_regime.market_regime
        == "TRENDING_BULLISH"
    )


def test_evidence_analyzer_applies_evidence_to_requested_timeframe():
    candles = {
        "5m": make_candles("5m", 5),
        "10m": make_candles("10m", 10),
    }

    evidence = {
        "5m": EvidenceRequest(
            breakout=BreakoutEvidenceRequest(
                high=105.0,
                low=99.0,
                close=104.0,
                level_price=100.0,
                level_type="HIGH",
                candle_index=5,
                level_index=2,
            )
        )
    }

    results = analyze_multi_timeframe_with_evidence(candles, evidence)

    assert results["5m"].analysis_context.breakout is not None
    assert (
        results["5m"].analysis_context.breakout.breakout_type
        == "BULLISH_BREAKOUT"
    )

    assert results["10m"].analysis_context.breakout is None


def test_evidence_analyzer_preserves_mtf_context():
    candles = {
        "5m": make_candles("5m", 5),
        "10m": make_candles("10m", 10),
    }

    evidence = {
        "5m": EvidenceRequest(
            breakout=BreakoutEvidenceRequest(
                high=105.0,
                low=99.0,
                close=104.0,
                level_price=100.0,
                level_type="HIGH",
                candle_index=5,
                level_index=2,
            )
        )
    }

    results = analyze_multi_timeframe_with_evidence(candles, evidence)

    context = results["5m"].analysis_context

    assert context.mtf_context.higher_timeframe == "10m"
    assert context.mtf_context.relationship == "ALIGNED_BULLISH"


def test_evidence_analyzer_rejects_unknown_evidence_timeframe():
    candles = {
        "5m": make_candles("5m", 5),
    }

    evidence = {
        "10m": EvidenceRequest(),
    }

    try:
        analyze_multi_timeframe_with_evidence(candles, evidence)
    except ValueError as exc:
        assert "Evidence timeframe 10m is not present" in str(exc)
    else:
        raise AssertionError("Expected unknown evidence timeframe failure")
