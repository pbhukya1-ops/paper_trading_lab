"""Paper Trading Lab — Immutable completed paper-trade record."""

from dataclasses import dataclass
from datetime import datetime

from app.position import Position


@dataclass(frozen=True)
class Trade:
    """Validated descriptive record of a completed paper position."""

    position: Position
    exit_price: float
    entry_time: datetime
    exit_time: datetime

    def __post_init__(self) -> None:
        self.validate()

    @property
    def realized_pnl(self) -> float:
        entry_price = self.position.target_geometry.entry_price
        quantity = self.position.quantity

        if self.position.direction == "LONG_GEOMETRY":
            return (self.exit_price - entry_price) * quantity

        if self.position.direction == "SHORT_GEOMETRY":
            return (entry_price - self.exit_price) * quantity

        raise ValueError(
            f"Unsupported position direction: {self.position.direction}"
        )

    def validate(self) -> None:
        if self.exit_price <= 0:
            raise ValueError("exit_price must be greater than zero")

        if self.exit_time < self.entry_time:
            raise ValueError("exit_time must not be before entry_time")

        self.position.validate()
