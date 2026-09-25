"""
Pure adapter from EvidenceProjection to StrategyAnalysisContext.

This module preserves the existing analysis context and overlays only the
evidence fields already supported by StrategyAnalysisContext.

It does not:
- select references,
- discover levels,
- score setups,
- generate trading signals,
- recommend actions,
- place orders,
- connect to brokers.
"""

from .analysis_context import StrategyAnalysisContext
from .evidence_projection import EvidenceProjection


def apply_evidence_projection(
    context: StrategyAnalysisContext,
    projection: EvidenceProjection,
) -> StrategyAnalysisContext:
    """
    Return a new validated analysis context containing the supplied evidence.

    The original context is never mutated.

    Only fields already supported by StrategyAnalysisContext are transferred.
    Liquidity-sweep and inducement raw evidence remain outside the context
    because StrategyAnalysisContext has no corresponding fields.
    """

    result = StrategyAnalysisContext(
        timeframe=context.timeframe,
        mtf_context=context.mtf_context,
        market_regime=context.market_regime,
        trend_quality=context.trend_quality,
        references=context.references,
        breakout=projection.breakout,
        volume_breakout=projection.volume_breakout,
        ema_support=projection.ema_support,
        rsi_pullback=projection.rsi_pullback,
        pullback=projection.pullback,
        false_breakout=projection.false_breakout,
        target_geometry=projection.target_geometry,
        liquidity_observation=projection.liquidity_observation,
        fvg_observation=projection.fvg_observation,
        inducement_observation=projection.inducement_observation,
    )

    result.validate()
    return result
