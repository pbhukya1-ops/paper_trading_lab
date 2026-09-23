"""
RSI(14) pullback analysis foundations for Paper Trading Lab.

This module describes observable RSI behavior:
- RSI location relative to a configurable reference level.
- Whether RSI is turning upward.
- Whether RSI is near the commonly observed 40 region.

RSI is treated as one analytical component only.
This module does NOT establish a trading decision.

This module does NOT:
- make automatic trading decisions,
- recommend trades,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass


DEFAULT_PERIOD = 14
DEFAULT_REFERENCE = 40.0
DEFAULT_TOLERANCE = 5.0


VALID_STATES = {
    "BELOW_REFERENCE",
    "NEAR_REFERENCE",
    "ABOVE_REFERENCE",
    "INSUFFICIENT_DATA",
}


VALID_TURN_STATES = {
    "UPWARD_TURN",
    "NO_UPWARD_TURN",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True)
class RSIPullbackContext:
    period: int
    current_rsi: float
    previous_rsi: float | None
    reference_level: float
    tolerance: float
    location_state: str
    turn_state: str

    def validate(self) -> None:
        if self.period <= 0:
            raise ValueError(
                "RSI period must be greater than zero"
            )

        if not 0.0 <= self.current_rsi <= 100.0:
            raise ValueError(
                "Current RSI must be between 0 and 100"
            )

        if self.previous_rsi is not None:
            if not 0.0 <= self.previous_rsi <= 100.0:
                raise ValueError(
                    "Previous RSI must be between 0 and 100"
                )

        if not 0.0 < self.reference_level < 100.0:
            raise ValueError(
                "Reference level must be between 0 and 100"
            )

        if self.tolerance < 0:
            raise ValueError(
                "Tolerance cannot be negative"
            )

        if self.reference_level - self.tolerance < 0:
            raise ValueError(
                "Reference/tolerance range cannot go below 0"
            )

        if self.reference_level + self.tolerance > 100:
            raise ValueError(
                "Reference/tolerance range cannot exceed 100"
            )

        if self.location_state not in VALID_STATES:
            raise ValueError(
                f"Unsupported RSI location state: "
                f"{self.location_state}"
            )

        if self.turn_state not in VALID_TURN_STATES:
            raise ValueError(
                f"Unsupported RSI turn state: "
                f"{self.turn_state}"
            )


def classify_rsi_location(
    rsi_value: float,
    reference_level: float = DEFAULT_REFERENCE,
    tolerance: float = DEFAULT_TOLERANCE,
) -> str:
    """
    Classify RSI location relative to a reference level.

    The default reference is 40 with a +/-5 tolerance.

    35 <= RSI <= 45:
        NEAR_REFERENCE

    RSI < 35:
        BELOW_REFERENCE

    RSI > 45:
        ABOVE_REFERENCE
    """

    if not 0.0 <= rsi_value <= 100.0:
        raise ValueError(
            "RSI value must be between 0 and 100"
        )

    if not 0.0 < reference_level < 100.0:
        raise ValueError(
            "Reference level must be between 0 and 100"
        )

    if tolerance < 0:
        raise ValueError(
            "Tolerance cannot be negative"
        )

    lower = reference_level - tolerance
    upper = reference_level + tolerance

    if lower < 0 or upper > 100:
        raise ValueError(
            "Reference/tolerance range must remain within 0-100"
        )

    if rsi_value < lower:
        return "BELOW_REFERENCE"

    if rsi_value <= upper:
        return "NEAR_REFERENCE"

    return "ABOVE_REFERENCE"


def classify_rsi_turn(
    previous_rsi: float | None,
    current_rsi: float,
) -> str:
    """
    Describe whether RSI has moved upward from the previous observation.

    previous < current:
        UPWARD_TURN

    previous >= current:
        NO_UPWARD_TURN

    No previous observation:
        INSUFFICIENT_DATA
    """

    if not 0.0 <= current_rsi <= 100.0:
        raise ValueError(
            "Current RSI must be between 0 and 100"
        )

    if previous_rsi is None:
        return "INSUFFICIENT_DATA"

    if not 0.0 <= previous_rsi <= 100.0:
        raise ValueError(
            "Previous RSI must be between 0 and 100"
        )

    if current_rsi > previous_rsi:
        return "UPWARD_TURN"

    return "NO_UPWARD_TURN"


def build_rsi_pullback_context(
    current_rsi: float,
    previous_rsi: float | None = None,
    period: int = DEFAULT_PERIOD,
    reference_level: float = DEFAULT_REFERENCE,
    tolerance: float = DEFAULT_TOLERANCE,
) -> RSIPullbackContext:
    """
    Build an immutable descriptive RSI pullback context.

    The default configuration observes RSI(14) near the 40 region.

    This function does not combine RSI with other indicators
    and does not produce a trading decision.
    """

    if period <= 0:
        raise ValueError(
            "RSI period must be greater than zero"
        )

    location_state = classify_rsi_location(
        current_rsi,
        reference_level,
        tolerance,
    )

    turn_state = classify_rsi_turn(
        previous_rsi,
        current_rsi,
    )

    result = RSIPullbackContext(
        period=period,
        current_rsi=float(current_rsi),
        previous_rsi=(
            None
            if previous_rsi is None
            else float(previous_rsi)
        ),
        reference_level=float(reference_level),
        tolerance=float(tolerance),
        location_state=location_state,
        turn_state=turn_state,
    )

    result.validate()
    return result


def is_near_reference_and_turning_up(
    context: RSIPullbackContext,
) -> bool:
    """
    Return whether the supplied context simultaneously describes:

    1. RSI near the reference level.
    2. RSI turning upward.

    This is an analytical observation only.
    It is only an analytical observation.
    """

    context.validate()

    return (
        context.location_state == "NEAR_REFERENCE"
        and context.turn_state == "UPWARD_TURN"
    )
