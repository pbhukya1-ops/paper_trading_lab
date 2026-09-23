"""
Paper Trading Lab — Global Configuration

This project is research / simulation only.
No live order placement is implemented.
"""

PROJECT_NAME = "paper_trading_lab"

# Hard safety boundary
PAPER_ONLY = True
LIVE_TRADING = False
ORDER_PLACEMENT_ENABLED = False

# Market-analysis configuration
TIMEFRAMES = [
    "5m",
    "10m",
    "15m",
    "30m",
    "1W",
]

# Initial state
STARTING_CAPITAL = 100000.0

# Risk controls are configuration only at this stage.
# No execution logic exists yet.
MAX_RISK_PER_TRADE = 0.01
MAX_OPEN_POSITIONS = 1


def assert_paper_only():
    """Fail closed unless this project is explicitly configured for paper mode."""
    if not PAPER_ONLY:
        raise RuntimeError("SAFETY VIOLATION: PAPER_ONLY must be True")

    if LIVE_TRADING:
        raise RuntimeError("SAFETY VIOLATION: LIVE_TRADING must be False")

    if ORDER_PLACEMENT_ENABLED:
        raise RuntimeError(
            "SAFETY VIOLATION: ORDER_PLACEMENT_ENABLED must be False"
        )

    return True
