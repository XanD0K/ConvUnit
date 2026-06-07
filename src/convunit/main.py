import sys

from .cli import _handle_cli
from .data_manager import _load_data
from .data_models import DataStore
from .errors import DataError, ValidationError, UnitError
from .interactive import _run_interactive
from .utils import _print_introductory_messages


def main() -> None:
    """
    Main entry point of the application.

    Loads data and decides whether to run in CLI or Interactive mode.
    """

    # ================== LOADS DATA ==================
    try:
        data: DataStore = DataStore(*_load_data())
    except DataError as e:
        print(f"Data error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while loading data: {e}")
        sys.exit(1)

    # =================== CLI MODE ===================
    if len(sys.argv) > 1:
        try:
            _handle_cli(data, sys.argv)
            sys.exit(0)
        except (ValidationError, UnitError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

    # =============== INTERACTIVE MODE ===============
    _print_introductory_messages()
    _run_interactive(data)
