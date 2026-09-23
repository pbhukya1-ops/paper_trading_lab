import pytest

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


def test_empty_evidence_request_is_valid():
    request = EvidenceRequest()

    assert request.breakout is None
    assert request.volume_breakout is None
    assert request.ema_support is None
    assert request.rsi_pullback is None
    assert request.pullback is None
    assert request.false_breakout is None
    assert request.target_geometry is None
    assert request.liquidity_sweep is None
    assert request.inducement is None
    assert request.liquidity_observation is False
    assert request.fvg_observation is False
    assert request.inducement_observation is False


def test_breakout_request_preserves_exact_fields():
    request = BreakoutEvidenceRequest(
        high=105.0,
        low=98.0,
        close=103.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert request.high == 105.0
    assert request.low == 98.0
    assert request.close == 103.0
    assert request.level_price == 100.0
    assert request.level_type == "HIGH"
    assert request.candle_index == 5
    assert request.level_index == 2


def test_volume_breakout_defaults():
    request = VolumeBreakoutEvidenceRequest(
        high=105.0,
        low=99.0,
        close=104.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
        relative_volume=2.0,
    )

    assert request.relative_volume == 2.0
    assert request.threshold == 1.5


def test_ema_support_default_zone():
    request = EMASupportEvidenceRequest(
        price=100.0,
        ema21=100.0,
    )

    assert request.price == 100.0
    assert request.ema21 == 100.0
    assert request.zone is None


def test_rsi_pullback_defaults():
    request = RSIPullbackEvidenceRequest(
        current_rsi=40.0,
        previous_rsi=39.0,
    )

    assert request.period == 14
    assert request.reference_level == 40.0
    assert request.tolerance == 5.0


def test_pullback_default_tolerance():
    request = PullbackEvidenceRequest(
        reference_price=100.0,
        move_extreme=110.0,
        retest_price=100.0,
        move_type="BULLISH_MOVE",
        reference_index=0,
        move_index=1,
        retest_index=2,
    )

    assert request.tolerance == 0.0


def test_false_breakout_request():
    request = FalseBreakoutEvidenceRequest(
        breakout_extreme=105.0,
        failure_close=99.0,
        level_price=100.0,
        breakout_type="BULLISH_BREAKOUT",
        level_index=0,
        failure_candle_index=2,
    )

    assert request.breakout_extreme == 105.0
    assert request.failure_close == 99.0
    assert request.level_price == 100.0
    assert request.breakout_type == "BULLISH_BREAKOUT"


def test_target_geometry_request():
    request = TargetGeometryEvidenceRequest(
        reference_price=100.0,
        entry_price=102.0,
        stop_price=98.0,
        target_price=110.0,
        direction="LONG_GEOMETRY",
    )

    assert request.reference_price == 100.0
    assert request.entry_price == 102.0
    assert request.stop_price == 98.0
    assert request.target_price == 110.0
    assert request.direction == "LONG_GEOMETRY"


def test_liquidity_sweep_request():
    request = LiquiditySweepEvidenceRequest(
        high=105.0,
        low=95.0,
        close=98.0,
        level_price=100.0,
        level_type="HIGH",
        candle_index=5,
        level_index=2,
    )

    assert request.candle_index == 5
    assert request.level_index == 2
    assert request.level_type == "HIGH"


def test_inducement_request():
    prices = [100.0, 105.0, 110.0, 108.0, 115.0]

    request = InducementEvidenceRequest(
        prices=prices,
        reference_index=0,
        inducement_index=2,
        target_index=4,
        inducement_type="HIGH_INDUCEMENT",
    )

    assert request.prices == prices
    assert request.reference_index == 0
    assert request.inducement_index == 2
    assert request.target_index == 4
    assert request.inducement_type == "HIGH_INDUCEMENT"


def test_evidence_request_can_carry_all_request_objects():
    request = EvidenceRequest(
        breakout=BreakoutEvidenceRequest(
            105.0, 98.0, 103.0, 100.0, "HIGH", 5, 2
        ),
        volume_breakout=VolumeBreakoutEvidenceRequest(
            105.0, 99.0, 104.0, 100.0, "HIGH", 5, 2, 2.0
        ),
        ema_support=EMASupportEvidenceRequest(100.0, 100.0),
        rsi_pullback=RSIPullbackEvidenceRequest(40.0, 39.0),
        pullback=PullbackEvidenceRequest(
            100.0, 110.0, 100.0, "BULLISH_MOVE", 0, 1, 2
        ),
        false_breakout=FalseBreakoutEvidenceRequest(
            105.0, 99.0, 100.0, "BULLISH_BREAKOUT", 0, 2
        ),
        target_geometry=TargetGeometryEvidenceRequest(
            100.0, 102.0, 98.0, 110.0, "LONG_GEOMETRY"
        ),
        liquidity_sweep=LiquiditySweepEvidenceRequest(
            105.0, 95.0, 98.0, 100.0, "HIGH", 5, 2
        ),
        inducement=InducementEvidenceRequest(
            [100.0, 105.0, 110.0], 0, 1, 2, "HIGH_INDUCEMENT"
        ),
        liquidity_observation=True,
        fvg_observation=True,
        inducement_observation=True,
    )

    assert request.breakout is not None
    assert request.volume_breakout is not None
    assert request.ema_support is not None
    assert request.rsi_pullback is not None
    assert request.pullback is not None
    assert request.false_breakout is not None
    assert request.target_geometry is not None
    assert request.liquidity_sweep is not None
    assert request.inducement is not None
    assert request.liquidity_observation is True
    assert request.fvg_observation is True
    assert request.inducement_observation is True


@pytest.mark.parametrize(
    "factory",
    [
        lambda: BreakoutEvidenceRequest(
            105.0, 98.0, 103.0, 100.0, "HIGH", 5, 2
        ),
        lambda: VolumeBreakoutEvidenceRequest(
            105.0, 99.0, 104.0, 100.0, "HIGH", 5, 2, 2.0
        ),
        lambda: EMASupportEvidenceRequest(100.0, 100.0),
        lambda: RSIPullbackEvidenceRequest(40.0, 39.0),
        lambda: PullbackEvidenceRequest(
            100.0, 110.0, 100.0, "BULLISH_MOVE", 0, 1, 2
        ),
        lambda: FalseBreakoutEvidenceRequest(
            105.0, 99.0, 100.0, "BULLISH_BREAKOUT", 0, 2
        ),
        lambda: TargetGeometryEvidenceRequest(
            100.0, 102.0, 98.0, 110.0, "LONG_GEOMETRY"
        ),
        lambda: LiquiditySweepEvidenceRequest(
            105.0, 95.0, 98.0, 100.0, "HIGH", 5, 2
        ),
        lambda: InducementEvidenceRequest(
            [100.0, 105.0, 110.0], 0, 1, 2, "HIGH_INDUCEMENT"
        ),
    ],
)
def test_nested_request_objects_are_frozen(factory):
    request = factory()

    with pytest.raises((AttributeError, TypeError)):
        if isinstance(request, EMASupportEvidenceRequest):
            request.price = 101.0
        else:
            request.candle_index = 99


def test_evidence_request_is_frozen():
    request = EvidenceRequest()

    with pytest.raises(AttributeError):
        request.liquidity_observation = True
