import pytest

from app.strategy.structure import (
    classify_structure_regime,
    classify_swing_highs,
    classify_swing_lows,
    structural_levels,
    swing_highs,
    swing_lows,
)


def test_swing_high_detects_local_high():
    highs = [10, 11, 15, 12, 13]

    result = swing_highs(highs, left=1, right=1)

    assert result == [False, False, True, False, False]


def test_swing_low_detects_local_low():
    lows = [10, 9, 5, 8, 7]

    result = swing_lows(lows, left=1, right=1)

    assert result == [False, False, True, False, False]


def test_swing_boundaries_are_not_confirmed():
    highs = [10, 20, 10]
    lows = [10, 5, 10]

    assert swing_highs(highs, left=1, right=1) == [False, True, False]
    assert swing_lows(lows, left=1, right=1) == [False, True, False]


def test_swing_high_requires_strict_greater_than_neighbors():
    highs = [10, 15, 15, 10]

    result = swing_highs(highs, left=1, right=1)

    assert result == [False, False, False, False]


def test_swing_low_requires_strict_less_than_neighbors():
    lows = [10, 5, 5, 10]

    result = swing_lows(lows, left=1, right=1)

    assert result == [False, False, False, False]


def test_invalid_swing_window_is_rejected():
    with pytest.raises(ValueError, match="greater than zero"):
        swing_highs([1, 2, 1], left=0, right=1)

    with pytest.raises(ValueError, match="greater than zero"):
        swing_lows([3, 2, 3], left=1, right=0)


def test_empty_swing_input_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        swing_highs([], left=1, right=1)

    with pytest.raises(ValueError, match="cannot be empty"):
        swing_lows([], left=1, right=1)


def test_non_positive_swing_values_are_rejected():
    with pytest.raises(ValueError, match="greater than zero"):
        swing_highs([10, 0, 10], left=1, right=1)

    with pytest.raises(ValueError, match="greater than zero"):
        swing_lows([10, -1, 10], left=1, right=1)


def test_swing_high_classification_produces_hh_lh_eh():
    highs = [100, 110, 105, 110, 100, 110]
    flags = [False, True, False, True, False, True]

    result = classify_swing_highs(highs, flags)

    assert result == [None, None, None, "EH", None, "EH"]


def test_swing_high_classification_produces_hh_and_lh():
    highs = [100, 110, 105, 120, 100, 115]
    flags = [False, True, False, True, False, True]

    result = classify_swing_highs(highs, flags)

    assert result == [None, None, None, "HH", None, "LH"]


def test_swing_low_classification_produces_hl_ll_el():
    lows = [100, 90, 95, 90, 95, 90]
    flags = [False, True, False, True, False, True]

    result = classify_swing_lows(lows, flags)

    assert result == [None, None, None, "EL", None, "EL"]


def test_swing_low_classification_produces_hl_and_ll():
    lows = [100, 90, 95, 100, 95, 85]
    flags = [False, True, False, True, False, True]

    result = classify_swing_lows(lows, flags)

    assert result == [None, None, None, "HL", None, "LL"]


def test_classification_requires_equal_lengths():
    with pytest.raises(ValueError, match="equal length"):
        classify_swing_highs([100, 110], [False])

    with pytest.raises(ValueError, match="equal length"):
        classify_swing_lows([100, 90], [True])


def test_classification_ignores_non_swing_observations():
    highs = [100, 110, 105, 120]
    flags = [False, True, False, True]

    result = classify_swing_highs(highs, flags)

    assert result[1] is None
    assert result[2] is None
    assert result[3] == "HH"


def test_first_confirmed_swing_has_no_classification():
    highs = [100, 110, 100]
    flags = [False, True, False]

    lows = [100, 90, 100]

    high_result = classify_swing_highs(highs, flags)
    low_result = classify_swing_lows(lows, flags)

    assert high_result == [None, None, None]
    assert low_result == [None, None, None]


def test_bullish_structure_regime():
    highs = [None, "HH"]
    lows = [None, "HL"]

    assert classify_structure_regime(highs, lows) == "BULLISH"


def test_bearish_structure_regime():
    highs = [None, "LH"]
    lows = [None, "LL"]

    assert classify_structure_regime(highs, lows) == "BEARISH"


def test_mixed_structure_is_non_directional():
    highs = [None, "HH"]
    lows = [None, "LL"]

    assert classify_structure_regime(highs, lows) == "RANGE_OR_MIXED"


def test_equal_structure_is_non_directional():
    highs = [None, "EH"]
    lows = [None, "EL"]

    assert classify_structure_regime(highs, lows) == "RANGE_OR_MIXED"


def test_missing_high_or_low_is_insufficient():
    assert classify_structure_regime([None], [None]) == "INSUFFICIENT_DATA"
    assert classify_structure_regime(["HH"], [None]) == "INSUFFICIENT_DATA"
    assert classify_structure_regime([None], ["HL"]) == "INSUFFICIENT_DATA"


def test_structure_regime_uses_latest_confirmed_classifications():
    highs = ["HH", None, "LH"]
    lows = ["HL", None, "LL"]

    assert classify_structure_regime(highs, lows) == "BEARISH"


def test_structure_regime_requires_equal_lengths():
    with pytest.raises(ValueError, match="equal length"):
        classify_structure_regime(["HH"], ["HL", "LL"])


def test_structural_levels_returns_confirmed_levels_chronologically():
    highs = [100, 110, 105, 120]
    lows = [90, 95, 85, 100]
    high_flags = [False, True, False, True]
    low_flags = [True, False, True, False]

    result = structural_levels(
        highs,
        lows,
        high_flags,
        low_flags,
    )

    assert result == [
        (0, 90.0, "LOW"),
        (1, 110.0, "HIGH"),
        (2, 85.0, "LOW"),
        (3, 120.0, "HIGH"),
    ]


def test_structural_levels_can_contain_high_and_low_at_same_index():
    highs = [100, 120, 100]
    lows = [90, 80, 90]
    high_flags = [False, True, False]
    low_flags = [False, True, False]

    result = structural_levels(
        highs,
        lows,
        high_flags,
        low_flags,
    )

    assert result == [
        (1, 120.0, "HIGH"),
        (1, 80.0, "LOW"),
    ]


def test_structural_levels_requires_equal_lengths():
    with pytest.raises(ValueError, match="equal length"):
        structural_levels(
            [100, 110],
            [90],
            [False, True],
            [True],
        )


def test_structural_levels_rejects_non_positive_prices():
    with pytest.raises(ValueError, match="greater than zero"):
        structural_levels(
            [100, 0],
            [90, 80],
            [False, True],
            [True, False],
        )

    with pytest.raises(ValueError, match="greater than zero"):
        structural_levels(
            [100, 110],
            [90, -1],
            [False, True],
            [True, False],
        )
