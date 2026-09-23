import pytest

from app.strategy.ema_support import (
    VALID_EMA_RELATIONSHIPS,
    VALID_ZONE_RELATIONSHIPS,
    VALID_INTERACTION_TYPES,
    EMA21SupportContext,
    classify_ema_relationship,
    classify_zone_relationship,
    classify_ema_zone_interaction,
)
from app.strategy.zones import PriceZone


def make_support_zone():
    return PriceZone(
        center=100.0,
        lower=99.0,
        upper=101.0,
        source="SUPPORT:100.0",
    )


def make_resistance_zone():
    return PriceZone(
        center=200.0,
        lower=199.0,
        upper=201.0,
        source="RESISTANCE:200.0",
    )


def test_valid_constant_sets():
    assert VALID_EMA_RELATIONSHIPS == {
        "ABOVE_EMA",
        "BELOW_EMA",
        "AT_EMA",
    }
    assert VALID_ZONE_RELATIONSHIPS == {
        "IN_SUPPORT_ZONE",
        "IN_RESISTANCE_ZONE",
        "OUTSIDE_ZONE",
    }
    assert VALID_INTERACTION_TYPES == {
        "SUPPORT_EMA_INTERACTION",
        "RESISTANCE_EMA_INTERACTION",
        "SUPPORT_ONLY",
        "RESISTANCE_ONLY",
        "EMA_ONLY",
        "NO_INTERACTION",
    }


def test_context_validates():
    context = EMA21SupportContext(
        price=100.0,
        ema21=100.0,
        ema_relationship="AT_EMA",
        zone_relationship="IN_SUPPORT_ZONE",
        interaction_type="SUPPORT_EMA_INTERACTION",
        zone_source="SUPPORT:100.0",
    )
    context.validate()


def test_context_is_frozen():
    context = EMA21SupportContext(
        price=100.0,
        ema21=100.0,
        ema_relationship="AT_EMA",
        zone_relationship="IN_SUPPORT_ZONE",
        interaction_type="SUPPORT_EMA_INTERACTION",
        zone_source="SUPPORT:100.0",
    )

    with pytest.raises(Exception):
        context.price = 101.0


@pytest.mark.parametrize(
    ("price", "ema21", "expected"),
    [
        (101.0, 100.0, "ABOVE_EMA"),
        (99.0, 100.0, "BELOW_EMA"),
        (100.0, 100.0, "AT_EMA"),
    ],
)
def test_classify_ema_relationship(price, ema21, expected):
    assert classify_ema_relationship(price, ema21) == expected


@pytest.mark.parametrize(
    ("price", "ema21"),
    [
        (0.0, 100.0),
        (-1.0, 100.0),
        (100.0, 0.0),
        (100.0, -1.0),
    ],
)
def test_classify_ema_relationship_rejects_nonpositive_values(price, ema21):
    with pytest.raises(ValueError):
        classify_ema_relationship(price, ema21)


def test_classify_zone_relationship_without_zone():
    assert classify_zone_relationship(100.0, None) == (
        "OUTSIDE_ZONE",
        None,
    )


def test_classify_zone_relationship_inside_support():
    assert classify_zone_relationship(
        100.0,
        make_support_zone(),
    ) == (
        "IN_SUPPORT_ZONE",
        "SUPPORT:100.0",
    )


def test_classify_zone_relationship_inside_resistance():
    assert classify_zone_relationship(
        200.0,
        make_resistance_zone(),
    ) == (
        "IN_RESISTANCE_ZONE",
        "RESISTANCE:200.0",
    )


def test_classify_zone_relationship_outside_support():
    assert classify_zone_relationship(
        105.0,
        make_support_zone(),
    ) == (
        "OUTSIDE_ZONE",
        None,
    )


def test_classify_zone_relationship_outside_resistance():
    assert classify_zone_relationship(
        205.0,
        make_resistance_zone(),
    ) == (
        "OUTSIDE_ZONE",
        None,
    )


def test_classify_zone_relationship_rejects_nonpositive_price():
    with pytest.raises(ValueError):
        classify_zone_relationship(0.0, None)

    with pytest.raises(ValueError):
        classify_zone_relationship(-1.0, None)


def test_support_and_ema_at_same_price():
    context = classify_ema_zone_interaction(
        price=100.0,
        ema21=100.0,
        zone=make_support_zone(),
    )

    assert context.ema_relationship == "AT_EMA"
    assert context.zone_relationship == "IN_SUPPORT_ZONE"
    assert context.interaction_type == "SUPPORT_EMA_INTERACTION"
    assert context.zone_source == "SUPPORT:100.0"


def test_resistance_and_ema_at_same_price():
    context = classify_ema_zone_interaction(
        price=200.0,
        ema21=200.0,
        zone=make_resistance_zone(),
    )

    assert context.ema_relationship == "AT_EMA"
    assert context.zone_relationship == "IN_RESISTANCE_ZONE"
    assert context.interaction_type == "RESISTANCE_EMA_INTERACTION"
    assert context.zone_source == "RESISTANCE:200.0"


def test_support_without_ema_interaction():
    context = classify_ema_zone_interaction(
        price=100.0,
        ema21=95.0,
        zone=make_support_zone(),
    )

    assert context.ema_relationship == "ABOVE_EMA"
    assert context.zone_relationship == "IN_SUPPORT_ZONE"
    assert context.interaction_type == "SUPPORT_ONLY"


def test_resistance_without_ema_interaction():
    context = classify_ema_zone_interaction(
        price=200.0,
        ema21=205.0,
        zone=make_resistance_zone(),
    )

    assert context.ema_relationship == "BELOW_EMA"
    assert context.zone_relationship == "IN_RESISTANCE_ZONE"
    assert context.interaction_type == "RESISTANCE_ONLY"


def test_ema_only_interaction():
    context = classify_ema_zone_interaction(
        price=100.0,
        ema21=100.0,
        zone=None,
    )

    assert context.ema_relationship == "AT_EMA"
    assert context.zone_relationship == "OUTSIDE_ZONE"
    assert context.interaction_type == "EMA_ONLY"
    assert context.zone_source is None


def test_no_interaction():
    context = classify_ema_zone_interaction(
        price=105.0,
        ema21=100.0,
        zone=make_support_zone(),
    )

    assert context.ema_relationship == "ABOVE_EMA"
    assert context.zone_relationship == "OUTSIDE_ZONE"
    assert context.interaction_type == "NO_INTERACTION"
    assert context.zone_source is None


def test_zone_boundary_is_inside():
    assert classify_zone_relationship(
        99.0,
        make_support_zone(),
    ) == (
        "IN_SUPPORT_ZONE",
        "SUPPORT:100.0",
    )

    assert classify_zone_relationship(
        101.0,
        make_support_zone(),
    ) == (
        "IN_SUPPORT_ZONE",
        "SUPPORT:100.0",
    )


def test_outside_zone_cannot_have_zone_source():
    context = EMA21SupportContext(
        price=105.0,
        ema21=100.0,
        ema_relationship="ABOVE_EMA",
        zone_relationship="OUTSIDE_ZONE",
        interaction_type="NO_INTERACTION",
        zone_source="SUPPORT:100.0",
    )

    with pytest.raises(
        ValueError,
        match="Outside-zone context cannot contain a zone source",
    ):
        context.validate()


def test_inside_zone_requires_zone_source():
    context = EMA21SupportContext(
        price=100.0,
        ema21=100.0,
        ema_relationship="AT_EMA",
        zone_relationship="IN_SUPPORT_ZONE",
        interaction_type="SUPPORT_EMA_INTERACTION",
        zone_source=None,
    )

    with pytest.raises(
        ValueError,
        match="Zone source is required",
    ):
        context.validate()


@pytest.mark.parametrize(
    "field,value",
    [
        ("ema_relationship", "INVALID"),
        ("zone_relationship", "INVALID"),
        ("interaction_type", "INVALID"),
    ],
)
def test_invalid_enum_values_are_rejected(field, value):
    kwargs = {
        "price": 100.0,
        "ema21": 100.0,
        "ema_relationship": "AT_EMA",
        "zone_relationship": "IN_SUPPORT_ZONE",
        "interaction_type": "SUPPORT_EMA_INTERACTION",
        "zone_source": "SUPPORT:100.0",
    }
    kwargs[field] = value

    context = EMA21SupportContext(**kwargs)

    with pytest.raises(ValueError):
        context.validate()


@pytest.mark.parametrize(
    ("price", "ema21"),
    [
        (0.0, 100.0),
        (-1.0, 100.0),
        (100.0, 0.0),
        (100.0, -1.0),
    ],
)
def test_classify_interaction_rejects_nonpositive_price_or_ema(price, ema21):
    with pytest.raises(ValueError):
        classify_ema_zone_interaction(
            price=price,
            ema21=ema21,
            zone=None,
        )
