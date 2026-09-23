import pytest

from app.strategy.confluence import (
    VALID_REGIMES,
    VALID_RELATIONSHIPS,
    VALID_BREAKOUT_STATES,
    VALID_RETEST_STATES,
    VALID_VOLUME_STATES,
    VALID_INTERACTION_TYPES,
    VALID_FAILURE_STATES,
    ConfluenceContext,
    build_confluence_context,
    observation_count,
)


def make_context(**overrides):
    values = {
        "timeframe": "15m",
        "higher_timeframe": "1W",
        "market_regime": "TRENDING_BULLISH",
        "mtf_relationship": "ALIGNED_BULLISH",
        "breakout_state": "BULLISH_BREAKOUT",
        "retest_state": "BULLISH_RETEST",
        "volume_state": "HIGH_VOLUME",
        "ema_zone_interaction": "SUPPORT_EMA_INTERACTION",
        "false_breakout_state": "NO_FAILURE",
        "rsi_location_state": "NEAR_REFERENCE",
        "rsi_turn_state": "UPWARD_TURN",
        "liquidity_observation": True,
        "fvg_observation": True,
        "inducement_observation": True,
        "target_geometry_available": True,
    }
    values.update(overrides)
    return ConfluenceContext(**values)


def test_valid_constant_sets():
    assert VALID_REGIMES == {
        "TRENDING_BULLISH",
        "TRENDING_BEARISH",
        "RANGE",
        "TRANSITION",
        "INSUFFICIENT_DATA",
    }

    assert VALID_RELATIONSHIPS == {
        "ALIGNED_BULLISH",
        "ALIGNED_BEARISH",
        "COUNTER_TREND_BULLISH",
        "COUNTER_TREND_BEARISH",
        "HIGHER_TIMEFRAME_MIXED",
        "LOWER_TIMEFRAME_MIXED",
        "INSUFFICIENT_CONTEXT",
        "NO_HIGHER_TIMEFRAME",
    }

    assert VALID_BREAKOUT_STATES == {
        "BULLISH_BREAKOUT",
        "BEARISH_BREAKOUT",
        "NO_BREAKOUT",
        "INSUFFICIENT_DATA",
    }

    assert VALID_RETEST_STATES == {
        "BULLISH_RETEST",
        "BEARISH_RETEST",
        "NO_RETEST",
        "INSUFFICIENT_DATA",
    }

    assert VALID_VOLUME_STATES == {
        "HIGH_VOLUME",
        "NORMAL_VOLUME",
        "LOW_VOLUME",
        "NO_BREAKOUT",
        "INSUFFICIENT_DATA",
    }

    assert VALID_INTERACTION_TYPES == {
        "SUPPORT_EMA_INTERACTION",
        "RESISTANCE_EMA_INTERACTION",
        "SUPPORT_ONLY",
        "RESISTANCE_ONLY",
        "EMA_ONLY",
        "NO_INTERACTION",
    }

    assert VALID_FAILURE_STATES == {
        "BULLISH_BREAKOUT_FAILURE",
        "BEARISH_BREAKOUT_FAILURE",
        "NO_FAILURE",
        "INSUFFICIENT_DATA",
    }


def test_valid_context_passes_validation():
    context = make_context()
    context.validate()


def test_context_is_frozen():
    context = make_context()

    with pytest.raises(Exception):
        context.market_regime = "RANGE"


def test_higher_timeframe_can_be_none():
    context = make_context(higher_timeframe=None)
    context.validate()


def test_higher_timeframe_empty_string_is_rejected():
    context = make_context(higher_timeframe="")

    with pytest.raises(ValueError, match="Higher timeframe"):
        context.validate()


def test_empty_timeframe_is_rejected():
    context = make_context(timeframe="")

    with pytest.raises(ValueError, match="Timeframe"):
        context.validate()


@pytest.mark.parametrize(
    "field,value",
    [
        ("market_regime", "INVALID"),
        ("mtf_relationship", "INVALID"),
        ("breakout_state", "INVALID"),
        ("retest_state", "INVALID"),
        ("volume_state", "INVALID"),
        ("ema_zone_interaction", "INVALID"),
        ("false_breakout_state", "INVALID"),
        ("rsi_location_state", "INVALID"),
        ("rsi_turn_state", "INVALID"),
    ],
)
def test_invalid_enum_states_are_rejected(field, value):
    context = make_context(**{field: value})

    with pytest.raises(ValueError):
        context.validate()


@pytest.mark.parametrize(
    "field",
    [
        "liquidity_observation",
        "fvg_observation",
        "inducement_observation",
        "target_geometry_available",
    ],
)
def test_boolean_observations_must_be_boolean(field):
    context = make_context(**{field: 1})

    with pytest.raises(ValueError, match="must be boolean"):
        context.validate()


def test_observation_count_all_four():
    context = make_context(
        liquidity_observation=True,
        fvg_observation=True,
        inducement_observation=True,
        target_geometry_available=True,
    )

    assert observation_count(context) == 4


def test_observation_count_none():
    context = make_context(
        liquidity_observation=False,
        fvg_observation=False,
        inducement_observation=False,
        target_geometry_available=False,
    )

    assert observation_count(context) == 0


def test_observation_count_partial():
    context = make_context(
        liquidity_observation=True,
        fvg_observation=False,
        inducement_observation=True,
        target_geometry_available=False,
    )

    assert observation_count(context) == 2


def test_observation_count_validates_context_first():
    context = make_context(market_regime="INVALID")

    with pytest.raises(ValueError):
        observation_count(context)


def test_build_context_returns_confluence_context():
    context = build_confluence_context(
        timeframe="15m",
        higher_timeframe="1W",
        market_regime="TRENDING_BULLISH",
        mtf_relationship="ALIGNED_BULLISH",
        breakout_state="BULLISH_BREAKOUT",
        retest_state="BULLISH_RETEST",
        volume_state="HIGH_VOLUME",
        ema_zone_interaction="SUPPORT_EMA_INTERACTION",
        false_breakout_state="NO_FAILURE",
        rsi_location_state="NEAR_REFERENCE",
        rsi_turn_state="UPWARD_TURN",
        liquidity_observation=True,
        fvg_observation=True,
        inducement_observation=False,
        target_geometry_available=True,
    )

    assert isinstance(context, ConfluenceContext)
    assert context.timeframe == "15m"
    assert context.higher_timeframe == "1W"
    assert context.market_regime == "TRENDING_BULLISH"
    assert context.mtf_relationship == "ALIGNED_BULLISH"
    assert context.breakout_state == "BULLISH_BREAKOUT"
    assert context.retest_state == "BULLISH_RETEST"
    assert context.volume_state == "HIGH_VOLUME"
    assert context.ema_zone_interaction == "SUPPORT_EMA_INTERACTION"
    assert context.false_breakout_state == "NO_FAILURE"
    assert context.rsi_location_state == "NEAR_REFERENCE"
    assert context.rsi_turn_state == "UPWARD_TURN"
    assert observation_count(context) == 3


def test_build_context_rejects_empty_timeframe():
    with pytest.raises(ValueError, match="Timeframe"):
        build_confluence_context(
            timeframe="",
            higher_timeframe="1W",
            market_regime="TRENDING_BULLISH",
            mtf_relationship="ALIGNED_BULLISH",
            breakout_state="BULLISH_BREAKOUT",
            retest_state="BULLISH_RETEST",
            volume_state="HIGH_VOLUME",
            ema_zone_interaction="SUPPORT_EMA_INTERACTION",
            false_breakout_state="NO_FAILURE",
            rsi_location_state="NEAR_REFERENCE",
            rsi_turn_state="UPWARD_TURN",
            liquidity_observation=True,
            fvg_observation=True,
            inducement_observation=True,
            target_geometry_available=True,
        )


def test_bearish_context_is_preserved():
    context = make_context(
        market_regime="TRENDING_BEARISH",
        mtf_relationship="ALIGNED_BEARISH",
        breakout_state="BEARISH_BREAKOUT",
        retest_state="BEARISH_RETEST",
        ema_zone_interaction="RESISTANCE_EMA_INTERACTION",
        false_breakout_state="BEARISH_BREAKOUT_FAILURE",
    )

    context.validate()

    assert context.market_regime == "TRENDING_BEARISH"
    assert context.mtf_relationship == "ALIGNED_BEARISH"
    assert context.breakout_state == "BEARISH_BREAKOUT"
    assert context.retest_state == "BEARISH_RETEST"
    assert context.ema_zone_interaction == "RESISTANCE_EMA_INTERACTION"
    assert context.false_breakout_state == "BEARISH_BREAKOUT_FAILURE"


def test_range_context_is_preserved():
    context = make_context(
        market_regime="RANGE",
        mtf_relationship="HIGHER_TIMEFRAME_MIXED",
        breakout_state="NO_BREAKOUT",
        retest_state="NO_RETEST",
        volume_state="NO_BREAKOUT",
        ema_zone_interaction="NO_INTERACTION",
        false_breakout_state="NO_FAILURE",
        rsi_location_state="NEAR_REFERENCE",
        rsi_turn_state="NO_UPWARD_TURN",
    )

    context.validate()

    assert context.market_regime == "RANGE"
    assert context.breakout_state == "NO_BREAKOUT"
    assert context.volume_state == "NO_BREAKOUT"


def test_no_higher_timeframe_relationship_is_preserved():
    context = make_context(
        higher_timeframe=None,
        mtf_relationship="NO_HIGHER_TIMEFRAME",
    )

    context.validate()

    assert context.higher_timeframe is None
    assert context.mtf_relationship == "NO_HIGHER_TIMEFRAME"
