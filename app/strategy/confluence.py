"""
Confluence context foundations for Paper Trading Lab.

This module aggregates previously computed analytical observations
into one immutable descriptive context.

Confluence here means coexistence of observable analytical states.
It does NOT mean that a trade is recommended or that a signal exists.

This module does NOT:
- generate trade signals,
- recommend trades,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass

from .rsi_pullback import (
    VALID_STATES as VALID_RSI_LOCATION_STATES,
    VALID_TURN_STATES as VALID_RSI_TURN_STATES,
)


VALID_REGIMES = {
    "TRENDING_BULLISH",
    "TRENDING_BEARISH",
    "RANGE",
    "TRANSITION",
    "INSUFFICIENT_DATA",
}

VALID_RELATIONSHIPS = {
    "ALIGNED_BULLISH",
    "ALIGNED_BEARISH",
    "COUNTER_TREND_BULLISH",
    "COUNTER_TREND_BEARISH",
    "HIGHER_TIMEFRAME_MIXED",
    "LOWER_TIMEFRAME_MIXED",
    "INSUFFICIENT_CONTEXT",
    "NO_HIGHER_TIMEFRAME",
}

VALID_BREAKOUT_STATES = {
    "BULLISH_BREAKOUT",
    "BEARISH_BREAKOUT",
    "NO_BREAKOUT",
    "INSUFFICIENT_DATA",
}

VALID_RETEST_STATES = {
    "BULLISH_RETEST",
    "BEARISH_RETEST",
    "NO_RETEST",
    "INSUFFICIENT_DATA",
}

VALID_VOLUME_STATES = {
    "HIGH_VOLUME",
    "NORMAL_VOLUME",
    "LOW_VOLUME",
    "NO_BREAKOUT",
    "INSUFFICIENT_DATA",
}

VALID_INTERACTION_TYPES = {
    "SUPPORT_EMA_INTERACTION",
    "RESISTANCE_EMA_INTERACTION",
    "SUPPORT_ONLY",
    "RESISTANCE_ONLY",
    "EMA_ONLY",
    "NO_INTERACTION",
}

VALID_FAILURE_STATES = {
    "BULLISH_BREAKOUT_FAILURE",
    "BEARISH_BREAKOUT_FAILURE",
    "NO_FAILURE",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True)
class ConfluenceContext:
    timeframe: str
    higher_timeframe: str | None
    market_regime: str
    mtf_relationship: str
    breakout_state: str
    retest_state: str
    volume_state: str
    ema_zone_interaction: str
    false_breakout_state: str
    rsi_location_state: str
    rsi_turn_state: str
    liquidity_observation: bool
    fvg_observation: bool
    inducement_observation: bool
    target_geometry_available: bool

    def validate(self) -> None:
        if not self.timeframe:
            raise ValueError("Timeframe cannot be empty")

        if self.higher_timeframe == "":
            raise ValueError(
                "Higher timeframe must be None or non-empty"
            )

        if self.market_regime not in VALID_REGIMES:
            raise ValueError(
                f"Unsupported market regime: {self.market_regime}"
            )

        if self.mtf_relationship not in VALID_RELATIONSHIPS:
            raise ValueError(
                f"Unsupported MTF relationship: "
                f"{self.mtf_relationship}"
            )

        if self.breakout_state not in VALID_BREAKOUT_STATES:
            raise ValueError(
                f"Unsupported breakout state: "
                f"{self.breakout_state}"
            )

        if self.retest_state not in VALID_RETEST_STATES:
            raise ValueError(
                f"Unsupported retest state: {self.retest_state}"
            )

        if self.volume_state not in VALID_VOLUME_STATES:
            raise ValueError(
                f"Unsupported volume state: {self.volume_state}"
            )

        if self.ema_zone_interaction not in VALID_INTERACTION_TYPES:
            raise ValueError(
                f"Unsupported EMA/zone interaction: "
                f"{self.ema_zone_interaction}"
            )

        if self.false_breakout_state not in VALID_FAILURE_STATES:
            raise ValueError(
                f"Unsupported false-breakout state: "
                f"{self.false_breakout_state}"
            )

        if self.rsi_location_state not in VALID_RSI_LOCATION_STATES:
            raise ValueError(
                f"Unsupported RSI location state: "
                f"{self.rsi_location_state}"
            )

        if self.rsi_turn_state not in VALID_RSI_TURN_STATES:
            raise ValueError(
                f"Unsupported RSI turn state: "
                f"{self.rsi_turn_state}"
            )

        boolean_fields = {
            "liquidity_observation": self.liquidity_observation,
            "fvg_observation": self.fvg_observation,
            "inducement_observation": self.inducement_observation,
            "target_geometry_available": self.target_geometry_available,
        }

        for name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise ValueError(
                    f"{name} must be boolean"
                )


def build_confluence_context(
    timeframe: str,
    higher_timeframe: str | None,
    market_regime: str,
    mtf_relationship: str,
    breakout_state: str,
    retest_state: str,
    volume_state: str,
    ema_zone_interaction: str,
    false_breakout_state: str,
    rsi_location_state: str,
    rsi_turn_state: str,
    liquidity_observation: bool,
    fvg_observation: bool,
    inducement_observation: bool,
    target_geometry_available: bool,
) -> ConfluenceContext:
    """
    Build an immutable descriptive confluence context.

    This function only aggregates supplied analytical observations.
    It does not convert them into a trading decision.
    """

    if not timeframe:
        raise ValueError("Timeframe cannot be empty")

    result = ConfluenceContext(
        timeframe=timeframe,
        higher_timeframe=higher_timeframe,
        market_regime=market_regime,
        mtf_relationship=mtf_relationship,
        breakout_state=breakout_state,
        retest_state=retest_state,
        volume_state=volume_state,
        ema_zone_interaction=ema_zone_interaction,
        false_breakout_state=false_breakout_state,
        rsi_location_state=rsi_location_state,
        rsi_turn_state=rsi_turn_state,
        liquidity_observation=liquidity_observation,
        fvg_observation=fvg_observation,
        inducement_observation=inducement_observation,
        target_geometry_available=target_geometry_available,
    )

    result.validate()
    return result


def observation_count(context: ConfluenceContext) -> int:
    """
    Count explicitly present boolean analytical observations.

    This is a descriptive count only.
    It is NOT a setup score or trading recommendation.
    """

    context.validate()

    return sum(
        (
            context.liquidity_observation,
            context.fvg_observation,
            context.inducement_observation,
            context.target_geometry_available,
        )
    )
