import pytest
from unittest.mock import patch

from convunit.cli import _handle_cli
from convunit.data_models import DataStore
from convunit.data_manager import _load_data


@pytest.fixture
def data_store():
    """Returns a DataStore instance with real data."""
    return DataStore(*_load_data())


def test_cli_groups(data_store):
    with patch("unitconverter.cli._print_groups") as mock:
        _handle_cli(data_store, ["cli.py", "groups"])
        mock.assert_called_once()


def test_cli_groups_alias(data_store):
    with patch("unitconverter.cli._print_groups") as mock:
        _handle_cli(data_store, ["cli.py", "g"])
        mock.assert_called_once()


def test_cli_types(data_store):
    with patch("unitconverter.cli._print_types") as mock:
        _handle_cli(data_store, ["cli.py", "types", "length"])
        mock.assert_called_once()


def test_cli_types_all(data_store):
    with patch("unitconverter.cli._print_types") as mock:
        _handle_cli(data_store, ["cli.py", "types", "--all"])
        mock.assert_called_once()


def test_cli_types_invalid_group(data_store):
    with pytest.raises(Exception):
        _handle_cli(data_store, ["cli.py", "types", "invalid"])


def test_cli_base(data_store):
    with patch("unitconverter.cli._print_base") as mock:
        _handle_cli(data_store, ["cli.py", "base", "length"])
        mock.assert_called_once()


def test_cli_base_all(data_store):
    with patch("unitconverter.cli._print_base") as mock:
        _handle_cli(data_store, ["cli.py", "base", "--all"])
        mock.assert_called_once()


def test_cli_history(data_store):
    with patch("unitconverter.cli._print_history") as mock:
        _handle_cli(data_store, ["cli.py", "history"])
        mock.assert_called_once()


def test_cli_history_limit(data_store):
    with patch("unitconverter.cli._print_history") as mock:
        _handle_cli(data_store, ["cli.py", "history", "--limit", "5"])
        mock.assert_called_once()


def test_cli_history_reset(data_store):
    with patch("unitconverter.cli._reset_history") as mock:
        _handle_cli(data_store, ["cli.py", "history", "--reset"])
        mock.assert_called_once()


def test_cli_convert_normal(data_store):
    with patch("unitconverter.cli._conversion_logic") as mock:
        _handle_cli(data_store, ["cli.py", "convert", "length", "meters", "feet", "10"])
        mock.assert_called_once()


def test_cli_convert_alias(data_store):
    with patch("unitconverter.cli._conversion_logic") as mock:
        _handle_cli(data_store, ["cli.py", "c", "length", "meters", "feet", "10"])
        mock.assert_called_once()


def test_cli_convert_time(data_store):
    with patch("unitconverter.cli._conversion_logic") as mock:
        _handle_cli(data_store, ["cli.py", "convert", "time", "minutes", "seconds", "60"])
        mock.assert_called_once()


def test_cli_convert_invalid_group(data_store):
    with pytest.raises(Exception):
        _handle_cli(data_store, ["cli.py", "convert", "invalid", "meters", "feet", "10"])


def test_cli_manage_group_add(data_store):
    with patch("unitconverter.cli._manage_group") as mock:
        _handle_cli(data_store, ["cli.py", "manage-group", "add", "new_group", "base"])
        mock.assert_called_once()


def test_cli_manage_group_remove(data_store):
    with patch("unitconverter.cli._manage_group") as mock:
        _handle_cli(data_store, ["cli.py", "manage-group", "remove", "length"])
        mock.assert_called_once()


def test_cli_manage_group_invalid_action(data_store):
    with patch("unitconverter.cli._manage_group") as mock:
        _handle_cli(data_store, ["cli.py", "manage-group", "invalid", "new_group"])
        mock.assert_called_once()


def test_cli_manage_type_add(data_store):
    with patch("unitconverter.cli._manage_type") as mock:
        _handle_cli(data_store, ["cli.py", "manage-type", "length", "add", "new_unit", "2"])
        mock.assert_called_once()


def test_cli_manage_type_remove(data_store):
    with patch("unitconverter.cli._manage_type") as mock:
        _handle_cli(data_store, ["cli.py", "manage-type", "length", "remove", "mile"])
        mock.assert_called_once()


def test_cli_aliases_add(data_store):
    with patch("unitconverter.cli._manage_aliases") as mock:
        _handle_cli(data_store, ["cli.py", "aliases", "length", "meters", "add", "mtr"])
        mock.assert_called_once()


def test_cli_aliases_remove(data_store):
    with patch("unitconverter.cli._manage_aliases") as mock:
        _handle_cli(data_store, ["cli.py", "aliases", "length", "meters", "remove", "m"])
        mock.assert_called_once()


def test_cli_change_base(data_store):
    with patch("unitconverter.cli._change_base_unit") as mock:
        _handle_cli(data_store, ["cli.py", "change-base", "length", "feet"])
        mock.assert_called_once()


def test_cli_reset(data_store):
    with patch("unitconverter.cli._reset_user_data") as mock:
        mock.return_value = True
        _handle_cli(data_store, ["cli.py", "reset"])
        mock.assert_called_once()


def test_cli_invalid_command(data_store):
    with pytest.raises(SystemExit):
        _handle_cli(data_store, ["cli.py", "invalid_command"])
