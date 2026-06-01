import shutil
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_models import DataStore, ConversionData


def _print_introductory_messages() -> None:
    """Displays introductory messages and instructions"""

    print(
        _print_divider("="),
        "Welcome to UnitConverter!",
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
        "Quit anytime by entering 'quit' or by pressing ctrl+d or ctrl+c",
        sep="\n"
    )


def _get_users_input(prompt: str) -> str:
    """Exits the program anytime by entering 'quit' on input"""

    value: str = input(prompt).strip().lower()

    if value == "quit":
        print("Bye!")
        sys.exit(0)

    return value


def _get_unit_group(data: DataStore) -> str:
    """Retrives unit group"""

    unit_group: str = _get_users_input("Unit group: ")
    _validate_unit_group(unit_group, data)

    return unit_group


def _validate_unit_group(unit_group: str|None, data: DataStore) -> None:
    """Validates unit group"""

    if not unit_group:
        raise ValueError("Unit group cannot be empty!")
    if unit_group not in data.units:
        raise KeyError(f"'{unit_group}' is not a valid group!")


def _get_converter_units(data: DataStore, unit_data: ConversionData) -> None:
    """Retrieves unit_type for conversion"""

    unit_data.from_type = _get_users_input("From: ")
    unit_data.to_type = _get_users_input("To: ")
    unit_data._validate_from_type(data)
    unit_data._validate_to_type(data)


def _get_amount(unit_data: ConversionData) -> None:
    """Retrieves unit amount to be converted"""

    raw = _get_users_input("Amount: ")

    try:
        unit_data.amount = float(raw)
    except ValueError as e:
        raise ValueError("Invalid amount! Use integer or decimal (e.g. 10, 10.0)") from e


def _resolve_aliases(data: "DataStore", unit_group: str, unit_type: str) -> str:
    """Checks user's input for any match with unit type or its aliases"""

    # Checks for literal name
    if not unit_type:
        raise KeyError("Invalid unit type!")
    
    # Checks for aliases
    if unit_type in data.unit_aliases[unit_group]:
        return data.unit_aliases[unit_group][unit_type]
    
    raise KeyError(f"Unit type '{unit_type}' not found in '{unit_group}' neither its aliases!")


def _print_divider(symbol="-"):
    """Print symbols to custom messages in interactive mode"""

    # Retrives terminal's size to customize messages
    columns, _ = shutil.get_terminal_size()
    return(symbol * columns)


def _format_value(value: float | str) -> str:
    """Formats value by keeping 5 decimal values and eliminating trailling zeroes"""

    formatted_value = f"{value:,.5f}".rstrip("0").rstrip(".")
    # Adds '.0' if formatted value ended up with no decimal values
    return formatted_value if "." in formatted_value else formatted_value + ".0"
