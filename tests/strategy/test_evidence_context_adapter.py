from app.strategy.analysis_context import StrategyAnalysisContext
from app.strategy.evidence_context_adapter import apply_evidence_projection
from app.strategy.evidence_projection import EvidenceProjection
from app.strategy.evidence_request import (
    BreakoutEvidenceRequest,
    EMASupportEvidenceRequest,
    EvidenceRequest,
    FalseBreakoutEvidenceRequest,
    PullbackEvidenceRequest,
    RSIPullbackEvidenceRequest,
    TargetGeometryEvidenceRequest,
    VolumeBreakoutEvidenceRequest,
)
from app.strategy.mtf_context import MTFPriceActionContext
from app.strategy.regime import MarketRegime
from app.strategy.trend_quality import TrendQuality
from app.strategy.evidence_projection import build_evidence_projection


def make_context() -> StrategyAnalysisContext:
    return StrategyAnalysisContext(
        timeframe="15m",
        mtf_context=MTFPriceActionContext(
            timeframe="15m",
            timeframe_regime="BULLISH",
            higher_timeframe="30m",
            higher_regime="BULLISH",
            relationship="ALIGNED_BULLISH",
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


def make_full_projection() -> EvidenceProjection:
    request = EvidenceRequest(
        breakout=BreakoutEvidenceRequest(
            high=105.0,
            low=99.0,
            close=104.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        ),
        volume_breakout=VolumeBreakoutEvidenceRequest(
            high=105.0,
            low=99.0,
            close=104.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
            relative_volume=2.0,
        ),
        ema_support=EMASupportEvidenceRequest(
            price=100.0,
            ema21=100.0,
        ),
        rsi_pullback=RSIPullbackEvidenceRequest(
            current_rsi=42.0,
            previous_rsi=39.0,
        ),
        pullback=PullbackEvidenceRequest(
            reference_price=100.0,
            move_extreme=110.0,
            retest_price=100.0,
            move_type="BULLISH_MOVE",
            reference_index=1,
            move_index=3,
            retest_index=5,
        ),
        false_breakout=FalseBreakoutEvidenceRequest(
            breakout_extreme=105.0,
            failure_close=99.0,
            level_price=100.0,
            breakout_type="BULLISH_BREAKOUT",
            level_index=2,
            failure_candle_index=5,
        ),
        target_geometry=TargetGeometryEvidenceRequest(
            reference_price=100.0,
            entry_price=101.0,
            stop_price=99.0,
            target_price=105.0,
            direction="LONG_GEOMETRY",
        ),
        liquidity_observation=True,
        fvg_observation=True,
        inducement_observation=True,
    )

    return build_evidence_projection(request)


def test_adapter_copies_all_supported_evidence_fields():
    context = make_context()
    projection = make_full_projection()

    result = apply_evidence_projection(context, projection)

    assert result.breakout is projection.breakout
    assert result.volume_breakout is projection.volume_breakout
    assert result.ema_support is projection.ema_support
    assert result.rsi_pullback is projection.rsi_pullback
    assert result.pullback is projection.pullback
    assert result.false_breakout is projection.false_breakout
    assert result.target_geometry is projection.target_geometry


def test_adapter_preserves_core_context():
    context = make_context()
    projection = make_full_projection()

    result = apply_evidence_projection(context, projection)

    assert result.timeframe == context.timeframe
    assert result.mtf_context is context.mtf_context
    assert result.market_regime is context.market_regime
    assert result.trend_quality is context.trend_quality
    assert result.references is context.references


def test_adapter_copies_observation_flags_exactly():
    context = make_context()
    projection = EvidenceProjection(
        liquidity_observation=True,
        fvg_observation=True,
        inducement_observation=True,
    )

    result = apply_evidence_projection(context, projection)

    assert result.liquidity_observation is True
    assert result.fvg_observation is True
    assert result.inducement_observation is True


def test_empty_projection_produces_no_optional_evidence():
    context = make_context()
    projection = EvidenceProjection()

    result = apply_evidence_projection(context, projection)

    assert result.breakout is None
    assert result.volume_breakout is None
    assert result.ema_support is None
    assert result.rsi_pullback is None
    assert result.pullback is None
    assert result.false_breakout is None
    assert result.target_geometry is None

    assert result.liquidity_observation is False
    assert result.fvg_observation is False
    assert result.inducement_observation is False


def test_adapter_does_not_mutate_original_context():
    context = make_context()
    projection = make_full_projection()

    original = context

    result = apply_evidence_projection(context, projection)

    assert result is not original

    assert original.breakout is None
    assert original.volume_breakout is None
    assert original.ema_support is None
    assert original.rsi_pullback is None
    assert original.pullback is None
    assert original.false_breakout is None
    assert original.target_geometry is None

    assert original.liquidity_observation is False
    assert original.fvg_observation is False
    assert original.inducement_observation is False


def test_adapter_result_validates():
    context = make_context()
    projection = make_full_projection()

    result = apply_evidence_projection(context, projection)

    result.validate()


def test_adapter_does_not_expand_context_for_sweep_or_inducement():
    projection = EvidenceProjection(
        liquidity_sweep=object(),
        inducement=object(),
    )

    result = apply_evidence_projection(make_context(), projection)

    assert not hasattr(result, "liquidity_sweep")
    assert not hasattr(result, "inducement")
