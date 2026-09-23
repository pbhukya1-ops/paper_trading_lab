import pytest

from app.strategy.regime import (
    DEFAULT_MIN_CONFIRMATIONS,
    MarketRegime,
    classify_market_regime,
    regime_from_structure,
)


def test_default_min_confirmations():
    assert DEFAULT_MIN_CONFIRMATIONS == 2


def test_market_regime_is_frozen():
    result = MarketRegime(
        structure_regime="BULLISH",
        market_regime="TRENDING_BULLISH",
    )

    with pytest.raises(AttributeError):
        result.market_regime = "RANGE"


def test_market_regime_validation_accepts_valid_values():
    result = MarketRegime(
        structure_regime="BULLISH",
        market_regime="TRENDING_BULLISH",
    )

    result.validate()


@pytest.mark.parametrize(
    "structure_regime,market_regime",
    [
        ("BULLISH", "TRENDING_BULLISH"),
        ("BEARISH", "TRENDING_BEARISH"),
        ("RANGE_OR_MIXED", "RANGE"),
        ("BULLISH", "TRANSITION"),
        ("INSUFFICIENT_DATA", "INSUFFICIENT_DATA"),
    ],
)
def test_market_regime_validation_accepts_supported_combinations(
    structure_regime,
    market_regime,
):
    result = MarketRegime(
        structure_regime=structure_regime,
        market_regime=market_regime,
    )

    result.validate()


def test_market_regime_rejects_invalid_structure_regime():
    result = MarketRegime(
        structure_regime="INVALID",
        market_regime="RANGE",
    )

    with pytest.raises(ValueError, match="Unsupported structure regime"):
        result.validate()


def test_market_regime_rejects_invalid_market_regime():
    result = MarketRegime(
        structure_regime="BULLISH",
        market_regime="INVALID",
    )

    with pytest.raises(ValueError, match="Unsupported market regime"):
        result.validate()


def test_classify_bullish_with_repeated_confirmations():
    result = classify_market_regime(
        "BULLISH",
        ["HH", "HH"],
        ["HL", "HL"],
    )

    assert isinstance(result, MarketRegime)
    assert result.structure_regime == "BULLISH"
    assert result.market_regime == "TRENDING_BULLISH"


def test_classify_bearish_with_repeated_confirmations():
    result = classify_market_regime(
        "BEARISH",
        ["LH", "LH"],
        ["LL", "LL"],
    )

    assert result.structure_regime == "BEARISH"
    assert result.market_regime == "TRENDING_BEARISH"


def test_classify_range_or_mixed_as_range():
    result = classify_market_regime(
        "RANGE_OR_MIXED",
        ["HH", "LH"],
        ["HL", "LL"],
    )

    assert result.market_regime == "RANGE"


def test_classify_conflicting_bullish_structure_as_transition():
    result = classify_market_regime(
        "BULLISH",
        ["HH", "LH"],
        ["HL", "LL"],
    )

    assert result.market_regime == "TRANSITION"


def test_classify_conflicting_bearish_structure_as_transition():
    result = classify_market_regime(
        "BEARISH",
        ["LH", "HH"],
        ["LL", "HL"],
    )

    assert result.market_regime == "TRANSITION"


def test_classify_insufficient_confirmed_pairs():
    result = classify_market_regime(
        "BULLISH",
        [None, "HH"],
        [None, "HL"],
    )

    assert result.market_regime == "INSUFFICIENT_DATA"


def test_missing_one_side_excludes_pair_from_confirmation_count():
    result = classify_market_regime(
        "BULLISH",
        ["HH", None, "HH"],
        ["HL", "HL", "HL"],
    )

    assert result.market_regime == "TRENDING_BULLISH"


def test_recent_confirmations_are_required_for_bullish_trend():
    result = classify_market_regime(
        "BULLISH",
        ["HH", "HH", "LH"],
        ["HL", "HL", "LL"],
        min_confirmations=2,
    )

    assert result.market_regime == "TRANSITION"


def test_recent_confirmations_are_required_for_bearish_trend():
    result = classify_market_regime(
        "BEARISH",
        ["LH", "LH", "HH"],
        ["LL", "LL", "HL"],
        min_confirmations=2,
    )

    assert result.market_regime == "TRANSITION"


def test_older_confirmations_do_not_replace_recent_confirmation_requirement():
    result = classify_market_regime(
        "BULLISH",
        ["HH", "HH", "LH", "HH"],
        ["HL", "HL", "LL", "HL"],
        min_confirmations=2,
    )

    assert result.market_regime == "TRANSITION"


def test_custom_min_confirmations():
    result = classify_market_regime(
        "BULLISH",
        ["HH", "HH", "HH"],
        ["HL", "HL", "HL"],
        min_confirmations=3,
    )

    assert result.market_regime == "TRENDING_BULLISH"


def test_custom_min_confirmations_can_make_data_insufficient():
    result = classify_market_regime(
        "BULLISH",
        ["HH", "HH"],
        ["HL", "HL"],
        min_confirmations=3,
    )

    assert result.market_regime == "INSUFFICIENT_DATA"


def test_range_classification_does_not_require_directional_confirmation():
    result = classify_market_regime(
        "RANGE_OR_MIXED",
        [None, "HH"],
        [None, "HL"],
        min_confirmations=1,
    )

    assert result.market_regime == "RANGE"


def test_insufficient_structure_regime_returns_insufficient_data():
    result = classify_market_regime(
        "INSUFFICIENT_DATA",
        ["HH", "HH"],
        ["HL", "HL"],
    )

    assert result.market_regime == "INSUFFICIENT_DATA"


def test_classify_rejects_unsupported_structure_regime():
    with pytest.raises(ValueError, match="Unsupported structure regime"):
        classify_market_regime(
            "INVALID",
            ["HH", "HH"],
            ["HL", "HL"],
        )


def test_classify_rejects_zero_min_confirmations():
    with pytest.raises(
        ValueError,
        match="min_confirmations must be greater than zero",
    ):
        classify_market_regime(
            "BULLISH",
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=0,
        )


def test_classify_rejects_negative_min_confirmations():
    with pytest.raises(
        ValueError,
        match="min_confirmations must be greater than zero",
    ):
        classify_market_regime(
            "BULLISH",
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=-1,
        )


def test_classify_rejects_mismatched_classification_lengths():
    with pytest.raises(
        ValueError,
        match="High and low classifications must have equal length",
    ):
        classify_market_regime(
            "BULLISH",
            ["HH", "HH"],
            ["HL"],
        )


def test_regime_from_structure_detects_bullish():
    result = regime_from_structure(
        ["HH", "HH"],
        ["HL", "HL"],
    )

    assert result.structure_regime == "BULLISH"
    assert result.market_regime == "TRENDING_BULLISH"


def test_regime_from_structure_detects_bearish():
    result = regime_from_structure(
        ["LH", "LH"],
        ["LL", "LL"],
    )

    assert result.structure_regime == "BEARISH"
    assert result.market_regime == "TRENDING_BEARISH"


def test_regime_from_structure_detects_range_or_mixed():
    result = regime_from_structure(
        ["HH", "LH"],
        ["HL", "LL"],
    )

    assert result.structure_regime == "RANGE_OR_MIXED"
    assert result.market_regime == "RANGE"


def test_regime_from_structure_detects_insufficient_data():
    result = regime_from_structure(
        [None, "HH"],
        [None, "HL"],
    )

    assert result.structure_regime == "INSUFFICIENT_DATA"
    assert result.market_regime == "INSUFFICIENT_DATA"


def test_regime_from_structure_uses_recent_pairs():
    result = regime_from_structure(
        ["HH", "HH", "LH"],
        ["HL", "HL", "LL"],
        min_confirmations=2,
    )

    assert result.structure_regime == "RANGE_OR_MIXED"
    assert result.market_regime == "RANGE"


def test_regime_from_structure_rejects_mismatched_lengths():
    with pytest.raises(
        ValueError,
        match="High and low classifications must have equal length",
    ):
        regime_from_structure(
            ["HH", "HH"],
            ["HL"],
        )


def test_regime_from_structure_rejects_invalid_min_confirmations():
    with pytest.raises(
        ValueError,
        match="min_confirmations must be greater than zero",
    ):
        regime_from_structure(
            ["HH", "HH"],
            ["HL", "HL"],
            min_confirmations=0,
        )


def test_regime_from_structure_ignores_unconfirmed_pairs():
    result = regime_from_structure(
        [None, "HH", None, "HH"],
        [None, "HL", None, "HL"],
    )

    assert result.structure_regime == "BULLISH"
    assert result.market_regime == "TRENDING_BULLISH"
