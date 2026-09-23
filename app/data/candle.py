"""
Market candle contract for Paper Trading Lab.

This module defines the canonical OHLCV representation used by
backtesting and paper-trading analysis.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    """
    One completed OHLCV candle.

    timestamp:
        Candle timestamp. The project expects timezone-aware timestamps.

    open/high/low/close:
        Price values.

    volume:
        Non-negative traded volume.

    timeframe:
        Canonical timeframe label such as 5m, 10m, 15m, 30m, or 1W.

    completed:
        True only when the candle is closed and safe for analysis.
    """

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str
    completed: bool = True

    def validate(self) -> None:
        """Fail closed if the candle violates the data contract."""

        if self.timestamp.tzinfo is None:
            raise ValueError("Candle timestamp must be timezone-aware")

        if self.timeframe not in {"5m", "10m", "15m", "30m", "1W"}:
            raise ValueError(f"Unsupported timeframe: {self.timeframe}")

        prices = {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
        }

        for name, value in prices.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")

        if self.high < max(self.open, self.close):
            raise ValueError("High is below open/close")

        if self.low > min(self.open, self.close):
            raise ValueError("Low is above open/close")

        if self.low > self.high:
            raise ValueError("Low cannot be greater than high")

        if self.volume < 0:
            raise ValueError("Volume cannot be negative")

        if not self.completed:
            raise ValueError(
                "Incomplete candle cannot enter the analysis pipeline"
            )
