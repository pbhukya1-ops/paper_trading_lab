"""
Price-structure foundations for Paper Trading Lab.

This module detects local swing highs and swing lows.
It does not generate trading signals or place orders.
"""

from collections.abc import Sequence


def swing_highs(
    highs: Sequence[float],
    left: int = 2,
    right: int = 2,
) -> list[bool]:
    """
    Detect local swing highs.

    A candle is a swing high when its high is strictly greater
    than all highs in the left and right observation windows.

    Boundary candles without a complete window are False.
    """
    if left <= 0 or right <= 0:
        raise ValueError("Swing windows must be greater than zero")

    if not highs:
        raise ValueError("High input cannot be empty")

    if any(value <= 0 for value in highs):
        raise ValueError("High values must be greater than zero")

    values = [float(value) for value in highs]
    result = [False] * len(values)

    for index in range(left, len(values) - right):
        current = values[index]
        left_window = values[index - left:index]
        right_window = values[index + 1:index + right + 1]

        if current > max(left_window) and current > max(right_window):
            result[index] = True

    return result


def swing_lows(
    lows: Sequence[float],
    left: int = 2,
    right: int = 2,
) -> list[bool]:
    """
    Detect local swing lows.

    A candle is a swing low when its low is strictly lower
    than all lows in the left and right observation windows.

    Boundary candles without a complete window are False.
    """
    if left <= 0 or right <= 0:
        raise ValueError("Swing windows must be greater than zero")

    if not lows:
        raise ValueError("Low input cannot be empty")

    if any(value <= 0 for value in lows):
        raise ValueError("Low values must be greater than zero")

    values = [float(value) for value in lows]
    result = [False] * len(values)

    for index in range(left, len(values) - right):
        current = values[index]
        left_window = values[index - left:index]
        right_window = values[index + 1:index + right + 1]

        if current < min(left_window) and current < min(right_window):
            result[index] = True

    return result


def classify_swing_highs(
    highs: Sequence[float],
    swing_flags: Sequence[bool],
) -> list[str | None]:
    """
    Classify confirmed swing highs relative to the previous
    confirmed swing high.

    Returns:
        HH = Higher High
        LH = Lower High
        EH = Equal High
        None = not a confirmed swing or no previous swing
    """
    if len(highs) != len(swing_flags):
        raise ValueError("Highs and swing_flags must have equal length")

    if any(value <= 0 for value in highs):
        raise ValueError("High values must be greater than zero")

    result: list[str | None] = [None] * len(highs)
    previous_high = None

    for index, (high, is_swing) in enumerate(zip(highs, swing_flags)):
        if not is_swing:
            continue

        current = float(high)

        if previous_high is None:
            previous_high = current
            continue

        if current > previous_high:
            result[index] = "HH"
        elif current < previous_high:
            result[index] = "LH"
        else:
            result[index] = "EH"

        previous_high = current

    return result


def classify_swing_lows(
    lows: Sequence[float],
    swing_flags: Sequence[bool],
) -> list[str | None]:
    """
    Classify confirmed swing lows relative to the previous
    confirmed swing low.

    Returns:
        HL = Higher Low
        LL = Lower Low
        EL = Equal Low
        None = not a confirmed swing or no previous swing
    """
    if len(lows) != len(swing_flags):
        raise ValueError("Lows and swing_flags must have equal length")

    if any(value <= 0 for value in lows):
        raise ValueError("Low values must be greater than zero")

    result: list[str | None] = [None] * len(lows)
    previous_low = None

    for index, (low, is_swing) in enumerate(zip(lows, swing_flags)):
        if not is_swing:
            continue

        current = float(low)

        if previous_low is None:
            previous_low = current
            continue

        if current > previous_low:
            result[index] = "HL"
        elif current < previous_low:
            result[index] = "LL"
        else:
            result[index] = "EL"

        previous_low = current

    return result


def classify_structure_regime(
    high_classifications: Sequence[str | None],
    low_classifications: Sequence[str | None],
) -> str:
    """
    Classify the current market structure conservatively.

    Returns:
        BULLISH
        BEARISH
        RANGE_OR_MIXED
        INSUFFICIENT_DATA

    The latest confirmed high and low classifications are used.
    Equal classifications are treated as non-directional.
    """
    if len(high_classifications) != len(low_classifications):
        raise ValueError(
            "High and low classification series must have equal length"
        )

    latest_high = next(
        (value for value in reversed(high_classifications) if value is not None),
        None,
    )

    latest_low = next(
        (value for value in reversed(low_classifications) if value is not None),
        None,
    )

    if latest_high is None or latest_low is None:
        return "INSUFFICIENT_DATA"

    if latest_high == "HH" and latest_low == "HL":
        return "BULLISH"

    if latest_high == "LH" and latest_low == "LL":
        return "BEARISH"

    return "RANGE_OR_MIXED"


def structural_levels(
    highs: Sequence[float],
    lows: Sequence[float],
    high_flags: Sequence[bool],
    low_flags: Sequence[bool],
) -> list[tuple[int, float, str]]:
    """
    Return confirmed swing levels in chronological order.

    Each level is represented as:

        (index, price, "HIGH")
        (index, price, "LOW")

    No trading decision is made by this function.
    """
    if not (
        len(highs)
        == len(lows)
        == len(high_flags)
        == len(low_flags)
    ):
        raise ValueError(
            "Highs, lows, high_flags, and low_flags must have equal length"
        )

    if any(value <= 0 for value in highs):
        raise ValueError("High values must be greater than zero")

    if any(value <= 0 for value in lows):
        raise ValueError("Low values must be greater than zero")

    levels: list[tuple[int, float, str]] = []

    for index in range(len(highs)):
        if high_flags[index]:
            levels.append((index, float(highs[index]), "HIGH"))

        if low_flags[index]:
            levels.append((index, float(lows[index]), "LOW"))

    return levels
