import pytest

from unittest.mock import patch

from src.unit_converter.data_manager import load_data, validate_data, add_to_log, clean_history, save_data, refactor_value, zero_division_checker
from src.unit_converter.data_models import DataStore


# Setup DataStore to be used on all tests that require DataStore
@pytest.fixture
def data_store():
    return DataStore(*load_data())


# TODO: Test 'load_data' function

# TODO: Test 'vlaidate_data' function

# TODO: Test 'add_to_log' function

# TODO: Test 'clean_history' function

# TODO: Test 'save_data' function


# Test 'refactor_value' function
def test_refactor_value_length(data_store):
    original_meters = data_store.units["length"]["meters"]
    original_kilometers = data_store.units["length"]["kilometers"]
    refactor_value(data_store, "length", "kilometers")
    assert data_store.units["length"]["meters"] == original_meters / original_kilometers
    assert data_store.units["length"]["kilometers"] == 1.0

def test_refactor_value_temperature(data_store):
    original_celsius = data_store.units["temperature"]["celsius"]
    original_kelvin = data_store.units["temperature"]["kelvin"]
    refactor_value(data_store, "temperature", "kelvin")
    assert data_store.units["temperature"]["celsius"] == [original_celsius[0] / original_kelvin[0], original_celsius[1] - original_kelvin[1]]
    assert data_store.units["temperature"]["kelvin"] == [1.0, 0.0]


# Test 'zero_division_checker' function
def test_zero_division_checker_valid():
    zero_division_checker(1.0)

def test_zero_division_checker_zero():
    with pytest.raises(ZeroDivisionError, match="Can't Divide by zero"):
        zero_division_checker(0)