"""
Trend-quality and structure-consistency context for Paper Trading Lab.

This module evaluates the consistency of already-confirmed
structural classifications.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.

The output is descriptive market context only.
"""

from dataclasses import dataclass
from collections.abc import Sequence


VALID_TREND_QUALITIES = {
    "STRONG_TREND",
    "NORMAL_TREND",
    "WEAK_TREND",
    "RANGE",
    "TRANSITION",
    "INSUFFICIENT_DATA",
}


DEFAULT_MIN_CONFIRMATIONS = 2
DEFAULT_STRONG_CONFIRMATIONS = 3


@dataclass(frozen=True)
class TrendQuality:
    """
    Descriptive quality assessment of structural consistency.
    """

    market_regime: str
    trend_quality: str
    confirmation_count: int

    def validate(self) -> None:
        if self.market_regime not in {
            "TRENDING_BULLISH",
            "TRENDING_BEARISH",
            "RANGE",
            "TRANSITION",
            "INSUFFICIENT_DATA",
        }:
            raise ValueError(
                f"Unsupported market regime: {self.market_regime}"
            )

        if self.trend_quality not in VALID_TREND_QUALITIES:
            raise ValueError(
                f"Unsupported trend quality: {self.trend_quality}"
            )

        if self.confirmation_count < 0:
            raise ValueError(
                "Confirmation count cannot be negative"
            )


def _confirmed_pairs(
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
) -> list[tuple[str, str]]:
    """
    Return only aligned confirmed structural pairs.

    Inputs are not modified.
    """

    if len(high_classifications) != len(low_classifications):
        raise ValueError(
            "High and low classifications must have equal length"
        )

    pairs: list[tuple[str, str]] = []

    for high, low in zip(
        high_classifications,
        low_classifications,
    ):
        if high is None or low is None:
            continue

        pairs.append((high, low))

    return pairs


def classify_trend_quality(
    market_regime: str,
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
    min_confirmations: int = DEFAULT_MIN_CONFIRMATIONS,
    strong_confirmations: int = DEFAULT_STRONG_CONFIRMATIONS,
) -> TrendQuality:
    """
    Assess structural consistency within an existing market regime.

    Rules:

    STRONG_TREND:
        At least `strong_confirmations` consecutive recent
        structural pairs support the same direction.

    NORMAL_TREND:
        At least `min_confirmations` consecutive recent
        structural pairs support the same direction.

    WEAK_TREND:
        A directional market regime exists but the requested
        confirmation threshold is not fully satisfied.

    RANGE:
        Existing range regime.

    TRANSITION:
        Conflicting directional structure.

    INSUFFICIENT_DATA:
        Not enough confirmed structural pairs.

    This function does not generate trading signals.
    """

    if market_regime not in {
        "TRENDING_BULLISH",
        "TRENDING_BEARISH",
        "RANGE",
        "TRANSITION",
        "INSUFFICIENT_DATA",
    }:
        raise ValueError(
            f"Unsupported market regime: {market_regime}"
        )

    if min_confirmations <= 0:
        raise ValueError(
            "min_confirmations must be greater than zero"
        )

    if strong_confirmations < min_confirmations:
        raise ValueError(
            "strong_confirmations must be greater than or equal "
            "to min_confirmations"
        )

    pairs = _confirmed_pairs(
        high_classifications,
        low_classifications,
    )

    if len(pairs) < min_confirmations:
        result = TrendQuality(
            market_regime=market_regime,
            trend_quality="INSUFFICIENT_DATA",
            confirmation_count=len(pairs),
        )
        result.validate()
        return result

    if market_regime == "INSUFFICIENT_DATA":
        result = TrendQuality(
            market_regime=market_regime,
            trend_quality="INSUFFICIENT_DATA",
            confirmation_count=len(pairs),
        )
        result.validate()
        return result

    if market_regime == "RANGE":
        result = TrendQuality(
            market_regime=market_regime,
            trend_quality="RANGE",
            confirmation_count=len(pairs),
        )
        result.validate()
        return result

    if market_regime == "TRANSITION":
        result = TrendQuality(
            market_regime=market_regime,
            trend_quality="TRANSITION",
            confirmation_count=len(pairs),
        )
        result.validate()
        return result

    bullish_pair = ("HH", "HL")
    bearish_pair = ("LH", "LL")

    target_pair = (
        bullish_pair
        if market_regime == "TRENDING_BULLISH"
        else bearish_pair
    )

    recent_minimum = pairs[-min_confirmations:]

    if not all(
        pair == target_pair
        for pair in recent_minimum
    ):
        result = TrendQuality(
            market_regime=market_regime,
            trend_quality="WEAK_TREND",
            confirmation_count=len(pairs),
        )
        result.validate()
        return result

    if len(pairs) >= strong_confirmations:
        recent_strong = pairs[-strong_confirmations:]

        if all(
            pair == target_pair
            for pair in recent_strong
        ):
            quality = "STRONG_TREND"
        else:
            quality = "NORMAL_TREND"
    else:
        quality = "NORMAL_TREND"

    result = TrendQuality(
        market_regime=market_regime,
        trend_quality=quality,
        confirmation_count=len(pairs),
    )

    result.validate()
    return result


def trend_quality_from_structure(
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
    min_confirmations: int = DEFAULT_MIN_CONFIRMATIONS,
    strong_confirmations: int = DEFAULT_STRONG_CONFIRMATIONS,
) -> TrendQuality:
    """
    Infer the current structural direction and assess its quality.

    This is descriptive analysis only.
    """

    if len(high_classifications) != len(low_classifications):
        raise ValueError(
            "High and low classifications must have equal length"
        )

    if min_confirmations <= 0:
        raise ValueError(
            "min_confirmations must be greater than zero"
        )

    if strong_confirmations < min_confirmations:
        raise ValueError(
            "strong_confirmations must be greater than or equal "
            "to min_confirmations"
        )

    pairs = _confirmed_pairs(
        high_classifications,
        low_classifications,
    )

    if len(pairs) < min_confirmations:
        market_regime = "INSUFFICIENT_DATA"

    else:
        recent_minimum = pairs[-min_confirmations:]

        recent_bullish = all(
            pair == ("HH", "HL")
            for pair in recent_minimum
        )

        recent_bearish = all(
            pair == ("LH", "LL")
            for pair in recent_minimum
        )

        if recent_bullish:
            market_regime = "TRENDING_BULLISH"
        elif recent_bearish:
            market_regime = "TRENDING_BEARISH"
        else:
            market_regime = "RANGE"

    return classify_trend_quality(
        market_regime=market_regime,
        high_classifications=high_classifications,
        low_classifications=low_classifications,
        min_confirmations=min_confirmations,
        strong_confirmations=strong_confirmations,
    )
