import pytest

from app.strategy.fvg import (
    FairValueGap,
    detect_all_fvgs,
    detect_fvg,
)


def test_fvg_validates_valid_bullish_gap():
    gap = FairValueGap(
        lower=100.0,
        upper=105.0,
        gap_type="BULLISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )

    gap.validate()


def test_fvg_validates_valid_bearish_gap():
    gap = FairValueGap(
        lower=95.0,
        upper=100.0,
        gap_type="BEARISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )

    gap.validate()


def test_fvg_rejects_non_positive_lower():
    gap = FairValueGap(
        lower=0.0,
        upper=105.0,
        gap_type="BULLISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )

    with pytest.raises(ValueError, match="lower bound must be greater than zero"):
        gap.validate()


def test_fvg_rejects_non_positive_upper():
    gap = FairValueGap(
        lower=95.0,
        upper=0.0,
        gap_type="BEARISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )

    with pytest.raises(ValueError, match="upper bound must be greater than zero"):
        gap.validate()


def test_fvg_requires_lower_strictly_below_upper():
    gap = FairValueGap(
        lower=100.0,
        upper=100.0,
        gap_type="BULLISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )

    with pytest.raises(
        ValueError,
        match="lower bound must be strictly below upper bound",
    ):
        gap.validate()


def test_fvg_rejects_unsupported_type():
    gap = FairValueGap(
        lower=100.0,
        upper=105.0,
        gap_type="UNKNOWN",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )

    with pytest.raises(ValueError, match="Unsupported FVG type"):
        gap.validate()


def test_fvg_rejects_negative_first_index():
    gap = FairValueGap(
        lower=100.0,
        upper=105.0,
        gap_type="BULLISH_FVG",
        first_candle_index=-1,
        middle_candle_index=0,
        third_candle_index=1,
    )

    with pytest.raises(ValueError, match="First candle index cannot be negative"):
        gap.validate()


def test_fvg_requires_middle_after_first():
    gap = FairValueGap(
        lower=100.0,
        upper=105.0,
        gap_type="BULLISH_FVG",
        first_candle_index=1,
        middle_candle_index=1,
        third_candle_index=2,
    )

    with pytest.raises(
        ValueError,
        match="Middle candle index must follow first candle index",
    ):
        gap.validate()


def test_fvg_requires_third_after_middle():
    gap = FairValueGap(
        lower=100.0,
        upper=105.0,
        gap_type="BULLISH_FVG",
        first_candle_index=0,
        middle_candle_index=2,
        third_candle_index=2,
    )

    with pytest.raises(
        ValueError,
        match="Third candle index must follow middle candle index",
    ):
        gap.validate()


def test_detect_fvg_returns_none_before_three_candles():
    highs = [105.0, 110.0]
    lows = [100.0, 105.0]

    assert detect_fvg(highs, lows, index=0) is None
    assert detect_fvg(highs, lows, index=1) is None


def test_detect_bullish_fvg():
    highs = [100.0, 110.0, 115.0]
    lows = [95.0, 105.0, 105.0]

    result = detect_fvg(highs, lows, index=2)

    assert result == FairValueGap(
        lower=100.0,
        upper=105.0,
        gap_type="BULLISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )


def test_detect_bearish_fvg():
    highs = [105.0, 100.0, 95.0]
    lows = [100.0, 95.0, 90.0]

    result = detect_fvg(highs, lows, index=2)

    assert result == FairValueGap(
        lower=95.0,
        upper=100.0,
        gap_type="BEARISH_FVG",
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
    )


def test_detect_fvg_requires_strict_gap_for_bullish():
    highs = [100.0, 110.0, 105.0]
    lows = [95.0, 105.0, 100.0]

    assert detect_fvg(highs, lows, index=2) is None


def test_detect_fvg_requires_strict_gap_for_bearish():
    highs = [105.0, 100.0, 100.0]
    lows = [100.0, 95.0, 90.0]

    assert detect_fvg(highs, lows, index=2) is None


def test_detect_fvg_returns_none_when_no_gap_exists():
    highs = [105.0, 110.0, 108.0]
    lows = [100.0, 105.0, 103.0]

    assert detect_fvg(highs, lows, index=2) is None


def test_detect_fvg_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="equal length"):
        detect_fvg(
            highs=[100.0, 110.0],
            lows=[95.0],
            index=1,
        )


def test_detect_fvg_rejects_empty_input():
    with pytest.raises(ValueError, match="cannot be empty"):
        detect_fvg(
            highs=[],
            lows=[],
            index=0,
        )


def test_detect_fvg_rejects_non_positive_highs():
    with pytest.raises(ValueError, match="High values must be greater than zero"):
        detect_fvg(
            highs=[100.0, 0.0, 110.0],
            lows=[95.0, 90.0, 105.0],
            index=2,
        )


def test_detect_fvg_rejects_non_positive_lows():
    with pytest.raises(ValueError, match="Low values must be greater than zero"):
        detect_fvg(
            highs=[100.0, 110.0, 115.0],
            lows=[95.0, 0.0, 105.0],
            index=2,
        )


def test_detect_fvg_rejects_negative_index():
    with pytest.raises(ValueError, match="Index cannot be negative"):
        detect_fvg(
            highs=[100.0, 110.0, 115.0],
            lows=[95.0, 105.0, 105.0],
            index=-1,
        )


def test_detect_fvg_rejects_index_outside_series():
    with pytest.raises(ValueError, match="Index is outside the price series"):
        detect_fvg(
            highs=[100.0, 110.0, 115.0],
            lows=[95.0, 105.0, 105.0],
            index=3,
        )


def test_detect_all_fvgs_returns_chronological_gaps():
    highs = [
        100.0,
        110.0,
        115.0,
        120.0,
        125.0,
    ]
    lows = [
        95.0,
        105.0,
        105.0,
        115.0,
        130.0,
    ]

    result = detect_all_fvgs(highs, lows)

    assert result == [
        FairValueGap(
            lower=100.0,
            upper=105.0,
            gap_type="BULLISH_FVG",
            first_candle_index=0,
            middle_candle_index=1,
            third_candle_index=2,
        ),
        FairValueGap(
            lower=110.0,
            upper=115.0,
            gap_type="BULLISH_FVG",
            first_candle_index=1,
            middle_candle_index=2,
            third_candle_index=3,
        ),
        FairValueGap(
            lower=115.0,
            upper=130.0,
            gap_type="BULLISH_FVG",
            first_candle_index=2,
            middle_candle_index=3,
            third_candle_index=4,
        ),
    ]


def test_detect_all_fvgs_returns_empty_when_no_gaps_exist():
    highs = [105.0, 110.0, 108.0, 112.0]
    lows = [100.0, 105.0, 103.0, 107.0]

    assert detect_all_fvgs(highs, lows) == []


def test_detect_all_fvgs_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="equal length"):
        detect_all_fvgs(
            highs=[100.0, 110.0],
            lows=[95.0],
        )


def test_detect_all_fvgs_rejects_empty_input():
    with pytest.raises(ValueError, match="cannot be empty"):
        detect_all_fvgs(
            highs=[],
            lows=[],
        )
