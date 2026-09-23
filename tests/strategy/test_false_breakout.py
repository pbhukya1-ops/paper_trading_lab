import pytest

from app.strategy.false_breakout import (
    FalseBreakoutContext,
    VALID_FAILURE_TYPES,
    classify_level_reclaim,
    detect_false_breakout,
)


def test_valid_failure_types():
    assert VALID_FAILURE_TYPES == {
        "BULLISH_BREAKOUT_FAILURE",
        "BEARISH_BREAKOUT_FAILURE",
        "NO_FAILURE",
        "INSUFFICIENT_DATA",
    }


def test_bullish_breakout_failure():
    result = detect_false_breakout(
        breakout_extreme=105.0,
        failure_close=99.0,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        level_index=0,
        failure_candle_index=2,
    )

    assert result.failure_type == "BULLISH_BREAKOUT_FAILURE"
    assert result.breakout_type == "BULLISH_BREAKOUT"
    assert result.breakout_extreme == 105.0
    assert result.failure_close == 99.0


def test_bearish_breakout_failure():
    result = detect_false_breakout(
        breakout_extreme=95.0,
        failure_close=101.0,
        level_price=100.0,
        breakout_type="BEARISH_BREAKOUT",
        level_index=0,
        failure_candle_index=2,
    )

    assert result.failure_type == "BEARISH_BREAKOUT_FAILURE"
    assert result.breakout_type == "BEARISH_BREAKOUT"
    assert result.breakout_extreme == 95.0
    assert result.failure_close == 101.0


def test_bullish_breakout_with_close_at_level_is_no_failure():
    result = detect_false_breakout(
        breakout_extreme=105.0,
        failure_close=100.0,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        level_index=0,
        failure_candle_index=1,
    )

    assert result.failure_type == "NO_FAILURE"


def test_bullish_breakout_with_close_above_level_is_no_failure():
    result = detect_false_breakout(
        breakout_extreme=105.0,
        failure_close=101.0,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        level_index=0,
        failure_candle_index=1,
    )

    assert result.failure_type == "NO_FAILURE"


def test_bearish_breakout_with_close_at_level_is_no_failure():
    result = detect_false_breakout(
        breakout_extreme=95.0,
        failure_close=100.0,
        level_price=100.0,
        breakout_type="BEARISH_BREAKOUT",
        level_index=0,
        failure_candle_index=1,
    )

    assert result.failure_type == "NO_FAILURE"


def test_bearish_breakout_with_close_below_level_is_no_failure():
    result = detect_false_breakout(
        breakout_extreme=95.0,
        failure_close=99.0,
        level_price=100.0,
        breakout_type="BEARISH_BREAKOUT",
        level_index=0,
        failure_candle_index=1,
    )

    assert result.failure_type == "NO_FAILURE"


@pytest.mark.parametrize(
    "breakout_type,breakout_extreme,failure_close",
    [
        ("BULLISH_BREAKOUT", 100.0, 99.0),
        ("BULLISH_BREAKOUT", 99.0, 98.0),
        ("BEARISH_BREAKOUT", 100.0, 101.0),
        ("BEARISH_BREAKOUT", 101.0, 102.0),
    ],
)
def test_invalid_breakout_extreme(
    breakout_type,
    breakout_extreme,
    failure_close,
):
    with pytest.raises(ValueError):
        detect_false_breakout(
            breakout_extreme=breakout_extreme,
            failure_close=failure_close,
            level_price=100.0,
            breakout_type=breakout_type,
            level_index=0,
            failure_candle_index=1,
        )


@pytest.mark.parametrize(
    "breakout_type",
    [
        "INVALID",
        "",
        "BULLISH",
        "BEARISH",
    ],
)
def test_invalid_breakout_type(breakout_type):
    with pytest.raises(ValueError, match="Unsupported breakout type"):
        detect_false_breakout(
            breakout_extreme=105.0,
            failure_close=99.0,
            level_price=100.0,
            breakout_type=breakout_type,
            level_index=0,
            failure_candle_index=1,
        )


@pytest.mark.parametrize(
    "level_index,failure_candle_index",
    [
        (-1, 1),
        (1, 1),
        (2, 1),
    ],
)
def test_invalid_indices(level_index, failure_candle_index):
    with pytest.raises(ValueError):
        detect_false_breakout(
            breakout_extreme=105.0,
            failure_close=99.0,
            level_price=100.0,
            breakout_type="BULLISH_BREAKOUT",
            level_index=level_index,
            failure_candle_index=failure_candle_index,
        )


@pytest.mark.parametrize(
    "breakout_extreme,failure_close,level_price",
    [
        (0.0, 99.0, 100.0),
        (105.0, 0.0, 100.0),
        (105.0, 99.0, 0.0),
    ],
)
def test_invalid_prices(
    breakout_extreme,
    failure_close,
    level_price,
):
    with pytest.raises(ValueError):
        detect_false_breakout(
            breakout_extreme=breakout_extreme,
            failure_close=failure_close,
            level_price=level_price,
            breakout_type="BULLISH_BREAKOUT",
            level_index=0,
            failure_candle_index=1,
        )


def test_context_is_frozen():
    result = detect_false_breakout(
        breakout_extreme=105.0,
        failure_close=99.0,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        level_index=0,
        failure_candle_index=1,
    )

    with pytest.raises(AttributeError):
        result.failure_type = "NO_FAILURE"


def test_context_validation_rejects_negative_level_index():
    context = FalseBreakoutContext(
        level_index=-1,
        failure_candle_index=1,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        failure_type="BULLISH_BREAKOUT_FAILURE",
        breakout_extreme=105.0,
        failure_close=99.0,
    )

    with pytest.raises(ValueError, match="Level index"):
        context.validate()


def test_context_validation_rejects_invalid_failure_type():
    context = FalseBreakoutContext(
        level_index=0,
        failure_candle_index=1,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        failure_type="INVALID",
        breakout_extreme=105.0,
        failure_close=99.0,
    )

    with pytest.raises(ValueError, match="Unsupported failure type"):
        context.validate()


def test_context_validation_rejects_mismatched_bullish_failure():
    context = FalseBreakoutContext(
        level_index=0,
        failure_candle_index=1,
        level_price=100.0,
        breakout_type="BEARISH_BREAKOUT",
        failure_type="BULLISH_BREAKOUT_FAILURE",
        breakout_extreme=95.0,
        failure_close=101.0,
    )

    with pytest.raises(ValueError, match="Bullish breakout failure"):
        context.validate()


def test_context_validation_rejects_mismatched_bearish_failure():
    context = FalseBreakoutContext(
        level_index=0,
        failure_candle_index=1,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        failure_type="BEARISH_BREAKOUT_FAILURE",
        breakout_extreme=105.0,
        failure_close=99.0,
    )

    with pytest.raises(ValueError, match="Bearish breakout failure"):
        context.validate()


@pytest.mark.parametrize(
    "price,expected",
    [
        (99.0, "BELOW_BROKEN_LEVEL"),
        (100.0, "ABOVE_OR_AT_LEVEL"),
        (101.0, "ABOVE_OR_AT_LEVEL"),
    ],
)
def test_bullish_level_reclaim(price, expected):
    assert (
        classify_level_reclaim(
            price=price,
            level_price=100.0,
            breakout_type="BULLISH_BREAKOUT",
        )
        == expected
    )


@pytest.mark.parametrize(
    "price,expected",
    [
        (99.0, "BELOW_OR_AT_LEVEL"),
        (100.0, "BELOW_OR_AT_LEVEL"),
        (101.0, "ABOVE_BROKEN_LEVEL"),
    ],
)
def test_bearish_level_reclaim(price, expected):
    assert (
        classify_level_reclaim(
            price=price,
            level_price=100.0,
            breakout_type="BEARISH_BREAKOUT",
        )
        == expected
    )


@pytest.mark.parametrize(
    "price,level_price",
    [
        (0.0, 100.0),
        (100.0, 0.0),
    ],
)
def test_level_reclaim_rejects_invalid_prices(price, level_price):
    with pytest.raises(ValueError):
        classify_level_reclaim(
            price=price,
            level_price=level_price,
            breakout_type="BULLISH_BREAKOUT",
        )


def test_level_reclaim_rejects_invalid_breakout_type():
    with pytest.raises(ValueError, match="Unsupported breakout type"):
        classify_level_reclaim(
            price=100.0,
            level_price=100.0,
            breakout_type="INVALID",
        )
