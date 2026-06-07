import pytest
from unittest.mock import patch

from convunit.api import Converter


@pytest.fixture
def converter():
    """Fixture that creates a Converter with mocked data (including 'time' group)."""
    with patch("unitconverter.api._load_data") as mock_load:
        mock_load.return_value = (
            {
                "length": {"meters": 1.0, "feet": 0.3048},
                "time": {"minutes": 60, "seconds": 1}
            },
            {
                "length": "meters",
                "time": "seconds"
            },
            [],
            {
                "length": {"meters": "meters", "feet": "feet"},
                "time": {"minutes": "minutes", "seconds": "seconds"}
            },
            {},
            {
                "length": {"meters": 1.0, "feet": 0.3048},
                "time": {"minutes": 60, "seconds": 1}
            },
            {}
        )
        yield Converter()


def test_groups(converter):
    result = converter.groups()
    assert "length" in result


def test_groups_alias(converter):
    assert converter.g() == converter.groups()


def test_convert_length(converter):
    result = converter.convert("length", "meters", "feet", 10)
    assert isinstance(result, float)
    assert result > 0


def test_convert_time(converter):
    result = converter.convert("time", time_input="minutes seconds 60")
    assert result == 3600.0


def test_convert_invalid_group(converter):
    result = converter.convert("invalid", "meters", "feet", 10)
    assert "Error" in str(result)


def test_history_empty(converter):
    result = converter.history()
    assert "Error" in str(result) or result == ""


def test_reset_history(converter):
    result = converter.reset_history()
    assert result is True or result is None


def test_manage_group_add(converter):
    result = converter.manage_group("test_group", "add", "base_unit")
    assert "created" in str(result).lower() or result is True


def test_manage_type_add(converter):
    result = converter.manage_type("length", "new_unit", "add", 2.0)
    assert result is True or "added" in str(result).lower()


def test_aliases_add(converter):
    result = converter.aliases("length", "meters", "add", "mtr")
    assert result is True or "added" in str(result).lower()


def test_change_base(converter):
    result = converter.change_base("length", "feet")
    assert result is True or "changed" in str(result).lower()


def test_reset(converter):
    result = converter.reset()
    assert "reset" in str(result).lower() or result is True
