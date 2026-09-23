"""
Composite descriptive strategy-analysis context for Paper Trading Lab.

This module combines already-computed analytical observations into one
immutable context object.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- select trading levels automatically,
- place orders,
- connect to brokers.

All optional analytical objects must be computed explicitly by their
respective strategy modules before being supplied here.
"""

from dataclasses import dataclass

from .mtf_context import MTFPriceActionContext
from .regime import MarketRegime
from .trend_quality import TrendQuality
from .breakout import BreakoutEvent
from .volume_breakout import VolumeBreakoutContext
from .ema_support import EMA21SupportContext
from .rsi_pullback import RSIPullbackContext
from .pullback import PullbackRetestContext
from .false_breakout import FalseBreakoutContext
from .targets import TargetGeometry
from .reference_context import StrategyReferenceContext


@dataclass(frozen=True)
class StrategyAnalysisContext:
    """
    Immutable descriptive snapshot of already-computed strategy analysis.
    """

    timeframe: str
    mtf_context: MTFPriceActionContext
    market_regime: MarketRegime
    trend_quality: TrendQuality
    references: StrategyReferenceContext | None = None

    breakout: BreakoutEvent | None = None
    volume_breakout: VolumeBreakoutContext | None = None
    ema_support: EMA21SupportContext | None = None
    rsi_pullback: RSIPullbackContext | None = None
    pullback: PullbackRetestContext | None = None
    false_breakout: FalseBreakoutContext | None = None
    target_geometry: TargetGeometry | None = None

    liquidity_observation: bool = False
    fvg_observation: bool = False
    inducement_observation: bool = False

    def validate(self) -> None:
        """
        Validate the composite context and all supplied analytical objects.

        No trading decision is made.
        """
        if not self.timeframe:
            raise ValueError("Timeframe cannot be empty")

        self.mtf_context.validate()
        self.market_regime.validate()
        self.trend_quality.validate()

        if self.references is not None:
            self.references.validate()

        if self.mtf_context.timeframe != self.timeframe:
            raise ValueError(
                "MTF context timeframe must match analysis timeframe"
            )

        if self.trend_quality.market_regime != self.market_regime.market_regime:
            raise ValueError(
                "Trend-quality market regime must match market-regime context"
            )

        optional_objects = (
            self.breakout,
            self.volume_breakout,
            self.ema_support,
            self.rsi_pullback,
            self.pullback,
            self.false_breakout,
            self.target_geometry,
        )

        for obj in optional_objects:
            if obj is not None:
                obj.validate()

        boolean_fields = {
            "liquidity_observation": self.liquidity_observation,
            "fvg_observation": self.fvg_observation,
            "inducement_observation": self.inducement_observation,
        }

        for name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise ValueError(f"{name} must be boolean")
