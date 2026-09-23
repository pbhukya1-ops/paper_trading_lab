import pytest

from app.strategy.rsi_pullback import (
    DEFAULT_PERIOD,
    DEFAULT_REFERENCE,
    DEFAULT_TOLERANCE,
    VALID_STATES,
    VALID_TURN_STATES,
    RSIPullbackContext,
    classify_rsi_location,
    classify_rsi_turn,
    build_rsi_pullback_context,
    is_near_reference_and_turning_up,
)


def test_default_configuration():
    assert DEFAULT_PERIOD == 14
    assert DEFAULT_REFERENCE == 40.0
    assert DEFAULT_TOLERANCE == 5.0


def test_valid_state_sets():
    assert VALID_STATES == {
        "BELOW_REFERENCE",
        "NEAR_REFERENCE",
        "ABOVE_REFERENCE",
        "INSUFFICIENT_DATA",
    }

    assert VALID_TURN_STATES == {
        "UPWARD_TURN",
        "NO_UPWARD_TURN",
        "INSUFFICIENT_DATA",
    }


@pytest.mark.parametrize(
    ("rsi", "expected"),
    [
        (34.9, "BELOW_REFERENCE"),
        (35.0, "NEAR_REFERENCE"),
        (40.0, "NEAR_REFERENCE"),
        (45.0, "NEAR_REFERENCE"),
        (45.1, "ABOVE_REFERENCE"),
    ],
)
def test_default_rsi_location(rsi, expected):
    assert classify_rsi_location(rsi) == expected


@pytest.mark.parametrize(
    ("rsi", "reference", "tolerance", "expected"),
    [
        (49.9, 50.0, 10.0, "NEAR_REFERENCE"),
        (60.0, 50.0, 10.0, "NEAR_REFERENCE"),
        (60.1, 50.0, 10.0, "ABOVE_REFERENCE"),
        (39.9, 50.0, 10.0, "BELOW_REFERENCE"),
        (40.0, 50.0, 10.0, "NEAR_REFERENCE"),
    ],
)
def test_custom_rsi_location(rsi, reference, tolerance, expected):
    assert classify_rsi_location(
        rsi,
        reference_level=reference,
        tolerance=tolerance,
    ) == expected


@pytest.mark.parametrize(
    "rsi",
    [-0.1, 100.1],
)
def test_rsi_location_rejects_out_of_range_rsi(rsi):
    with pytest.raises(ValueError):
        classify_rsi_location(rsi)


@pytest.mark.parametrize(
    ("reference", "tolerance"),
    [
        (0.0, 5.0),
        (100.0, 5.0),
        (40.0, -1.0),
        (2.0, 5.0),
        (98.0, 5.0),
    ],
)
def test_rsi_location_rejects_invalid_reference_range(
    reference,
    tolerance,
):
    with pytest.raises(ValueError):
        classify_rsi_location(
            40.0,
            reference_level=reference,
            tolerance=tolerance,
        )


@pytest.mark.parametrize(
    ("previous", "current", "expected"),
    [
        (39.0, 40.0, "UPWARD_TURN"),
        (40.0, 40.1, "UPWARD_TURN"),
        (40.0, 40.0, "NO_UPWARD_TURN"),
        (41.0, 40.0, "NO_UPWARD_TURN"),
    ],
)
def test_rsi_turn_classification(previous, current, expected):
    assert classify_rsi_turn(previous, current) == expected


def test_rsi_turn_without_previous_observation():
    assert (
        classify_rsi_turn(None, 40.0)
        == "INSUFFICIENT_DATA"
    )


@pytest.mark.parametrize(
    "current",
    [-0.1, 100.1],
)
def test_rsi_turn_rejects_invalid_current_rsi(current):
    with pytest.raises(ValueError):
        classify_rsi_turn(40.0, current)


@pytest.mark.parametrize(
    "previous",
    [-0.1, 100.1],
)
def test_rsi_turn_rejects_invalid_previous_rsi(previous):
    with pytest.raises(ValueError):
        classify_rsi_turn(previous, 40.0)


def test_default_pullback_context():
    context = build_rsi_pullback_context(
        current_rsi=40.0,
        previous_rsi=39.0,
    )

    assert context.period == 14
    assert context.current_rsi == 40.0
    assert context.previous_rsi == 39.0
    assert context.reference_level == 40.0
    assert context.tolerance == 5.0
    assert context.location_state == "NEAR_REFERENCE"
    assert context.turn_state == "UPWARD_TURN"


def test_pullback_context_is_frozen():
    context = build_rsi_pullback_context(
        current_rsi=40.0,
        previous_rsi=39.0,
    )

    with pytest.raises(Exception):
        context.current_rsi = 41.0


def test_near_reference_and_turning_up_is_true():
    context = build_rsi_pullback_context(
        current_rsi=40.0,
        previous_rsi=39.0,
    )

    assert is_near_reference_and_turning_up(context) is True


def test_near_reference_without_upward_turn_is_false():
    context = build_rsi_pullback_context(
        current_rsi=40.0,
        previous_rsi=41.0,
    )

    assert context.location_state == "NEAR_REFERENCE"
    assert context.turn_state == "NO_UPWARD_TURN"
    assert is_near_reference_and_turning_up(context) is False


def test_upward_turn_above_reference_is_false():
    context = build_rsi_pullback_context(
        current_rsi=50.0,
        previous_rsi=49.0,
    )

    assert context.location_state == "ABOVE_REFERENCE"
    assert context.turn_state == "UPWARD_TURN"
    assert is_near_reference_and_turning_up(context) is False


def test_below_reference_with_upward_turn_is_false():
    context = build_rsi_pullback_context(
        current_rsi=30.0,
        previous_rsi=29.0,
    )

    assert context.location_state == "BELOW_REFERENCE"
    assert context.turn_state == "UPWARD_TURN"
    assert is_near_reference_and_turning_up(context) is False


def test_missing_previous_rsi_produces_insufficient_turn_data():
    context = build_rsi_pullback_context(
        current_rsi=40.0,
        previous_rsi=None,
    )

    assert context.location_state == "NEAR_REFERENCE"
    assert context.turn_state == "INSUFFICIENT_DATA"
    assert is_near_reference_and_turning_up(context) is False


@pytest.mark.parametrize(
    "period",
    [0, -1],
)
def test_context_rejects_invalid_period(period):
    with pytest.raises(ValueError):
        build_rsi_pullback_context(
            current_rsi=40.0,
            previous_rsi=39.0,
            period=period,
        )


def test_context_with_custom_reference_and_tolerance():
    context = build_rsi_pullback_context(
        current_rsi=50.0,
        previous_rsi=49.0,
        period=14,
        reference_level=50.0,
        tolerance=2.0,
    )

    assert context.reference_level == 50.0
    assert context.tolerance == 2.0
    assert context.location_state == "NEAR_REFERENCE"
    assert context.turn_state == "UPWARD_TURN"
    assert is_near_reference_and_turning_up(context) is True


def test_context_validation_rejects_invalid_location_state():
    context = RSIPullbackContext(
        period=14,
        current_rsi=40.0,
        previous_rsi=39.0,
        reference_level=40.0,
        tolerance=5.0,
        location_state="INVALID",
        turn_state="UPWARD_TURN",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_validation_rejects_invalid_turn_state():
    context = RSIPullbackContext(
        period=14,
        current_rsi=40.0,
        previous_rsi=39.0,
        reference_level=40.0,
        tolerance=5.0,
        location_state="NEAR_REFERENCE",
        turn_state="INVALID",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_validation_rejects_invalid_current_rsi():
    context = RSIPullbackContext(
        period=14,
        current_rsi=101.0,
        previous_rsi=39.0,
        reference_level=40.0,
        tolerance=5.0,
        location_state="NEAR_REFERENCE",
        turn_state="UPWARD_TURN",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_validation_rejects_invalid_previous_rsi():
    context = RSIPullbackContext(
        period=14,
        current_rsi=40.0,
        previous_rsi=-1.0,
        reference_level=40.0,
        tolerance=5.0,
        location_state="NEAR_REFERENCE",
        turn_state="UPWARD_TURN",
    )

    with pytest.raises(ValueError):
        context.validate()


def test_context_validation_rejects_invalid_reference_tolerance():
    context = RSIPullbackContext(
        period=14,
        current_rsi=40.0,
        previous_rsi=39.0,
        reference_level=2.0,
        tolerance=5.0,
        location_state="NEAR_REFERENCE",
        turn_state="UPWARD_TURN",
    )

    with pytest.raises(ValueError):
        context.validate()
