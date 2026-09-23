"""
Trend/range regime context for Paper Trading Lab.

This module interprets confirmed structural classifications
into a broader descriptive market regime.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.

The output is descriptive market context only.
"""

from dataclasses import dataclass
from collections.abc import Sequence


VALID_STRUCTURE_REGIMES = {
    "BULLISH",
    "BEARISH",
    "RANGE_OR_MIXED",
    "INSUFFICIENT_DATA",
}

VALID_MARKET_REGIMES = {
    "TRENDING_BULLISH",
    "TRENDING_BEARISH",
    "RANGE",
    "TRANSITION",
    "INSUFFICIENT_DATA",
}

DEFAULT_MIN_CONFIRMATIONS = 2


@dataclass(frozen=True)
class MarketRegime:
    """
    Descriptive market regime derived from structural regimes.
    """

    structure_regime: str
    market_regime: str

    def validate(self) -> None:
        if self.structure_regime not in VALID_STRUCTURE_REGIMES:
            raise ValueError(
                f"Unsupported structure regime: "
                f"{self.structure_regime}"
            )

        if self.market_regime not in VALID_MARKET_REGIMES:
            raise ValueError(
                f"Unsupported market regime: "
                f"{self.market_regime}"
            )


def _confirmed_pairs(
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
) -> list[tuple[str, str]]:
    """
    Return aligned confirmed high/low structural classifications.

    Entries where either side is missing are excluded.
    Input sequences are not modified.
    """

    if len(high_classifications) != len(low_classifications):
        raise ValueError(
            "High and low classifications must have equal length"
        )

    pairs = []

    for high, low in zip(
        high_classifications,
        low_classifications,
    ):
        if high is None or low is None:
            continue

        pairs.append((high, low))

    return pairs


def classify_market_regime(
    structure_regime: str,
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
    min_confirmations: int = DEFAULT_MIN_CONFIRMATIONS,
) -> MarketRegime:
    """
    Convert structural classifications into a broader
    descriptive market regime.

    A trend requires repeated structural confirmation.

    Bullish trend:
        minimum confirmed HH + HL observations.

    Bearish trend:
        minimum confirmed LH + LL observations.

    Range:
        explicitly mixed/range structural regime.

    Transition:
        conflicting structure that does not establish a
        sustained directional regime.

    Insufficient data:
        fewer than the required confirmed observations.

    This function does not generate trading signals.
    """

    if structure_regime not in VALID_STRUCTURE_REGIMES:
        raise ValueError(
            f"Unsupported structure regime: {structure_regime}"
        )

    if min_confirmations <= 0:
        raise ValueError(
            "min_confirmations must be greater than zero"
        )

    pairs = _confirmed_pairs(
        high_classifications,
        low_classifications,
    )

    if len(pairs) < min_confirmations:
        result = MarketRegime(
            structure_regime=structure_regime,
            market_regime="INSUFFICIENT_DATA",
        )
        result.validate()
        return result

    if structure_regime == "INSUFFICIENT_DATA":
        result = MarketRegime(
            structure_regime=structure_regime,
            market_regime="INSUFFICIENT_DATA",
        )
        result.validate()
        return result

    bullish_count = sum(
        high == "HH" and low == "HL"
        for high, low in pairs
    )

    bearish_count = sum(
        high == "LH" and low == "LL"
        for high, low in pairs
    )

    recent_pairs = pairs[-min_confirmations:]

    recent_bullish = all(
        high == "HH" and low == "HL"
        for high, low in recent_pairs
    )

    recent_bearish = all(
        high == "LH" and low == "LL"
        for high, low in recent_pairs
    )

    if (
        structure_regime == "BULLISH"
        and bullish_count >= min_confirmations
        and recent_bullish
    ):
        market_regime = "TRENDING_BULLISH"

    elif (
        structure_regime == "BEARISH"
        and bearish_count >= min_confirmations
        and recent_bearish
    ):
        market_regime = "TRENDING_BEARISH"

    elif structure_regime == "RANGE_OR_MIXED":
        market_regime = "RANGE"

    else:
        market_regime = "TRANSITION"

    result = MarketRegime(
        structure_regime=structure_regime,
        market_regime=market_regime,
    )

    result.validate()
    return result


def regime_from_structure(
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
    min_confirmations: int = DEFAULT_MIN_CONFIRMATIONS,
) -> MarketRegime:
    """
    Infer the structural regime and convert it into a broader
    descriptive market regime.

    A directional regime is accepted only when the required
    number of recent confirmed structural pairs supports it.
    """

    if len(high_classifications) != len(low_classifications):
        raise ValueError(
            "High and low classifications must have equal length"
        )

    if min_confirmations <= 0:
        raise ValueError(
            "min_confirmations must be greater than zero"
        )

    pairs = _confirmed_pairs(
        high_classifications,
        low_classifications,
    )

    if len(pairs) < min_confirmations:
        structure_regime = "INSUFFICIENT_DATA"

    else:
        recent_pairs = pairs[-min_confirmations:]

        recent_bullish = all(
            high == "HH" and low == "HL"
            for high, low in recent_pairs
        )

        recent_bearish = all(
            high == "LH" and low == "LL"
            for high, low in recent_pairs
        )

        if recent_bullish:
            structure_regime = "BULLISH"

        elif recent_bearish:
            structure_regime = "BEARISH"

        else:
            structure_regime = "RANGE_OR_MIXED"

    return classify_market_regime(
        structure_regime=structure_regime,
        high_classifications=high_classifications,
        low_classifications=low_classifications,
        min_confirmations=min_confirmations,
    )
