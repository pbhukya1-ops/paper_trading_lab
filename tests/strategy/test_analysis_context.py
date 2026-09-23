import pytest

from app.strategy.analysis_context import StrategyAnalysisContext
from app.strategy.mtf_context import MTFPriceActionContext
from app.strategy.regime import MarketRegime
from app.strategy.trend_quality import TrendQuality


def make_mtf_context(timeframe="15m"):
    return MTFPriceActionContext(
        timeframe=timeframe,
        timeframe_regime="BULLISH",
        higher_timeframe="30m",
        higher_regime="BULLISH",
        relationship="ALIGNED_BULLISH",
    )


def make_market_regime():
    return MarketRegime(
        structure_regime="BULLISH",
        market_regime="TRENDING_BULLISH",
    )


def make_trend_quality():
    return TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="NORMAL_TREND",
        confirmation_count=2,
    )


def make_context(**overrides):
    values = {
        "timeframe": "15m",
        "mtf_context": make_mtf_context("15m"),
        "market_regime": make_market_regime(),
        "trend_quality": make_trend_quality(),
    }
    values.update(overrides)
    return StrategyAnalysisContext(**values)


def test_valid_minimal_context():
    context = make_context()
    context.validate()


def test_optional_analysis_objects_default_to_none():
    context = make_context()

    assert context.breakout is None
    assert context.volume_breakout is None
    assert context.ema_support is None
    assert context.rsi_pullback is None
    assert context.pullback is None
    assert context.false_breakout is None
    assert context.target_geometry is None


def test_boolean_observations_default_to_false():
    context = make_context()

    assert context.liquidity_observation is False
    assert context.fvg_observation is False
    assert context.inducement_observation is False


def test_timeframe_mismatch_is_rejected():
    context = make_context(
        timeframe="15m",
        mtf_context=make_mtf_context("30m"),
    )

    with pytest.raises(ValueError, match="MTF context timeframe"):
        context.validate()


def test_market_regime_mismatch_is_rejected():
    context = make_context(
        trend_quality=TrendQuality(
            market_regime="TRENDING_BEARISH",
            trend_quality="NORMAL_TREND",
            confirmation_count=2,
        )
    )

    with pytest.raises(
        ValueError,
        match="Trend-quality market regime",
    ):
        context.validate()


def test_invalid_boolean_observation_is_rejected():
    context = make_context(
        liquidity_observation=1,
    )

    with pytest.raises(
        ValueError,
        match="liquidity_observation must be boolean",
    ):
        context.validate()


def test_optional_object_validation_is_called():
    class InvalidObject:
        def validate(self):
            raise ValueError("invalid optional object")

    context = make_context(
        breakout=InvalidObject(),
    )

    with pytest.raises(
        ValueError,
        match="invalid optional object",
    ):
        context.validate()


def test_context_is_frozen():
    context = make_context()

    with pytest.raises(AttributeError):
        context.timeframe = "5m"


def test_valid_reference_context_is_accepted():
    from app.strategy.reference_context import StrategyReferenceContext

    references = StrategyReferenceContext(
        level_index=10,
        level_price=100.0,
        level_type="HIGH",
        reference_index=5,
        move_index=8,
        retest_index=12,
        target_index=15,
    )

    context = make_context(references=references)

    context.validate()
    assert context.references is references


def test_invalid_reference_context_is_rejected():
    from app.strategy.reference_context import StrategyReferenceContext

    references = StrategyReferenceContext(level_index=-1)
    context = make_context(references=references)

    with pytest.raises(
        ValueError,
        match="level_index cannot be negative",
    ):
        context.validate()


def test_reference_context_is_optional():
    context = make_context()

    assert context.references is None
    context.validate()
