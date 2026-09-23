"""
Volume-confirmed breakout analysis foundations for Paper Trading Lab.

This module combines an already-detected breakout event with
observable volume information.

Volume classification is descriptive market context only.

This module does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass

from .breakout import BreakoutEvent


VALID_VOLUME_STRENGTHS = {
    "HIGH_VOLUME",
    "NORMAL_VOLUME",
    "LOW_VOLUME",
    "NO_BREAKOUT",
    "INSUFFICIENT_DATA",
}

DEFAULT_RELATIVE_VOLUME_THRESHOLD = 1.5


@dataclass(frozen=True)
class VolumeBreakoutContext:
    """
    Descriptive volume context for a breakout event.
    """

    breakout_type: str
    confirmation_type: str
    relative_volume: float | None
    volume_strength: str

    def validate(self) -> None:
        if self.breakout_type not in {
            "BULLISH_BREAKOUT",
            "BEARISH_BREAKOUT",
            "NO_BREAKOUT",
        }:
            raise ValueError(
                f"Unsupported breakout type: {self.breakout_type}"
            )

        if self.confirmation_type not in {
            "CLOSE_CONFIRMED",
            "WICK_ONLY",
            "NO_CONFIRMATION",
        }:
            raise ValueError(
                f"Unsupported confirmation type: "
                f"{self.confirmation_type}"
            )

        if self.relative_volume is not None:
            if self.relative_volume < 0:
                raise ValueError(
                    "Relative volume cannot be negative"
                )

        if self.volume_strength not in VALID_VOLUME_STRENGTHS:
            raise ValueError(
                f"Unsupported volume strength: "
                f"{self.volume_strength}"
            )


def classify_volume_strength(
    breakout_event: BreakoutEvent,
    relative_volume: float | None,
    threshold: float = DEFAULT_RELATIVE_VOLUME_THRESHOLD,
) -> VolumeBreakoutContext:
    """
    Classify the volume context of an existing breakout event.

    Rules:

    No breakout:
        NO_BREAKOUT

    Missing volume:
        INSUFFICIENT_DATA

    Relative volume >= threshold:
        HIGH_VOLUME

    Relative volume >= 1.0 but below threshold:
        NORMAL_VOLUME

    Relative volume < 1.0:
        LOW_VOLUME

    This function does not generate a trading signal.
    """

    breakout_event.validate()

    if threshold <= 0:
        raise ValueError(
            "Volume threshold must be greater than zero"
        )

    if relative_volume is not None and relative_volume < 0:
        raise ValueError(
            "Relative volume cannot be negative"
        )

    if breakout_event.breakout_type == "NO_BREAKOUT":
        strength = "NO_BREAKOUT"

    elif relative_volume is None:
        strength = "INSUFFICIENT_DATA"

    elif relative_volume >= threshold:
        strength = "HIGH_VOLUME"

    elif relative_volume >= 1.0:
        strength = "NORMAL_VOLUME"

    else:
        strength = "LOW_VOLUME"

    result = VolumeBreakoutContext(
        breakout_type=breakout_event.breakout_type,
        confirmation_type=breakout_event.confirmation_type,
        relative_volume=(
            None
            if relative_volume is None
            else float(relative_volume)
        ),
        volume_strength=strength,
    )

    result.validate()
    return result


def volume_breakout_from_values(
    high: float,
    low: float,
    close: float,
    level_price: float,
    level_type: str,
    candle_index: int,
    level_index: int,
    relative_volume: float | None,
    threshold: float = DEFAULT_RELATIVE_VOLUME_THRESHOLD,
) -> VolumeBreakoutContext:
    """
    Detect a breakout and classify its volume context.

    This is descriptive analysis only.
    """

    from .breakout import detect_breakout

    breakout_event = detect_breakout(
        high=high,
        low=low,
        close=close,
        level_price=level_price,
        level_type=level_type,
        candle_index=candle_index,
        level_index=level_index,
    )

    return classify_volume_strength(
        breakout_event=breakout_event,
        relative_volume=relative_volume,
        threshold=threshold,
    )
