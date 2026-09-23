"""
Pure projection from caller-supplied EvidenceRequest objects
to already-existing descriptive evidence objects.

This module does not:
- select references,
- discover levels,
- score setups,
- generate trading signals,
- recommend actions,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass

from .breakout import BreakoutEvent, detect_breakout
from .ema_support import EMA21SupportContext, classify_ema_zone_interaction
from .false_breakout import FalseBreakoutContext, detect_false_breakout
from .inducement import InducementLevel, detect_inducement
from .rsi_pullback import RSIPullbackContext, build_rsi_pullback_context
from .pullback import PullbackRetestContext, detect_pullback_retest
from .sweeps import LiquiditySweep, detect_liquidity_sweep
from .targets import TargetGeometry, calculate_target_geometry
from .volume_breakout import (
    VolumeBreakoutContext,
    volume_breakout_from_values,
)

from .evidence_request import (
    BreakoutEvidenceRequest,
    EMASupportEvidenceRequest,
    EvidenceRequest,
    FalseBreakoutEvidenceRequest,
    InducementEvidenceRequest,
    LiquiditySweepEvidenceRequest,
    PullbackEvidenceRequest,
    RSIPullbackEvidenceRequest,
    TargetGeometryEvidenceRequest,
    VolumeBreakoutEvidenceRequest,
)


@dataclass(frozen=True)
class EvidenceProjection:
    breakout: BreakoutEvent | None = None
    volume_breakout: VolumeBreakoutContext | None = None
    ema_support: EMA21SupportContext | None = None
    rsi_pullback: RSIPullbackContext | None = None
    pullback: PullbackRetestContext | None = None
    false_breakout: FalseBreakoutContext | None = None
    target_geometry: TargetGeometry | None = None
    liquidity_sweep: LiquiditySweep | None = None
    inducement: InducementLevel | None = None

    liquidity_observation: bool = False
    fvg_observation: bool = False
    inducement_observation: bool = False


def _project_breakout(
    request: BreakoutEvidenceRequest | None,
) -> BreakoutEvent | None:
    if request is None:
        return None

    return detect_breakout(
        high=request.high,
        low=request.low,
        close=request.close,
        level_price=request.level_price,
        level_type=request.level_type,
        candle_index=request.candle_index,
        level_index=request.level_index,
    )


def _project_volume_breakout(
    request: VolumeBreakoutEvidenceRequest | None,
) -> VolumeBreakoutContext | None:
    if request is None:
        return None

    return volume_breakout_from_values(
        high=request.high,
        low=request.low,
        close=request.close,
        level_price=request.level_price,
        level_type=request.level_type,
        candle_index=request.candle_index,
        level_index=request.level_index,
        relative_volume=request.relative_volume,
        threshold=request.threshold,
    )


def _project_ema_support(
    request: EMASupportEvidenceRequest | None,
) -> EMA21SupportContext | None:
    if request is None:
        return None

    return classify_ema_zone_interaction(
        price=request.price,
        ema21=request.ema21,
        zone=request.zone,
    )


def _project_rsi_pullback(
    request: RSIPullbackEvidenceRequest | None,
) -> RSIPullbackContext | None:
    if request is None:
        return None

    return build_rsi_pullback_context(
        current_rsi=request.current_rsi,
        previous_rsi=request.previous_rsi,
        period=request.period,
        reference_level=request.reference_level,
        tolerance=request.tolerance,
    )


def _project_pullback(
    request: PullbackEvidenceRequest | None,
) -> PullbackRetestContext | None:
    if request is None:
        return None

    return detect_pullback_retest(
        reference_price=request.reference_price,
        move_extreme=request.move_extreme,
        retest_price=request.retest_price,
        move_type=request.move_type,
        reference_index=request.reference_index,
        move_index=request.move_index,
        retest_index=request.retest_index,
        tolerance=request.tolerance,
    )


def _project_false_breakout(
    request: FalseBreakoutEvidenceRequest | None,
) -> FalseBreakoutContext | None:
    if request is None:
        return None

    return detect_false_breakout(
        breakout_extreme=request.breakout_extreme,
        failure_close=request.failure_close,
        level_price=request.level_price,
        breakout_type=request.breakout_type,
        level_index=request.level_index,
        failure_candle_index=request.failure_candle_index,
    )


def _project_target_geometry(
    request: TargetGeometryEvidenceRequest | None,
) -> TargetGeometry | None:
    if request is None:
        return None

    return calculate_target_geometry(
        reference_price=request.reference_price,
        entry_price=request.entry_price,
        stop_price=request.stop_price,
        target_price=request.target_price,
        direction=request.direction,
    )


def _project_liquidity_sweep(
    request: LiquiditySweepEvidenceRequest | None,
) -> LiquiditySweep | None:
    if request is None:
        return None

    return detect_liquidity_sweep(
        high=request.high,
        low=request.low,
        close=request.close,
        level_price=request.level_price,
        level_type=request.level_type,
        candle_index=request.candle_index,
        level_index=request.level_index,
    )


def _project_inducement(
    request: InducementEvidenceRequest | None,
) -> InducementLevel | None:
    if request is None:
        return None

    return detect_inducement(
        prices=request.prices,
        reference_index=request.reference_index,
        inducement_index=request.inducement_index,
        target_index=request.target_index,
        inducement_type=request.inducement_type,
    )


def build_evidence_projection(
    request: EvidenceRequest,
) -> EvidenceProjection:
    """
    Construct only the evidence explicitly requested by the caller.

    No request presence is converted into an observation boolean.
    The three observation flags are copied exactly from EvidenceRequest.
    """

    return EvidenceProjection(
        breakout=_project_breakout(request.breakout),
        volume_breakout=_project_volume_breakout(request.volume_breakout),
        ema_support=_project_ema_support(request.ema_support),
        rsi_pullback=_project_rsi_pullback(request.rsi_pullback),
        pullback=_project_pullback(request.pullback),
        false_breakout=_project_false_breakout(request.false_breakout),
        target_geometry=_project_target_geometry(request.target_geometry),
        liquidity_sweep=_project_liquidity_sweep(request.liquidity_sweep),
        inducement=_project_inducement(request.inducement),
        liquidity_observation=request.liquidity_observation,
        fvg_observation=request.fvg_observation,
        inducement_observation=request.inducement_observation,
    )
