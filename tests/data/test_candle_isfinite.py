import pytest
from math import nan, inf
from tests.data.test_candle import make_candle


@pytest.mark.parametrize("field", ["open", "high", "low", "close"])
@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_non_finite_price_is_rejected(field, value):
    candle = make_candle(**{field: value})
    with pytest.raises(ValueError):
        candle.validate()


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_non_finite_volume_is_rejected(value):
    candle = make_candle(volume=value)
    with pytest.raises(ValueError):
        candle.validate()
