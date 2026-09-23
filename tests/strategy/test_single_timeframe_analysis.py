from app.strategy.analysis_context import StrategyAnalysisContext
from app.strategy.mtf_context import MTFPriceActionContext
from app.strategy.regime import MarketRegime
from app.strategy.single_timeframe_analysis import SingleTimeframeAnalysis
from app.strategy.trend_quality import TrendQuality


def make_context() -> StrategyAnalysisContext:
    mtf = MTFPriceActionContext(
        timeframe="5m",
        timeframe_regime="BULLISH",
        higher_timeframe=None,
        higher_regime=None,
        relationship="NO_HIGHER_TIMEFRAME",
    )

    regime = MarketRegime(
        structure_regime="BULLISH",
        market_regime="TRENDING_BULLISH",
    )

    trend = TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="NORMAL_TREND",
        confirmation_count=2,
    )

    return StrategyAnalysisContext(
        timeframe="5m",
        mtf_context=mtf,
        market_regime=regime,
        trend_quality=trend,
    )


def make_result() -> SingleTimeframeAnalysis:
    values = (1.0, 2.0, 3.0)

    return SingleTimeframeAnalysis(
        timeframe="5m",
        opens=values,
        highs=(1.5, 2.5, 3.5),
        lows=(0.5, 1.5, 2.5),
        closes=values,
        volumes=(100.0, 110.0, 120.0),
        ema21=values,
        rsi14=(40.0, 41.0, 42.0),
        relative_volume20=(1.0, 1.1, 1.2),
        swing_high_flags=(False, True, False),
        swing_low_flags=(True, False, True),
        high_classifications=(None, "HH", None),
        low_classifications=(None, "HL", None),
        analysis_context=make_context(),
    )


def test_result_validates():
    result = make_result()
    result.validate()


def test_result_rejects_mismatched_series_lengths():
    result = make_result()

    invalid = SingleTimeframeAnalysis(
        timeframe=result.timeframe,
        opens=result.opens,
        highs=result.highs,
        lows=result.lows,
        closes=result.closes,
        volumes=result.volumes,
        ema21=(1.0, 2.0),
        rsi14=result.rsi14,
        relative_volume20=result.relative_volume20,
        swing_high_flags=result.swing_high_flags,
        swing_low_flags=result.swing_low_flags,
        high_classifications=result.high_classifications,
        low_classifications=result.low_classifications,
        analysis_context=result.analysis_context,
    )

    try:
        invalid.validate()
    except ValueError as exc:
        assert "series lengths must match" in str(exc)
    else:
        raise AssertionError("Expected mismatched-length validation failure")


def test_result_rejects_context_timeframe_mismatch():
    result = make_result()

    invalid_context = StrategyAnalysisContext(
        timeframe="15m",
        mtf_context=result.analysis_context.mtf_context,
        market_regime=result.analysis_context.market_regime,
        trend_quality=result.analysis_context.trend_quality,
    )

    invalid = SingleTimeframeAnalysis(
        timeframe="5m",
        opens=result.opens,
        highs=result.highs,
        lows=result.lows,
        closes=result.closes,
        volumes=result.volumes,
        ema21=result.ema21,
        rsi14=result.rsi14,
        relative_volume20=result.relative_volume20,
        swing_high_flags=result.swing_high_flags,
        swing_low_flags=result.swing_low_flags,
        high_classifications=result.high_classifications,
        low_classifications=result.low_classifications,
        analysis_context=invalid_context,
    )

    try:
        invalid.validate()
    except ValueError as exc:
        assert "timeframe must match" in str(exc)
    else:
        raise AssertionError("Expected timeframe validation failure")
