"""
Multi-timeframe structure context for Paper Trading Lab.

This module combines already-computed structural classifications
from multiple timeframes into a descriptive market-context object.

It does not generate trading signals.
It does not place orders.
It does not infer hidden order-book information.

Weekly structure is treated as a higher-timeframe context and is
not mixed with intraday session-boundary calculations.
"""

from dataclasses import dataclass

from .structure import classify_structure_regime


SUPPORTED_TIMEFRAMES = (
    "5m",
    "10m",
    "15m",
    "30m",
    "1W",
)


@dataclass(frozen=True)
class TimeframeStructure:
    """
    Structural state for one timeframe.
    """

    timeframe: str
    high_classifications: tuple[str | None, ...]
    low_classifications: tuple[str | None, ...]
    regime: str

    def validate(self) -> None:
        if self.timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(
                f"Unsupported timeframe: {self.timeframe}"
            )

        if len(self.high_classifications) != len(
            self.low_classifications
        ):
            raise ValueError(
                "High and low classifications must have equal length"
            )

        if self.regime not in {
            "BULLISH",
            "BEARISH",
            "RANGE_OR_MIXED",
            "INSUFFICIENT_DATA",
        }:
            raise ValueError(
                f"Unsupported structural regime: {self.regime}"
            )


def build_timeframe_structure(
    timeframe: str,
    high_classifications: list[str | None],
    low_classifications: list[str | None],
) -> TimeframeStructure:
    """
    Build a validated structural snapshot for one timeframe.

    The regime is calculated from the existing structure module.
    """

    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    if len(high_classifications) != len(low_classifications):
        raise ValueError(
            "High and low classifications must have equal length"
        )

    regime = classify_structure_regime(
        high_classifications,
        low_classifications,
    )

    snapshot = TimeframeStructure(
        timeframe=timeframe,
        high_classifications=tuple(high_classifications),
        low_classifications=tuple(low_classifications),
        regime=regime,
    )

    snapshot.validate()
    return snapshot


@dataclass(frozen=True)
class MultiTimeframeContext:
    """
    Descriptive structural context across multiple timeframes.

    Higher timeframes provide context for lower timeframes.
    This object does not determine an entry, exit, or trade direction.
    """

    structures: tuple[TimeframeStructure, ...]

    def validate(self) -> None:
        if not self.structures:
            raise ValueError(
                "Multi-timeframe context cannot be empty"
            )

        seen = set()

        for structure in self.structures:
            structure.validate()

            if structure.timeframe in seen:
                raise ValueError(
                    f"Duplicate timeframe: {structure.timeframe}"
                )

            seen.add(structure.timeframe)


def build_mtf_context(
    structures: list[TimeframeStructure],
) -> MultiTimeframeContext:
    """
    Build a validated multi-timeframe structural context.

    Input order is preserved.

    No signal generation occurs.
    """

    context = MultiTimeframeContext(
        structures=tuple(structures),
    )

    context.validate()
    return context


def get_timeframe_structure(
    context: MultiTimeframeContext,
    timeframe: str,
) -> TimeframeStructure | None:
    """
    Retrieve the structural snapshot for one timeframe.

    Returns None when that timeframe is not present.
    """

    context.validate()

    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    for structure in context.structures:
        if structure.timeframe == timeframe:
            return structure

    return None


def higher_timeframe_regime(
    context: MultiTimeframeContext,
    timeframe: str,
) -> str | None:
    """
    Return the regime of the next higher configured timeframe.

    Hierarchy:

        5m  → 10m
        10m → 15m
        15m → 30m
        30m → 1W
        1W  → None

    Missing higher-timeframe data returns None.

    This is context only; it does not create a signal.
    """

    context.validate()

    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    index = SUPPORTED_TIMEFRAMES.index(timeframe)

    if index == len(SUPPORTED_TIMEFRAMES) - 1:
        return None

    higher = get_timeframe_structure(
        context,
        SUPPORTED_TIMEFRAMES[index + 1],
    )

    if higher is None:
        return None

    return higher.regime
