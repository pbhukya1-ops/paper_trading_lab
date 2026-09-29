"""Paper Trading Lab — explicit paper-simulation boundary."""

from dataclasses import dataclass
from datetime import datetime

from app.strategy.analysis_context import StrategyAnalysisContext
from app.strategy.targets import TargetGeometry


@dataclass(frozen=True)
class PaperSimulationRequest:
    """Explicit inputs for one paper-simulation position."""

    analysis_context: StrategyAnalysisContext
    direction: str
    entry_price: float
    stop_price: float
    target_price: float
    entry_time: datetime
    target_geometry: TargetGeometry

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.analysis_context, StrategyAnalysisContext):
            raise TypeError(
                "analysis_context must be a StrategyAnalysisContext"
            )

        if not isinstance(self.entry_time, datetime):
            raise TypeError("entry_time must be a datetime")

        self.analysis_context.validate()
        self.target_geometry.validate()

        if self.direction != self.target_geometry.direction:
            raise ValueError(
                "direction must match target_geometry direction"
            )

        if self.entry_price != self.target_geometry.entry_price:
            raise ValueError(
                "entry_price must match target_geometry entry_price"
            )

        if self.stop_price != self.target_geometry.stop_price:
            raise ValueError(
                "stop_price must match target_geometry stop_price"
            )

        if self.target_price != self.target_geometry.target_price:
            raise ValueError(
                "target_price must match target_geometry target_price"
            )


def open_paper_simulation(
    engine,
    request: PaperSimulationRequest,
) -> object:
    """Open one explicitly requested paper position in the simulation engine."""
    from app.position import Position

    if not engine.paper_only:
        raise RuntimeError("Paper simulation requires a paper-only engine")

    if not isinstance(request, PaperSimulationRequest):
        raise TypeError("request must be a PaperSimulationRequest")

    quantity = engine.calculate_position_size(
        entry_price=request.entry_price,
        stop_price=request.stop_price,
        direction=request.direction,
    )

    position = Position(
        direction=request.direction,
        quantity=quantity,
        target_geometry=request.target_geometry,
    )

    return engine.open_position(
        position=position,
        entry_time=request.entry_time,
    )
