import pytest

from app.strategy.reference_context import StrategyReferenceContext


def test_valid_empty_reference_context():
    context = StrategyReferenceContext()
    context.validate()


def test_valid_explicit_references():
    context = StrategyReferenceContext(
        level_index=10,
        level_price=100.0,
        level_type="HIGH",
        reference_index=5,
        move_index=8,
        retest_index=12,
        target_index=15,
    )

    context.validate()


def test_negative_level_index_is_rejected():
    context = StrategyReferenceContext(level_index=-1)

    with pytest.raises(ValueError, match="level_index cannot be negative"):
        context.validate()


def test_non_positive_level_price_is_rejected():
    context = StrategyReferenceContext(level_price=0.0)

    with pytest.raises(ValueError, match="level_price must be positive"):
        context.validate()


def test_empty_level_type_is_rejected():
    context = StrategyReferenceContext(level_type="")

    with pytest.raises(ValueError, match="level_type cannot be empty"):
        context.validate()


@pytest.mark.parametrize(
    "field_name",
    [
        "reference_index",
        "move_index",
        "retest_index",
        "target_index",
    ],
)
def test_negative_reference_indices_are_rejected(field_name):
    context = StrategyReferenceContext(**{field_name: -1})

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be negative",
    ):
        context.validate()


def test_context_is_frozen():
    context = StrategyReferenceContext(level_index=1)

    with pytest.raises(AttributeError):
        context.level_index = 2
