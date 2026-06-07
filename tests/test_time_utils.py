import pytest

from convunit.time_utils import (
    _parse_time_input,  _parse_time_component, _parse_date_input, _validate_date,
    _calculate_approximate_seconds, _get_days_from_month, _get_index_from_month,
)
from convunit.data_models import DataStore
from convunit.data_manager import _load_data


@pytest.fixture
def data_store():
    return DataStore(*_load_data())


def test_parse_time_input():
    assert _parse_time_input("10h:30m:15s") == 10*3600 + 30*60 + 15
    assert _parse_time_input("5h") == 5*3600
    assert _parse_time_input(":30m") == 30*60


def test_parse_time_component():
    assert _parse_time_component("10") == 10
    assert _parse_time_component(None) == 0
    assert _parse_time_component("") == 0


def test_parse_date_input():
    assert _parse_date_input("2025-06-05") == (2025, 6, 5)
    assert _parse_date_input("0-0-0") == (0, 0, 0)


def test_validate_date_valid():
    assert _validate_date(2025, 6, 5) is True


def test_validate_date_invalid_month():
    with pytest.raises(Exception):
        _validate_date(2025, 13, 5)


def test_validate_date_invalid_day():
    with pytest.raises(Exception):
        _validate_date(2025, 2, 30)


def test_calculate_approximate_seconds(data_store):
    result = _calculate_approximate_seconds(data_store, "time", 1, 1, 1)
    assert result > 0


def test_get_days_from_month(data_store):
    assert _get_days_from_month(data_store, "December") == 31


def test_get_index_from_month(data_store):
    assert _get_index_from_month(data_store, "June") == 6
