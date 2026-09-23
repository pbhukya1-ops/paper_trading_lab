from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.data.candle import Candle
from app.strategy.analyzer import (
    analyze_multi_timeframe,
    analyze_timeframe,
)


IST = ZoneInfo("Asia/Kolkata")


def make_candles(timeframe: str, step_minutes: int) -> list[Candle]:
    highs = [
        100.0, 105.0, 110.0, 104.0, 103.0,
        120.0, 114.0, 113.0, 130.0, 124.0, 123.0,
    ]
    lows = [
        95.0, 94.0, 90.0, 96.0, 97.0,
        95.0, 99.0, 100.0, 98.0, 104.0, 105.0,
    ]

    candles = []

    for index, (high, low) in enumerate(zip(highs, lows)):
        close = (high + low) / 2.0
        open_price = close - 0.5

        timestamp = datetime(
            2026,
            9,
            21,
            9,
            15,
            tzinfo=IST,
        ) + timedelta(minutes=index * step_minutes)

        candles.append(
            Candle(
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=1000.0 + index * 100.0,
                timeframe=timeframe,
                completed=True,
            )
        )

    return candles


def test_analyze_timeframe_builds_complete_result():
    candles = make_candles("5m", 5)

    result = analyze_timeframe("5m", candles)

    assert result.timeframe == "5m"
    assert len(result.closes) == len(candles)
    assert len(result.ema21) == len(candles)
    assert len(result.rsi14) == len(candles)
    assert len(result.relative_volume20) == len(candles)

    assert result.analysis_context.market_regime.market_regime == (
        "TRENDING_BULLISH"
    )
    assert result.analysis_context.trend_quality.market_regime == (
        "TRENDING_BULLISH"
    )
    assert result.analysis_context.mtf_context.relationship == (
        "INSUFFICIENT_CONTEXT"
    )


def test_analyze_multi_timeframe_builds_higher_timeframe_context():
    candles_5m = make_candles("5m", 5)
    candles_10m = make_candles("10m", 10)

    results = analyze_multi_timeframe(
        {
            "5m": candles_5m,
            "10m": candles_10m,
        }
    )

    assert set(results) == {"5m", "10m"}

    five_minute = results["5m"]
    ten_minute = results["10m"]

    assert five_minute.analysis_context.mtf_context.higher_timeframe == "10m"
    assert five_minute.analysis_context.mtf_context.higher_regime == "BULLISH"
    assert five_minute.analysis_context.mtf_context.relationship == (
        "ALIGNED_BULLISH"
    )

    assert ten_minute.analysis_context.mtf_context.higher_timeframe == "15m"
    assert ten_minute.analysis_context.mtf_context.higher_regime is None
    assert ten_minute.analysis_context.mtf_context.relationship == (
        "INSUFFICIENT_CONTEXT"
    )


def test_analyze_timeframe_rejects_wrong_candle_timeframe():
    candles = make_candles("5m", 5)

    try:
        analyze_timeframe("10m", candles)
    except ValueError as exc:
        assert "Timeframe key 10m does not match" in str(exc)
    else:
        raise AssertionError("Expected timeframe mismatch failure")
