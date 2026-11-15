import pytest
from pydantic import TypeAdapter, ValidationError
from src.models import ItemName

adapter = TypeAdapter(ItemName)


def test_empty_name_is_invalid():
    with pytest.raises(ValidationError):
        adapter.validate_python("")


def test_space_only_name_is_invalid():
    with pytest.raises(ValidationError):
        adapter.validate_python("   ")


def test_surrounding_spaces_are_trimmed():
    assert adapter.validate_python("  Buy milk  ") == "Buy milk"


def test_255_characters_is_valid():
    name = "a" * 255
    assert adapter.validate_python(name) == name


def test_256_characters_is_invalid():
    with pytest.raises(ValidationError):
        adapter.validate_python("a" * 256)
