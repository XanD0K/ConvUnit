import pytest

from convunit.data_manager import _load_data
from convunit.data_models import (
    DataStore, ConversionData, ManageGroupData,
    ManageTypeData, AliasesData, ChangeBaseData,
)
from convunit.display import _validate_for_history


@pytest.fixture
def data_store():
    """Returns a DataStore instance with real data."""
    return DataStore(*_load_data())


# ==================== ConversionData Tests ====================
@pytest.fixture
def conversion_data():
    return ConversionData(unit_group="length")


def test_validate_from_type_success(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data._validate_from_type(data_store)
    assert conversion_data.from_type == "meters"


def test_validate_from_type_empty(data_store, conversion_data):
    conversion_data.from_type = ""
    with pytest.raises(Exception):
        conversion_data._validate_from_type(data_store)


def test_validate_to_type_success(data_store, conversion_data):
    conversion_data.to_type = "feet"
    conversion_data._validate_to_type(data_store)
    assert conversion_data.to_type == "feet"


def test_validate_amount_success(conversion_data):
    conversion_data.amount = "10.5"
    conversion_data._validate_amount()
    assert conversion_data.amount == 10.5


def test_validate_amount_negative_kelvin(conversion_data):
    conversion_data.unit_group = "temperature"
    conversion_data.from_type = "kelvin"
    conversion_data.amount = -5
    with pytest.raises(Exception):
        conversion_data._validate_amount()


def test_validate_time_args_2_arguments(data_store, conversion_data):
    conversion_data.unit_group = "time"
    conversion_data.time_input = "minutes seconds 90"
    conversion_data._validate_time_args(data_store)
    assert conversion_data.from_time == "minutes"
    assert conversion_data.factor_time == 90.0


def test_validate_for_conversion_normal(data_store, conversion_data):
    conversion_data.from_type = "meters"
    conversion_data.to_type = "feet"
    conversion_data.amount = 10
    conversion_data._validate_for_conversion(data_store)


# ==================== ManageGroupData Tests ====================
@pytest.fixture
def manage_group_data():
    return ManageGroupData(unit_group="weight", action="add", new_base_unit="kilogram")


def test_validate_action_success(manage_group_data):
    manage_group_data._validate_action()


def test_validate_action_invalid(manage_group_data):
    manage_group_data.action = "invalid"
    with pytest.raises(Exception):
        manage_group_data._validate_action()


def test_validate_add_action_success(data_store, manage_group_data):
    manage_group_data.unit_group = "new_group"
    manage_group_data._validate_add_action(data_store)


def test_validate_new_base_unit_success(data_store, manage_group_data):
    manage_group_data.new_base_unit = "gram"
    manage_group_data._validate_new_base_unit(data_store)


# ==================== ManageTypeData Tests ====================
@pytest.fixture
def manage_type_data():
    return ManageTypeData(
        unit_group="length",
        unit_type="new_unit",
        action="add",
        value=2.0
    )


def test_validate_add_action_success(data_store, manage_type_data):
    manage_type_data._validate_add_action(data_store)


def test_validate_remove_action_success(data_store, manage_type_data):
    manage_type_data.unit_type = "mile"
    manage_type_data.action = "remove"
    
    # Limpa os campos que não devem estar preenchidos na remoção
    manage_type_data.value = None
    manage_type_data.factor = None
    manage_type_data.offset = None

    manage_type_data._validate_remove_action(data_store)


def test_validate_factor_temperature(data_store, manage_type_data):
    manage_type_data.unit_group = "temperature"
    manage_type_data.factor = 1.8
    manage_type_data.offset = 32
    manage_type_data._validate_factor()
    manage_type_data._validate_offset()


# ==================== AliasesData Tests ====================
@pytest.fixture
def aliases_data():
    return AliasesData(unit_group="length", unit_type="meters", action="add", alias="mtr")


def test_validate_unit_type_success(data_store, aliases_data):
    aliases_data._validate_unit_type(data_store)


def test_validate_alias_add_success(data_store, aliases_data):
    aliases_data._validate_alias(data_store)


def test_validate_alias_already_exists(data_store, aliases_data):
    aliases_data.alias = "m"
    with pytest.raises(Exception):
        aliases_data._validate_alias(data_store)


# ==================== ChangeBaseData Tests ====================
@pytest.fixture
def change_base_data():
    return ChangeBaseData(unit_group="length", new_base_unit="mile")


def test_validate_for_change_base_success(data_store, change_base_data):
    change_base_data._validate_for_change_base(data_store)


def test_validate_for_change_base_already_base(data_store, change_base_data):
    change_base_data.new_base_unit = data_store.base_units["length"]
    with pytest.raises(Exception):
        change_base_data._validate_for_change_base(data_store)


# Convertion Log Tests
def test_validate_for_history_empty(data_store):
    data_store.conversion_log = []
    with pytest.raises(Exception):
        _validate_for_history(data_store, limit=10)


def test_validate_for_history_negative_limit(data_store):
    with pytest.raises(Exception):
        _validate_for_history(data_store, limit=-5)
