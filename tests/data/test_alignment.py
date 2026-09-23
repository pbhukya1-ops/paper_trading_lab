from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.data.alignment import (
    is_valid_intraday_boundary,
    validate_intraday_boundary,
)


IST = ZoneInfo("Asia/Kolkata")


def ts(hour, minute):
    return datetime(2026, 9, 1, hour, minute, tzinfo=IST)


@pytest.mark.parametrize(
    ("timestamp", "timeframe"),
    [
        (ts(9, 15), "5m"),
        (ts(9, 20), "5m"),
        (ts(9, 25), "10m"),
        (ts(9, 45), "30m"),
        (ts(10, 15), "15m"),
    ],
)
def test_valid_intraday_boundaries(timestamp, timeframe):
    assert is_valid_intraday_boundary(timestamp, timeframe) is True
    validate_intraday_boundary(timestamp, timeframe)


def test_invalid_boundary_is_rejected():
    timestamp = ts(9, 17)

    assert is_valid_intraday_boundary(timestamp, "5m") is False

    with pytest.raises(ValueError, match="not aligned"):
        validate_intraday_boundary(timestamp, "5m")


def test_weekly_timeframe_requires_separate_semantics():
    with pytest.raises(ValueError, match="Weekly"):
        is_valid_intraday_boundary(ts(9, 15), "1W")
