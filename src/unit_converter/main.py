import json
import sys

from .cli import _handle_cli
from .data_manager import _load_data
from .data_models import DataStore
from .interactive import _get_action
from .utils import _print_introductory_messages


def main() -> None:
    """
    Handles data loading and validation
    Decides between interactive and CLI approaches
    """

    try:
        # Initiates a 'DataStore' object
        data: DataStore = DataStore(*_load_data())
    except (ValueError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    # Handles command-line arguments approach
    if len(sys.argv) > 1:
        try:
            _handle_cli(data, sys.argv)
            sys.exit(0)
        except (ValueError, KeyError, ZeroDivisionError, TypeError) as e:
            print(f"Error: {e.args[0] if e.args else str(e)}")
            sys.exit(1)

    # Handles interactive approach
    _print_introductory_messages()
    _get_action(data)
