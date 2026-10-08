"""Paper Trading Lab — Read-only completed-trade evaluation."""

from dataclasses import dataclass

from app.trade import Trade


@dataclass(frozen=True)
class EvaluationReport:
    """Immutable aggregate evaluation of completed paper trades."""

    completed_trade_count: int
    winning_trade_count: int
    losing_trade_count: int
    breakeven_trade_count: int
    realized_pnl: float
    win_rate: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    average_realized_pnl: float


def evaluate_trades(trades) -> EvaluationReport:
    """Evaluate completed immutable Trade records without modifying them."""

    trades = tuple(trades)

    for trade in trades:
        if not isinstance(trade, Trade):
            raise TypeError("all inputs must be Trade instances")

    completed_trade_count = len(trades)

    realized_pnls = tuple(trade.realized_pnl for trade in trades)

    winning_trade_count = sum(pnl > 0 for pnl in realized_pnls)
    losing_trade_count = sum(pnl < 0 for pnl in realized_pnls)
    breakeven_trade_count = sum(pnl == 0 for pnl in realized_pnls)

    realized_pnl = sum(realized_pnls)
    gross_profit = sum(pnl for pnl in realized_pnls if pnl > 0)
    gross_loss = sum(-pnl for pnl in realized_pnls if pnl < 0)

    if completed_trade_count == 0:
        win_rate = 0.0
        average_realized_pnl = 0.0
    else:
        win_rate = winning_trade_count / completed_trade_count * 100.0
        average_realized_pnl = realized_pnl / completed_trade_count

    if gross_loss == 0:
        profit_factor = 0.0
    else:
        profit_factor = gross_profit / gross_loss

    return EvaluationReport(
        completed_trade_count=completed_trade_count,
        winning_trade_count=winning_trade_count,
        losing_trade_count=losing_trade_count,
        breakeven_trade_count=breakeven_trade_count,
        realized_pnl=realized_pnl,
        win_rate=win_rate,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        profit_factor=profit_factor,
        average_realized_pnl=average_realized_pnl,
    )
