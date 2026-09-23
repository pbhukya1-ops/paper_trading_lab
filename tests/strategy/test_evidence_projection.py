import pytest

from app.strategy.breakout import BreakoutEvent
from app.strategy.ema_support import EMA21SupportContext
from app.strategy.evidence_projection import (
    EvidenceProjection,
    build_evidence_projection,
)
from app.strategy.evidence_request import (
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
from app.strategy.false_breakout import FalseBreakoutContext
from app.strategy.inducement import InducementLevel
from app.strategy.pullback import PullbackRetestContext
from app.strategy.rsi_pullback import RSIPullbackContext
from app.strategy.sweeps import LiquiditySweep
from app.strategy.targets import TargetGeometry
from app.strategy.volume_breakout import VolumeBreakoutContext


def test_empty_request_projects_to_empty_evidence():
    result = build_evidence_projection(EvidenceRequest())

    assert isinstance(result, EvidenceProjection)
    assert result.breakout is None
    assert result.volume_breakout is None
    assert result.ema_support is None
    assert result.rsi_pullback is None
    assert result.pullback is None
    assert result.false_breakout is None
    assert result.target_geometry is None
    assert result.liquidity_sweep is None
    assert result.inducement is None


def test_breakout_request_maps_exactly():
    request = EvidenceRequest(
        breakout=BreakoutEvidenceRequest(
            high=105.0,
            low=99.0,
            close=104.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        )
    )

    result = build_evidence_projection(request)

    assert result.breakout == BreakoutEvent(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        wick_extreme=105.0,
        close_price=104.0,
    )


def test_volume_breakout_request_maps_exactly():
    request = EvidenceRequest(
        volume_breakout=VolumeBreakoutEvidenceRequest(
            high=105.0,
            low=99.0,
            close=104.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
            relative_volume=2.0,
        )
    )

    result = build_evidence_projection(request)

    assert result.volume_breakout == VolumeBreakoutContext(
        breakout_type="BULLISH_BREAKOUT",
        confirmation_type="CLOSE_CONFIRMED",
        relative_volume=2.0,
        volume_strength="HIGH_VOLUME",
    )


def test_ema_support_request_maps_exactly():
    request = EvidenceRequest(
        ema_support=EMASupportEvidenceRequest(
            price=100.0,
            ema21=100.0,
        )
    )

    result = build_evidence_projection(request)

    assert result.ema_support == EMA21SupportContext(
        price=100.0,
        ema21=100.0,
        ema_relationship="AT_EMA",
        zone_relationship="OUTSIDE_ZONE",
        interaction_type="EMA_ONLY",
        zone_source=None,
    )


def test_rsi_pullback_request_maps_exactly():
    request = EvidenceRequest(
        rsi_pullback=RSIPullbackEvidenceRequest(
            current_rsi=42.0,
            previous_rsi=39.0,
        )
    )

    result = build_evidence_projection(request)

    assert result.rsi_pullback == RSIPullbackContext(
        period=14,
        current_rsi=42.0,
        previous_rsi=39.0,
        reference_level=40.0,
        tolerance=5.0,
        location_state="NEAR_REFERENCE",
        turn_state="UPWARD_TURN",
    )


def test_pullback_request_maps_exactly():
    request = EvidenceRequest(
        pullback=PullbackEvidenceRequest(
            reference_price=100.0,
            move_extreme=110.0,
            retest_price=100.0,
            move_type="BULLISH_MOVE",
            reference_index=1,
            move_index=3,
            retest_index=5,
        )
    )

    result = build_evidence_projection(request)

    assert result.pullback == PullbackRetestContext(
        move_type="BULLISH_MOVE",
        reference_index=1,
        move_index=3,
        retest_index=5,
        reference_price=100.0,
        retest_price=100.0,
        retest_type="BULLISH_RETEST",
    )


def test_false_breakout_request_maps_exactly():
    request = EvidenceRequest(
        false_breakout=FalseBreakoutEvidenceRequest(
            breakout_extreme=105.0,
            failure_close=99.0,
            level_price=100.0,
            breakout_type="BULLISH_BREAKOUT",
            level_index=2,
            failure_candle_index=5,
        )
    )

    result = build_evidence_projection(request)

    assert result.false_breakout == FalseBreakoutContext(
        level_index=2,
        failure_candle_index=5,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        failure_type="BULLISH_BREAKOUT_FAILURE",
        breakout_extreme=105.0,
        failure_close=99.0,
    )


def test_target_geometry_request_maps_exactly():
    request = EvidenceRequest(
        target_geometry=TargetGeometryEvidenceRequest(
            reference_price=100.0,
            entry_price=101.0,
            stop_price=99.0,
            target_price=105.0,
            direction="LONG_GEOMETRY",
        )
    )

    result = build_evidence_projection(request)

    assert result.target_geometry == TargetGeometry(
        direction="LONG_GEOMETRY",
        reference_price=100.0,
        entry_price=101.0,
        stop_price=99.0,
        target_price=105.0,
        risk_distance=2.0,
        reward_distance=4.0,
        reward_risk_ratio=2.0,
    )


def test_liquidity_sweep_request_maps_exactly():
    request = EvidenceRequest(
        liquidity_sweep=LiquiditySweepEvidenceRequest(
            high=105.0,
            low=95.0,
            close=99.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        )
    )

    result = build_evidence_projection(request)

    assert result.liquidity_sweep == LiquiditySweep(
        candle_index=5,
        level_index=2,
        level_price=100.0,
        sweep_type="BUY_SIDE_SWEEP",
        wick_extreme=105.0,
        close_price=99.0,
    )


def test_inducement_request_maps_exactly():
    request = EvidenceRequest(
        inducement=InducementEvidenceRequest(
            prices=[100.0, 105.0, 102.0, 110.0],
            reference_index=0,
            inducement_index=2,
            target_index=3,
            inducement_type="LOW_INDUCEMENT",
        )
    )

    result = build_evidence_projection(request)

    assert result.inducement == InducementLevel(
        index=2,
        price=102.0,
        inducement_type="LOW_INDUCEMENT",
        reference_index=0,
        target_index=3,
    )


def test_observation_flags_are_copied_exactly():
    request = EvidenceRequest(
        liquidity_observation=True,
        fvg_observation=True,
        inducement_observation=True,
    )

    result = build_evidence_projection(request)

    assert result.liquidity_observation is True
    assert result.fvg_observation is True
    assert result.inducement_observation is True


def test_request_presence_does_not_infer_observation_flags():
    request = EvidenceRequest(
        liquidity_sweep=LiquiditySweepEvidenceRequest(
            high=105.0,
            low=95.0,
            close=99.0,
            level_price=100.0,
            level_type="HIGH",
            candle_index=5,
            level_index=2,
        ),
        inducement=InducementEvidenceRequest(
            prices=[100.0, 105.0, 102.0, 110.0],
            reference_index=0,
            inducement_index=2,
            target_index=3,
            inducement_type="LOW_INDUCEMENT",
        ),
    )

    result = build_evidence_projection(request)

    assert result.liquidity_sweep is not None
    assert result.inducement is not None
    assert result.liquidity_observation is False
    assert result.fvg_observation is False
    assert result.inducement_observation is False


@pytest.mark.parametrize(
    "evidence_request",
    [
        EvidenceRequest(
            breakout=BreakoutEvidenceRequest(
                105.0, 99.0, 104.0, 100.0, "HIGH", 5, 2
            )
        ),
        EvidenceRequest(
            volume_breakout=VolumeBreakoutEvidenceRequest(
                105.0, 99.0, 104.0, 100.0, "HIGH", 5, 2, 2.0
            )
        ),
        EvidenceRequest(
            ema_support=EMASupportEvidenceRequest(100.0, 100.0)
        ),
        EvidenceRequest(
            rsi_pullback=RSIPullbackEvidenceRequest(42.0, 39.0)
        ),
    ],
)
def test_projection_is_deterministic(evidence_request):
    first = build_evidence_projection(evidence_request)
    second = build_evidence_projection(evidence_request)

    assert first == second
