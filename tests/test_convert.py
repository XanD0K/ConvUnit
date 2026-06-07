import pytest
from unittest.mock import patch

from convunit.convert import _conversion_logic, _converter_standard_units, _converter_temperature
from convunit.convert_time import _converter_time
from convunit.data_models import DataStore, ConversionData
from convunit.data_manager import _load_data


@pytest.fixture
def data_store():
    return DataStore(*_load_data())


@pytest.fixture
def conversion_data():
    return ConversionData(unit_group="length")


def test_conversion_logic_normal(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "feet"
    conversion_data.amount = 10
    result = _conversion_logic(data_store, conversion_data)
    assert "meters" in result
    assert "feet" in result


def test_convert_standard_units(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "feet"
    conversion_data.amount = 10
    result = _converter_standard_units(data_store, conversion_data)
    assert result > 0


def test_convert_temperature(data_store, conversion_data):
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "celsius"
    conversion_data.to_type = "kelvin"
    conversion_data.amount = 0
    result = _converter_temperature(data_store, conversion_data)
    assert result == 273.15


def test_converter_time_simple(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds 1"
    conversion_data._validate_time_args(data_store)   # preenche os campos
    result = _converter_time(data_store, conversion_data)
    assert "60.0 seconds" in result