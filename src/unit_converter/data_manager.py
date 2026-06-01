import json

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Union

from .data_models import DataStore, ConversionData  

# Creates path to root directory
_BASE_DIR = Path(__file__).parent.parent.parent


def _load_data() -> tuple[dict, dict, list, dict, dict, dict, dict]:
    """Imports all JSON files which handle data management"""

    # Dictionary with all units available and their respective values
    with open(_BASE_DIR / "data" / "units.json", "r") as file:
        units = json.load(file)
    # Dictionary with base units for each group
    with open(_BASE_DIR / "data" / "base_units.json", "r") as file:
        base_units = json.load(file)
    # List to store the conversion log records
    with open(_BASE_DIR / "data" / "conversion_log.json", "r") as file:
        conversion_log = json.load(file)
    # Dictionary with all aliases for each unit_type
    with open(_BASE_DIR / "data" / "unit_aliases.json", "r") as file:
        unit_aliases = json.load(file)
    # Dictionary that relates a month with its maximum number of days
    with open(_BASE_DIR / "data" / "month_days.json", "r") as file:
        month_days = json.load(file)
    # Dictionary with the original conversion factor for all unit_types
    with open(_BASE_DIR / "data" / "original_units.json", "r") as file:
        original_units = json.load(file)
    # Dictionary with all aliases dor each month
    with open(_BASE_DIR / "data" / "month_aliases.json", "r") as file:
        month_aliases = json.load(file)
    # Validates all JSON files
    _validate_data(
        units, base_units, conversion_log, unit_aliases,
        month_days, original_units, month_aliases
    )
    return (
        units, base_units, conversion_log, unit_aliases,
        month_days, original_units, month_aliases
    )


def _validate_data(
    units: dict, base_units: dict, conversion_log: list, unit_aliases: dict,
    month_days: dict, original_units: dict, month_aliases: dict
) -> None:
    """Validates all JSON files to prevent operations with corrupted data"""

    # ------------------------------------- units.json ------------------------------------
    # Ensures 'units.json' is a dictionary and it's not empty
    if not isinstance(units, dict) or not units:
        raise ValueError("'units.json' structure is corrupted!")
    for unit_group in units:
        # Ensures every unit_group in 'units.json' is also a dictionary
        if not isinstance(units[unit_group], dict):
            raise ValueError(f"'units.json' is corrupted! Group '{unit_group}' should be a dictionary!")
        # Ensures every group in 'units.json' is also a group in 'base_units.json'
        if unit_group not in base_units:
            raise KeyError(f"'{unit_group}' exists in 'units.json' but not in 'base_units.json'!")

    # ---------------------------------- base_units.json ----------------------------------
    # Ensures 'base_units.json' is a dictionary and it's not empty
    if not isinstance(base_units, dict) or not base_units:
        raise ValueError("'base_units.json' structure is corrupted!")

    for unit_group in units:
        # Ensures base unit for each group is correctly define in 'units.json'
        if base_units[unit_group] not in units[unit_group]:
            raise KeyError(f"'{unit_group}' exists in 'base_units.json' but not in 'units.json'!")

    # --------------------------------- unit_aliases.json ---------------------------------
    # Ensures 'unit_aliases.json' is a dictionary and it's not empty
    if not isinstance(unit_aliases, dict) or not unit_aliases:
        raise ValueError("'unit_aliases.json' structure is corrupted!")
    for unit_group in unit_aliases:
        # Ensures every unit_group in 'unit_aliases.json' is also a unit_group in 'units.json'
        if unit_group not in units:
            raise KeyError(f"'{unit_group}' exists in 'unit_aliases.json' but not in 'units.json'!")
        # Ensures every unit_group in 'unit_aliases.json' is also a dictionary
        if not isinstance(unit_aliases[unit_group], dict):
            raise ValueError(f"'unit_aliases.json' is corrupted! Group '{unit_group}' should be a dictionary!")
        # Ensures no duplicate aliases in the same unit group
        seen_aliases = set()
        for alias in unit_aliases[unit_group]:
            if alias in seen_aliases:
                raise ValueError(
                    f"'unit_aliases.json' is corrupted! "
                    f"There are duplicate aliases in '{unit_aliases[unit_group]}' group!"
                )
            seen_aliases.add(alias)
        
        # Ensures all aliases' targets are valid unit_types
        for alias, target in unit_aliases[unit_group].items():
            if target not in units[unit_group]:
                raise KeyError(
                    f"'unit_aliases.json' is corrupted! "
                    f"Alias '{alias}' in group '{unit_group}' points to '{target}', "
                    f"which does not exist in 'units.json'!"
                )

    # -------------------------------- original_units.json --------------------------------
    # Ensures 'original_units.json' is a dictionary and it's not empty
    if not isinstance(original_units, dict) or not original_units:
        raise ValueError("'original_units.json' structure is corrupted!")
    for unit_group in original_units:
        # Ensures every unit_group in 'original_units.json' is also a dictionary
        if not isinstance(original_units[unit_group], dict):
            raise ValueError(f"'original_units.json' is corrupted! Group '{unit_group}' should be a dictionary!")
        # Ensures every group in 'original_units.json' is also a group in 'base_units.json'
        if unit_group not in base_units:
            raise KeyError(f"'{unit_group}' exists in 'original_units.json' but not in 'base_units.json'!")
        # Ensures base unit for each group is correctly define in 'original_units.json'
        if base_units[unit_group] not in original_units[unit_group]:
            raise KeyError(
                f"Base unit '{base_units[unit_group]}' for group '{unit_group}' "
                f"is not present in 'original_units.json'!"
            )
        # Ensures every unit_type in 'original_units.json' is also an unit-type in 'units.json'
        for unit_type in original_units[unit_group]:
            if unit_type not in units[unit_group]:
                raise KeyError(
                    f"Unit type '{unit_type}' exists in 'original_units.json' "
                    f"but not in 'units.json' (group '{unit_group}')!"
                )
    
    # ------------------------------------ OTHER FILES ------------------------------------
    # Ensures 'conversion_log.json' is a list
    if not isinstance(conversion_log, list):
        raise ValueError("'conversion_log.json' structure is corrupted!")
    # Ensures 'month_days.json' is a dictionary and it's not empty
    if not isinstance(month_days, dict) or not month_days:
        raise ValueError("'month_days.json' structure is corrupted!")
    # Ensures 'month_aliases.json' is a dictionary and it's not empty
    if not isinstance(month_aliases, dict) or not month_aliases:
        raise ValueError("'month_aliases.json' structure is corrupted!")


def _add_to_log(
    data: DataStore, conversion_data: ConversionData,
    is_time_convertion: bool=False
) -> None:
    """Adds successfully converted value to conversion_log.json file"""

    unit_group: str = conversion_data.unit_group

    if is_time_convertion:
        from_time = conversion_data.from_time
        to_time = conversion_data.to_time
        factor_time = conversion_data.factor_time
        new_time = float(conversion_data.new_time)
        if all(x is None for x in (from_time, to_time, factor_time, new_time)):
            raise ValueError("Missing required arguments!")
        entry = {
            "date": datetime.now().isoformat(),
            "unit_group": unit_group,
            "from_time": from_time,
            "to_time": to_time,
            "factor_time": factor_time,
            "result": new_time
        }
    else:
        from_type = conversion_data.from_type
        to_type = conversion_data.to_type
        amount = conversion_data.amount
        new_value = float(conversion_data.new_value)
        if all(x is None for x in (from_type, to_type, amount, new_value)):
            raise ValueError("Missing required arguments!")
        entry = {
            "date": datetime.now().isoformat(),
            "unit_group": unit_group,
            "from_type": from_type,
            "to_type": to_type,
            "amount": amount,
            "result": new_value
        }

    # Cleans 'conversion_log.json' file, preventing big files
    data.conversion_log = _clean_history(data)
    # Appends new entry
    data.conversion_log.append(entry)

    try:
        _save_data(data.conversion_log, "conversion_log")
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        raise


def _clean_history(data: DataStore) -> list[dict]:
    """Cleans 'conversion_log.json' file keeping only entries not older than 3 days"""

    return [
        entry for entry in data.conversion_log if "date" in entry and datetime.now() -
        datetime.fromisoformat(entry["date"]) <= timedelta(days=3)
    ]


def _save_data(
    data: Union[dict[Any, Any], list[dict[str, Any]]],
    file_name: str
) -> Union[dict[Any, Any], list[dict[str, Any]]]:
    """Saves data in the respective JSON file"""

    try:
        with open(_BASE_DIR / "data" / f"{file_name}.json", "w") as file:
            json.dump(data, file, indent=4)
    except PermissionError:
        print(f"Error! You don't have permission to write to {file_name}.json!")
        raise
    except Exception as e:
        print(f"Error while saving {file_name}.json: {e}")
        raise


def _zero_division_checker(num: float) -> None:
    """Prevents division by zero"""

    if num == 0:
        raise ZeroDivisionError("Can't Divide by zero")
