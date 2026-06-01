from typing import Optional

from .data_manager import _save_data
from .data_models import DataStore
from .utils import (
    _get_unit_group, _validate_unit_group, _format_value, _get_users_input
)


def _print_groups(data: DataStore) -> str:
    """Prints all available group of units"""

    return "Groups: " + ", ".join(data.units.keys())


def _manage_history(data: DataStore) -> str:
    """Handles history logic by choosing between view and reset logic"""

    choice = _get_users_input("Do you want to [v]iew or [r]eset the history log? ")

    match choice:
        case "v" | "view":
            raw_limit = _get_users_input("How many entries? (default 10): ") or "10"
            try:
                limit = int(raw_limit)
            except ValueError:
                limit = 10
            return _print_history(data, limit)
        case "r" | "reset":
            if _reset_history(data):
                return "History log successfully reseted!"
            else:
                return "Error: Failed to reset history"
        case _:
            return "Invalid action! Choose between 'View' and 'Reset'!"


def _print_history(data: DataStore, limit: int = 10) -> str:
    """Prints the previous 10 conversion entries"""

    try:
        _validate_for_history(data, limit)
        # Used to construct the sequence of entries to be saved
        entries: list[str] = []
        for entry in data.conversion_log[-int(limit):]:  # Last 10 entries
            # Generates specific messages based on 'unit_group'
            if entry["unit_group"] == "time":
                if entry["from_time"] in data.units["time"]:
                    entries.append(
                        f"{_format_value(entry['factor_time'])} "
                        f"{entry['from_time']} = {_format_value(entry['result'])} "
                        f"{entry['to_time']} (Group: time)"
                    )
                elif (
                    ":" in entry["from_time"]
                    or entry["from_time"].lower() in data.month_aliases
                    or "-" in entry["from_time"]
                ):
                    entries.append(
                        f"{_format_value(entry['result'])} {entry['factor_time']} "
                        f"between {entry['from_time']} and {entry['to_time']} "
                        f"(Group: time)"
                    )
                elif len(entry["from_time"].split()) > 1:
                    entries.append(
                        f"{entry['from_time']} = {_format_value(entry['result'])} "
                        f"{entry['to_time']} (Group: time)"
                    )
            else:
                entries.append(
                    f"{_format_value(entry['amount'])} {entry['from_type']} = "
                    f"{_format_value(entry['result'])} {entry['to_type']} "
                    f"(Group: {entry['unit_group']})"
                )
        return "\n".join(entries)
    except (ValueError, KeyError) as e:
        return f"Error: {e.args[0] if e.args else str(e)}"


def _reset_history(data: DataStore) -> bool:
    """Resets conversion history log"""
    try:
        data.conversion_log = []
        _save_data(data.conversion_log, "conversion_log")
        return True
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        return False


def _print_types(data: DataStore, unit_group: Optional[str]=None) -> str:
    """Prints all unit types for a specific unit group"""

    try:
        # Interactive approach
        if unit_group is None:
            unit_group = _get_users_input("Unit group: ")
        
        # Checks for 'all' flag
        if unit_group == "all":
            return _print_all_types(data)
        
        # Prints type for single group
        _validate_unit_group(unit_group, data)
        return _print_single_type(data, unit_group)

    except (ValueError, KeyError) as e:
        return f"Error: {e.args[0] if e.args else str(e)}"


def _print_base(data: DataStore, unit_group: Optional[str]=None) -> str:
    """Prints the base unit for a specific unit group"""
    
    try:
        # Interactive approach
        if unit_group is None:
            unit_group = _get_users_input("Unit group: ")
        
        # Checks for 'all' flag
        if unit_group == "all":
            formatted_output: list[str] = [
                f"{group}'s base unit: {base_unit}"
                for group, base_unit in data.base_units.items()
            ]

            return "\n".join(formatted_output)
            
        # Prints type for single group
        _validate_unit_group(unit_group, data)
        return f"{data.base_units[unit_group]}"

    except (ValueError, KeyError) as e:
        return f"Error: {e.args[0] if e.args else str(e)}"


def _validate_for_history(data: DataStore, limit: int):
    """Validates data and limit values on conversion log"""

    if not data.conversion_log:
        raise ValueError("Conversion history is empty!")
    try:
        limit = int(limit)        
    except:
        raise ValueError("'limit' must be a number!")
    if limit < 0:
        raise ValueError("'limit' must be a positive number!")


def _print_single_type(data: DataStore, unit_group: str):
    # Used to construct the sequence of unit_type and its respective aliases
    formatted_output: list[str] = []
    # Iterates over the outter keys of 'units.json' dictionary
    for unit_type in data.units[unit_group]:
        # Gets all aliases for a specific unit_type
        aliases: list[str] = [
            alias for alias, unit in data.unit_aliases.get(unit_group, {}).items()
            if unit == unit_type and alias != unit_type
        ]
        if aliases:
            formatted_output.append(
                f"{unit_type} ({', '.join(f'\'{alias}\'' for alias in aliases)})"
            )
        else:
            formatted_output.append(unit_type)
    return f"{unit_group.capitalize()} units:\n" + "\n".join(formatted_output)


def _print_all_types(data: DataStore):
    # Used to construct the sequence of unit_type and its respective aliases
    formatted_output: list[str] = []
    for unit_group in data.units:
        unit_structure = _print_single_type(data, unit_group)
        formatted_output.append(unit_structure)
    return f"\n\n".join(formatted_output)
