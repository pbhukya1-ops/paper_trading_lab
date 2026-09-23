import pytest

from app.strategy.pullback import (
    PullbackRetestContext,
    VALID_MOVE_TYPES,
    VALID_RETEST_TYPES,
    classify_retest_distance,
    detect_pullback_retest,
)


def test_valid_move_types():
    assert VALID_MOVE_TYPES == {
        "BULLISH_MOVE",
        "BEARISH_MOVE",
    }


def test_valid_retest_types():
    assert VALID_RETEST_TYPES == {
        "BULLISH_RETEST",
        "BEARISH_RETEST",
        "NO_RETEST",
        "INSUFFICIENT_DATA",
    }


def test_bullish_retest_with_exact_reference():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=110.0,
        retest_price=100.0,
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
    )

    assert result.retest_type == "BULLISH_RETEST"
    assert result.retest_index == 2
    assert result.retest_price == 100.0


def test_bullish_retest_within_tolerance():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=110.0,
        retest_price=104.0,
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
        tolerance=5.0,
    )

    assert result.retest_type == "BULLISH_RETEST"


def test_bullish_price_outside_tolerance_is_no_retest():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=110.0,
        retest_price=106.0,
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
        tolerance=5.0,
    )

    assert result.retest_type == "NO_RETEST"
    assert result.retest_index is None
    assert result.retest_price is None


def test_bearish_retest_with_exact_reference():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=90.0,
        retest_price=100.0,
        move_type="BEARISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
    )

    assert result.retest_type == "BEARISH_RETEST"
    assert result.retest_index == 2
    assert result.retest_price == 100.0


def test_bearish_retest_within_tolerance():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=90.0,
        retest_price=104.0,
        move_type="BEARISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
        tolerance=5.0,
    )

    assert result.retest_type == "BEARISH_RETEST"


def test_bearish_price_outside_tolerance_is_no_retest():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=90.0,
        retest_price=106.0,
        move_type="BEARISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
        tolerance=5.0,
    )

    assert result.retest_type == "NO_RETEST"
    assert result.retest_index is None
    assert result.retest_price is None


def test_tolerance_boundary_counts_as_retest():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=110.0,
        retest_price=105.0,
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
        tolerance=5.0,
    )

    assert result.retest_type == "BULLISH_RETEST"


def test_context_is_frozen():
    result = detect_pullback_retest(
        reference_price=100.0,
        move_extreme=110.0,
        retest_price=100.0,
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
    )

    with pytest.raises(AttributeError):
        result.retest_type = "NO_RETEST"


def test_classify_retest_distance_inside():
    assert (
        classify_retest_distance(
            reference_price=100.0,
            current_price=103.0,
            tolerance=5.0,
        )
        == "WITHIN_RETEST_AREA"
    )


def test_classify_retest_distance_exact_boundary():
    assert (
        classify_retest_distance(
            reference_price=100.0,
            current_price=105.0,
            tolerance=5.0,
        )
        == "WITHIN_RETEST_AREA"
    )


def test_classify_retest_distance_outside():
    assert (
        classify_retest_distance(
            reference_price=100.0,
            current_price=105.1,
            tolerance=5.0,
        )
        == "OUTSIDE_RETEST_AREA"
    )


@pytest.mark.parametrize(
    "reference_price,move_extreme,retest_price",
    [
        (100.0, 100.0, 100.0),
        (100.0, 99.0, 100.0),
    ],
)
def test_bullish_move_requires_extreme_above_reference(
    reference_price,
    move_extreme,
    retest_price,
):
    with pytest.raises(ValueError, match="Bullish move extreme"):
        detect_pullback_retest(
            reference_price=reference_price,
            move_extreme=move_extreme,
            retest_price=retest_price,
            move_type="BULLISH_MOVE",
            reference_index=0,
            move_index=1,
            retest_index=2,
        )


def test_bullish_retest_cannot_exceed_move_extreme():
    with pytest.raises(
        ValueError,
        match="Bullish retest price cannot exceed move extreme",
    ):
        detect_pullback_retest(
            reference_price=100.0,
            move_extreme=110.0,
            retest_price=111.0,
            move_type="BULLISH_MOVE",
            reference_index=0,
            move_index=1,
            retest_index=2,
        )


def test_bearish_move_requires_extreme_below_reference():
    with pytest.raises(ValueError, match="Bearish move extreme"):
        detect_pullback_retest(
            reference_price=100.0,
            move_extreme=100.0,
            retest_price=100.0,
            move_type="BEARISH_MOVE",
            reference_index=0,
            move_index=1,
            retest_index=2,
        )


def test_bearish_retest_cannot_be_below_move_extreme():
    with pytest.raises(
        ValueError,
        match="Bearish retest price cannot be below move extreme",
    ):
        detect_pullback_retest(
            reference_price=100.0,
            move_extreme=90.0,
            retest_price=89.0,
            move_type="BEARISH_MOVE",
            reference_index=0,
            move_index=1,
            retest_index=2,
        )


@pytest.mark.parametrize(
    "reference_index,move_index,retest_index",
    [
        (-1, 1, 2),
        (1, 1, 2),
        (0, 1, 1),
    ],
)
def test_invalid_indices(reference_index, move_index, retest_index):
    with pytest.raises(ValueError):
        detect_pullback_retest(
            reference_price=100.0,
            move_extreme=110.0,
            retest_price=100.0,
            move_type="BULLISH_MOVE",
            reference_index=reference_index,
            move_index=move_index,
            retest_index=retest_index,
        )


def test_invalid_move_type():
    with pytest.raises(ValueError, match="Unsupported move type"):
        detect_pullback_retest(
            reference_price=100.0,
            move_extreme=110.0,
            retest_price=100.0,
            move_type="INVALID",
            reference_index=0,
            move_index=1,
            retest_index=2,
        )


@pytest.mark.parametrize(
    "reference_price,move_extreme,retest_price,tolerance",
    [
        (0.0, 110.0, 100.0, 0.0),
        (100.0, 0.0, 100.0, 0.0),
        (100.0, 110.0, 0.0, 0.0),
        (100.0, 110.0, 100.0, -1.0),
    ],
)
def test_invalid_numeric_inputs(
    reference_price,
    move_extreme,
    retest_price,
    tolerance,
):
    with pytest.raises(ValueError):
        detect_pullback_retest(
            reference_price=reference_price,
            move_extreme=move_extreme,
            retest_price=retest_price,
            move_type="BULLISH_MOVE",
            reference_index=0,
            move_index=1,
            retest_index=2,
            tolerance=tolerance,
        )


def test_classify_retest_distance_invalid_reference():
    with pytest.raises(ValueError, match="Reference price"):
        classify_retest_distance(
            reference_price=0.0,
            current_price=100.0,
            tolerance=5.0,
        )


def test_classify_retest_distance_invalid_current_price():
    with pytest.raises(ValueError, match="Current price"):
        classify_retest_distance(
            reference_price=100.0,
            current_price=0.0,
            tolerance=5.0,
        )


def test_classify_retest_distance_negative_tolerance():
    with pytest.raises(ValueError, match="Tolerance"):
        classify_retest_distance(
            reference_price=100.0,
            current_price=100.0,
            tolerance=-1.0,
        )


def test_context_validation_rejects_invalid_retest_index():
    context = PullbackRetestContext(
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=1,
        reference_price=100.0,
        retest_price=100.0,
        retest_type="BULLISH_RETEST",
    )

    with pytest.raises(ValueError, match="Retest index"):
        context.validate()


def test_context_validation_rejects_no_retest_payload():
    context = PullbackRetestContext(
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
        reference_price=100.0,
        retest_price=100.0,
        retest_type="NO_RETEST",
    )

    with pytest.raises(ValueError, match="NO_RETEST"):
        context.validate()
