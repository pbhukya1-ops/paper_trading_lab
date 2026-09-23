"""
Single-timeframe analytical result contract.

This module stores already-computed analytical evidence for one timeframe.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass

from .analysis_context import StrategyAnalysisContext


@dataclass(frozen=True)
class SingleTimeframeAnalysis:
    timeframe: str

    opens: tuple[float, ...]
    highs: tuple[float, ...]
    lows: tuple[float, ...]
    closes: tuple[float, ...]
    volumes: tuple[float, ...]

    ema21: tuple[float, ...]
    rsi14: tuple[float, ...]
    relative_volume20: tuple[float, ...]

    swing_high_flags: tuple[bool, ...]
    swing_low_flags: tuple[bool, ...]

    high_classifications: tuple[str | None, ...]
    low_classifications: tuple[str | None, ...]

    analysis_context: StrategyAnalysisContext

    def validate(self) -> None:
        if not self.timeframe:
            raise ValueError("Timeframe cannot be empty")

        sequences = {
            "opens": self.opens,
            "highs": self.highs,
            "lows": self.lows,
            "closes": self.closes,
            "volumes": self.volumes,
            "ema21": self.ema21,
            "rsi14": self.rsi14,
            "relative_volume20": self.relative_volume20,
            "swing_high_flags": self.swing_high_flags,
            "swing_low_flags": self.swing_low_flags,
            "high_classifications": self.high_classifications,
            "low_classifications": self.low_classifications,
        }

        lengths = {name: len(values) for name, values in sequences.items()}

        if len(set(lengths.values())) != 1:
            raise ValueError(
                f"Analytical series lengths must match: {lengths}"
            )

        self.analysis_context.validate()

        if self.analysis_context.timeframe != self.timeframe:
            raise ValueError(
                "Analysis-context timeframe must match result timeframe"
            )
