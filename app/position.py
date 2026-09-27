"""Paper Trading Lab — Immutable paper position model."""

from dataclasses import dataclass

from app.strategy.targets import TargetGeometry


@dataclass(frozen=True)
class Position:
    """Validated descriptive position state for paper simulation."""

    direction: str
    quantity: float
    target_geometry: TargetGeometry

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.direction not in {'LONG_GEOMETRY', 'SHORT_GEOMETRY'}:
            raise ValueError("direction must be LONG_GEOMETRY or SHORT_GEOMETRY")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if self.target_geometry.direction != self.direction:
            raise ValueError(
                "direction must match target_geometry direction"
            )

        self.target_geometry.validate()
