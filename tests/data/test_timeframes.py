import pytest

from app.data.timeframes import get_timeframe, validate_timeframe


def test_supported_intraday_timeframes():
    for name, minutes in (
        ("5m", 5),
        ("10m", 10),
        ("15m", 15),
        ("30m", 30),
    ):
        spec = get_timeframe(name)
        assert spec.name == name
        assert spec.minutes == minutes
        assert spec.is_weekly is False


def test_weekly_timeframe():
    spec = get_timeframe("1W")

    assert spec.name == "1W"
    assert spec.minutes is None
    assert spec.is_weekly is True


def test_unknown_timeframe_is_rejected():
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        get_timeframe("1m")


def test_validate_timeframe_accepts_supported_values():
    for name in ("5m", "10m", "15m", "30m", "1W"):
        validate_timeframe(name)
