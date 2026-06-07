import sys

from .aliases import _manage_aliases
from .change_base import _change_base_unit
from .convert import _conversion_logic
from .data_manager import _reset_user_data
from .data_models import DataStore
from .display import _print_groups, _manage_history, _print_types, _print_base
from .errors import AppError
from .groups import _manage_group
from .manage_types import _manage_type
from .utils import _get_user_input, _print_divider


# Interactive approach
def _run_interactive(data: DataStore) -> None:
    """
    Main loop of the interactive mode.

    Continuously prompts the user for commands and executes them until exit.
    """
    
    while True:
        try:
            print(_print_divider("="))
            action = _get_user_input("Let's begin! What do you want to do? ")
            message = ""
            # Checks action validity
            match action:
                case "aliases" | "a":
                    message = _manage_aliases(data)
                case "base" | "b":
                    message = _print_base(data)
                case "convert" | "c":
                    message = _conversion_logic(data)
                case "change-base" | "cb":
                    message = _change_base_unit(data)
                case "groups" | "g":
                    message = _print_groups(data)
                case "history" | "h":
                    message = _manage_history(data)
                case "manage-group" | "mg":
                    message = _manage_group(data)
                case "manage-type" | "mt":
                    message = _manage_type(data)
                case "types" | "t":
                    message = _print_types(data)
                case "reset":
                    if _reset_user_data():
                        message = "Data files successfully reset to original state!"
                    else:
                        message = "Error: Failed to reset data files."
                # Fallback
                case _:
                    raise ValueError(f"'{action}' is not a valid action!")
            print(message)
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nBye!")
        except AppError as e:
            print(f"Error: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            continue
