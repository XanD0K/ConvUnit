import pytest

from unittest.mock import patch

from project import get_action, print_groups, print_history, print_types, conversion_logic, converter, converter_temp, converter_time, converter_time_2args, converter_time_3args, manage_group, manage_type, add_temp_type, manage_aliases, change_base_unit
from src.unit_converter.data_manager import load_data
from src.unit_converter.data_models import DataStore, ConversionData, ManageGroupData, ManageTypeData, AliasesData, ChangeBaseData


# Setup DataStore to be used on all tests that require DataStore
@pytest.fixture
def data_store():
    return DataStore(*load_data())

# Setup fixtures to be used on their respective class tests
@pytest.fixture
def conversion_data():
    with patch("project.add_to_log") as mocked_add_to_log:
        mocked_add_to_log.return_value = None
        yield ConversionData(unit_group="length")

@pytest.fixture
def manage_group_data():
    with patch("project.save_data") as mocked_save_data:
        mocked_save_data.return_value = None
        yield ManageGroupData(unit_group="length")

@pytest.fixture
def manage_type_data():
    with patch("project.save_data") as mocked_save_data:
        mocked_save_data.return_value = None
        yield ManageTypeData(unit_group="length")

@pytest.fixture
def aliases_data():
    with patch("project.save_data") as mocked_save_data:
        mocked_save_data.return_value = None
        yield AliasesData(unit_group="length")

@pytest.fixture
def change_base_data():
    with patch("project.save_data") as mocked_save_data:
        with patch("project.refactor_value") as mocked_refactor_value:
            mocked_save_data.return_value = None
            mocked_refactor_value.return_value = None
            yield ChangeBaseData(unit_group="length", new_base_unit=None)


# TODO: Test 'get_action' function


# Test 'print_groups' function
def test_print_groups(data_store):
    assert print_groups(data_store) == "Groups: length, time, mass, temperature, volume, area, speed"


# Test 'print_history' function
def test_print_history(data_store):
    data_store.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    result = print_history(data_store)
    assert "50,000.12306 meters = 54,680.7995 yards (Group: length)" in result

def test_print_history_time(data_store):
    data_store.conversion_log = [
        {
            "date": "2025-09-23T09:39:56.914011",
            "unit_group": "time",
            "from_time": "minutes",
            "to_time": "seconds",
            "factor_time": 1.0,
            "result": 60.0
        },
        {
            "date": "2025-09-23T09:40:11.681262",
            "unit_group": "time",
            "from_time": "jan",
            "to_time": "dec",
            "factor_time": "days",
            "result": 365.0
        }
    ]
    result = print_history(data_store)
    assert "1.0 minutes = 60.0 seconds (Group: time)" in result
    assert "365.0 days between jan dec (Group: time)" in result

def test_print_history_empty(data_store):
    data_store.conversion_log = []
    assert print_history(data_store) == "Error: Conversion history is empty!"

def test_print_history_valid_limit(data_store):
    data_store.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        },
        {
            "date": "2025-09-20T18:43:48.752476",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 10.99999,
            "result": 12.029735345581804
        }
    ]
    result = print_history(data_store, limit=1)
    assert "10.99999 meters = 12.02974 yards (Group: length)" in result
    assert "50,000.12306 meters = 54,680.7995 yards (Group: length)" not in result

def test_print_history_invalid_limit(data_store):
    data_store.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    assert print_history(data_store, limit="invalid") == "Error: 'limit' must be a number!"

def test_print_history_negative_limit(data_store):
    data_store.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    assert print_history(data_store, limit=-1) == "Error: 'limit' must be a positive number!"


# Test 'print_types' function
def test_print_types(data_store):
    assert print_types(data_store, "length") == "'length' units: meters ('m', 'meter', 'metre', 'metres'), centimeters ('cm', 'centimeter', 'centimetre', 'centimetres'), millimeters ('mm', 'millimeter', 'millimetre', 'millimetres'), kilometers ('km', 'kilometer', 'kilometre', 'kilometres'), feet ('ft', 'foot'), inches ('in', 'inch'), yards ('yd', 'yds', 'yard'), miles ('mi', 'mile'), nautical_miles ('nmi', 'nm', 'nautical_mile')"

def test_types_print_invalid_group(data_store):
    assert print_types(data_store, "invalid") == "Error: 'invalid' is not a valid group!"

def test_print_types_get_input(data_store):
    with patch("project.get_unit_group", return_value="length"):
        assert print_types(data_store) == "'length' units: meters ('m', 'meter', 'metre', 'metres'), centimeters ('cm', 'centimeter', 'centimetre', 'centimetres'), millimeters ('mm', 'millimeter', 'millimetre', 'millimetres'), kilometers ('km', 'kilometer', 'kilometre', 'kilometres'), feet ('ft', 'foot'), inches ('in', 'inch'), yards ('yd', 'yds', 'yard'), miles ('mi', 'mile'), nautical_miles ('nmi', 'nm', 'nautical_mile')"

def test_print_types_get_input_empty_group(data_store):
    with patch("project.get_unit_group", return_value=""):
        assert print_types(data_store) == "Error: Unit group cannot be empty!"

def test_print_types_get_input_invalid_group(data_store):
    with patch("project.get_unit_group", return_value="invalid"):
        assert print_types(data_store) == "Error: 'invalid' is not a valid group!"


# Test 'conversion_logic' function
def test_conversion_logic(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = "10"
    assert conversion_logic(data_store, conversion_data) == "10.0 meters = 10.93613 yards"

def test_conversion_logic_empty_group(data_store, conversion_data):
    conversion_data.unit_group = None
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = "10"
    with pytest.raises(ValueError, match="Unit group cannot be empty!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_invalid_group(data_store, conversion_data):
    conversion_data.unit_group = "invalid"
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = "10"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_empty_from_type(data_store, conversion_data):
    conversion_data.to_type = "yards"
    conversion_data.amount = "10"
    with pytest.raises(ValueError, match="'unit_type' cannot be empty!"):
        conversion_logic(data_store, conversion_data)   

def test_conversion_logic_invalid_from_type(data_store, conversion_data):
    conversion_data.from_type = "invalid"
    conversion_data.to_type = "yards"
    conversion_data.amount = "10"
    with pytest.raises(KeyError, match="Invalid unit type!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_empty_to_type(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.amount = "10"
    with pytest.raises(ValueError, match="'unit_type' cannot be empty!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_invalid_to_type(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "invalid"
    conversion_data.amount = "10"
    with pytest.raises(KeyError, match="Invalid unit type!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_empty_amount(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    with pytest.raises(ValueError, match="'amount' cannot be empty"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_invalid_amount(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = "invalid"
    with pytest.raises(ValueError, match="Invalid amount!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_temperature_negative_amount(data_store, conversion_data):
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "kelvin"
    conversion_data.to_type = "celsius"
    conversion_data.amount = "-10"
    with pytest.raises(ValueError, match="Kelvin temperature cannot be negative!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds 1"
    assert conversion_logic(data_store, conversion_data) == "1.0 minutes = 60.0 seconds"

def test_conversion_logic_empty_time_input(data_store, conversion_data):
    conversion_data.unit_group = "time"
    with pytest.raises(ValueError, match="Time conversion can't be empty! Enter an expression!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_invalid_time_input(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "invalid"
    with pytest.raises(ValueError, match="Incorrect format for time conversion!"):
        conversion_logic(data_store, conversion_data)
    
def test_conversion_logic_invalid_from_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "invalid seconds 10"
    conversion_data.from_time = "invalid"
    conversion_data.to_time = "seconds"
    conversion_data.factor_time = "10"
    with pytest.raises(ValueError, match="Invalid 'from_time': 'invalid'"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_invalid_to_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes invalid 10"
    conversion_data.from_time = "minutes"
    conversion_data.to_time = "invalid"
    conversion_data.factor_time = "10"
    with pytest.raises(ValueError, match="Invalid 'to_time'"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_invalid_factor_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds invalid"
    with pytest.raises(KeyError, match="Factor time 'invalid' not found in 'time' group!"):
        conversion_logic(data_store, conversion_data)

def test_conversion_logic_get_input(data_store):
    with patch("project.get_unit_group", return_value="length"):
        with patch("project.get_converter_units", return_value=("meters", "yards")):
            with patch("project.get_amount", return_value=10.0):
                assert conversion_logic(data_store) == "10.0 meters = 10.93613 yards"

def test_conversion_logic_get_input_time(data_store):
    with patch("project.get_unit_group", return_value="time"):
        with patch("project.get_users_input", side_effect=["minutes seconds 1"]):
            assert conversion_logic(data_store) == "1.0 minutes = 60.0 seconds"


# Test 'converter' function
def test_converter(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = 10.0
    assert converter(data_store, conversion_data) == 10.936132983377078

def test_converter_temperature(data_store, conversion_data):
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "celsius"
    conversion_data.to_type = "kelvin"
    conversion_data.amount = 10.0
    assert converter(data_store, conversion_data) == 283.15

def test_converter_zero_division(data_store, conversion_data):
    data_store.units["length"]["yards"] = 0
    conversion_data.from_type = "meters"
    conversion_data.to_type = "yards"
    conversion_data.amount = 10.0    
    with pytest.raises(ZeroDivisionError, match="Can't Divide by zero"):
        converter(data_store, conversion_data)


# Test 'converter_temp' function
def test_converter_temp(data_store, conversion_data):
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "celsius"
    conversion_data.to_type = "kelvin"
    conversion_data.amount = 10.0
    assert converter_temp(data_store, conversion_data) == 283.15

def test_converter_temp_zero_division(data_store, conversion_data):
    data_store.units["temperature"]["celsius"] = [0.0, 273.15]
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "celsius"
    conversion_data.to_type = "kelvin"
    conversion_data.amount = 10.0    
    with pytest.raises(ZeroDivisionError, match="Can't Divide by zero"):
        converter_temp(data_store, conversion_data)


# Test 'converter_time' function
def test_converter_time_len_higher(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "1 years 1 month 1 days days"
    assert converter_time(data_store, conversion_data) == "1.0 years 1.0 months 1.0 days = 396.25 days"

def test_converter_time_invalid_format(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds 1 seconds"
    with pytest.raises(ValueError, match="Invalid format for date and time conversion!"):
        converter_time(data_store, conversion_data)


# Test 'converter_time_3args' function
def test_converter_time_3args_units(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "minutes"
    conversion_data.to_time = "seconds"
    conversion_data.factor_time = 1
    assert converter_time_3args(data_store, conversion_data) == "1.0 minutes = 60.0 seconds"

def test_converter_time_3args_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "17h:28m:36s"
    conversion_data.to_time = "04h:15m:22s"
    conversion_data.factor_time = "seconds"
    assert converter_time_3args(data_store, conversion_data) == "There are 38,806.0 seconds between 17h:28m:36s and 04h:15m:22s"

def test_converter_time_3args_months(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "jan"
    conversion_data.to_time = "dec"
    conversion_data.factor_time = "days"
    assert converter_time_3args(data_store, conversion_data) == "Between January and December there are 365.0 days"

def test_converter_time_3args_date(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "2019-11-04"
    conversion_data.to_time = "2056-04-28"
    conversion_data.factor_time = "days"
    assert converter_time_3args(data_store, conversion_data) == "Between 2019-11-04 and 2056-04-28 there are 13,326.0 days"


# Test 'converter_time_2args' function
def test_converter_time_2args_time(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "17h:28m:36s"
    conversion_data.factor_time = "seconds"
    assert converter_time_2args(data_store, conversion_data) == "There are 62,916.0 seconds in 17h:28m:36s"

def test_converter_time_2args_month(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "january"
    conversion_data.factor_time = "days"
    assert converter_time_2args(data_store, conversion_data) == "There are 31.0 days in January"

def test_converter_time_2args_date(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.from_time = "2019-11-04"
    conversion_data.factor_time = "days"
    assert converter_time_2args(data_store, conversion_data) == "There are 737,763.41312 days in 2019 years, 11 months, 4 days"


# Test 'manage_group' function
def test_manage_group_add(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "add"
    manage_group_data.new_base_unit = "new_base_unit"
    assert manage_group(data_store, manage_group_data) == "You've just created a 'new_group' group, with 'new_base_unit' as its base unit!"

def test_manage_group_remove(data_store, manage_group_data):
    manage_group_data.unit_group = "length"
    manage_group_data.action = "remove"
    assert manage_group(data_store, manage_group_data) == "Group 'length' successfully removed!"

def test_manage_group_empty_action(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    with pytest.raises(ValueError, match="'action' cannot be empty!"):
        manage_group(data_store, manage_group_data)

def test_manage_group_invalid_action(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "invalid"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_group(data_store, manage_group_data)

def test_manage_group_already_group(data_store, manage_group_data):
    manage_group_data.unit_group = "length"
    manage_group_data.action = "add"
    with pytest.raises(KeyError, match="'length' is already an existed group!"):
        manage_group(data_store, manage_group_data)

def test_manage_group_invalid_group(data_store, manage_group_data):
    manage_group_data.unit_group = "invalid"
    manage_group_data.action = "remove"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        manage_group(data_store, manage_group_data)

def test_manage_group_invalid_remove_format(data_store, manage_group_data):
    manage_group_data.unit_group = "length"
    manage_group_data.action = "remove"
    manage_group_data.new_base_unit = "invalid"
    with pytest.raises(ValueError, match="Incorrect usage when removing a group! Usage: <unit_group> remove"):
        manage_group(data_store, manage_group_data)

def test_manage_group_empty_new_base(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "add"
    with pytest.raises(ValueError, match="'new_base_unit' cannot be empty"):
        manage_group(data_store, manage_group_data)

def test_manage_group_invalid_new_base(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "add"
    manage_group_data.new_base_unit = "length"
    with pytest.raises(KeyError, match="'length' is already an unit group name!"):
        manage_group(data_store, manage_group_data)

def test_manage_group_empty_invalid_new_base(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data.action = "add"
    manage_group_data.new_base_unit = "new_group"
    with pytest.raises(ValueError, match="'new_base_unit' can't have the same name as 'unit_group'"):
        manage_group(data_store, manage_group_data)

def test_manage_group_get_input_add(data_store):
    with patch("project.save_data"):
        with patch("project.get_users_input", side_effect=["add", "new_group", "new_base_unit"]):
            assert manage_group(data_store) == "You've just created a 'new_group' group, with 'new_base_unit' as its base unit!"

def test_manage_group_get_input_remove(data_store):
    with patch("project.save_data"):
        with patch("project.get_users_input", return_value="remove"):
            with patch("project.get_unit_group", return_value="length"):            
                assert manage_group(data_store) == "Group 'length' successfully removed!"

# Test 'manage_type' function
def test_manage_type_add(data_store, manage_type_data):
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.value = "10"
    assert manage_type(data_store, manage_type_data) == "A new unit type was added on 'length' group: new_type = 10.0"

def test_manage_type_remove(data_store, manage_type_data):
    data_store.units["length"]["miles"] = 1609.344
    manage_type_data.unit_type = "miles"
    manage_type_data.action = "remove"
    assert manage_type(data_store, manage_type_data) == "'miles' was removed from 'length'"

def test_manage_type_add_invalid_group(data_store, manage_type_data):
    manage_type_data.unit_group = "invalid"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.value = "10"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        manage_type(data_store, manage_type_data)
        
def test_manage_type_invalid_action(data_store, manage_type_data):
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "invalid"
    manage_type_data.value = "10"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_already_group(data_store, manage_type_data):
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "length"
    manage_type_data.action = "add"
    manage_type_data.value = "10"
    with pytest.raises(KeyError, match="'length' is already an unit group name!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_already_type(data_store, manage_type_data):
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "meters"
    manage_type_data.action = "add"
    manage_type_data.value = "10"
    with pytest.raises(ValueError, match="'meters' is already an unit type in 'length' group!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_already_alias(data_store, manage_type_data):
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "m"
    manage_type_data.action = "add"
    manage_type_data.value = "10"
    with pytest.raises(ValueError, match="'m' is already being used as an alias in 'length' group"):
        manage_type(data_store, manage_type_data)

def test_manage_type_remove_invalid_type(data_store, manage_type_data):
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "invalid"
    manage_type_data.action = "remove"
    with pytest.raises(ValueError, match="'invalid' is not an unit type in 'length' group!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_remove_base_unit(data_store, manage_type_data):
    data_store.base_units["length"] = "meters"
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "meters"
    manage_type_data.action = "remove"
    with pytest.raises(ValueError, match="Cannot remove base unit!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_remove_invalid_format(data_store, manage_type_data):
    data_store.base_units["length"] = "meters"
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "mile"
    manage_type_data.action = "remove"
    manage_type_data.value = "10"
    with pytest.raises(ValueError, match="Incorrect usage when removing a type! Usage: <unit_group> remove <unit_type>"):
        manage_type(data_store, manage_type_data)

def test_manage_type_empty_value(data_store, manage_type_data):
    data_store.base_units["length"] = "meters"
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    with pytest.raises(ValueError, match="'value' cannot be empty!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_invalid_value(data_store, manage_type_data):
    data_store.base_units["length"] = "meters"
    manage_type_data.unit_group = "length"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.value = "invalid"
    with pytest.raises(ValueError, match="Invalid conversion factor!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_get_input_add(data_store):
    with patch("project.save_data"):
        with patch("project.get_unit_group", return_value="length"):
            with patch("project.get_users_input", side_effect=["add", "new_type", "10"]):
                assert manage_type(data_store) == "A new unit type was added on 'length' group: new_type = 10.0"


# Test 'add_temp_type' function
def test_manage_type_add_temperature(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.factor = "1"
    manage_type_data.offset = "0"
    assert manage_type(data_store, manage_type_data) == "A new unit type was added on 'temperature' group: new_type = [1.0, 0.0]"

def test_manage_type_add_temperature_empty_factor(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.offset = "0"
    with pytest.raises(ValueError, match="'factor' cannot be empty!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_temperature_invalid_factor(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.factor = "invalid"
    manage_type_data.offset = "0"
    with pytest.raises(ValueError, match="Invalid conversion factor!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_temperature_negative_factor(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.factor = "-1"
    manage_type_data.offset = "0"
    with pytest.raises(ValueError, match="Conversion factor must be positive!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_temperature_empty_offset(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.factor = "1"
    with pytest.raises(ValueError, match="'offset' cannot be empty!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_add_temperature_invalid_offset(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.unit_type = "new_type"
    manage_type_data.action = "add"
    manage_type_data.factor = "1"
    manage_type_data.offset = "invalid"
    with pytest.raises(ValueError, match="Invalid conversion offset!"):
        manage_type(data_store, manage_type_data)

def test_manage_type_get_input_add_temperature(data_store):
    with patch("project.save_data"):
        with patch("project.get_unit_group", return_value="temperature"):
            with patch("project.get_users_input", side_effect=["add", "new_type", "1", "0"]):
                assert manage_type(data_store) == "A new unit type was added on 'temperature' group: new_type = [1.0, 0.0]"


# Test 'manage_aliases' function
def test_manage_aliases_add(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "add"
    aliases_data.alias = "mtr"
    assert manage_aliases(data_store, aliases_data) == "Alias successfully added! New alias for 'meters': 'mtr'"

def test_manage_aliases_remove(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "remove"
    aliases_data.alias = "m"
    assert manage_aliases(data_store, aliases_data) == "'m' successfully removed from 'meters'!"
    
def test_manage_alias_invalid_group(data_store, aliases_data):
    aliases_data.unit_group = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_invalid_unit_type(data_store, aliases_data):
    aliases_data.unit_type = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not a valid unit type for 'length' group!"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_invalid_action(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "invalid"
    aliases_data.alias = "mtr"
    with pytest.raises(ValueError, match="Invalid action: 'invalid'"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_empty_alias(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "add"
    with pytest.raises(ValueError, match="'alias' cannot be empty!"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_add_invalid_alias(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "add"
    aliases_data.alias = "m"
    with pytest.raises(ValueError, match="'m' is already being used as an alias in 'length'!"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_add_already_group(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "add"
    aliases_data.alias = "length"
    with pytest.raises(KeyError, match="'length' is already being used to name an unit group!"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_add_already_type(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "add"
    aliases_data.alias = "meters"
    with pytest.raises(KeyError, match="'meters' is already being used as an unit type in 'length' group!"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_remove_invalid_group(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "remove"
    aliases_data.alias = "invalid"
    with pytest.raises(ValueError, match="'invalid' is not an alias of 'length' group"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_remove_invalid_type(data_store, aliases_data):
    aliases_data.unit_type = "meters"
    aliases_data.action = "remove"
    aliases_data.alias = "yd"
    with pytest.raises(ValueError, match="'yd' is not an alias for 'meters'"):
        manage_aliases(data_store, aliases_data)

def test_manage_alias_get_input_add(data_store):
    with patch("project.save_data"):
        with patch("project.get_unit_group", return_value="length"):
            with patch("project.get_users_input", side_effect=["meters", "add", "mtr"]):
                assert manage_aliases(data_store) == "Alias successfully added! New alias for 'meters': 'mtr'"

def test_manage_alias_get_input_remove(data_store):
    data_store.unit_aliases["length"]["mtr"] = "meters"
    with patch("project.save_data"):
        with patch("project.get_unit_group", return_value="length"):
            with patch("project.get_users_input", side_effect=["meters", "remove", "mtr"]):
                assert manage_aliases(data_store) == "'mtr' successfully removed from 'meters'!"


# Test 'change_base_unit' function
def test_change_base(data_store, change_base_data):
    change_base_data.new_base_unit = "mile"
    assert change_base_unit(data_store, change_base_data) == "You've just changed the base unit from 'length' group, to 'miles'!"

def test_change_base_invalid_group(data_store, change_base_data):
    change_base_data.unit_group = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not a valid group!"):
        change_base_unit(data_store, change_base_data)

def test_change_base_empty_new_base_unit(data_store, change_base_data):
    with pytest.raises(ValueError, match="Unit type cannot be empty!"):
        change_base_unit(data_store, change_base_data)

def test_change_base_invalid_new_base_unit(data_store, change_base_data):
    change_base_data.new_base_unit = "invalid"
    with pytest.raises(KeyError, match="'invalid' is not an unit type for 'length' group"):
        change_base_unit(data_store, change_base_data)

def test_change_base_already_new_base_unit(data_store, change_base_data):
    data_store.base_units["length"] = "meters"
    change_base_data.new_base_unit = "meters"
    with pytest.raises(ValueError, match="'meters' is already the current base unit for 'length' group"):
        change_base_unit(data_store, change_base_data)

def test_change_base_get_input(data_store):
    with patch("project.save_data"):
        with patch("project.get_unit_group", return_value="length"):
            with patch("project.get_users_input", return_value="miles"):
                assert change_base_unit(data_store) == "You've just changed the base unit from 'length' group, to 'miles'!"