import pytest
from unittest.mock import patch

from convunit.interactive import _run_interactive
from convunit.data_models import DataStore
from convunit.data_manager import _load_data


@pytest.fixture
def data_store():
    """Returns a DataStore instance with real data."""
    return DataStore(*_load_data())


def test_interactive_quit(data_store):
    """Test that the interactive mode exits when the user types 'quit'."""
    with patch("builtins.input", return_value="quit"):
        with pytest.raises(SystemExit):
            _run_interactive(data_store)


def test_interactive_groups_command(data_store):
    """Test the 'groups' command in interactive mode."""
    inputs = iter(["groups", "quit"])
    with patch("builtins.input", lambda prompt="": next(inputs)):
        with patch("unitconverter.interactive._print_groups") as mock:
            try:
                _run_interactive(data_store)
            except SystemExit:
                pass
            mock.assert_called_once()


def test_interactive_history_command(data_store):
    """Test the 'history' command in interactive mode."""
    inputs = iter(["history", "quit"])
    with patch("builtins.input", lambda prompt="": next(inputs)):
        with patch("unitconverter.interactive._manage_history") as mock:
            try:
                _run_interactive(data_store)
            except SystemExit:
                pass
            mock.assert_called_once()


def test_interactive_invalid_command(data_store):
    """Test an invalid command in interactive mode."""
    inputs = iter(["invalid_command", "quit"])
    with patch("builtins.input", lambda prompt="": next(inputs)):
        try:
            _run_interactive(data_store)
        except SystemExit:
            pass
