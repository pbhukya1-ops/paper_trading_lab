import pytest

from app.strategy.indicators import (
    ema,
    relative_volume,
    rsi,
    volume_sma,
)


def test_ema_returns_expected_length():
    values = [1, 2, 3, 4, 5]

    result = ema(values, period=3)

    assert len(result) == len(values)


def test_ema_initial_value_matches_first_observation():
    values = [10, 20, 30, 40]

    result = ema(values, period=3)

    assert result[0] == pytest.approx(10.0)


def test_ema_is_monotonic_for_increasing_input():
    values = [10, 20, 30, 40, 50]

    result = ema(values, period=3)

    assert all(
        result[index] <= result[index + 1]
        for index in range(len(result) - 1)
    )


def test_ema_reacts_more_than_sma_to_recent_change():
    values = [10, 10, 10, 10, 20]

    result = ema(values, period=3)

    assert result[-1] > 13.0


def test_rsi_returns_expected_length():
    values = list(range(1, 21))

    result = rsi(values, period=14)

    assert len(result) == len(values)


def test_rsi_strongly_increasing_series_is_high():
    values = list(range(1, 31))

    result = rsi(values, period=14)

    assert result[-1] > 90.0


def test_rsi_strongly_decreasing_series_is_low():
    values = list(range(30, 0, -1))

    result = rsi(values, period=14)

    assert result[-1] < 10.0


def test_rsi_flat_series_follows_current_zero_loss_contract():
    values = [100.0] * 30

    result = rsi(values, period=14)

    # Current implementation defines avg_loss == 0 as RSI 100.0.
    assert result[-1] == pytest.approx(100.0)


def test_volume_sma_returns_expected_length():
    volumes = [100, 200, 300, 400, 500]

    result = volume_sma(volumes, period=3)

    assert len(result) == len(volumes)


def test_volume_sma_matches_recent_average():
    volumes = [100, 200, 300, 400, 500]

    result = volume_sma(volumes, period=3)

    assert result[-1] == pytest.approx(400.0)


def test_relative_volume_is_one_when_volume_equals_average():
    volumes = [100, 100, 100, 100, 100]

    result = relative_volume(volumes, period=3)

    assert result[-1] == pytest.approx(1.0)


def test_relative_volume_uses_current_inclusive_volume_sma():
    volumes = [100, 100, 100, 200]

    result = relative_volume(volumes, period=3)

    # Current implementation uses the current-inclusive SMA:
    # 200 / ((100 + 100 + 200) / 3) = 1.5
    assert result[-1] == pytest.approx(1.5)


def test_invalid_ema_period_is_rejected():
    with pytest.raises(ValueError):
        ema([1, 2, 3], period=0)


def test_invalid_rsi_period_is_rejected():
    with pytest.raises(ValueError):
        rsi([1, 2, 3], period=0)


def test_invalid_volume_sma_period_is_rejected():
    with pytest.raises(ValueError):
        volume_sma([1, 2, 3], period=0)


def test_invalid_relative_volume_period_is_rejected():
    with pytest.raises(ValueError):
        relative_volume([1, 2, 3], period=0)
