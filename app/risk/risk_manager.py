"""
Paper Trading Lab — Risk Management

Pure mathematical risk controls for paper/simulation analysis.

This module:
- validates risk configuration,
- calculates a risk budget,
- calculates descriptive paper position size,
- enforces the configured maximum number of open positions.

It does not:
- generate trading signals,
- select entry/stop levels,
- place orders,
- connect to brokers,
- perform live trading.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskParameters:
    """Validated configuration for descriptive risk calculations."""

    max_risk_per_trade: float
    max_open_positions: int

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.max_risk_per_trade <= 0:
            raise ValueError(
                "max_risk_per_trade must be greater than zero"
            )

        if self.max_risk_per_trade >= 1:
            raise ValueError(
                "max_risk_per_trade must be less than one"
            )

        if self.max_open_positions <= 0:
            raise ValueError(
                "max_open_positions must be greater than zero"
            )


class RiskManager:
    """Pure risk calculations for the paper-trading layer."""

    def __init__(self, parameters: RiskParameters) -> None:
        parameters.validate()
        self.parameters = parameters

    @classmethod
    def from_config(cls) -> 'RiskManager':
        """Create a RiskManager from the project risk configuration."""

        from config import MAX_OPEN_POSITIONS, MAX_RISK_PER_TRADE

        return cls(
            RiskParameters(
                max_risk_per_trade=MAX_RISK_PER_TRADE,
                max_open_positions=MAX_OPEN_POSITIONS,
            )
        )

    def calculate_risk_budget(self, capital: float) -> float:
        """Return the maximum monetary risk permitted for one paper position."""

        if capital <= 0:
            raise ValueError("capital must be greater than zero")

        return float(
            capital * self.parameters.max_risk_per_trade
        )

    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_price: float,
        direction: str = "LONG_GEOMETRY",
    ) -> float:
        """
        Calculate descriptive paper position size from explicit price geometry.

        Position size = risk budget / risk distance.

        LONG_GEOMETRY:
            stop_price < entry_price
            risk_distance = entry_price - stop_price

        SHORT_GEOMETRY:
            stop_price > entry_price
            risk_distance = stop_price - entry_price

        No orders are placed and no broker functionality is involved.
        """
        if capital <= 0:
            raise ValueError("capital must be greater than zero")

        if entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero"
            )

        if stop_price <= 0:
            raise ValueError(
                "stop_price must be greater than zero"
            )

        if entry_price == stop_price:
            raise ValueError(
                "risk distance must be greater than zero"
            )

        if direction == "LONG_GEOMETRY":
            if stop_price > entry_price:
                raise ValueError(
                    "Long geometry requires stop below entry"
                )
            risk_distance = float(entry_price - stop_price)

        elif direction == "SHORT_GEOMETRY":
            if stop_price < entry_price:
                raise ValueError(
                    "Short geometry requires stop above entry"
                )
            risk_distance = float(stop_price - entry_price)

        else:
            raise ValueError(
                f"Unsupported direction: {direction}"
            )

        if risk_distance <= 0:
            raise ValueError(
                "risk distance must be greater than zero"
            )

        risk_budget = self.calculate_risk_budget(capital)

        return float(risk_budget / risk_distance)

    def can_open_position(
        self,
        current_open_positions: int,
    ) -> bool:
        """Return whether another paper position may be opened."""

        if current_open_positions < 0:
            raise ValueError(
                "current_open_positions cannot be negative"
            )

        return (
            current_open_positions
            < self.parameters.max_open_positions
        )
