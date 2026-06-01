import pytest
import re

from unittest.mock import patch

from src.unit_converter.data_manager import load_data
from src.unit_converter.data_models import DataStore, ConversionData, ManageGroupData, ManageTypeData, AliasesData, ChangeBaseData, validate_for_history, validate_args_number


# Setup DataStore to be used on all tests that require DataStore
@pytest.fixture
def data_store():
    return DataStore(*load_data())

# Setup fixtures to be used on their respective class tests
@pytest.fixture
def conversion_data():
    return ConversionData(unit_group="length")

@pytest.fixture
def manage_group_data():
    return ManageGroupData(unit_group="length")

@pytest.fixture
def manage_type_data():
    return ManageTypeData(unit_group="length")

@pytest.fixture
def aliases_data():
    return AliasesData(unit_group="length")

@pytest.fixture
def change_base_data():
    return ChangeBaseData(unit_group="length", new_base_unit=None)


# Test 'ConversionData' class methods
def test_validate_from_type(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.validate_from_type(data_store)

def test_validate_from_type_empty(data_store, conversion_data):
    with pytest.raises(ValueError, match="'unit_type' cannot be empty!"):
        conversion_data.validate_from_type(data_store)

def test_validate_from_type_invalid(data_store, conversion_data):
    conversion_data.from_type = "invalid"
    with pytest.raises(KeyError, match="Invalid unit type!"):
        conversion_data.validate_from_type(data_store)

def test_validate_to_type(data_store, conversion_data):
    conversion_data.to_type = "meters"
    conversion_data.validate_to_type(data_store)

def test_validate_to_type_empty(data_store, conversion_data):
    with pytest.raises(ValueError, match="'unit_type' cannot be empty!"):
        conversion_data.validate_to_type(data_store)

def test_validate_to_type_invalid(data_store, conversion_data):
    conversion_data.to_type = "invalid"
    with pytest.raises(KeyError, match="Invalid unit type!"):
        conversion_data.validate_to_type(data_store)

def test_validate_amount(conversion_data):
    conversion_data.amount = "10"
    conversion_data.validate_amount()
    assert conversion_data.amount == 10.0

def test_validate_amount_empty(conversion_data):
    with pytest.raises(ValueError, match="'amount' cannot be empty"):
        conversion_data.validate_amount()

def test_validate_amount_invalid(conversion_data):
    conversion_data.amount = "invalid"
    with pytest.raises(ValueError, match="Invalid amount!"):
        conversion_data.validate_amount()

def test_validate_amount_negative_kelvin(conversion_data):
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "kelvin"
    conversion_data.amount = "-10"
    with pytest.raises(ValueError, match="Kelvin temperature cannot be negative!"):
        conversion_data.validate_amount()

def test_validate_time_input(conversion_data):
    conversion_data.time_input = "minutes seconds 10"
    conversion_data.validate_time_input()

def test_validate_time_input_empty(conversion_data):
    with pytest.raises(ValueError, match="Time conversion can't be empty! Enter an expression!"):
        conversion_data.validate_time_input()

def test_validate_time_input_invalid_format(conversion_data):
    conversion_data.time_input = "minutes"
    with pytest.raises(ValueError, match="Incorrect format for time conversion!"):
        conversion_data.validate_time_input()

def test_validate_from_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "minutes"
    conversion_data.validate_from_time(data_store)

def test_validate_from_time_empty(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = ""
    with pytest.raises(ValueError, match="Enter a value to convert from!"):
        conversion_data.validate_from_time(data_store)

def test_validate_from_time_invalid_format(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "invalid"
    with pytest.raises(ValueError, match="Invalid 'from_time': 'invalid'"):
        conversion_data.validate_from_time(data_store)

def test_validate_from_time_invalid_date_month(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "1994-13-01"
    conversion_data.to_time = "2020-12-01"
    with pytest.raises(ValueError, match="Invalid date! '13' is not a valid month"):
        conversion_data.validate_from_time(data_store)

def test_validate_from_time_invalid_date_day(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "1994-12-32"
    conversion_data.to_time = "2020-12-01"
    with pytest.raises(ValueError, match="Invalid date! '32' is not a valid day for '12' month"):
        conversion_data.validate_from_time(data_store)

def test_validate_to_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.to_time = "seconds"
    conversion_data.validate_to_time(data_store)

def test_validate_to_time_empty(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.to_time = ""
    with pytest.raises(ValueError, match="Enter a value to convert to!"):
        conversion_data.validate_to_time(data_store)

def test_validate_to_time_invalid_format(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.to_time = "invalid"
    with pytest.raises(ValueError, match="Invalid 'to_time': 'invalid'"):
        conversion_data.validate_to_time(data_store)

def test_validate_to_time_invalid_date_month(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.to_time = "1994-13-01"
    with pytest.raises(ValueError, match="Invalid date! '13' is not a valid month"):
        conversion_data.validate_to_time(data_store)

def test_validate_to_time_invalid_date_day(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.to_time = "1994-12-32"
    with pytest.raises(ValueError, match="Invalid date! '32' is not a valid day for '12' month"):
        conversion_data.validate_to_time(data_store)

def test_validate_factor_time_int(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.factor_time = "10"
    conversion_data.validate_factor_time(data_store)
    assert conversion_data.factor_time == 10.0

def test_validate_factor_time_type(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.factor_time = "minutes"
    conversion_data.validate_factor_time(data_store)

def test_validate_factor_time_empty(data_store, conversion_data):
    with pytest.raises(ValueError, match="'factor_time' cannot be empty!"):
        conversion_data.validate_factor_time(data_store)

def test_validate_factor_time_invalid(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.factor_time = "invalid"
    with pytest.raises(KeyError, match="Factor time 'invalid' not found in 'time' group!"):
        conversion_data.validate_factor_time(data_store)

def test_validate_time_args(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds 10"
    conversion_data.validate_time_args(data_store)
    assert conversion_data.from_time == "minutes"
    assert conversion_data.to_time == "seconds"
    assert conversion_data.factor_time == 10.0

def test_validate_time_args_invalid_length(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes"
    with pytest.raises(ValueError, match="Invalid format for date and time conversion!"):
        conversion_data.validate_time_args(data_store)

def test_validate_time_args_invalid_number(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "invalid days 10 hours seconds"
    with pytest.raises(ValueError, match="'invalid' is an invalid amount!"):
        conversion_data.validate_time_args(data_store)

def test_validate_time_args_invalid_unit(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "10 days 10 invalid seconds"
    with pytest.raises(ValueError, match="'invalid' is an invalid unit type!"):
        conversion_data.validate_time_args(data_store)

def test_validate_for_conversion(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = "10"
    conversion_data.validate_for_conversion(data_store)

def test_validate_for_conversion_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds 10"
    conversion_data.validate_for_conversion(data_store)

def test_validate_for_conversion_invalid_group(data_store, conversion_data):
    conversion_data.unit_group = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        conversion_data.validate_for_conversion(data_store)

def test_validate_for_conversion_empty_field(data_store, conversion_data):
    with pytest.raises(ValueError, match="Invalid conversion format!"):
        conversion_data.validate_for_conversion(data_store)

def test_validate_for_conversion_invalid_time_format(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes"
    with pytest.raises(ValueError, match="Incorrect format for time conversion!"):
        conversion_data.validate_for_conversion(data_store)


# Test 'ManageGroupData' class methods
def test_validate_group_action(manage_group_data):
    manage_group_data.action = "add"
    manage_group_data.validate_action()

def test_validate_group_action_empty(manage_group_data):
    with pytest.raises(ValueError, match="'action' cannot be empty!"):
        manage_group_data.validate_action()

def test_validate_action_invalid(manage_group_data):
    manage_group_data.action = "invalid"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_group_data.validate_action()

def test_validate_add_action_group(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.validate_add_action(data_store)

def test_validate_group_add_action_already_group(data_store, manage_group_data):
    with pytest.raises(KeyError, match="'length' is already an existed group!"):
        manage_group_data.validate_add_action(data_store)

def test_validate_remove_group_action(data_store, manage_group_data):
    manage_group_data.validate_remove_action(data_store)

def test_validate_group_remove_action_invalid_type(data_store, manage_group_data):
    manage_group_data.unit_group = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        manage_group_data.validate_remove_action(data_store)

def test_validate_new_base_unit(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.new_base_unit = "new_base_unit"
    manage_group_data.validate_new_base_unit(data_store)

def test_validate_new_base_unit_empty(data_store, manage_group_data):
    with pytest.raises(ValueError, match="'new_base_unit' cannot be empty"):
        manage_group_data.validate_new_base_unit(data_store)

def test_validate_new_base_unit_already_group(data_store, manage_group_data):
    manage_group_data.new_base_unit = "length"
    with pytest.raises(KeyError, match="'length' is already an unit group name!"):
        manage_group_data.validate_new_base_unit(data_store)

def test_validate_new_base_unit_same_name(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.new_base_unit = "new_group"
    with pytest.raises(ValueError, match="'new_base_unit' can't have the same name as 'unit_group'"):
        manage_group_data.validate_new_base_unit(data_store)

def test_validate_for_manage_group_add(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "add"
    manage_group_data.new_base_unit = "new_base"
    manage_group_data.validate_for_manage_group(data_store)

def test_validate_for_manage_group_remove(data_store, manage_group_data):
    manage_group_data.action = "remove"
    manage_group_data.validate_for_manage_group(data_store)

def test_validate_for_manage_group_add_already_group(data_store, manage_group_data):
    manage_group_data.action = "add"
    manage_group_data.new_base_unit = "new_base"
    with pytest.raises(KeyError, match="'length' is already an existed group!"):
        manage_group_data.validate_for_manage_group(data_store)

def test_validate_for_manage_group_remove_invalid_group(data_store, manage_group_data):
    manage_group_data.unit_group = "invalid"
    manage_group_data.action = "remove"
    manage_group_data.new_base_unit = "new_base"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        manage_group_data.validate_for_manage_group(data_store)

def test_validate_for_manage_group_invalid_action(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "invalid"
    manage_group_data.new_base_unit = "new_base"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_group_data.validate_for_manage_group(data_store)

def test_validate_for_manage_group_empty_new_base(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "add"
    manage_group_data.new_base_unit = ""
    with pytest.raises(ValueError, match="'new_base_unit' cannot be empty"):
        manage_group_data.validate_for_manage_group(data_store)

# Test 'ManageTypeData' class methods
def test_validate_type_action(manage_type_data):
    manage_type_data.action = "add"
    manage_type_data.validate_action()

def test_validate_type_action_empty(manage_type_data):
    with pytest.raises(ValueError, match="'action' cannot be empty!"):
        manage_type_data.validate_action()

def test_validate_type_action_invalid(manage_type_data):
    manage_type_data.action = "invalid"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_type_data.validate_action()

def test_validate_add_action_type(data_store, manage_type_data):
    manage_type_data.unit_type = "new_type"
    manage_type_data.validate_add_action(data_store)

def test_validate_add_action_empty_type(data_store, manage_type_data):
    with pytest.raises(ValueError, match="You can't leave that field empty!"):
        manage_type_data.validate_add_action(data_store)

def test_validate_type_add_action_already_group(data_store, manage_type_data):
    manage_type_data.unit_type = "length"
    with pytest.raises(KeyError, match="'length' is already an unit group name!"):
        manage_type_data.validate_add_action(data_store)

def test_validate_add_action_already_type(data_store, manage_type_data):
    manage_type_data.unit_type = "meters"
    with pytest.raises(ValueError, match="'meters' is already an unit type in 'length' group!"):
        manage_type_data.validate_add_action(data_store)

def test_validate_add_action_already_alias(data_store, manage_type_data):
    manage_type_data.unit_type = "m"
    with pytest.raises(ValueError, match="'m' is already being used as an alias in 'length' group"):
        manage_type_data.validate_add_action(data_store)

def test_validate_remove_action(data_store, manage_type_data):
    manage_type_data.unit_type = "mile"
    manage_type_data.validate_remove_action(data_store)

def test_validate_remove_action_empty_type(data_store, manage_type_data):
    with pytest.raises(ValueError, match="You can't leave that field empty!"):
        manage_type_data.validate_remove_action(data_store)

def test_validate_type_remove_action_invalid_type(data_store, manage_type_data):
    manage_type_data.unit_type = "invalid"
    with pytest.raises(ValueError, match="'invalid' is not an unit type in 'length' group!"):
        manage_type_data.validate_remove_action(data_store)

def test_validate_remove_action_already_base(data_store, manage_type_data):
    manage_type_data.unit_type = data_store.base_units["length"]
    with pytest.raises(ValueError, match= "Cannot remove base unit!"):
        manage_type_data.validate_remove_action(data_store)

def test_validate_value(manage_type_data):
    manage_type_data.value = "10"
    manage_type_data.validate_value()
    assert manage_type_data.value == 10.0

def test_validate_value_empty(manage_type_data):
    with pytest.raises(ValueError, match="'value' cannot be empty!"):
        manage_type_data.validate_value()

def test_validate_value_invalid(manage_type_data):
    manage_type_data.value = "invalid"
    with pytest.raises(ValueError, match="Invalid conversion factor!"):
        manage_type_data.validate_value()

def test_validate_factor(manage_type_data):
    manage_type_data.factor = "10"
    manage_type_data.validate_factor()
    assert manage_type_data.factor == 10.0

def test_validate_factor_empty(manage_type_data):
    with pytest.raises(ValueError, match="'factor' cannot be empty!"):
        manage_type_data.validate_factor()

def test_validate_factor_invalid(manage_type_data):
    manage_type_data.factor = "invalid"
    with pytest.raises(ValueError, match="Invalid conversion factor!"):
        manage_type_data.validate_factor()

def test_validate_factor_negative(manage_type_data):
    manage_type_data.factor = "-10"
    with pytest.raises(ValueError, match="Conversion factor must be positive!"):
        manage_type_data.validate_factor()

def test_validate_offset(manage_type_data):
    manage_type_data.offset = "10"
    manage_type_data.validate_offset()
    assert manage_type_data.offset == 10.0

def test_validate_offset_empty(manage_type_data):
    with pytest.raises(ValueError, match="'offset' cannot be empty!"):
        manage_type_data.validate_offset()

def test_validate_offset_invalid(manage_type_data):
    manage_type_data.offset = "invalid"
    with pytest.raises(ValueError, match="Invalid conversion offset!"):
        manage_type_data.validate_offset()

def test_validate_for_manage_type_add_(data_store, manage_type_data):
    manage_type_data.action = "add"
    manage_type_data.unit_type = "new_type"
    manage_type_data.value = "2"
    manage_type_data.validate_for_manage_type(data_store)
    assert manage_type_data.value == 2.0

def test_validate_for_manage_type_add_temperature(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.action = "add"
    manage_type_data.unit_type = "new_type"
    manage_type_data.factor = "2"
    manage_type_data.offset = "1"
    manage_type_data.validate_for_manage_type(data_store)
    assert manage_type_data.factor == 2.0
    assert manage_type_data.offset == 1.0

def test_validate_for_manage_type_remove(data_store, manage_type_data):
    manage_type_data.action = "remove"
    manage_type_data.unit_type = "mile"
    manage_type_data.validate_for_manage_type(data_store)

def test_validate_for_manage_type_invalid_group(data_store, manage_type_data):
    manage_type_data.unit_group = "invalid"
    manage_type_data.action = "add"
    manage_type_data.unit_type = "new_type"
    manage_type_data.value = "2"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        manage_type_data.validate_for_manage_type(data_store)

def test_validate_for_manage_type_invalid_action(data_store, manage_type_data):
    manage_type_data.action = "invalid"
    manage_type_data.unit_type = "mile"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_type_data.validate_for_manage_type(data_store)

def test_validate_for_manage_type_add_empty_type(data_store, manage_type_data):
    manage_type_data.action = "add"
    manage_type_data.unit_type = ""
    manage_type_data.value = "2"
    with pytest.raises(ValueError, match="You can't leave that field empty!"):
        manage_type_data.validate_for_manage_type(data_store)

def test_validate_for_manage_type_add_empty_value(data_store, manage_type_data):
    manage_type_data.action = "add"
    manage_type_data.unit_type = "new_type"
    manage_type_data.value = ""
    with pytest.raises(ValueError, match="'value' cannot be empty!"):
        manage_type_data.validate_for_manage_type(data_store)

def test_validate_for_manage_type_remove_empty_type(data_store, manage_type_data):
    manage_type_data.action = "remove"
    manage_type_data.unit_type = ""
    with pytest.raises(ValueError, match="You can't leave that field empty!"):
        manage_type_data.validate_for_manage_type(data_store)

def test_validate_for_manage_type_negative_factor(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.action = "add"
    manage_type_data.unit_type = "new_type"
    manage_type_data.factor = "-2"
    with pytest.raises(ValueError, match="Conversion factor must be positive!"):
        manage_type_data.validate_for_manage_type(data_store)


# Test 'AliasesData' class methods
def test_validate_unit_type(data_store, aliases_data):
    aliases_data.unit_type = 'meters'
    aliases_data.validate_unit_type(data_store)

def test_validate_unit_type_empty_type(data_store, aliases_data):
    with pytest.raises(ValueError, match="Unit type cannot be empty!"):
        aliases_data.validate_unit_type(data_store)

def test_validate_aliases_action(aliases_data):
    aliases_data.action = "add"
    aliases_data.validate_action()

def test_validate_aliases_action_empty(aliases_data):
    with pytest.raises(ValueError, match="'action' cannot be empty!"):
        aliases_data.validate_action()

def test_validate_aliases_action_invalid(aliases_data):
    aliases_data.action = "invalid"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        aliases_data.validate_action()

def test_validate_alias_add(data_store, aliases_data):
    aliases_data.action = "add"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "mtr"
    aliases_data.validate_alias(data_store)

def test_validate_alias_remove(data_store, aliases_data):
    aliases_data.action = "remove"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "m"
    aliases_data.validate_alias(data_store)

def test_validate_alias_empty(data_store, aliases_data):
    with pytest.raises(ValueError, match="'alias' cannot be empty!"):
        aliases_data.validate_alias(data_store)

def test_validate_alias_already_alias(data_store, aliases_data):
    aliases_data.action = "add"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "m"
    with pytest.raises(ValueError, match=f"'m' is already being used as an alias in 'length'!"):
        aliases_data.validate_alias(data_store)

def test_validate_alias_already_unit_group(data_store, aliases_data):
    aliases_data.action = "add"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "length"
    with pytest.raises(KeyError, match="'length' is already being used to name an unit group!"):
        aliases_data.validate_alias(data_store)

def test_validate_alias_already_unit_type(data_store, aliases_data):
    aliases_data.action = "add"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "meters"
    with pytest.raises(KeyError, match="'meters' is already being used as an unit type in 'length' group!"):
        aliases_data.validate_alias(data_store)

def test_validate_alias_no_alias_in_group(data_store, aliases_data):
    aliases_data.action = "remove"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "invalid"
    with pytest.raises(ValueError, match="'invalid' is not an alias of 'length' group"):
        aliases_data.validate_alias(data_store)

def test_validate_alias_no_alias_in_type(data_store, aliases_data):
    aliases_data.action = "remove"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "km"
    with pytest.raises(ValueError, match="'km' is not an alias for 'meters'"):
        aliases_data.validate_alias(data_store)

def test_validate_for_aliases_alias(data_store, aliases_data):
    aliases_data.action = "add"
    aliases_data.unit_type = "meters"
    aliases_data.alias = "mtr"
    aliases_data.validate_for_aliases(data_store)    

def test_validate_for_aliases_invalid_type(data_store, aliases_data):
    aliases_data.action = "add"
    aliases_data.unit_type = "invalid"
    aliases_data.alias = "m"
    with pytest.raises(KeyError, match="'invalid' is not a valid unit type for 'length' group!"):
        aliases_data.validate_for_aliases(data_store)


# Test 'ChangeBaseData' class methods
def test_validate_for_change_base(data_store, change_base_data, new_base_unit=None):
    change_base_data.new_base_unit = "mile"
    change_base_data.validate_for_change_base(data_store)

def test_validate_for_change_base_empty_type(data_store, change_base_data, new_base_unit=None):
    with pytest.raises(ValueError, match="Unit type cannot be empty!"):
        change_base_data.validate_for_change_base(data_store)

def test_validate_for_change_base_wrong_group(data_store, change_base_data, new_base_unit=None):
    change_base_data.new_base_unit = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not an unit type for 'length' group"):
        change_base_data.validate_for_change_base(data_store)

def test_validate_for_change_base_already_base(data_store, change_base_data, new_base_unit=None):
    change_base_data.new_base_unit = data_store.base_units["length"]
    with pytest.raises(ValueError, match=f"'{change_base_data.new_base_unit}' is already the current base unit for 'length' group"):
        change_base_data.validate_for_change_base(data_store)


# Test 'validate_for_history' function
def test_validate_for_history_empty(data_store):
    data_store.conversion_log = []
    with pytest.raises(ValueError, match="Conversion history is empty!"):
        validate_for_history(data_store, limit=10)

def test_validate_for_history_invalid_limit(data_store):
    with pytest.raises(ValueError, match="'limit' must be a number!"):
        validate_for_history(data_store, limit="invalid")

def test_validate_for_history_negative_limit(data_store):
    with pytest.raises(ValueError, match="'limit' must be a positive number!"):
        validate_for_history(data_store, limit=-10)


# Test 'validate_args_number' function
def test_validate_args_number():
    validate_args_number(command="test")

def test_validate_args_number_args():
    with pytest.raises(TypeError, match="Too many positional arguments for 'command' command!"):
        validate_args_number("extra", command="command")

def test_validate_args_number_kwargs():
    with pytest.raises(TypeError, match="Unexpected keyword argument for 'command' command!"):
        validate_args_number(command="command", extra="extra")