import pytest

from app.strategy.sweeps import (
    LiquiditySweep,
    detect_liquidity_sweep,
    detect_liquidity_sweeps,
)


def test_valid_buy_side_sweep():
    sweep = LiquiditySweep(5, 2, 100.0, "BUY_SIDE_SWEEP", 105.0, 98.0)
    sweep.validate()


def test_valid_sell_side_sweep():
    sweep = LiquiditySweep(5, 2, 100.0, "SELL_SIDE_SWEEP", 95.0, 102.0)
    sweep.validate()


def test_negative_candle_index_rejected():
    sweep = LiquiditySweep(-1, 0, 100.0, "BUY_SIDE_SWEEP", 105.0, 98.0)
    with pytest.raises(ValueError, match="Candle index cannot be negative"):
        sweep.validate()


def test_negative_level_index_rejected():
    sweep = LiquiditySweep(5, -1, 100.0, "BUY_SIDE_SWEEP", 105.0, 98.0)
    with pytest.raises(
        ValueError,
        match="Liquidity level index cannot be negative",
    ):
        sweep.validate()


def test_non_positive_level_price_rejected():
    sweep = LiquiditySweep(5, 2, 0.0, "BUY_SIDE_SWEEP", 105.0, 98.0)
    with pytest.raises(
        ValueError,
        match="Liquidity level price must be greater than zero",
    ):
        sweep.validate()


def test_non_positive_wick_extreme_rejected():
    sweep = LiquiditySweep(5, 2, 100.0, "BUY_SIDE_SWEEP", 0.0, 98.0)
    with pytest.raises(
        ValueError,
        match="Sweep wick extreme must be greater than zero",
    ):
        sweep.validate()


def test_non_positive_close_rejected():
    sweep = LiquiditySweep(5, 2, 100.0, "BUY_SIDE_SWEEP", 105.0, 0.0)
    with pytest.raises(
        ValueError,
        match="Sweep close price must be greater than zero",
    ):
        sweep.validate()


def test_invalid_sweep_type_rejected():
    sweep = LiquiditySweep(5, 2, 100.0, "UNKNOWN", 105.0, 98.0)
    with pytest.raises(ValueError, match="Unsupported sweep type"):
        sweep.validate()


def test_level_must_precede_candle():
    sweep = LiquiditySweep(2, 2, 100.0, "BUY_SIDE_SWEEP", 105.0, 98.0)
    with pytest.raises(
        ValueError,
        match="Liquidity level must precede the sweep candle",
    ):
        sweep.validate()


def test_detect_buy_side_sweep():
    result = detect_liquidity_sweep(
        high=105.0,
        low=95.0,
        close=98.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert result == LiquiditySweep(
        5, 2, 100.0, "BUY_SIDE_SWEEP", 105.0, 98.0
    )


def test_detect_sell_side_sweep():
    result = detect_liquidity_sweep(
        high=105.0,
        low=95.0,
        close=102.0,
        level_price=100.0,
        level_type="LOW",
        candle_index=5,
        level_index=2,
    )

    assert result == LiquiditySweep(
        5, 2, 100.0, "SELL_SIDE_SWEEP", 95.0, 102.0
    )


def test_exact_high_touch_is_not_sweep():
    assert detect_liquidity_sweep(
        100.0, 95.0, 98.0, 100.0, "HIGH", 5, 2
    ) is None


def test_exact_low_touch_is_not_sweep():
    assert detect_liquidity_sweep(
        105.0, 100.0, 102.0, 100.0, "LOW", 5, 2
    ) is None


def test_buy_side_close_at_level_is_not_sweep():
    assert detect_liquidity_sweep(
        105.0, 95.0, 100.0, 100.0, "HIGH", 5, 2
    ) is None


def test_sell_side_close_at_level_is_not_sweep():
    assert detect_liquidity_sweep(
        105.0, 95.0, 100.0, 100.0, "LOW", 5, 2
    ) is None


def test_invalid_candle_range_rejected():
    with pytest.raises(ValueError, match="Low cannot be greater than high"):
        detect_liquidity_sweep(
            95.0, 100.0, 98.0, 100.0, "HIGH", 5, 2
        )


def test_close_outside_range_rejected():
    with pytest.raises(
        ValueError,
        match="Close must lie within the candle's high-low range",
    ):
        detect_liquidity_sweep(
            105.0, 95.0, 110.0, 100.0, "HIGH", 5, 2
        )


def test_invalid_level_order_rejected():
    with pytest.raises(
        ValueError,
        match="Liquidity level must precede the sweep candle",
    ):
        detect_liquidity_sweep(
            105.0, 95.0, 98.0, 100.0, "HIGH", 2, 2
        )


def test_invalid_level_type_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported liquidity level type",
    ):
        detect_liquidity_sweep(
            105.0, 95.0, 98.0, 100.0, "INVALID", 5, 2
        )


def test_all_buy_side_sweeps_are_chronological():
    highs = [100.0, 105.0, 110.0, 106.0, 115.0]
    lows = [95.0, 95.0, 96.0, 94.0, 97.0]
    closes = [99.0, 98.0, 98.0, 98.0, 99.0]

    result = detect_liquidity_sweeps(
        highs, lows, closes, 0, 100.0, "HIGH"
    )

    assert result == [
        LiquiditySweep(1, 0, 100.0, "BUY_SIDE_SWEEP", 105.0, 98.0),
        LiquiditySweep(2, 0, 100.0, "BUY_SIDE_SWEEP", 110.0, 98.0),
        LiquiditySweep(3, 0, 100.0, "BUY_SIDE_SWEEP", 106.0, 98.0),
        LiquiditySweep(4, 0, 100.0, "BUY_SIDE_SWEEP", 115.0, 99.0),
    ]


def test_all_sweeps_empty_when_none_exist():
    highs = [100.0, 101.0, 102.0]
    lows = [95.0, 96.0, 97.0]
    closes = [99.0, 100.0, 101.0]

    assert detect_liquidity_sweeps(
        highs, lows, closes, 0, 100.0, "HIGH"
    ) == []


def test_all_sweeps_reject_mismatched_lengths():
    with pytest.raises(
        ValueError,
        match="Highs, lows, and closes must have equal length",
    ):
        detect_liquidity_sweeps(
            [100.0, 105.0],
            [95.0],
            [99.0, 100.0],
            0,
            100.0,
            "HIGH",
        )


def test_all_sweeps_reject_empty_input():
    with pytest.raises(ValueError, match="Price input cannot be empty"):
        detect_liquidity_sweeps(
            [], [], [], 0, 100.0, "HIGH"
        )


def test_all_sweeps_reject_level_index_outside_series():
    with pytest.raises(
        ValueError,
        match="Liquidity level index is outside the price series",
    ):
        detect_liquidity_sweeps(
            [100.0, 105.0],
            [95.0, 96.0],
            [99.0, 100.0],
            2,
            100.0,
            "HIGH",
        )


def test_all_sweeps_reject_non_positive_level_price():
    with pytest.raises(
        ValueError,
        match="Liquidity level price must be greater than zero",
    ):
        detect_liquidity_sweeps(
            [100.0, 105.0],
            [95.0, 96.0],
            [99.0, 100.0],
            0,
            0.0,
            "HIGH",
        )
