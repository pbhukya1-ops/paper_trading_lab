"""
Multi-timeframe price-action context for Paper Trading Lab.

This module describes the relationship between a timeframe's
structure and its configured higher timeframe.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- infer hidden order-book information.

The output is descriptive market context only.
"""

from dataclasses import dataclass

from .mtf_structure import (
    SUPPORTED_TIMEFRAMES,
    MultiTimeframeContext,
    get_timeframe_structure,
    higher_timeframe_regime,
)


@dataclass(frozen=True)
class MTFPriceActionContext:
    """
    Descriptive relationship between a timeframe and its
    next configured higher timeframe.
    """

    timeframe: str
    timeframe_regime: str
    higher_timeframe: str | None
    higher_regime: str | None
    relationship: str

    def validate(self) -> None:
        if self.timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(
                f"Unsupported timeframe: {self.timeframe}"
            )

        if self.timeframe_regime not in {
            "BULLISH",
            "BEARISH",
            "RANGE_OR_MIXED",
            "INSUFFICIENT_DATA",
        }:
            raise ValueError(
                f"Unsupported timeframe regime: "
                f"{self.timeframe_regime}"
            )

        if self.higher_timeframe is not None:
            if self.higher_timeframe not in SUPPORTED_TIMEFRAMES:
                raise ValueError(
                    f"Unsupported higher timeframe: "
                    f"{self.higher_timeframe}"
                )

        if self.higher_regime is not None:
            if self.higher_regime not in {
                "BULLISH",
                "BEARISH",
                "RANGE_OR_MIXED",
                "INSUFFICIENT_DATA",
            }:
                raise ValueError(
                    f"Unsupported higher timeframe regime: "
                    f"{self.higher_regime}"
                )

        if self.relationship not in {
            "ALIGNED_BULLISH",
            "ALIGNED_BEARISH",
            "COUNTER_TREND_BULLISH",
            "COUNTER_TREND_BEARISH",
            "HIGHER_TIMEFRAME_MIXED",
            "LOWER_TIMEFRAME_MIXED",
            "INSUFFICIENT_CONTEXT",
            "NO_HIGHER_TIMEFRAME",
        }:
            raise ValueError(
                f"Unsupported MTF relationship: "
                f"{self.relationship}"
            )


def _classify_relationship(
    timeframe_regime: str,
    higher_regime: str | None,
    has_higher_timeframe: bool,
) -> str:
    """
    Classify the descriptive relationship between two regimes.

    This function does not create a trading signal.
    """

    if not has_higher_timeframe:
        return "NO_HIGHER_TIMEFRAME"

    if (
        timeframe_regime == "INSUFFICIENT_DATA"
        or higher_regime is None
        or higher_regime == "INSUFFICIENT_DATA"
    ):
        return "INSUFFICIENT_CONTEXT"

    if (
        timeframe_regime == "BULLISH"
        and higher_regime == "BULLISH"
    ):
        return "ALIGNED_BULLISH"

    if (
        timeframe_regime == "BEARISH"
        and higher_regime == "BEARISH"
    ):
        return "ALIGNED_BEARISH"

    if (
        timeframe_regime == "BULLISH"
        and higher_regime == "BEARISH"
    ):
        return "COUNTER_TREND_BULLISH"

    if (
        timeframe_regime == "BEARISH"
        and higher_regime == "BULLISH"
    ):
        return "COUNTER_TREND_BEARISH"

    if higher_regime == "RANGE_OR_MIXED":
        return "HIGHER_TIMEFRAME_MIXED"

    if timeframe_regime == "RANGE_OR_MIXED":
        return "LOWER_TIMEFRAME_MIXED"

    return "INSUFFICIENT_CONTEXT"


def build_mtf_price_action_context(
    context: MultiTimeframeContext,
    timeframe: str,
) -> MTFPriceActionContext:
    """
    Build descriptive price-action context for one timeframe.

    The relationship is based only on already-computed structural
    regimes.

    No trading signal is generated.
    """

    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    structure = get_timeframe_structure(
        context,
        timeframe,
    )

    if structure is None:
        raise ValueError(
            f"Timeframe {timeframe} is not present in the MTF context"
        )

    higher = higher_timeframe_regime(
        context,
        timeframe,
    )

    timeframe_index = SUPPORTED_TIMEFRAMES.index(timeframe)

    if timeframe_index == len(SUPPORTED_TIMEFRAMES) - 1:
        higher_timeframe = None
    else:
        higher_timeframe = SUPPORTED_TIMEFRAMES[
            timeframe_index + 1
        ]

    relationship = _classify_relationship(
        timeframe_regime=structure.regime,
        higher_regime=higher,
        has_higher_timeframe=higher_timeframe is not None,
    )

    result = MTFPriceActionContext(
        timeframe=timeframe,
        timeframe_regime=structure.regime,
        higher_timeframe=higher_timeframe,
        higher_regime=higher,
        relationship=relationship,
    )

    result.validate()
    return result
