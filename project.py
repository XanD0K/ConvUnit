import json
import sys

from src.unit_converter.cli import handle_cli
from src.unit_converter.data_manager import load_data
from src.unit_converter.data_models import DataStore
from src.unit_converter.interactive import get_action
from src.unit_converter.utils import print_introductory_messages


def main() -> None:
    """Handles data loading and validation"""
    try:
        # Initiates a 'DataStore' object
        data: DataStore = DataStore(*load_data())
    except (ValueError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error: {str(e)}")
        sys.exit(1)  # Exits the program if any error happens

    # Handles command-line arguments approach
    try:
        if len(sys.argv) > 1:
            handle_cli(data, sys.argv)
            sys.exit(0)  # Exits program after command-line execution
    except (ValueError, KeyError, ZeroDivisionError, TypeError) as e:
        print(f"Error: {e.args[0] if e.args else str(e)}")
        sys.exit(1)  # Exits the program if any error happens

    # Handles interactive approach
    print_introductory_messages()
    get_action(data)


if __name__ == "__main__":
    main()
