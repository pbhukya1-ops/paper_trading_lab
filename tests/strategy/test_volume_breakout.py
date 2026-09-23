import pytest

from app.strategy.breakout import BreakoutEvent
from app.strategy.volume_breakout import (
    DEFAULT_RELATIVE_VOLUME_THRESHOLD,
    VALID_VOLUME_STRENGTHS,
    VolumeBreakoutContext,
    classify_volume_strength,
    volume_breakout_from_values,
)


def make_event(
    breakout_type="BULLISH_BREAKOUT",
    confirmation_type="CLOSE_CONFIRMED",
):
    return BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type=breakout_type,
        confirmation_type=confirmation_type,
        wick_extreme=105.0,
        close_price=104.0,
    )


def test_volume_constants():
    assert VALID_VOLUME_STRENGTHS == {
        "HIGH_VOLUME",
        "NORMAL_VOLUME",
        "LOW_VOLUME",
        "NO_BREAKOUT",
        "INSUFFICIENT_DATA",
    }


def test_default_relative_volume_threshold():
    assert DEFAULT_RELATIVE_VOLUME_THRESHOLD == 1.5


def test_context_is_frozen():
    context = VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=2.0,
        volume_strength="HIGH_VOLUME",
    )

    with pytest.raises(Exception):
        context.volume_strength = "LOW_VOLUME"


def test_context_validation_accepts_valid_context():
    context = VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=2.0,
        volume_strength="HIGH_VOLUME",
    )

    context.validate()


def test_context_allows_none_relative_volume():
    context = VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=None,
        volume_strength="INSUFFICIENT_DATA",
    )

    context.validate()


def test_context_rejects_invalid_breakout_type():
    context = VolumeBreakoutContext(
        breakout_type="INVALID",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=2.0,
        volume_strength="HIGH_VOLUME",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_rejects_invalid_confirmation_type():
    context = VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="INVALID",
        relative_volume=2.0,
        volume_strength="HIGH_VOLUME",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_rejects_negative_relative_volume():
    context = VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=-0.1,
        volume_strength="LOW_VOLUME",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_rejects_invalid_volume_strength():
    context = VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=2.0,
        volume_strength="INVALID",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_no_breakout_has_no_breakout_volume_strength():
    event = make_event(
        breakout_type="NO_BREAKOUT",
        confirmation_type="NO_CONFIRMATION",
    )

    result = classify_volume_strength(event, relative_volume=3.0)

    assert result.breakout_type == "NO_BREAKOUT"
    assert result.volume_strength == "NO_BREAKOUT"


def test_missing_volume_is_insufficient_data():
    event = make_event()

    result = classify_volume_strength(event, relative_volume=None)

    assert result.volume_strength == "INSUFFICIENT_DATA"
    assert result.relative_volume is None


def test_high_volume_at_threshold():
    event = make_event()

    result = classify_volume_strength(
        event,
        relative_volume=DEFAULT_RELATIVE_VOLUME_THRESHOLD,
    )

    assert result.volume_strength == "HIGH_VOLUME"


def test_high_volume_above_threshold():
    event = make_event()

    result = classify_volume_strength(event, relative_volume=2.0)

    assert result.volume_strength == "HIGH_VOLUME"


def test_normal_volume_at_one():
    event = make_event()

    result = classify_volume_strength(event, relative_volume=1.0)

    assert result.volume_strength == "NORMAL_VOLUME"


def test_normal_volume_between_one_and_threshold():
    event = make_event()

    result = classify_volume_strength(event, relative_volume=1.2)

    assert result.volume_strength == "NORMAL_VOLUME"


def test_low_volume_below_one():
    event = make_event()

    result = classify_volume_strength(event, relative_volume=0.99)

    assert result.volume_strength == "LOW_VOLUME"


def test_zero_relative_volume_is_low_volume():
    event = make_event()

    result = classify_volume_strength(event, relative_volume=0.0)

    assert result.volume_strength == "LOW_VOLUME"


def test_threshold_must_be_positive():
    event = make_event()

    with pytest.raises(ValueError):
        classify_volume_strength(
            event,
            relative_volume=2.0,
            threshold=0.0,
        )


def test_negative_relative_volume_is_rejected():
    event = make_event()

    with pytest.raises(ValueError):
        classify_volume_strength(
            event,
            relative_volume=-1.0,
        )


def test_bearish_breakout_preserves_type():
    event = make_event(
        breakout_type="BEARISH_BREAKOUT",
    )

    result = classify_volume_strength(
        event,
        relative_volume=2.0,
    )

    assert result.breakout_type == "BEARISH_BREAKOUT"
    assert result.volume_strength == "HIGH_VOLUME"


def test_wick_only_confirmation_is_preserved():
    event = make_event(
        confirmation_type="WICK_ONLY",
    )

    result = classify_volume_strength(
        event,
        relative_volume=2.0,
    )

    assert result.confirmation_type == "WICK_ONLY"


def test_volume_breakout_from_values_high_volume():
    result = volume_breakout_from_values(
        high=105.0,
        low=99.0,
        close=104.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
        relative_volume=2.0,
    )

    assert result.breakout_type == "BULLISH_BREAKOUT"
    assert result.confirmation_type == "CLOSE_CONFIRMED"
    assert result.volume_strength == "HIGH_VOLUME"


def test_volume_breakout_from_values_wick_only():
    result = volume_breakout_from_values(
        high=105.0,
        low=99.0,
        close=100.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
        relative_volume=2.0,
    )

    assert result.breakout_type == "BULLISH_BREAKOUT"
    assert result.confirmation_type == "WICK_ONLY"
    assert result.volume_strength == "HIGH_VOLUME"


def test_volume_breakout_from_values_no_breakout():
    result = volume_breakout_from_values(
        high=100.0,
        low=95.0,
        close=99.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
        relative_volume=2.0,
    )

    assert result.breakout_type == "NO_BREAKOUT"
    assert result.confirmation_type == "NO_CONFIRMATION"
    assert result.volume_strength == "NO_BREAKOUT"


def test_volume_breakout_from_values_missing_volume():
    result = volume_breakout_from_values(
        high=105.0,
        low=99.0,
        close=104.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
        relative_volume=None,
    )

    assert result.breakout_type == "BULLISH_BREAKOUT"
    assert result.volume_strength == "INSUFFICIENT_DATA"


def test_volume_breakout_from_values_custom_threshold():
    result = volume_breakout_from_values(
        high=105.0,
        low=99.0,
        close=104.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
        relative_volume=1.8,
        threshold=2.0,
    )

    assert result.volume_strength == "NORMAL_VOLUME"


def test_volume_breakout_from_values_rejects_invalid_ohlc():
    with pytest.raises(ValueError):
        volume_breakout_from_values(
            high=95.0,
            low=100.0,
            close=97.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
            relative_volume=2.0,
        )
