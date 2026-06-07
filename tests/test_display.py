import pytest
from unittest.mock import patch

from convunit.display import (
    _print_groups, _print_types, _print_base, _print_history, _manage_history
)
from convunit.data_models import DataStore
from convunit.data_manager import _load_data


@pytest.fixture
def data_store():
    return DataStore(*_load_data())


def test_print_groups(data_store):
    result = _print_groups(data_store)
    assert "length" in result
    assert "time" in result


def test_print_types(data_store):
    result = _print_types(data_store, "length")
    assert "meters" in result


def test_print_base(data_store):
    result = _print_base(data_store, "length")
    assert result == "meters"


def test_print_history_empty(data_store):
    data_store.conversion_log = []
    result = _print_history(data_store)
    assert "Error" in result or result == ""


def test_manage_history_view(data_store):
    data_store.conversion_log = [
        {
            "date": "2025-06-01T00:00:00",
            "unit_group": "length",
            "from_type": "meters",
            "to_type": "feet",
            "amount": 10,
            "result": 32.8084
        }
    ]
    with patch("unitconverter.display._get_user_input", side_effect=["v", "5"]):
        result = _manage_history(data_store)
        assert "meters" in result or "feet" in result