import pytest
from unittest.mock import patch
from datetime import datetime, timedelta

from convunit.data_manager import _load_data, _add_to_log, _clean_history, _reset_user_data
from convunit.data_models import DataStore, ConversionData


@pytest.fixture
def data_store():
    """Fixture that provides a DataStore instance with real data."""
    return DataStore(*_load_data())


def test_load_data_returns_tuple_with_seven_elements():
    """_load_data should return a tuple containing exactly 7 elements."""
    result = _load_data()
    assert isinstance(result, tuple)
    assert len(result) == 7


def test_clean_history_removes_old_entries(data_store):
    """_clean_history should remove entries older than 3 days."""
    old_date = (datetime.now() - timedelta(days=10)).isoformat()
    recent_date = datetime.now().isoformat()

    data_store.conversion_log = [
        {"date": old_date, "unit_group": "length"},
        {"date": recent_date, "unit_group": "length"}
    ]

    cleaned = _clean_history(data_store)
    assert len(cleaned) == 1


def test_clean_history_keeps_recent_entries(data_store):
    """_clean_history should keep recent entries."""
    recent_date = datetime.now().isoformat()
    data_store.conversion_log = [{"date": recent_date, "unit_group": "length"}]

    cleaned = _clean_history(data_store)
    assert len(cleaned) == 1


def test_add_to_log_normal_conversion(data_store):
    """_add_to_log should correctly add a normal unit conversion."""
    conversion_data = ConversionData(
        unit_group="length",
        from_type="meters",
        to_type="feet",
        amount=10,
        new_value=32.8084
    )

    initial_count = len(data_store.conversion_log)
    _add_to_log(data_store, conversion_data)

    assert len(data_store.conversion_log) == initial_count + 1


def test_add_to_log_time_conversion(data_store):
    """_add_to_log should correctly add a time conversion."""
    conversion_data = ConversionData(
        unit_group="time",
        from_time="1h",
        to_time="minutes",
        factor_time=60,
        new_time=60
    )

    initial_count = len(data_store.conversion_log)
    _add_to_log(data_store, conversion_data, is_time_convertion=True)

    assert len(data_store.conversion_log) == initial_count + 1


@patch("unitconverter.data_manager.shutil.rmtree")
@patch("unitconverter.data_manager.USER_DATA_DIR")
@patch("unitconverter.data_manager._ensure_user_data_dir")
def test_reset_user_data_success(mock_ensure, mock_user_dir, mock_rmtree):
    """_reset_user_data should delete the user directory and recreate it."""
    mock_user_dir.exists.return_value = True

    result = _reset_user_data()

    mock_user_dir.exists.assert_called_once()
    mock_rmtree.assert_called_once()
    mock_ensure.assert_called_once()
    assert result is True


def test_reset_user_data_returns_false_on_error():
    """_reset_user_data should return False when an error occurs."""
    with patch(
        "unitconverter.data_manager.shutil.rmtree", side_effect=Exception("Simulated error")
    ):
        result = _reset_user_data()
        assert result is False
