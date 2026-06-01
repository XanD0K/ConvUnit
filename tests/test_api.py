import pytest

from unittest.mock import patch

from src.unit_converter.api import Converter


# Setup Converter to be used on all tests
@pytest.fixture
def converter():
    with patch("project.save_data") as mocked_save_data:
        mocked_save_data.return_value = None
        yield Converter()


# Test 'groups' action
def test_groups(converter):
    assert converter.groups() == "Groups: length, time, mass, temperature, volume, area, speed"

def test_groups_alias(converter):
        assert converter.g() == "Groups: length, time, mass, temperature, volume, area, speed"


# Test 'history' action
def test_history(converter):
    converter.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    result = converter.history()
    assert "50,000.12306 meters = 54,680.7995 yards (Group: length)" in result

def test_history_alias(converter):
    converter.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    result = converter.h()
    assert "50,000.12306 meters = 54,680.7995 yards (Group: length)" in result


def test_history_empty(converter):
    converter.conversion_log = []
    assert converter.history() == "Error: Conversion history is empty!"

def test_history_valid_limit(converter):
    converter.conversion_log = [
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
    result = converter.history(limit=1)
    assert "10.99999 meters = 12.02974 yards (Group: length)" in result
    assert "50,000.12306 meters = 54,680.7995 yards (Group: length)" not in result    

def test_history_invalid_limit(converter):
    converter.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    assert converter.history(limit="invalid") == "Error: 'limit' must be a number!"

def test_history_negative_limit(converter):
    converter.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    assert converter.history(limit=-1) == "Error: 'limit' must be a positive number!"

def test_history_extra_args(converter):
    converter.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    assert converter.history(1, "extra") == "Error: Too many positional arguments for 'history' command!"

def test_history_extra_kwargs(converter):
    converter.conversion_log = [
        {
            "date": "2025-09-20T18:39:27.743896",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "yards",
            "amount": 50000.123059,
            "result": 54680.799495844265
        }
    ]
    assert converter.history(limit=1, extra="extra") == "Error: Unexpected keyword argument for 'history' command!"


# Test 'types' action
def test_types(converter):
    assert converter.types("length") == "'length' units: meters ('m', 'meter', 'metre', 'metres'), centimeters ('cm', 'centimeter', 'centimetre', 'centimetres'), millimeters ('mm', 'millimeter', 'millimetre', 'millimetres'), kilometers ('km', 'kilometer', 'kilometre', 'kilometres'), feet ('ft', 'foot'), inches ('in', 'inch'), yards ('yd', 'yds', 'yard'), miles ('mi', 'mile'), nautical_miles ('nmi', 'nm', 'nautical_mile')"

def test_types_alias(converter):
    assert converter.t("length") == "'length' units: meters ('m', 'meter', 'metre', 'metres'), centimeters ('cm', 'centimeter', 'centimetre', 'centimetres'), millimeters ('mm', 'millimeter', 'millimetre', 'millimetres'), kilometers ('km', 'kilometer', 'kilometre', 'kilometres'), feet ('ft', 'foot'), inches ('in', 'inch'), yards ('yd', 'yds', 'yard'), miles ('mi', 'mile'), nautical_miles ('nmi', 'nm', 'nautical_mile')"

def test_types_invalid_group(converter):
    assert converter.types("invalid") == "Error: 'invalid' is not a valid group!"

def test_types_extra_args(converter):
    assert converter.types("length", "extra") == "Error: Too many positional arguments for 'types' command!"

def test_types_extra_kwargs(converter):
    assert converter.types(unit_group="length", extra="extra") == "Error: Unexpected keyword argument for 'types' command!"


# Test 'convert' action
def test_convert(converter):
    assert converter.convert("length", "m yd 10") == 10.936132983377078

def test_convert_alias(converter):
    assert converter.c("length", "m yd 10") == 10.936132983377078

def test_convert_print_message(converter):
    assert converter.convert("length", "m yd 10", print_message=True) == "10.0 meters = 10.93613 yards"

def test_convert_time(converter):
    assert converter.convert("time", "JAN DEC days") == 365.0

def test_convert_invalid_group(converter):
    assert converter.convert("invalid", "m yd 10") == "Error: 'invalid' is not a valid group!"

def test_convert_invalid_from_type(converter):
    assert converter.convert("length", "invalid yd 10") == "Error: Invalid unit type!"
    
def test_convert_invalid_to_type(converter):
    assert converter.convert("length", "m invalid 10") == "Error: Invalid unit type!"

def test_convert_invalid_amount(converter):
    assert converter.convert("length", "m yd invalid") == "Error: Invalid amount!"

def test_convert_invalid_format(converter):
    assert converter.convert("length", "meters 10") == "Error: Incorrect format! Usage: <unit_group> <from_type> <to_type> <amount>"

def test_convert_extra_args(converter):
    assert converter.convert("length", "m yd 10", "extra") == "Error: Too many positional arguments for 'convert' command!"

def test_convert_extra_kwargs(converter):
    assert converter.convert(unit_group="length", user_input="m yd 10", extra="extra") == "Error: Unexpected keyword argument for 'convert' command!"


# Test 'manage-group' action
def test_manage_group_add(converter):
    assert converter.manage_group("new_group", "add new_base_unit") == "You've just created a 'new_group' group, with 'new_base_unit' as its base unit!"

def test_manage_group_remove(converter):
    assert converter.manage_group("length", "remove") == "Group 'length' successfully removed!"

def test_manage_group_alias_add(converter):
    assert converter.mg("new_group", "add new_base_unit") == "You've just created a 'new_group' group, with 'new_base_unit' as its base unit!"

def test_manage_group_alias_remove(converter):
    assert converter.mg("length", "remove") == "Group 'length' successfully removed!"

def test_manage_group_add_print_message(converter):
    message = converter.manage_group("new_group", "add new_base_unit", print_message=True)
    assert message == "You've just created a 'new_group' group, with 'new_base_unit' as its base unit!"

def test_manage_group_remove_print_message(converter):
    message = converter.manage_group("length", "remove", print_message=True)
    assert message =="Group 'length' successfully removed!"

def test_manage_group_add_already_group(converter):
    assert converter.manage_group("length", "add new_base_unit") == "Error: 'length' is already an existed group!"

def test_manage_group_add_missing_new_base(converter):
    assert converter.manage_group("new_group", "add") == "Error: 'new_base_unit' cannot be empty"

def test_manage_group_add_already_group_name(converter):
    assert converter.manage_group("new_group", "add length") == "Error: 'length' is already an unit group name!"

def test_manage_group_add_same_name(converter):
    assert converter.manage_group("new_group", "add new_group") == "Error: 'new_base_unit' can't have the same name as 'unit_group'"

def test_manage_group_remove_invalid_group(converter):
    assert converter.manage_group("invalid", "remove") == "Error: 'invalid' is not a valid group!"

def test_manage_group_remove_included_new_base(converter):
    assert converter.manage_group("length", "remove new_base_unit") == "Error: Incorrect usage when removing a group! Usage: <unit_group> remove"

def test_manage_group_invalid_len(converter):
    assert converter.manage_group("new_group", "add new_base_unit extra") == "Error: Incorrect format! Usage: <unit_group> <action> [new_base_unit]"

def test_manage_group_invalid_action(converter):
    assert converter.manage_group("new_group", "invalid new_base_unit") == "Error: Invalid action: 'invalid'"

def test_manage_group_extra_args(converter):
    assert converter.manage_group("new_group", "add new_base_unit", "extra") == "Error: Too many positional arguments for 'manage-group' command!"

def test_manage_group_extra_kwargs(converter):
    assert converter.manage_group(unit_group="new_group", user_input="add new_base_unit", extra="extra") == "Error: Unexpected keyword argument for 'manage-group' command!"


# Test 'manage-type' action
def test_manage_type_add(converter):
    assert converter.manage_type("length", "add new_type 10") == "A new unit type was added on 'length' group: new_type = 10.0"

def test_manage_type_remove(converter):
    converter.units["length"]["miles"] = 1609.344
    converter.base_units["length"] = "meters"
    assert converter.manage_type("length", "remove miles") == "'miles' was removed from 'length'"

def test_manage_type_add_alias(converter):
    assert converter.mt("length", "add new_type 10") == "A new unit type was added on 'length' group: new_type = 10.0"

def test_manage_type_remove_alias(converter):
    converter.units["length"]["miles"] = 1609.344
    converter.base_units["length"] = "meters"
    assert converter.mt("length", "remove miles") == "'miles' was removed from 'length'"

def test_manage_type_add_print_message(converter):
    message = converter.manage_type("length", "add new_type 10", print_message=True)
    assert message == "A new unit type was added on 'length' group: new_type = 10.0"

def test_manage_type_remove_print_message(converter):
    message = converter.manage_type("length", "remove miles", print_message=True)
    assert message == "'miles' was removed from 'length'"

def test_manage_type_add_temperature(converter):
    assert converter.manage_type("temperature", "add new_type 1 1") == "A new unit type was added on 'temperature' group: new_type = [1.0, 1.0]"

def test_manage_type_invalid_len(converter):
    assert converter.manage_type("length", "add new_type 10 extra") == "Error: Incorrect format! Usage: <unit_group> <unit_type> <action> <value> [factor] [offset]"

def test_manage_type_empty_group(converter):
    assert converter.manage_type("", "add new_type 10") == "Error: Unit group cannot be empty!"

def test_manage_type_invalid_group(converter):
    assert converter.manage_type("invalid", "add new_type 10") == "Error: 'invalid' is not a valid group!"

def test_manage_type_invalid_action(converter):
    assert converter.manage_type("length", "invalid new_type 10") == "Error: Invalid action: 'invalid'"

def test_manage_type_add_already_group(converter):
    assert converter.manage_type("length", "add length 10") == "Error: 'length' is already an unit group name!"

def test_manage_type_add_already_type(converter):
    assert converter.manage_type("length", "add meters 10") == "Error: 'meters' is already an unit type in 'length' group!"

def test_manage_type_add_already_alias(converter):
    assert converter.manage_type("length", "add m 10") == "Error: 'm' is already being used as an alias in 'length' group"

def test_manage_type_remove_invalid_type(converter):
    assert converter.manage_type("length", "remove invalid") == "Error: 'invalid' is not an unit type in 'length' group!"

def test_manage_type_remove_base_unit(converter):
    assert converter.manage_type("length", "remove meters") == "Error: Cannot remove base unit!"

def test_manage_type_remove_extra_args(converter):
    assert converter.manage_type("length", "remove mile 10") == "Error: Incorrect usage when removing a type! Usage: <unit_group> remove <unit_type>"

def test_manage_type_remove_temperature_extra_args(converter):
    assert converter.manage_type("temperature", "remove kelvin 10") == "Error: Incorrect usage when removing a type! Usage: <unit_group> remove <unit_type>"

def test_manage_type_empty_value(converter):
    assert converter.manage_type("length", "add new_type") == "Error: 'value' cannot be empty!"

def test_manage_type_invalid_value(converter):
    assert converter.manage_type("length", "add new_type invalid") == "Error: Invalid conversion factor!"

def test_manage_type_temperature_empty_factor(converter):
    assert converter.manage_type("temperature", "add new_type") == "Error: 'factor' cannot be empty!"

def test_manage_type_temperature_invalid_factor(converter):
    assert converter.manage_type("temperature", "add new_type invalid 1") == "Error: Invalid conversion factor!"

def test_manage_type_temperature_negative_factor(converter):
    assert converter.manage_type("temperature", "add new_type -1 1") == "Error: Conversion factor must be positive!"

def test_manage_type_temperature_empty_offset(converter):
    assert converter.manage_type("temperature", "add new_type 1.0") == "Error: 'offset' cannot be empty!"

def test_manage_type_temperature_invalid_offset(converter):
    assert converter.manage_type("temperature", "add new_type 1 invalid") == "Error: Invalid conversion offset!"

def test_manage_type_extra_args(converter):
    assert converter.manage_type("length", "add new_type 10", "extra") == "Error: Too many positional arguments for 'manage-type' command!"

def test_manage_type_extra_kwargs(converter):
    assert converter.manage_type(unit_group="length", user_input="add new_type 10", extra="extra") == "Error: Unexpected keyword argument for 'manage-type' command!"


# Test 'aliases' action
def test_aliases_add(converter):
    assert converter.aliases("length", "add meters mtr") == "Alias successfully added! New alias for 'meters': 'mtr'"

def test_aliases_add_alias(converter):
    assert converter.a("length", "add meters mtr") == "Alias successfully added! New alias for 'meters': 'mtr'"

def test_aliases_remove(converter):
    converter.unit_aliases["length"]["mtr"] = "meters"
    assert converter.aliases("length", "remove meters mtr") == "'mtr' successfully removed from 'meters'!"

def test_aliases_remove_alias(converter):
    converter.unit_aliases["length"]["mtr"] = "meters"
    assert converter.a("length", "remove meters mtr") == "'mtr' successfully removed from 'meters'!"

def test_aliases_add_print_message(converter):
    message = converter.aliases("length", "add meters mtr", print_message=True) 
    assert message == "Alias successfully added! New alias for 'meters': 'mtr'"

def test_aliases_remove_print_message(converter):
    converter.unit_aliases["length"]["mtr"] = "meters"
    message = converter.aliases("length", "remove meters mtr", print_message=True) 
    assert message == "'mtr' successfully removed from 'meters'!"

def test_aliases_invalid_format(converter):
    assert converter.aliases("length", "add") == "Error: Incorrect format! Usage: <unit_group> <unit_type> <alias> <action>"

def test_aliases_invalid_group(converter):
    assert converter.aliases("invalid", "remove meters mtr") == "Error: 'invalid' is not a valid group!"

def test_aliases_invalid_action(converter):
    assert converter.aliases("length", "invalid meters mtr") == "Error: Invalid action: 'invalid'"

def test_aliases_invalid_type(converter):
    assert converter.aliases("length", "add invalid mtr") == "Error: 'invalid' is not a valid unit type for 'length' group!"

def test_aliases_add_already_alias(converter):
    assert converter.aliases("length", "add meters yd") == "Error: 'yd' is already being used as an alias in 'length'!"

def test_aliases_add_already_group(converter):
    assert converter.aliases("length", "add meters length") == "Error: 'length' is already being used to name an unit group!"

def test_aliases_add_already_type(converter):
    assert converter.aliases("length", "add meters yards") == "Error: 'yards' is already being used as an unit type in 'length' group!"

def test_aliases_remove_invalid_alias_group(converter):
    assert converter.aliases("length", "remove meters invalid") == "Error: 'invalid' is not an alias of 'length' group"

def test_aliases_remove_invalid_alias_type(converter):
    assert converter.aliases("length", "remove meters yd") == "Error: 'yd' is not an alias for 'meters'"

def test_aliases_extra_args(converter):
    assert converter.aliases("length", "add meters yard", "extra") == "Error: Too many positional arguments for 'aliases' command!"

def test_aliases_extra_kwargs(converter):
    assert converter.aliases(unit_group="length", user_input="add meters yard", extra="extra") == "Error: Unexpected keyword argument for 'aliases' command!"


# Test 'change-base' action
def test_change_base(converter):
    converter.base_units["length"] = "meters"
    assert converter.change_base("length", "yards") == "You've just changed the base unit from 'length' group, to 'yards'!"

def test_change_base_alias(converter):
    converter.base_units["length"] = "meters"
    assert converter.cb("length", "yd") == "You've just changed the base unit from 'length' group, to 'yards'!"

def test_change_base_print_message(converter):
    converter.base_units["length"] = "meters"
    message = converter.change_base("length", "yards", print_message=True) 
    assert message == "You've just changed the base unit from 'length' group, to 'yards'!"
    
def test_change_base_invalid_format(converter):
    assert converter.change_base("length", " ") == "Error: Incorrec format! Usage: <unit_group> <new_base_unit>"

def test_change_base_invalid_group(converter):
    assert converter.change_base("invalid", "new_base_unit") == "Error: 'invalid' is not a valid group!"

def test_change_base_invalid_alias(converter):
    assert converter.change_base("length", "invalid") == "Error: 'invalid' is not an unit type for 'length' group"

def test_change_base_already_base(converter):
    converter.base_units["length"] = "meters"
    assert converter.change_base("length", "meters") == "Error: 'meters' is already the current base unit for 'length' group"

def test_change_base_extra_args(converter):
    converter.base_units["length"] = "meters"
    assert converter.change_base("length", "yards", "extra") == "Error: Too many positional arguments for 'change-base' command!"

def test_change_base_extra_kwargs(converter):
    converter.base_units["length"] = "meters"
    assert converter.change_base(unit_group="length", user_input="yards", extra="extra") == "Error: Unexpected keyword argument for 'change-base' command!"