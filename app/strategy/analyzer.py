"""
Paper Trading Lab — descriptive strategy analysis orchestration.

This module combines validated OHLCV candle data with the existing
pure analytical components.

It does NOT:
- generate trading signals,
- place orders,
- connect to brokers,
- resample candles,
- mutate candle data.
"""

from collections.abc import Mapping, Sequence

from app.data.candle import Candle
from app.data.multi_timeframe_input import MultiTimeframeInput
from app.data.quality_gate import validate_data_quality

from .analysis_context import StrategyAnalysisContext
from .indicators import ema, relative_volume, rsi
from .mtf_context import build_mtf_price_action_context
from .mtf_structure import (
    TimeframeStructure,
    build_mtf_context,
    build_timeframe_structure,
)
from .regime import regime_from_structure
from .single_timeframe_analysis import SingleTimeframeAnalysis
from .structure import (
    classify_swing_highs,
    classify_swing_lows,
    swing_highs,
    swing_lows,
)
from .trend_quality import trend_quality_from_structure


def _calculate_timeframe_components(
    timeframe: str,
    candles: Sequence[Candle],
) -> dict[str, object]:
    """
    Calculate the independent descriptive components for one timeframe.

    No MTF relationship is calculated here because that requires all
    supplied timeframe structures to be known first.
    """

    validate_data_quality(candles)

    if not candles:
        raise ValueError("Candle series cannot be empty")

    if candles[0].timeframe != timeframe:
        raise ValueError(
            f"Timeframe key {timeframe} does not match "
            f"candle timeframe {candles[0].timeframe}"
        )

    opens = tuple(float(candle.open) for candle in candles)
    highs = tuple(float(candle.high) for candle in candles)
    lows = tuple(float(candle.low) for candle in candles)
    closes = tuple(float(candle.close) for candle in candles)
    volumes = tuple(float(candle.volume) for candle in candles)

    ema21 = tuple(ema(closes, period=21))
    rsi14 = tuple(rsi(closes, period=14))
    relative_volume20 = tuple(
        relative_volume(volumes, period=20)
    )

    swing_high_flags = tuple(swing_highs(highs))
    swing_low_flags = tuple(swing_lows(lows))

    high_classifications = tuple(
        classify_swing_highs(highs, swing_high_flags)
    )
    low_classifications = tuple(
        classify_swing_lows(lows, swing_low_flags)
    )

    structure = build_timeframe_structure(
        timeframe=timeframe,
        high_classifications=high_classifications,
        low_classifications=low_classifications,
    )

    market_regime = regime_from_structure(
        high_classifications,
        low_classifications,
    )

    trend_quality = trend_quality_from_structure(
        high_classifications,
        low_classifications,
    )

    return {
        "opens": opens,
        "highs": highs,
        "lows": lows,
        "closes": closes,
        "volumes": volumes,
        "ema21": ema21,
        "rsi14": rsi14,
        "relative_volume20": relative_volume20,
        "swing_high_flags": swing_high_flags,
        "swing_low_flags": swing_low_flags,
        "high_classifications": high_classifications,
        "low_classifications": low_classifications,
        "structure": structure,
        "market_regime": market_regime,
        "trend_quality": trend_quality,
    }


def analyze_multi_timeframe(
    candles_by_timeframe: Mapping[str, Sequence[Candle]],
) -> dict[str, SingleTimeframeAnalysis]:
    """
    Analyze already-supplied candles across one or more timeframes.

    The input is validated as a MultiTimeframeInput before analysis.

    Returns immutable SingleTimeframeAnalysis objects keyed by timeframe.

    This is descriptive analysis only.
    """

    input_data = MultiTimeframeInput(
        candles_by_timeframe=candles_by_timeframe,
    )
    input_data.validate()

    components_by_timeframe: dict[str, dict[str, object]] = {}

    for timeframe, candles in candles_by_timeframe.items():
        components_by_timeframe[timeframe] = _calculate_timeframe_components(
            timeframe,
            candles,
        )

    structures = [
        components["structure"]
        for components in components_by_timeframe.values()
    ]

    mtf_context = build_mtf_context(
        structures  # type: ignore[arg-type]
    )

    results: dict[str, SingleTimeframeAnalysis] = {}

    for timeframe, components in components_by_timeframe.items():
        mtf_price_action = build_mtf_price_action_context(
            mtf_context,
            timeframe,
        )

        analysis_context = StrategyAnalysisContext(
            timeframe=timeframe,
            mtf_context=mtf_price_action,
            market_regime=components["market_regime"],  # type: ignore[arg-type]
            trend_quality=components["trend_quality"],  # type: ignore[arg-type]
        )
        analysis_context.validate()

        result = SingleTimeframeAnalysis(
            timeframe=timeframe,
            opens=components["opens"],  # type: ignore[arg-type]
            highs=components["highs"],  # type: ignore[arg-type]
            lows=components["lows"],  # type: ignore[arg-type]
            closes=components["closes"],  # type: ignore[arg-type]
            volumes=components["volumes"],  # type: ignore[arg-type]
            ema21=components["ema21"],  # type: ignore[arg-type]
            rsi14=components["rsi14"],  # type: ignore[arg-type]
            relative_volume20=components["relative_volume20"],  # type: ignore[arg-type]
            swing_high_flags=components["swing_high_flags"],  # type: ignore[arg-type]
            swing_low_flags=components["swing_low_flags"],  # type: ignore[arg-type]
            high_classifications=components["high_classifications"],  # type: ignore[arg-type]
            low_classifications=components["low_classifications"],  # type: ignore[arg-type]
            analysis_context=analysis_context,
        )
        result.validate()
        results[timeframe] = result

    return results


def analyze_timeframe(
    timeframe: str,
    candles: Sequence[Candle],
) -> SingleTimeframeAnalysis:
    """
    Analyze one timeframe as a standalone analytical context.

    A standalone timeframe has no configured higher timeframe, so its
    MTF relationship is NO_HIGHER_TIMEFRAME.
    """

    return analyze_multi_timeframe(
        {timeframe: candles}
    )[timeframe]
