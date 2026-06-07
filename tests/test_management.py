import pytest
from unittest.mock import patch

from convunit.groups import _manage_group
from convunit.manage_types import _manage_type
from convunit.aliases import _manage_aliases
from convunit.change_base import _change_base_unit
from convunit.data_models import (
    DataStore,
    ManageGroupData,
    ManageTypeData,
    AliasesData,
    ChangeBaseData,
)


def get_clean_data_store():
    """Returns a DataStore with clean, controlled data."""
    units = {"length": {"meters": 1.0, "feet": 0.3048, "mile": 1609.0}}
    base_units = {"length": "meters"}
    unit_aliases = {"length": {"meters": "meters", "feet": "feet", "mile": "mile"}}
    original_units = units.copy()   # ← Add this line

    return DataStore(units, base_units, [], unit_aliases, {}, original_units, {})


def test_manage_group_add():
    data_store = get_clean_data_store()
    data = ManageGroupData(unit_group="new_group", action="add", new_base_unit="base")
    with patch("unitconverter.groups._save_data"):
        result = _manage_group(data_store, data)
        assert "created" in result.lower()


def test_manage_group_remove():
    data_store = get_clean_data_store()
    data = ManageGroupData(unit_group="length", action="remove")
    with patch("unitconverter.groups._save_data"):
        result = _manage_group(data_store, data)
        assert "removed" in result.lower()


def test_manage_type_add():
    data_store = get_clean_data_store()
    data = ManageTypeData(unit_group="length", unit_type="new_unit", action="add", value=2.0)
    with patch("unitconverter.manage_types._save_data"):
        result = _manage_type(data_store, data)
        assert "added" in result.lower()


def test_manage_type_remove():
    data_store = get_clean_data_store()
    data = ManageTypeData(unit_group="length", unit_type="mile", action="remove")
    with patch("unitconverter.manage_types._save_data"):
        result = _manage_type(data_store, data)
        assert "removed" in result.lower()


def test_manage_aliases_add():
    data_store = get_clean_data_store()
    data = AliasesData(unit_group="length", unit_type="meters", action="add", alias="mtr")
    with patch("unitconverter.aliases._save_data"):
        result = _manage_aliases(data_store, data)
        assert "added" in result.lower()


def test_manage_aliases_remove():
    data_store = get_clean_data_store()
    data_store.unit_aliases["length"]["mtr"] = "meters"
    data = AliasesData(unit_group="length", unit_type="meters", action="remove", alias="mtr")
    with patch("unitconverter.aliases._save_data"):
        result = _manage_aliases(data_store, data)
        assert "removed" in result.lower()


def test_change_base():
    data_store = get_clean_data_store()
    data = ChangeBaseData(unit_group="length", new_base_unit="feet")
    with patch("unitconverter.change_base._save_data"):
        result = _change_base_unit(data_store, data)
        assert result is not None