"""Paper Trading Lab — Paper Engine.

Simulation-only engine boundary. No broker or live-order functionality.
"""

from config import STARTING_CAPITAL
from app.risk.risk_manager import RiskManager


class PaperEngine:
    """Minimal paper-trading engine with configuration-driven risk controls."""

    def __init__(self) -> None:
        self.paper_only = True
        self.starting_capital = float(STARTING_CAPITAL)
        self.capital = self.starting_capital
        self.risk_manager = RiskManager.from_config()
        self.open_position_count = 0

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
    ) -> float:
        """Return descriptive paper position size using current paper capital."""

        return self.risk_manager.calculate_position_size(
            capital=self.capital,
            entry_price=entry_price,
            stop_price=stop_price,
        )

    def can_open_position(self) -> bool:
        """Return whether the configured paper position limit permits another position."""

        return self.risk_manager.can_open_position(
            self.open_position_count
        )
