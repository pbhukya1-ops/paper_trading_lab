"""Paper Trading Lab — Paper Engine.

Simulation-only engine boundary. No broker or live-order functionality.
"""

from datetime import datetime

from config import STARTING_CAPITAL
from app.position import Position
from app.risk.risk_manager import RiskManager
from app.trade import Trade


class PaperEngine:
    """Paper-only engine for maintaining simulated position state."""

    def __init__(self) -> None:
        self.paper_only = True
        self.starting_capital = float(STARTING_CAPITAL)
        self.capital = self.starting_capital
        self.risk_manager = RiskManager.from_config()
        self.open_position_count = 0
        self.current_position = None
        self._entry_time = None
        self._trade_history = []

    @property
    def trade_history(self):
        return tuple(self._trade_history)

    def calculate_position_size(self, entry_price: float, stop_price: float) -> float:
        return self.risk_manager.calculate_position_size(
            capital=self.capital,
            entry_price=entry_price,
            stop_price=stop_price,
        )

    def can_open_position(self) -> bool:
        return self.risk_manager.can_open_position(self.open_position_count)

    def open_position(
        self,
        position: Position,
        entry_time: datetime,
    ) -> Position:
        if self.current_position is not None:
            raise ValueError("Cannot open position while an open position exists")

        if not self.can_open_position():
            raise ValueError("Cannot open position: position limit reached")

        if not isinstance(position, Position):
            raise TypeError("position must be a Position")

        if not isinstance(entry_time, datetime):
            raise TypeError("entry_time must be a datetime")

        position.validate()
        self.current_position = position
        self._entry_time = entry_time
        self.open_position_count = 1
        return position

    def close_position(
        self,
        exit_price: float,
        exit_time: datetime,
    ) -> Trade:
        if self.current_position is None:
            raise ValueError("No open position to close")

        if not isinstance(exit_time, datetime):
            raise TypeError("exit_time must be a datetime")

        trade = Trade(
            position=self.current_position,
            exit_price=exit_price,
            entry_time=self._entry_time,
            exit_time=exit_time,
        )

        self.current_position = None
        self._entry_time = None
        self.open_position_count = 0
        self.capital += trade.realized_pnl
        self._trade_history.append(trade)

        return trade
