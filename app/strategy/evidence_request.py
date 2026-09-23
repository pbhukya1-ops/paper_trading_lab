"""
Immutable evidence-request specifications.

This module contains caller-supplied requests for descriptive strategy
evidence. It does not perform detection, reference selection, scoring,
signal generation, or execution.
"""

from dataclasses import dataclass

from .zones import PriceZone


@dataclass(frozen=True)
class BreakoutEvidenceRequest:
    high: float
    low: float
    close: float
    level_price: float
    level_type: str
    candle_index: int
    level_index: int


@dataclass(frozen=True)
class VolumeBreakoutEvidenceRequest:
    high: float
    low: float
    close: float
    level_price: float
    level_type: str
    candle_index: int
    level_index: int
    relative_volume: float | None
    threshold: float = 1.5


@dataclass(frozen=True)
class EMASupportEvidenceRequest:
    price: float
    ema21: float
    zone: PriceZone | None = None


@dataclass(frozen=True)
class RSIPullbackEvidenceRequest:
    current_rsi: float
    previous_rsi: float | None = None
    period: int = 14
    reference_level: float = 40.0
    tolerance: float = 5.0


@dataclass(frozen=True)
class PullbackEvidenceRequest:
    reference_price: float
    move_extreme: float
    retest_price: float
    move_type: str
    reference_index: int
    move_index: int
    retest_index: int
    tolerance: float = 0.0


@dataclass(frozen=True)
class FalseBreakoutEvidenceRequest:
    breakout_extreme: float
    failure_close: float
    level_price: float
    breakout_type: str
    level_index: int
    failure_candle_index: int


@dataclass(frozen=True)
class TargetGeometryEvidenceRequest:
    reference_price: float
    entry_price: float
    stop_price: float
    target_price: float
    direction: str


@dataclass(frozen=True)
class LiquiditySweepEvidenceRequest:
    high: float
    low: float
    close: float
    level_price: float
    level_type: str
    candle_index: int
    level_index: int


@dataclass(frozen=True)
class InducementEvidenceRequest:
    prices: list[float]
    reference_index: int
    inducement_index: int
    target_index: int
    inducement_type: str


@dataclass(frozen=True)
class EvidenceRequest:
    breakout: BreakoutEvidenceRequest | None = None
    volume_breakout: VolumeBreakoutEvidenceRequest | None = None
    ema_support: EMASupportEvidenceRequest | None = None
    rsi_pullback: RSIPullbackEvidenceRequest | None = None
    pullback: PullbackEvidenceRequest | None = None
    false_breakout: FalseBreakoutEvidenceRequest | None = None
    target_geometry: TargetGeometryEvidenceRequest | None = None
    liquidity_sweep: LiquiditySweepEvidenceRequest | None = None
    inducement: InducementEvidenceRequest | None = None

    liquidity_observation: bool = False
    fvg_observation: bool = False
    inducement_observation: bool = False
