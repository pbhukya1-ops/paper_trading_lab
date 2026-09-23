import pytest

from app.strategy.breakout import (
    BreakoutEvent,
    VALID_BREAKOUT_TYPES,
    VALID_CONFIRMATION_TYPES,
    detect_breakout,
    detect_breakouts,
)


def test_valid_breakout_constants():
    assert VALID_BREAKOUT_TYPES == {
        "BULLISH_BREAKOUT",
        "BEARISH_BREAKOUT",
        "NO_BREAKOUT",
        "INSUFFICIENT_DATA",
    }
    assert VALID_CONFIRMATION_TYPES == {
        "CLOSE_CONFIRMED",
        "WICK_ONLY",
        "NO_CONFIRMATION",
        "INSUFFICIENT_DATA",
    }


def test_breakout_event_is_frozen():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )

    with pytest.raises(AttributeError):
        event.close_price = 106.0


def test_breakout_event_validation_accepts_valid_event():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )
    event.validate()


def test_breakout_event_rejects_negative_candle_index():
    event = BreakoutEvent(
        candle_index=-1,
        level_index=0,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )
    with pytest.raises(ValueError, match="Candle index cannot be negative"):
        event.validate()


def test_breakout_event_rejects_negative_level_index():
    event = BreakoutEvent(
        candle_index=5,
        level_index=-1,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )
    with pytest.raises(ValueError, match="Level index cannot be negative"):
        event.validate()


def test_breakout_event_requires_level_before_candle():
    event = BreakoutEvent(
        candle_index=2,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )
    with pytest.raises(
        ValueError,
        match="Level index must precede breakout candle",
    ):
        event.validate()


def test_breakout_event_rejects_invalid_level_price():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=0.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )
    with pytest.raises(
        ValueError,
        match="Level price must be greater than zero",
    ):
        event.validate()


def test_breakout_event_rejects_invalid_wick_extreme():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=0.0,
        close_price=104.0,
    )
    with pytest.raises(
        ValueError,
        match="Wick extreme must be greater than zero",
    ):
        event.validate()


def test_breakout_event_rejects_invalid_close():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=0.0,
    )
    with pytest.raises(
        ValueError,
        match="Close price must be greater than zero",
    ):
        event.validate()


def test_breakout_event_rejects_invalid_breakout_type():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="INVALID",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )
    with pytest.raises(ValueError, match="Unsupported breakout type"):
        event.validate()


def test_breakout_event_rejects_invalid_confirmation_type():
    event = BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="INVALID",
        wick_extreme=105.0,
        close_price=104.0,
    )
    with pytest.raises(ValueError, match="Unsupported confirmation type"):
        event.validate()


def test_high_level_close_confirmed_bullish_breakout():
    result = detect_breakout(
        high=105.0,
        low=98.0,
        close=103.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "BULLISH_BREAKOUT"
    assert result.confirmation_type == "CLOSE_CONFIRMED"
    assert result.wick_extreme == 105.0
    assert result.close_price == 103.0


def test_high_level_wick_only_bullish_breakout():
    result = detect_breakout(
        high=105.0,
        low=98.0,
        close=100.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "BULLISH_BREAKOUT"
    assert result.confirmation_type == "WICK_ONLY"
    assert result.wick_extreme == 105.0
    assert result.close_price == 100.0


def test_high_level_no_breakout_when_high_does_not_cross():
    result = detect_breakout(
        high=100.0,
        low=98.0,
        close=99.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "NO_BREAKOUT"
    assert result.confirmation_type == "NO_CONFIRMATION"


def test_high_level_exact_touch_is_not_breakout():
    result = detect_breakout(
        high=100.0,
        low=99.0,
        close=100.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "NO_BREAKOUT"
    assert result.confirmation_type == "NO_CONFIRMATION"


def test_low_level_close_confirmed_bearish_breakout():
    result = detect_breakout(
        high=102.0,
        low=95.0,
        close=97.0,
        level_price=100.0,
        level_type="LOW",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "BEARISH_BREAKOUT"
    assert result.confirmation_type == "CLOSE_CONFIRMED"
    assert result.wick_extreme == 95.0
    assert result.close_price == 97.0


def test_low_level_wick_only_bearish_breakout():
    result = detect_breakout(
        high=102.0,
        low=95.0,
        close=100.0,
        level_price=100.0,
        level_type="LOW",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "BEARISH_BREAKOUT"
    assert result.confirmation_type == "WICK_ONLY"
    assert result.wick_extreme == 95.0
    assert result.close_price == 100.0


def test_low_level_no_breakout_when_low_does_not_cross():
    result = detect_breakout(
        high=102.0,
        low=100.0,
        close=101.0,
        level_price=100.0,
        level_type="LOW",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "NO_BREAKOUT"
    assert result.confirmation_type == "NO_CONFIRMATION"


def test_low_level_exact_touch_is_not_breakout():
    result = detect_breakout(
        high=102.0,
        low=100.0,
        close=100.0,
        level_price=100.0,
        level_type="LOW",
        candle_index=5,
        level_index=2,
    )

    assert result.breakout_type == "NO_BREAKOUT"
    assert result.confirmation_type == "NO_CONFIRMATION"


def test_unsupported_level_type_is_rejected():
    with pytest.raises(ValueError, match="Unsupported level type"):
        detect_breakout(
            high=105.0,
            low=98.0,
            close=103.0,
            level_price=100.0,
            level_type="MIDDLE",
            candle_index=5,
            level_index=2,
        )


def test_high_must_be_positive():
    with pytest.raises(ValueError, match="High must be greater than zero"):
        detect_breakout(
            high=0.0,
            low=0.0,
            close=0.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        )


def test_low_must_be_positive():
    with pytest.raises(ValueError, match="Low must be greater than zero"):
        detect_breakout(
            high=105.0,
            low=0.0,
            close=1.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        )


def test_low_cannot_exceed_high():
    with pytest.raises(ValueError, match="Low cannot be greater than high"):
        detect_breakout(
            high=98.0,
            low=105.0,
            close=100.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        )


def test_close_must_lie_inside_candle_range():
    with pytest.raises(
        ValueError,
        match="Close must lie within candle high-low range",
    ):
        detect_breakout(
            high=105.0,
            low=98.0,
            close=106.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        )


def test_level_index_must_precede_candle_index():
    with pytest.raises(
        ValueError,
        match="Level index must precede breakout candle",
    ):
        detect_breakout(
            high=105.0,
            low=98.0,
            close=103.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=2,
            level_index=2,
        )


def test_detect_breakouts_returns_only_later_nonzero_interactions():
    highs = [100.0, 101.0, 105.0, 102.0, 106.0]
    lows = [98.0, 99.0, 100.0, 99.0, 101.0]
    closes = [99.0, 100.0, 103.0, 100.0, 104.0]

    results = detect_breakouts(
        highs=highs,
        lows=lows,
        closes=closes,
        level_index=1,
        level_price=100.0,
        level_type="HIGH",
    )

    assert [event.candle_index for event in results] == [2, 3, 4]
    assert all(
        event.breakout_type == "BULLISH_BREAKOUT"
        for event in results
    )


def test_detect_breakouts_returns_bearish_interactions():
    highs = [102.0, 101.0, 101.0, 102.0, 100.0]
    lows = [98.0, 95.0, 99.0, 94.0, 93.0]
    closes = [100.0, 97.0, 100.0, 96.0, 95.0]

    results = detect_breakouts(
        highs=highs,
        lows=lows,
        closes=closes,
        level_index=1,
        level_price=100.0,
        level_type="LOW",
    )

    assert [event.candle_index for event in results] == [2, 3, 4]
    assert all(
        event.breakout_type == "BEARISH_BREAKOUT"
        for event in results
    )


def test_detect_breakouts_excludes_no_breakout_events():
    highs = [100.0, 101.0, 99.0, 100.0, 102.0]
    lows = [98.0, 99.0, 97.0, 98.0, 100.0]
    closes = [99.0, 100.0, 98.0, 99.0, 101.0]

    results = detect_breakouts(
        highs=highs,
        lows=lows,
        closes=closes,
        level_index=1,
        level_price=100.0,
        level_type="HIGH",
    )

    assert [event.candle_index for event in results] == [4]


def test_detect_breakouts_preserves_chronological_order():
    highs = [100.0, 101.0, 105.0, 106.0, 107.0]
    lows = [98.0, 99.0, 100.0, 101.0, 102.0]
    closes = [99.0, 100.0, 103.0, 104.0, 105.0]

    results = detect_breakouts(
        highs=highs,
        lows=lows,
        closes=closes,
        level_index=1,
        level_price=100.0,
        level_type="HIGH",
    )

    assert [event.candle_index for event in results] == [2, 3, 4]


def test_detect_breakouts_rejects_mismatched_lengths():
    with pytest.raises(
        ValueError,
        match="Highs, lows, and closes must have equal length",
    ):
        detect_breakouts(
            highs=[100.0, 101.0],
            lows=[98.0],
            closes=[99.0, 100.0],
            level_index=0,
            level_price=100.0,
            level_type="HIGH",
        )


def test_detect_breakouts_rejects_empty_input():
    with pytest.raises(
        ValueError,
        match="Price input cannot be empty",
    ):
        detect_breakouts(
            highs=[],
            lows=[],
            closes=[],
            level_index=0,
            level_price=100.0,
            level_type="HIGH",
        )


def test_detect_breakouts_rejects_negative_level_index():
    with pytest.raises(
        ValueError,
        match="Level index cannot be negative",
    ):
        detect_breakouts(
            highs=[100.0, 101.0],
            lows=[98.0, 99.0],
            closes=[99.0, 100.0],
            level_index=-1,
            level_price=100.0,
            level_type="HIGH",
        )


def test_detect_breakouts_rejects_out_of_range_level_index():
    with pytest.raises(
        ValueError,
        match="Level index is outside the price series",
    ):
        detect_breakouts(
            highs=[100.0, 101.0],
            lows=[98.0, 99.0],
            closes=[99.0, 100.0],
            level_index=2,
            level_price=100.0,
            level_type="HIGH",
        )


def test_detect_breakouts_rejects_nonpositive_level_price():
    with pytest.raises(
        ValueError,
        match="Level price must be greater than zero",
    ):
        detect_breakouts(
            highs=[100.0, 101.0],
            lows=[98.0, 99.0],
            closes=[99.0, 100.0],
            level_index=0,
            level_price=0.0,
            level_type="HIGH",
        )


def test_detect_breakouts_does_not_include_level_candle():
    highs = [105.0, 110.0]
    lows = [98.0, 99.0]
    closes = [104.0, 108.0]

    results = detect_breakouts(
        highs=highs,
        lows=lows,
        closes=closes,
        level_index=0,
        level_price=100.0,
        level_type="HIGH",
    )

    assert [event.candle_index for event in results] == [1]
