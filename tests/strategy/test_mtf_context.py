import pytest

from app.strategy.mtf_context import (
    MTFPriceActionContext,
    build_mtf_price_action_context,
)
from app.strategy.mtf_structure import build_mtf_context, build_timeframe_structure


def make_structure(timeframe, high, low):
    return build_timeframe_structure(
        timeframe,
        [None, high],
        [None, low],
    )


def test_aligned_bullish_relationship():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert isinstance(result, MTFPriceActionContext)
    assert result.timeframe == "5m"
    assert result.timeframe_regime == "BULLISH"
    assert result.higher_timeframe == "10m"
    assert result.higher_regime == "BULLISH"
    assert result.relationship == "ALIGNED_BULLISH"


def test_aligned_bearish_relationship():
    context = build_mtf_context([
        make_structure("5m", "LH", "LL"),
        make_structure("10m", "LH", "LL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "BEARISH"
    assert result.higher_regime == "BEARISH"
    assert result.relationship == "ALIGNED_BEARISH"


def test_counter_trend_bullish_relationship():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", "LH", "LL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.relationship == "COUNTER_TREND_BULLISH"


def test_counter_trend_bearish_relationship():
    context = build_mtf_context([
        make_structure("5m", "LH", "LL"),
        make_structure("10m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.relationship == "COUNTER_TREND_BEARISH"


def test_higher_timeframe_mixed_relationship():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", "HH", "LL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "BULLISH"
    assert result.higher_regime == "RANGE_OR_MIXED"
    assert result.relationship == "HIGHER_TIMEFRAME_MIXED"


def test_lower_timeframe_mixed_relationship():
    context = build_mtf_context([
        make_structure("5m", "HH", "LL"),
        make_structure("10m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "RANGE_OR_MIXED"
    assert result.higher_regime == "BULLISH"
    assert result.relationship == "LOWER_TIMEFRAME_MIXED"


def test_insufficient_lower_timeframe_context():
    context = build_mtf_context([
        make_structure("5m", None, None),
        make_structure("10m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "INSUFFICIENT_DATA"
    assert result.higher_regime == "BULLISH"
    assert result.relationship == "INSUFFICIENT_CONTEXT"


def test_insufficient_higher_timeframe_context():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", None, None),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "BULLISH"
    assert result.higher_regime == "INSUFFICIENT_DATA"
    assert result.relationship == "INSUFFICIENT_CONTEXT"


def test_missing_configured_higher_timeframe_returns_insufficient_context_when_lower_is_mixed():
    context = build_mtf_context([
        make_structure("5m", "HH", "LL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "RANGE_OR_MIXED"
    assert result.higher_timeframe == "10m"
    assert result.higher_regime is None
    assert result.relationship == "INSUFFICIENT_CONTEXT"


def test_weekly_has_no_higher_timeframe():
    context = build_mtf_context([
        make_structure("1W", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "1W")

    assert result.timeframe == "1W"
    assert result.timeframe_regime == "BULLISH"
    assert result.higher_timeframe is None
    assert result.higher_regime is None
    assert result.relationship == "NO_HIGHER_TIMEFRAME"


def test_missing_intermediate_higher_timeframe_returns_insufficient_context():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("15m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.higher_timeframe == "10m"
    assert result.higher_regime is None
    assert result.relationship == "INSUFFICIENT_CONTEXT"


def test_build_context_preserves_requested_timeframe():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", "LH", "LL"),
        make_structure("15m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "10m")

    assert result.timeframe == "10m"
    assert result.timeframe_regime == "BEARISH"
    assert result.higher_timeframe == "15m"
    assert result.higher_regime == "BULLISH"
    assert result.relationship == "COUNTER_TREND_BEARISH"


@pytest.mark.parametrize(
    "timeframe,higher_timeframe",
    [
        ("5m", "10m"),
        ("10m", "15m"),
        ("15m", "30m"),
        ("30m", "1W"),
    ],
)
def test_configured_higher_timeframe_relationship(
    timeframe,
    higher_timeframe,
):
    context = build_mtf_context([
        make_structure(timeframe, "HH", "HL"),
        make_structure(higher_timeframe, "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, timeframe)

    assert result.higher_timeframe == higher_timeframe
    assert result.higher_regime == "BULLISH"
    assert result.relationship == "ALIGNED_BULLISH"


def test_build_context_rejects_unsupported_timeframe():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
    ])

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        build_mtf_price_action_context(context, "1m")


def test_build_context_rejects_timeframe_not_present():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", "HH", "HL"),
    ])

    with pytest.raises(
        ValueError,
        match="Timeframe 15m is not present in the MTF context",
    ):
        build_mtf_price_action_context(context, "15m")


def test_context_validation_rejects_unsupported_timeframe():
    result = MTFPriceActionContext(
        timeframe="1m",
        timeframe_regime="BULLISH",
        higher_timeframe=None,
        higher_regime=None,
        relationship="NO_HIGHER_TIMEFRAME",
    )

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        result.validate()


def test_context_validation_rejects_invalid_timeframe_regime():
    result = MTFPriceActionContext(
        timeframe="5m",
        timeframe_regime="INVALID",
        higher_timeframe=None,
        higher_regime=None,
        relationship="NO_HIGHER_TIMEFRAME",
    )

    with pytest.raises(ValueError, match="Unsupported timeframe regime"):
        result.validate()


def test_context_validation_rejects_invalid_higher_timeframe():
    result = MTFPriceActionContext(
        timeframe="5m",
        timeframe_regime="BULLISH",
        higher_timeframe="1m",
        higher_regime="BULLISH",
        relationship="ALIGNED_BULLISH",
    )

    with pytest.raises(ValueError, match="Unsupported higher timeframe"):
        result.validate()


def test_context_validation_rejects_invalid_higher_regime():
    result = MTFPriceActionContext(
        timeframe="5m",
        timeframe_regime="BULLISH",
        higher_timeframe="10m",
        higher_regime="INVALID",
        relationship="ALIGNED_BULLISH",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported higher timeframe regime",
    ):
        result.validate()


def test_context_validation_rejects_invalid_relationship():
    result = MTFPriceActionContext(
        timeframe="5m",
        timeframe_regime="BULLISH",
        higher_timeframe="10m",
        higher_regime="BULLISH",
        relationship="INVALID",
    )

    with pytest.raises(ValueError, match="Unsupported MTF relationship"):
        result.validate()


def test_context_is_frozen():
    context = build_mtf_context([
        make_structure("5m", "HH", "HL"),
        make_structure("10m", "HH", "HL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    with pytest.raises(AttributeError):
        result.timeframe = "10m"


def test_higher_timeframe_mixed_takes_precedence_over_lower_mixed():
    context = build_mtf_context([
        make_structure("5m", "HH", "LL"),
        make_structure("10m", "HH", "LL"),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.timeframe_regime == "RANGE_OR_MIXED"
    assert result.higher_regime == "RANGE_OR_MIXED"
    assert result.relationship == "HIGHER_TIMEFRAME_MIXED"


def test_insufficient_higher_context_is_reported_before_mixed_classification():
    context = build_mtf_context([
        make_structure("5m", "HH", "LL"),
        make_structure("10m", None, None),
    ])

    result = build_mtf_price_action_context(context, "5m")

    assert result.relationship == "INSUFFICIENT_CONTEXT"
