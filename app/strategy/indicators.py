"""
Core technical indicators for Paper Trading Lab.

Indicators in this module are pure calculations:
they do not place orders and do not make trading decisions.
"""

from collections.abc import Sequence


def ema(values: Sequence[float], period: int) -> list[float]:
    """
    Calculate Exponential Moving Average.

    The first EMA value is initialized from the first input value.
    Subsequent values use the standard smoothing factor:

        alpha = 2 / (period + 1)

    Returns one EMA value for each input value.
    """
    if period <= 0:
        raise ValueError("EMA period must be greater than zero")

    if not values:
        raise ValueError("EMA input cannot be empty")

    if any(value <= 0 for value in values):
        raise ValueError("EMA input values must be greater than zero")

    alpha = 2.0 / (period + 1)

    result = [float(values[0])]

    for value in values[1:]:
        previous = result[-1]
        current = alpha * float(value) + (1.0 - alpha) * previous
        result.append(current)

    return result


def rsi(values: Sequence[float], period: int = 14) -> list[float]:
    """
    Calculate Relative Strength Index using Wilder-style smoothing.

    The first `period` values are initialized from the average gain/loss.
    Before enough observations exist, RSI is represented as 50.0.

    This function calculates an indicator only.
    It does not generate trading signals.
    """
    if period <= 0:
        raise ValueError("RSI period must be greater than zero")

    if len(values) == 0:
        raise ValueError("RSI input cannot be empty")

    if any(value <= 0 for value in values):
        raise ValueError("RSI input values must be greater than zero")

    prices = [float(value) for value in values]

    if len(prices) == 1:
        return [50.0]

    result = [50.0] * len(prices)

    if len(prices) <= period:
        return result

    gains = []
    losses = []

    for index in range(1, len(prices)):
        change = prices[index] - prices[index - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    average_gain = sum(gains[:period]) / period
    average_loss = sum(losses[:period]) / period

    def calculate_rsi(avg_gain: float, avg_loss: float) -> float:
        if avg_loss == 0:
            return 100.0
        if avg_gain == 0:
            return 0.0

        relative_strength = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + relative_strength))

    result[period] = calculate_rsi(average_gain, average_loss)

    for index in range(period + 1, len(prices)):
        gain = gains[index - 1]
        loss = losses[index - 1]

        average_gain = (
            (average_gain * (period - 1)) + gain
        ) / period

        average_loss = (
            (average_loss * (period - 1)) + loss
        ) / period

        result[index] = calculate_rsi(average_gain, average_loss)

    return result


def volume_sma(values: Sequence[float], period: int) -> list[float]:
    """
    Calculate a simple moving average of volume.

    Before enough observations exist, the available observations
    are used to calculate the average.
    """
    if period <= 0:
        raise ValueError("Volume SMA period must be greater than zero")

    if not values:
        raise ValueError("Volume input cannot be empty")

    if any(value < 0 for value in values):
        raise ValueError("Volume cannot be negative")

    volumes = [float(value) for value in values]
    result = []

    for index in range(len(volumes)):
        start = max(0, index - period + 1)
        window = volumes[start:index + 1]
        result.append(sum(window) / len(window))

    return result


def relative_volume(values: Sequence[float], period: int = 20) -> list[float]:
    """
    Calculate relative volume:

        current volume / volume SMA(period)

    Returns 0.0 when the corresponding average volume is zero.
    """
    if period <= 0:
        raise ValueError("Relative volume period must be greater than zero")

    if not values:
        raise ValueError("Volume input cannot be empty")

    if any(value < 0 for value in values):
        raise ValueError("Volume cannot be negative")

    volumes = [float(value) for value in values]
    averages = volume_sma(volumes, period)

    result = []

    for volume, average in zip(volumes, averages):
        if average == 0:
            result.append(0.0)
        else:
            result.append(volume / average)

    return result
