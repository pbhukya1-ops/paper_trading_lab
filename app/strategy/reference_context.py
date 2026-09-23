"""
Explicit reference inputs for Paper Trading Lab strategy analysis.

This module contains references supplied by the caller for analytical
evaluation. It does NOT discover, rank, or automatically select levels.

It does NOT:
- generate trade signals,
- recommend entries or exits,
- place orders,
- connect to brokers.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyReferenceContext:
    """
    Explicit structural references supplied to strategy analysis.

    Indices and prices are references only. Their presence does not imply
    that a trade should be taken.
    """

    level_index: int | None = None
    level_price: float | None = None
    level_type: str | None = None

    reference_index: int | None = None
    move_index: int | None = None
    retest_index: int | None = None

    target_index: int | None = None

    def validate(self) -> None:
        """Validate supplied reference values without making a decision."""

        if self.level_index is not None and self.level_index < 0:
            raise ValueError("level_index cannot be negative")

        if self.level_price is not None and self.level_price <= 0:
            raise ValueError("level_price must be positive")

        if self.level_type is not None and not self.level_type:
            raise ValueError("level_type cannot be empty")

        indices = {
            "reference_index": self.reference_index,
            "move_index": self.move_index,
            "retest_index": self.retest_index,
            "target_index": self.target_index,
        }

        for name, value in indices.items():
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
