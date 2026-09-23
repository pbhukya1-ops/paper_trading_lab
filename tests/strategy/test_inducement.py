import pytest

from app.strategy.inducement import (
    InducementLevel,
    detect_inducement,
    detect_inducements,
)


def test_inducement_level_validates_high():
    level = InducementLevel(
        index=2,
        price=105.0,
        inducement_type="HIGH_INDUCEMENT",
        reference_index=0,
        target_index=4,
    )

    assert level.validate() is None


def test_inducement_level_validates_low():
    level = InducementLevel(
        index=2,
        price=95.0,
        inducement_type="LOW_INDUCEMENT",
        reference_index=0,
        target_index=4,
    )

    assert level.validate() is None


def test_detect_inducement_returns_supplied_intermediate_price():
    prices = [100.0, 105.0, 110.0, 108.0, 115.0]

    result = detect_inducement(
        prices,
        reference_index=0,
        inducement_index=2,
        target_index=4,
        inducement_type="HIGH_INDUCEMENT",
    )

    assert result == InducementLevel(
        index=2,
        price=110.0,
        inducement_type="HIGH_INDUCEMENT",
        reference_index=0,
        target_index=4,
    )


def test_detect_low_inducement():
    prices = [110.0, 105.0, 100.0, 103.0, 95.0]

    result = detect_inducement(
        prices,
        reference_index=0,
        inducement_index=2,
        target_index=4,
        inducement_type="LOW_INDUCEMENT",
    )

    assert result == InducementLevel(
        index=2,
        price=100.0,
        inducement_type="LOW_INDUCEMENT",
        reference_index=0,
        target_index=4,
    )


def test_detect_inducements_returns_all_intermediate_levels():
    prices = [100.0, 105.0, 110.0, 108.0, 115.0]

    result = detect_inducements(
        prices,
        reference_index=0,
        target_index=4,
        inducement_type="HIGH_INDUCEMENT",
    )

    assert result == [
        InducementLevel(
            index=1,
            price=105.0,
            inducement_type="HIGH_INDUCEMENT",
            reference_index=0,
            target_index=4,
        ),
        InducementLevel(
            index=2,
            price=110.0,
            inducement_type="HIGH_INDUCEMENT",
            reference_index=0,
            target_index=4,
        ),
        InducementLevel(
            index=3,
            price=108.0,
            inducement_type="HIGH_INDUCEMENT",
            reference_index=0,
            target_index=4,
        ),
    ]


def test_detect_inducements_are_chronological():
    prices = [100.0, 105.0, 110.0, 108.0, 115.0, 120.0]

    result = detect_inducements(
        prices,
        reference_index=1,
        target_index=5,
        inducement_type="HIGH_INDUCEMENT",
    )

    assert [level.index for level in result] == [2, 3, 4]


def test_no_intermediate_indices_returns_empty_list():
    prices = [100.0, 110.0]

    result = detect_inducements(
        prices,
        reference_index=0,
        target_index=1,
        inducement_type="HIGH_INDUCEMENT",
    )

    assert result == []


@pytest.mark.parametrize(
    "inducement_type",
    ["HIGH_INDUCEMENT", "LOW_INDUCEMENT"],
)
def test_both_inducement_types_are_supported(inducement_type):
    prices = [100.0, 105.0, 110.0]

    result = detect_inducement(
        prices,
        reference_index=0,
        inducement_index=1,
        target_index=2,
        inducement_type=inducement_type,
    )

    assert result.inducement_type == inducement_type
    assert result.index == 1
    assert result.price == 105.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "reference_index": -1,
            "inducement_index": 1,
            "target_index": 2,
        },
        {
            "reference_index": 0,
            "inducement_index": -1,
            "target_index": 2,
        },
        {
            "reference_index": 0,
            "inducement_index": 1,
            "target_index": -1,
        },
        {
            "reference_index": 2,
            "inducement_index": 1,
            "target_index": 3,
        },
        {
            "reference_index": 0,
            "inducement_index": 0,
            "target_index": 2,
        },
        {
            "reference_index": 0,
            "inducement_index": 2,
            "target_index": 2,
        },
    ],
)
def test_invalid_index_relationships_are_rejected(kwargs):
    prices = [100.0, 105.0, 110.0, 115.0]

    with pytest.raises(ValueError):
        detect_inducement(
            prices,
            inducement_type="HIGH_INDUCEMENT",
            **kwargs,
        )


def test_invalid_inducement_type_is_rejected():
    prices = [100.0, 105.0, 110.0]

    with pytest.raises(ValueError):
        detect_inducement(
            prices,
            reference_index=0,
            inducement_index=1,
            target_index=2,
            inducement_type="UNKNOWN",
        )


def test_empty_price_series_is_rejected():
    with pytest.raises(ValueError):
        detect_inducement(
            [],
            reference_index=0,
            inducement_index=1,
            target_index=2,
            inducement_type="HIGH_INDUCEMENT",
        )


def test_non_positive_prices_are_rejected():
    with pytest.raises(ValueError):
        detect_inducement(
            [100.0, 0.0, 110.0],
            reference_index=0,
            inducement_index=1,
            target_index=2,
            inducement_type="HIGH_INDUCEMENT",
        )


def test_out_of_range_indices_are_rejected():
    prices = [100.0, 105.0, 110.0]

    with pytest.raises(ValueError):
        detect_inducement(
            prices,
            reference_index=0,
            inducement_index=3,
            target_index=4,
            inducement_type="HIGH_INDUCEMENT",
        )


def test_inducement_level_rejects_invalid_order():
    level = InducementLevel(
        index=2,
        price=105.0,
        inducement_type="HIGH_INDUCEMENT",
        reference_index=2,
        target_index=4,
    )

    with pytest.raises(ValueError):
        level.validate()


def test_inducement_level_rejects_invalid_type():
    level = InducementLevel(
        index=2,
        price=105.0,
        inducement_type="INVALID",
        reference_index=0,
        target_index=4,
    )

    with pytest.raises(ValueError):
        level.validate()


def test_inducement_level_rejects_non_positive_price():
    level = InducementLevel(
        index=2,
        price=0.0,
        inducement_type="HIGH_INDUCEMENT",
        reference_index=0,
        target_index=4,
    )

    with pytest.raises(ValueError):
        level.validate()


def test_detect_inducements_rejects_reference_after_target():
    prices = [100.0, 105.0, 110.0]

    with pytest.raises(ValueError):
        detect_inducements(
            prices,
            reference_index=2,
            target_index=0,
            inducement_type="HIGH_INDUCEMENT",
        )


def test_detect_inducements_rejects_invalid_type():
    prices = [100.0, 105.0, 110.0]

    with pytest.raises(ValueError):
        detect_inducements(
            prices,
            reference_index=0,
            target_index=2,
            inducement_type="INVALID",
        )


def test_detect_inducements_does_not_include_reference_or_target():
    prices = [100.0, 105.0, 110.0, 115.0]

    result = detect_inducements(
        prices,
        reference_index=0,
        target_index=3,
        inducement_type="HIGH_INDUCEMENT",
    )

    assert [level.index for level in result] == [1, 2]
    assert all(level.index != 0 for level in result)
    assert all(level.index != 3 for level in result)
