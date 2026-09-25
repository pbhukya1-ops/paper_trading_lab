"""
Evidence-aware orchestration for descriptive strategy analysis.

This module preserves the existing analyzer API and adds an optional,
caller-supplied evidence layer.

It does not:
- discover or select levels,
- generate trading signals,
- score setups,
- recommend actions,
- place orders,
- connect to brokers.
"""

from collections.abc import Mapping, Sequence

from app.data.candle import Candle

from .analysis_context import StrategyAnalysisContext
from .analyzer import analyze_multi_timeframe
from .evidence_context_adapter import apply_evidence_projection
from .evidence_projection import build_evidence_projection
from .evidence_request import EvidenceRequest
from .single_timeframe_analysis import SingleTimeframeAnalysis


def analyze_multi_timeframe_with_evidence(
    candles_by_timeframe: Mapping[str, Sequence[Candle]],
    evidence_by_timeframe: Mapping[str, EvidenceRequest],
) -> dict[str, SingleTimeframeAnalysis]:
    """
    Analyze supplied candles and overlay explicitly supplied evidence.

    Existing analyzer behavior remains the source of the baseline analysis.
    Evidence is optional and may be supplied for only a subset of timeframes.

    An evidence timeframe that is not present in the candle input is rejected.
    """

    unknown_timeframes = set(evidence_by_timeframe) - set(candles_by_timeframe)
    if unknown_timeframes:
        timeframe = sorted(unknown_timeframes)[0]
        raise ValueError(
            f"Evidence timeframe {timeframe} is not present in candle input"
        )

    baseline_results = analyze_multi_timeframe(candles_by_timeframe)

    if not evidence_by_timeframe:
        return baseline_results

    results: dict[str, SingleTimeframeAnalysis] = {}

    for timeframe, result in baseline_results.items():
        request = evidence_by_timeframe.get(timeframe)

        if request is None:
            results[timeframe] = result
            continue

        projection = build_evidence_projection(request)
        context: StrategyAnalysisContext = apply_evidence_projection(
            result.analysis_context,
            projection,
        )

        updated = SingleTimeframeAnalysis(
            timeframe=result.timeframe,
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
            analysis_context=context,
        )

        updated.validate()
        results[timeframe] = updated

    return results
