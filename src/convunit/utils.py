import shutil
import sys

from typing import TYPE_CHECKING

from .errors import InvalidInputError, UnitGroupNotFoundError, UnitNotFoundError

if TYPE_CHECKING:
    from .data_models import DataStore, ConversionData


__all__ = [
    "_print_introductory_messages",
    "_get_user_input",
    "_get_unit_group",
    "_validate_unit_group",
    "_get_converter_units",
    "_get_amount",
    "_resolve_aliases",
    "_print_divider",
    "_format_value",
    "_ensure_non_zero"
]


def _print_introductory_messages() -> None:
    """Prints welcome message and available commands for interactive mode."""

    print(
        _print_divider("="),
        "Welcome to ConvUnit!",
        _print_divider("-"),
        "Commands:",
        "- 'history' or 'h' → prints conversion history",
        "- 'groups' or 'g' → checks all group of units available",
        "- 'types' or 't' → checks all types for a specific group available",
        "- 'convert' or 'c' → converts units",
        "- 'manage-group' or 'mg' → add/remove unit groups",
        "- 'manage-types' or 'mt' → add/remove unit types",
        "- 'aliases' or 'a' → add/remove aliases",
        "- 'change-base' or 'cb' → changes conversion base unit",
        "Exit anytime by entering 'quit', 'exit' or by pressing ctrl+d or ctrl+c",
        sep="\n"
    )


def _get_user_input(prompt: str) -> str:
    """Gets user input and exits the program if 'quit', 'exit', 'q' or 'e' is entered."""

    value: str = input(prompt).strip().lower()

    if value in ["quit", "q", "exit", "e"]:
        print("Bye!")
        sys.exit(0)

    return value


def _get_unit_group(data: DataStore) -> str:
    """Prompts the user for a unit group and validates it."""

    unit_group: str = _get_user_input("Unit group: ")
    _validate_unit_group(unit_group, data)

    return unit_group


def _validate_unit_group(unit_group: str|None, data: DataStore) -> None:
    """Validates that a unit group exists and is not empty."""

    if not unit_group:
        raise InvalidInputError("Unit group cannot be empty!")
    if unit_group not in data.units:
        raise UnitGroupNotFoundError(f"'{unit_group}' is not a valid group!")


def _get_converter_units(data: DataStore, unit_data: ConversionData) -> None:
    """Prompts the user for source and target unit types and validates them."""

    unit_data.from_type = _get_user_input("From: ")
    unit_data.to_type = _get_user_input("To: ")
    unit_data._validate_from_type(data)
    unit_data._validate_to_type(data)


def _get_amount(unit_data: ConversionData) -> None:
    """Prompts the user for the amount to convert and validates it."""

    raw = _get_user_input("Amount: ")

    try:
        unit_data.amount = float(raw)
    except ValueError as e:
        raise InvalidInputError("Invalid amount! Use integer or decimal (e.g. 10, 10.0)") from e


def _resolve_aliases(data: "DataStore", unit_group: str, unit_type: str) -> str:
    """Returns the canonical unit type (resolving aliases if needed)."""

    # Checks for literal name
    if not unit_type:
        raise UnitNotFoundError("Invalid unit type!")
    
    # Checks for aliases
    if unit_type in data.unit_aliases[unit_group]:
        return data.unit_aliases[unit_group][unit_type]
    
    raise UnitNotFoundError(
        f"Unit type '{unit_type}' not found in '{unit_group}' neither its aliases!"
    )


def _print_divider(symbol: str = "-") -> str:
    """Returns a horizontal divider line using the terminal width."""

    # Retrives terminal's size to customize messages
    columns, _ = shutil.get_terminal_size()
    return symbol * columns


def _format_value(value: float | str) -> str:
    """Formats a number with up to 5 decimal places, removing trailing zeros."""

    formatted_value = f"{value:.5f}".rstrip("0").rstrip(".")
    # Adds '.0' if formatted value ended up with no decimal values
    return formatted_value if "." in formatted_value else formatted_value + ".0"


def _ensure_non_zero(num: float) -> None:
    """Raises ZeroDivisionError if the given number is zero."""

    if num == 0:
        raise ZeroDivisionError("Can't Divide by zero")
