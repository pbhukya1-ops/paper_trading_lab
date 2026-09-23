import pytest

from app.strategy.trend_quality import (
    DEFAULT_MIN_CONFIRMATIONS,
    DEFAULT_STRONG_CONFIRMATIONS,
    TrendQuality,
    classify_trend_quality,
    trend_quality_from_structure,
)


def test_default_confirmation_configuration():
    assert DEFAULT_MIN_CONFIRMATIONS == 2
    assert DEFAULT_STRONG_CONFIRMATIONS == 3


def test_trend_quality_is_frozen():
    result = TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="NORMAL_TREND",
        confirmation_count=2,
    )

    with pytest.raises(AttributeError):
        result.trend_quality = "STRONG_TREND"


def test_trend_quality_validation_accepts_valid_result():
    result = TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="NORMAL_TREND",
        confirmation_count=2,
    )

    result.validate()


@pytest.mark.parametrize(
    "market_regime,trend_quality",
    [
        ("TRENDING_BULLISH", "STRONG_TREND"),
        ("TRENDING_BULLISH", "NORMAL_TREND"),
        ("TRENDING_BULLISH", "WEAK_TREND"),
        ("TRENDING_BEARISH", "STRONG_TREND"),
        ("TRENDING_BEARISH", "NORMAL_TREND"),
        ("TRENDING_BEARISH", "WEAK_TREND"),
        ("RANGE", "RANGE"),
        ("TRANSITION", "TRANSITION"),
        ("INSUFFICIENT_DATA", "INSUFFICIENT_DATA"),
    ],
)
def test_trend_quality_validation_accepts_supported_values(
    market_regime,
    trend_quality,
):
    result = TrendQuality(
        market_regime=market_regime,
        trend_quality=trend_quality,
        confirmation_count=2,
    )

    result.validate()


def test_trend_quality_rejects_invalid_market_regime():
    result = TrendQuality(
        market_regime="INVALID",
        trend_quality="RANGE",
        confirmation_count=2,
    )

    with pytest.raises(ValueError, match="Unsupported market regime"):
        result.validate()


def test_trend_quality_rejects_invalid_trend_quality():
    result = TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="INVALID",
        confirmation_count=2,
    )

    with pytest.raises(ValueError, match="Unsupported trend quality"):
        result.validate()


def test_trend_quality_rejects_negative_confirmation_count():
    result = TrendQuality(
        market_regime="TRENDING_BULLISH",
        trend_quality="NORMAL_TREND",
        confirmation_count=-1,
    )

    with pytest.raises(
        ValueError,
        match="Confirmation count cannot be negative",
    ):
        result.validate()


def test_classify_bullish_strong_trend():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", "HH", "HH"],
        ["HL", "HL", "HL"],
    )

    assert result.market_regime == "TRENDING_BULLISH"
    assert result.trend_quality == "STRONG_TREND"
    assert result.confirmation_count == 3


def test_classify_bearish_strong_trend():
    result = classify_trend_quality(
        "TRENDING_BEARISH",
        ["LH", "LH", "LH"],
        ["LL", "LL", "LL"],
    )

    assert result.market_regime == "TRENDING_BEARISH"
    assert result.trend_quality == "STRONG_TREND"
    assert result.confirmation_count == 3


def test_classify_bullish_normal_trend():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", "HH"],
        ["HL", "HL"],
    )

    assert result.market_regime == "TRENDING_BULLISH"
    assert result.trend_quality == "NORMAL_TREND"
    assert result.confirmation_count == 2


def test_classify_bearish_normal_trend():
    result = classify_trend_quality(
        "TRENDING_BEARISH",
        ["LH", "LH"],
        ["LL", "LL"],
    )

    assert result.market_regime == "TRENDING_BEARISH"
    assert result.trend_quality == "NORMAL_TREND"
    assert result.confirmation_count == 2


def test_classify_bullish_weak_trend_when_recent_minimum_conflicts():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", "LH", "HH"],
        ["HL", "LL", "HL"],
    )

    assert result.trend_quality == "WEAK_TREND"
    assert result.confirmation_count == 3


def test_classify_bearish_weak_trend_when_recent_minimum_conflicts():
    result = classify_trend_quality(
        "TRENDING_BEARISH",
        ["LH", "HH", "LH"],
        ["LL", "HL", "LL"],
    )

    assert result.trend_quality == "WEAK_TREND"
    assert result.confirmation_count == 3


def test_strong_trend_requires_strong_confirmation_count():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", "HH", "HH"],
        ["HL", "HL", "HL"],
        min_confirmations=2,
        strong_confirmations=3,
    )

    assert result.trend_quality == "STRONG_TREND"
    assert result.confirmation_count == 3


def test_normal_trend_when_minimum_is_met_but_strong_threshold_is_not():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", "HH"],
        ["HL", "HL"],
        min_confirmations=2,
        strong_confirmations=3,
    )

    assert result.trend_quality == "NORMAL_TREND"
    assert result.confirmation_count == 2


def test_strong_trend_requires_recent_strong_pairs():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", "HH", "LH", "HH", "HH"],
        ["HL", "HL", "LL", "HL", "HL"],
        min_confirmations=2,
        strong_confirmations=3,
    )

    assert result.trend_quality == "NORMAL_TREND"


def test_range_regime_maps_to_range_quality():
    result = classify_trend_quality(
        "RANGE",
        ["HH", "LH"],
        ["HL", "LL"],
    )

    assert result.trend_quality == "RANGE"
    assert result.confirmation_count == 2


def test_transition_regime_maps_to_transition_quality():
    result = classify_trend_quality(
        "TRANSITION",
        ["HH", "LH"],
        ["HL", "LL"],
    )

    assert result.trend_quality == "TRANSITION"
    assert result.confirmation_count == 2


def test_insufficient_market_regime_maps_to_insufficient_quality():
    result = classify_trend_quality(
        "INSUFFICIENT_DATA",
        ["HH", "HH"],
        ["HL", "HL"],
    )

    assert result.trend_quality == "INSUFFICIENT_DATA"
    assert result.confirmation_count == 2


def test_fewer_than_minimum_confirmations_returns_insufficient_data():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        [None, "HH"],
        [None, "HL"],
        min_confirmations=2,
    )

    assert result.trend_quality == "INSUFFICIENT_DATA"
    assert result.confirmation_count == 1


def test_missing_one_side_is_excluded_from_confirmation_count():
    result = classify_trend_quality(
        "TRENDING_BULLISH",
        ["HH", None, "HH"],
        ["HL", "HL", "HL"],
        min_confirmations=2,
    )

    assert result.trend_quality == "NORMAL_TREND"
    assert result.confirmation_count == 2


def test_classify_rejects_unsupported_market_regime():
    with pytest.raises(ValueError, match="Unsupported market regime"):
        classify_trend_quality(
            "INVALID",
            ["HH", "HH"],
            ["HL", "HL"],
        )


def test_classify_rejects_zero_min_confirmations():
    with pytest.raises(
        ValueError,
        match="min_confirmations must be greater than zero",
    ):
        classify_trend_quality(
            "TRENDING_BULLISH",
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=0,
        )


def test_classify_rejects_negative_min_confirmations():
    with pytest.raises(
        ValueError,
        match="min_confirmations must be greater than zero",
    ):
        classify_trend_quality(
            "TRENDING_BULLISH",
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=-1,
        )


def test_classify_rejects_strong_threshold_below_minimum():
    with pytest.raises(
        ValueError,
        match="strong_confirmations must be greater than or equal",
    ):
        classify_trend_quality(
            "TRENDING_BULLISH",
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=3,
            strong_confirmations=2,
        )


def test_classify_rejects_mismatched_lengths():
    with pytest.raises(
        ValueError,
        match="High and low classifications must have equal length",
    ):
        classify_trend_quality(
            "TRENDING_BULLISH",
            ["HH", "HH"],
            ["HL"],
        )


def test_trend_quality_from_structure_detects_bullish():
    result = trend_quality_from_structure(
        ["HH", "HH", "HH"],
        ["HL", "HL", "HL"],
    )

    assert result.market_regime == "TRENDING_BULLISH"
    assert result.trend_quality == "STRONG_TREND"
    assert result.confirmation_count == 3


def test_trend_quality_from_structure_detects_bearish():
    result = trend_quality_from_structure(
        ["LH", "LH", "LH"],
        ["LL", "LL", "LL"],
    )

    assert result.market_regime == "TRENDING_BEARISH"
    assert result.trend_quality == "STRONG_TREND"
    assert result.confirmation_count == 3


def test_trend_quality_from_structure_detects_range():
    result = trend_quality_from_structure(
        ["HH", "LH"],
        ["HL", "LL"],
    )

    assert result.market_regime == "RANGE"
    assert result.trend_quality == "RANGE"


def test_trend_quality_from_structure_detects_insufficient_data():
    result = trend_quality_from_structure(
        [None, "HH"],
        [None, "HL"],
    )

    assert result.market_regime == "INSUFFICIENT_DATA"
    assert result.trend_quality == "INSUFFICIENT_DATA"
    assert result.confirmation_count == 1


def test_trend_quality_from_structure_uses_recent_minimum_pairs():
    result = trend_quality_from_structure(
        ["HH", "HH", "LH"],
        ["HL", "HL", "LL"],
        min_confirmations=2,
    )

    assert result.market_regime == "RANGE"
    assert result.trend_quality == "RANGE"


def test_trend_quality_from_structure_ignores_unconfirmed_pairs():
    result = trend_quality_from_structure(
        [None, "HH", None, "HH", "HH"],
        [None, "HL", None, "HL", "HL"],
    )

    assert result.market_regime == "TRENDING_BULLISH"
    assert result.trend_quality == "STRONG_TREND"
    assert result.confirmation_count == 3


def test_trend_quality_from_structure_rejects_mismatched_lengths():
    with pytest.raises(
        ValueError,
        match="High and low classifications must have equal length",
    ):
        trend_quality_from_structure(
            ["HH", "HH"],
            ["HL"],
        )


def test_trend_quality_from_structure_rejects_invalid_min_confirmations():
    with pytest.raises(
        ValueError,
        match="min_confirmations must be greater than zero",
    ):
        trend_quality_from_structure(
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=0,
        )


def test_trend_quality_from_structure_rejects_invalid_strong_threshold():
    with pytest.raises(
        ValueError,
        match="strong_confirmations must be greater than or equal",
    ):
        trend_quality_from_structure(
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=3,
            strong_confirmations=2,
        )
