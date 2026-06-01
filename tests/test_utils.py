import pytest
import re
import shutil
import sys

from unittest.mock import patch

from src.unit_converter.utils import get_users_input, get_unit_group, validate_unit_group, get_converter_units, get_amount, resolve_aliases, parse_time_input, check_time_is_none, get_seconds, parse_date_input, format_value, calculate_leap_years, is_leap, validate_date, get_days_from_month, get_index_from_month, gets_days_from_index, print_divider
from src.unit_converter.data_manager import load_data
from src.unit_converter.data_models import DataStore, ConversionData


# Setup DataStore to be used on all tests that require DataStore
@pytest.fixture
def data_store():
    return DataStore(*load_data())

# Setup ConversionData to be used on all tests that require ConversionData
@pytest.fixture
def conversion_data():
    return ConversionData(unit_group="length")


# Tests 'get_users_input' function
def test_get_users_input_str():
    with patch("builtins.input", return_value="Hello"):
        assert get_users_input("Input: ") == "hello"

def test_get_users_input_whitespace():
    with patch("builtins.input", return_value="  white space  "):
        assert get_users_input("Input: ") == "white space"

def test_get_users_input_empty():
    with patch("builtins.input", return_value=""):
        assert get_users_input("Input: ") == ""

def test_get_users_input_quit():
    with patch("builtins.input", return_value="quit"):
        with pytest.raises(SystemExit) as error:
            get_users_input("Input: ")
        assert error.value.code == 0


# Tests 'get_unit_group' function
def test_get_unit_group(data_store):
    with patch("unit_converter.utils.get_users_input", return_value=" Length "):
        result = get_unit_group(data_store)
        assert result == "length"

def test_get_unit_group_empty(data_store):
    with patch("unit_converter.utils.get_users_input", return_value=""):
        with pytest.raises(ValueError, match="Unit group cannot be empty!"):
            get_unit_group(data_store)

def test_get_unit_group_invalid(data_store):
    with patch("unit_converter.utils.get_users_input", return_value="invalid"):
        with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
            get_unit_group(data_store)


# Tests 'validate_unit_group' function
def test_validate_unit_group(data_store):
    validate_unit_group("length", data_store)

def test_validate_unit_group_empty(data_store):
    with pytest.raises(ValueError, match="Unit group cannot be empty!"):
            validate_unit_group("", data_store)

def test_validate_unit_group_invalid(data_store):
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
            validate_unit_group("invalid", data_store)


# Tests 'get_converter_units' function
def test_get_converter_units(data_store, conversion_data):
    with patch("unit_converter.utils.get_users_input", side_effect=["meters", "miles"]):        
        assert get_converter_units(data_store, conversion_data) == ("meters", "miles")

def test_get_converter_units_empty(data_store, conversion_data):
    with patch("unit_converter.utils.get_users_input", side_effect=["", "miles"]):
        with pytest.raises(ValueError, match="'unit_type' cannot be empty!"):
            get_converter_units(data_store, conversion_data)

def test_get_converter_units_invalid(data_store, conversion_data):
    with patch("unit_converter.utils.get_users_input", side_effect=["meters", "invalid"]):
        with pytest.raises(KeyError, match="Invalid unit type!"):
            get_converter_units(data_store, conversion_data)


# Test 'get_amount' function
def test_get_amount_integer(conversion_data):
    with patch("unit_converter.utils.get_users_input", return_value="10"):
        result = get_amount(conversion_data)
        assert result == "10"
        assert conversion_data.amount == "10"

def test_get_amount_decimal(conversion_data):
    with patch("unit_converter.utils.get_users_input", return_value="10.0"):
        result = get_amount(conversion_data)
        assert result == "10.0"
        assert conversion_data.amount == "10.0"

def test_get_amount_negative(conversion_data):
    with patch("unit_converter.utils.get_users_input", return_value="-10"):
        result = get_amount(conversion_data)
        assert result == "-10"
        assert conversion_data.amount == "-10"

def test_get_amount_empty(conversion_data):
    with patch("unit_converter.utils.get_users_input", return_value=""):
        with pytest.raises(ValueError, match=re.escape("Invalid amount! Please, insert integer or decimals! (e.g. 10 or 10.0)")):
            get_amount(conversion_data)

def test_get_amount_invalid_format(conversion_data):
    with patch("unit_converter.utils.get_users_input", return_value="10."):
        with pytest.raises(ValueError, match=re.escape("Invalid amount! Please, insert integer or decimals! (e.g. 10 or 10.0)")):
            get_amount(conversion_data)

def test_get_amount_str(conversion_data):
    with patch("unit_converter.utils.get_users_input", return_value="ten"):
        with pytest.raises(ValueError, match=re.escape("Invalid amount! Please, insert integer or decimals! (e.g. 10 or 10.0)")):
            get_amount(conversion_data)


# Test 'resolve_aliases' function
def test_resolve_aliases_unit(data_store):
    assert resolve_aliases(data_store, "length", "meters") == "meters"

def test_resolve_aliases_alias(data_store):
    assert resolve_aliases(data_store, "length", "m") == "meters"

def test_resolve_aliases_invalid(data_store):
    with pytest.raises(KeyError, match="Unit type 'invalid' not found in 'length' group neither its aliases!"):
        resolve_aliases(data_store, "length", "invalid")


# Test 'parse_time_input' function
def test_parse_time_input_complete():
    assert parse_time_input("10h:10m:10s") == 10 * 3600 + 10 * 60 + 10

def test_parse_time_input_no_hours():
    assert parse_time_input(":10m:10s") == 10 * 60 + 10

def test_parse_time_input_no_minutes():
    assert parse_time_input("10h:10s") == 10 * 3600 + 10

def test_parse_time_input_no_seconds():
    assert parse_time_input("10h:10m") == 10 * 3600 + 10 * 60

def test_parse_time_input_only_hours():
    assert parse_time_input("10h") == 10 * 3600

def test_parse_time_input_only_minutes():
    assert parse_time_input(":10m") == 10 * 60

def test_parse_time_input_only_seconds():
    assert parse_time_input(":10s") == 10

def test_parse_time_input_invalid_sign():
    with pytest.raises(ValueError, match="Invalid time format!"):
        parse_time_input("10h-10m-10s")

def test_parse_time_input_str():
    with pytest.raises(ValueError, match="Invalid time format!"):
        parse_time_input("Ten Hours")

def test_parse_time_input_empty():
    with pytest.raises(ValueError, match="Invalid time format!"):
        parse_time_input(" ")


# Test 'check_time_is_none' function
def test_check_time_is_none():
    assert check_time_is_none("10") == 10
def test_check_time_is_none_empty():
    assert check_time_is_none("") == 0
def test_check_time_is_none_none():
    assert check_time_is_none(None) == 0


# Test 'get_seconds' function
def test_get_seconds(data_store):
    assert get_seconds(data_store, "time", 10, 10, 10) == (10 * 365.2425 * 86400.0) + (10 * 30.436875 * 86400.0) + (10 * 86400.0)

def test_get_seconds_all_zeroes(data_store):
    assert get_seconds(data_store, "time", 0, 0, 0) == 0

def test_get_seconds_invalid(data_store):
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        get_seconds(data_store, "invalid", 10, 10, 10)


# Test 'parse_date_input' function
def test_parse_date_input():
    assert parse_date_input("1994-12-1") == (1994, 12, 1)

def test_parse_date_input_big_dates():
    assert parse_date_input("3000-100-50") == (3000, 100, 50)

def test_parse_date_input_no_year():
    assert parse_date_input("0-12-01") == (0, 12, 1)

def test_parse_date_input_no_month():
    assert parse_date_input("1994-0-1") == (1994, 0, 1)

def test_parse_date_input_no_days():
    assert parse_date_input("1994-12-0") == (1994, 12, 0)

def test_parse_date_input_only_year():
    assert parse_date_input("1994-0-0") == (1994, 0, 0)

def test_parse_date_input_only_month():
    assert parse_date_input("0-12-0") == (0, 12, 0)

def test_parse_date_input_only_days():
    assert parse_date_input("0-0-1") == (0, 0, 1)

def test_parse_date_input_all_zeroes():
    assert parse_date_input("0-0-0") == (0, 0, 0)

def test_parse_date_input_invalid_format():
    with pytest.raises(ValueError, match="invalid date format! Usage: YYYY-MM-DD"):
        parse_date_input("1994/12/1")

def test_parse_date_input_str():
    with pytest.raises(ValueError, match="invalid date format! Usage: YYYY-MM-DD"):
        parse_date_input("December first nineteen ninety four")


# Test 'format_value' function
def test_format_value_integer():
    assert format_value(10) == "10.0"

def test_format_value_float():
    assert format_value(10.0) == "10.0"

def test_format_value_trailling_zeroes():
    assert format_value(10.00000) == "10.0"

def test_format_value_decimals():
    assert format_value(10.99999) == "10.99999"

def test_format_value_round():
    assert format_value(10.999999) == "11.0"


# Test 'calculate_leap_years' function
def test_calculate_leap_years():
    assert calculate_leap_years(2000, 1, 2004, 1, 1) == 1

# Test 'calculate_leap_years' function
def test_calculate_leap_years_same_year():
    assert calculate_leap_years(2000, 1, 2000, 1, 1) == 0


# Test 'is_leap' function
def test_is_leap_by4():
    assert is_leap(2004) == True

def test_is_leap_by100():
    assert is_leap(2100) == False

def test_is_leap_by400():
    assert is_leap(2000) == True


# Test 'validate_date' function
def test_validate_date():
    assert validate_date(1994, 12, 1) == True

def test_validate_date_invalid_month():
    with pytest.raises(ValueError, match="Invalid date! '13' is not a valid month"):
        validate_date(1994, 13, 1)

def test_validate_date_negative_month():
    with pytest.raises(ValueError, match="Invalid date! '-12' is not a valid month"):
        validate_date(1994, -12, 1)

def test_validate_date_invalid_day():
    with pytest.raises(ValueError, match="Invalid date! '32' is not a valid day for '12'"):
        validate_date(1994, 12, 32)

def test_validate_date_invalid_leap_feb():
    with pytest.raises(ValueError, match="Invalid date! '29' is not a valid day for '2'"):
        validate_date(2003, 2, 29)


# Test 'get_days_from_month' function
def test_get_days_from_month(data_store):
    assert get_days_from_month(data_store, "December") == 31

def test_get_days_from_month_invalid(data_store):
    with pytest.raises(KeyError, match="Invalid month: 'invalid'"):
        get_days_from_month(data_store, "invalid")


# Test 'get_index_from_month' function
def test_get_index_from_month(data_store):
    assert get_index_from_month(data_store, "December") == 12

def test_get_index_from_month_invalid(data_store):
    with pytest.raises(KeyError, match="Invalid month: 'invalid'"):
        get_index_from_month(data_store, "invalid") is None


# Test 'gets_days_from_index' function
def test_get_days_from_index_valid(data_store):
    assert gets_days_from_index(data_store, "12") == 31


# Test 'print_divider' function
def test_print_divider():
    columns, _ = shutil.get_terminal_size()
    assert print_divider("-") == "-" * columns