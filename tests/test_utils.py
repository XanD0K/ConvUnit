import pytest
from unittest.mock import patch

from convunit.utils import (
    _get_user_input, _get_unit_group,  _validate_unit_group, _get_converter_units,
    _get_amount, _resolve_aliases, _format_value, _ensure_non_zero,
)
from convunit.data_models import DataStore, ConversionData
from convunit.data_manager import _load_data


@pytest.fixture
def data_store():
    return DataStore(*_load_data())


@pytest.fixture
def conversion_data():
    return ConversionData(unit_group="length")


def test_get_user_input_normal():
    with patch("builtins.input", return_value="  Hello  "):
        assert _get_user_input("Prompt: ") == "hello"


def test_get_user_input_quit():
    with patch("builtins.input", return_value="quit"):
        with pytest.raises(SystemExit):
            _get_user_input("Prompt: ")


def test_get_unit_group(data_store):
    with patch("unitconverter.utils._get_user_input", return_value="length"):
        result = _get_unit_group(data_store)
        assert result == "length"


def test_validate_unit_group_valid(data_store):
    _validate_unit_group("length", data_store)


def test_validate_unit_group_invalid(data_store):
    with pytest.raises(Exception):
        _validate_unit_group("invalid", data_store)


def test_get_converter_units(data_store, conversion_data):
    with patch("unitconverter.utils._get_user_input", side_effect=["meters", "feet"]):
        _get_converter_units(data_store, conversion_data)
        assert conversion_data.from_type == "meters"
        assert conversion_data.to_type == "feet"


def test_get_amount(conversion_data):
    with patch("unitconverter.utils._get_user_input", return_value="10.5"):
        _get_amount(conversion_data)
        assert conversion_data.amount == 10.5


def test_resolve_aliases_real_name(data_store):
    assert _resolve_aliases(data_store, "length", "meters") == "meters"


def test_resolve_aliases_alias(data_store):
    assert _resolve_aliases(data_store, "length", "m") == "meters"


def test_resolve_aliases_invalid(data_store):
    with pytest.raises(Exception):
        _resolve_aliases(data_store, "length", "invalid")


def test_format_value():
    assert _format_value(10) == "10.0"
    assert _format_value(10.5) == "10.5"
    assert _format_value(10.000) == "10.0"


def test_ensure_non_zero_valid():
    _ensure_non_zero(5)


def test_ensure_non_zero_zero():
    with pytest.raises(ZeroDivisionError):
        _ensure_non_zero(0)
