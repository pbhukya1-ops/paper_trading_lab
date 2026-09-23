import pytest

from app.strategy.mtf_structure import (
    SUPPORTED_TIMEFRAMES,
    MultiTimeframeContext,
    TimeframeStructure,
    build_mtf_context,
    build_timeframe_structure,
    get_timeframe_structure,
    higher_timeframe_regime,
)


def test_supported_timeframes_are_in_expected_hierarchy():
    assert SUPPORTED_TIMEFRAMES == (
        "5m",
        "10m",
        "15m",
        "30m",
        "1W",
    )


@pytest.mark.parametrize(
    "timeframe",
    SUPPORTED_TIMEFRAMES,
)
def test_build_timeframe_structure_accepts_supported_timeframes(timeframe):
    result = build_timeframe_structure(
        timeframe=timeframe,
        high_classifications=[None, "HH"],
        low_classifications=[None, "HL"],
    )

    assert isinstance(result, TimeframeStructure)
    assert result.timeframe == timeframe
    assert result.regime == "BULLISH"
    assert result.high_classifications == (None, "HH")
    assert result.low_classifications == (None, "HL")


def test_build_timeframe_structure_classifies_bearish_regime():
    result = build_timeframe_structure(
        timeframe="15m",
        high_classifications=[None, "LH"],
        low_classifications=[None, "LL"],
    )

    assert result.regime == "BEARISH"


def test_build_timeframe_structure_classifies_mixed_regime():
    result = build_timeframe_structure(
        timeframe="30m",
        high_classifications=[None, "HH"],
        low_classifications=[None, "LL"],
    )

    assert result.regime == "RANGE_OR_MIXED"


def test_build_timeframe_structure_handles_insufficient_data():
    result = build_timeframe_structure(
        timeframe="1W",
        high_classifications=[None],
        low_classifications=[None],
    )

    assert result.regime == "INSUFFICIENT_DATA"


def test_build_timeframe_structure_preserves_input_as_immutable_tuples():
    result = build_timeframe_structure(
        timeframe="5m",
        high_classifications=[None, "HH"],
        low_classifications=[None, "HL"],
    )

    assert isinstance(result.high_classifications, tuple)
    assert isinstance(result.low_classifications, tuple)


def test_build_timeframe_structure_rejects_unsupported_timeframe():
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        build_timeframe_structure(
            timeframe="1m",
            high_classifications=[None],
            low_classifications=[None],
        )


def test_build_timeframe_structure_rejects_mismatched_lengths():
    with pytest.raises(
        ValueError,
        match="High and low classifications must have equal length",
    ):
        build_timeframe_structure(
            timeframe="5m",
            high_classifications=[None, "HH"],
            low_classifications=[None],
        )


def test_timeframe_structure_rejects_unsupported_timeframe():
    structure = TimeframeStructure(
        timeframe="1m",
        high_classifications=(None,),
        low_classifications=(None,),
        regime="INSUFFICIENT_DATA",
    )

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        structure.validate()


def test_timeframe_structure_rejects_mismatched_classification_lengths():
    structure = TimeframeStructure(
        timeframe="5m",
        high_classifications=(None, "HH"),
        low_classifications=(None,),
        regime="BULLISH",
    )

    with pytest.raises(
        ValueError,
        match="High and low classifications must have equal length",
    ):
        structure.validate()


def test_timeframe_structure_rejects_invalid_regime():
    structure = TimeframeStructure(
        timeframe="5m",
        high_classifications=(None,),
        low_classifications=(None,),
        regime="INVALID",
    )

    with pytest.raises(ValueError, match="Unsupported structural regime"):
        structure.validate()


def test_build_mtf_context_preserves_input_order():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    weekly = build_timeframe_structure(
        "1W",
        [None, "LH"],
        [None, "LL"],
    )

    context = build_mtf_context([weekly, five])

    assert isinstance(context, MultiTimeframeContext)
    assert context.structures == (weekly, five)


def test_build_mtf_context_rejects_empty_context():
    with pytest.raises(
        ValueError,
        match="Multi-timeframe context cannot be empty",
    ):
        build_mtf_context([])


def test_build_mtf_context_rejects_duplicate_timeframes():
    first = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    second = build_timeframe_structure(
        "5m",
        [None, "LH"],
        [None, "LL"],
    )

    with pytest.raises(ValueError, match="Duplicate timeframe"):
        build_mtf_context([first, second])


def test_get_timeframe_structure_returns_matching_structure():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    fifteen = build_timeframe_structure(
        "15m",
        [None, "LH"],
        [None, "LL"],
    )

    context = build_mtf_context([five, fifteen])

    result = get_timeframe_structure(context, "15m")

    assert result is fifteen


def test_get_timeframe_structure_returns_none_when_missing():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )

    context = build_mtf_context([five])

    assert get_timeframe_structure(context, "15m") is None


def test_get_timeframe_structure_rejects_unsupported_timeframe():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    context = build_mtf_context([five])

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        get_timeframe_structure(context, "1m")


def test_higher_timeframe_regime_follows_configured_hierarchy():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    ten = build_timeframe_structure(
        "10m",
        [None, "LH"],
        [None, "LL"],
    )
    fifteen = build_timeframe_structure(
        "15m",
        [None, "HH"],
        [None, "HL"],
    )

    context = build_mtf_context([five, ten, fifteen])

    assert higher_timeframe_regime(context, "5m") == "BEARISH"
    assert higher_timeframe_regime(context, "10m") == "BULLISH"


def test_higher_timeframe_regime_returns_none_when_next_level_missing():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )

    context = build_mtf_context([five])

    assert higher_timeframe_regime(context, "5m") is None


def test_higher_timeframe_regime_for_weekly_returns_none():
    weekly = build_timeframe_structure(
        "1W",
        [None, "HH"],
        [None, "HL"],
    )

    context = build_mtf_context([weekly])

    assert higher_timeframe_regime(context, "1W") is None


def test_higher_timeframe_regime_handles_full_hierarchy():
    structures = [
        build_timeframe_structure("5m", [None, "HH"], [None, "HL"]),
        build_timeframe_structure("10m", [None, "LH"], [None, "LL"]),
        build_timeframe_structure("15m", [None, "HH"], [None, "HL"]),
        build_timeframe_structure("30m", [None, "LH"], [None, "LL"]),
        build_timeframe_structure("1W", [None, "HH"], [None, "HL"]),
    ]

    context = build_mtf_context(structures)

    assert higher_timeframe_regime(context, "5m") == "BEARISH"
    assert higher_timeframe_regime(context, "10m") == "BULLISH"
    assert higher_timeframe_regime(context, "15m") == "BEARISH"
    assert higher_timeframe_regime(context, "30m") == "BULLISH"
    assert higher_timeframe_regime(context, "1W") is None


def test_higher_timeframe_regime_rejects_unsupported_timeframe():
    five = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    context = build_mtf_context([five])

    with pytest.raises(ValueError, match="Unsupported timeframe"):
        higher_timeframe_regime(context, "1m")


def test_get_timeframe_structure_validates_context():
    invalid = MultiTimeframeContext(structures=())

    with pytest.raises(
        ValueError,
        match="Multi-timeframe context cannot be empty",
    ):
        get_timeframe_structure(invalid, "5m")


def test_higher_timeframe_regime_validates_context():
    invalid = MultiTimeframeContext(structures=())

    with pytest.raises(
        ValueError,
        match="Multi-timeframe context cannot be empty",
    ):
        higher_timeframe_regime(invalid, "5m")


def test_context_is_frozen():
    structure = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )
    context = build_mtf_context([structure])

    with pytest.raises(AttributeError):
        context.structures = (structure,)


def test_timeframe_structure_is_frozen():
    structure = build_timeframe_structure(
        "5m",
        [None, "HH"],
        [None, "HL"],
    )

    with pytest.raises(AttributeError):
        structure.timeframe = "10m"
