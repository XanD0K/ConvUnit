import importlib.resources as resources
import json
import platformdirs
import shutil

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Union

from .data_models import DataStore, ConversionData
from .errors import DataCorruptedError, DataInconsistencyError, InvalidInputError


__all__ = ["_load_data", "_save_data", "_reset_user_data"]

# User data directory (cross-platform)
# Linux/macOS: ~/.config/convunit/
# Windows: %APPDATA%\convunit\
USER_DATA_DIR: Path = Path(platformdirs.user_config_dir("convunit"))

# Files that can be modified by the user (stored in the user data directory)
MODIFIABLE_FILES = [
    "units.json",
    "base_units.json",
    "conversion_log.json",
    "unit_aliases.json",
    "original_units.json",
]

# Static files (shipped inside the package)
STATIC_FILES = [
    "month_days.json",
    "month_aliases.json",
]


def _ensure_user_data_dir() -> None:
    """
    Ensures the user data directory exists.

    On first run, copies the modifiable data files from the package to the user directory.
    """
    
    if USER_DATA_DIR.exists():
        return

    # Create user data directory
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Copies package's modifiable files to user's folder
    package_data_dir = _get_package_data_dir()

    for filename in MODIFIABLE_FILES:
        src = package_data_dir / filename
        dst = USER_DATA_DIR / filename

        if src.exists():
            shutil.copy2(src, dst)
        else:
            # Create empty file if it doesn't exist in the package
            if filename == "conversion_log.json":
                dst.write_text("[]", encoding="utf-8")
            else:
                dst.write_text("{}", encoding="utf-8")


def _get_package_data_dir() -> Path:
    """Returns the path to the data/ directory inside the package."""

    try:
        # Python 3.9+
        if hasattr(resources, "files"):
            return Path(resources.files("convunit") / "data")
        else:
            # Fallback for older Python versions
            with resources.path("convunit", "data") as path:
                return Path(path)
    except (ImportError, ModuleNotFoundError, FileNotFoundError):
        # Development mode (running from the repository)
        return Path(__file__).parent / "data"


def _load_data() -> tuple[dict, dict, list, dict, dict, dict, dict]:
    """Loads all required JSON data files."""

    _ensure_user_data_dir()

    package_data_dir = _get_package_data_dir()

    # --- Static files (loaded from the package) ---
    with open(package_data_dir / "month_days.json", "r", encoding="utf-8") as file:
        month_days = json.load(file)

    with open(package_data_dir / "month_aliases.json", "r", encoding="utf-8") as file:
        month_aliases = json.load(file)

    # --- Modifiable files (loaded from user data directory) ---
    with open(USER_DATA_DIR / "units.json", "r", encoding="utf-8") as file:
        units = json.load(file)

    with open(USER_DATA_DIR / "base_units.json", "r", encoding="utf-8") as file:
        base_units = json.load(file)

    with open(USER_DATA_DIR / "conversion_log.json", "r", encoding="utf-8") as file:
        conversion_log = json.load(file)

    with open(USER_DATA_DIR / "unit_aliases.json", "r", encoding="utf-8") as file:
        unit_aliases = json.load(file)

    with open(USER_DATA_DIR / "original_units.json", "r", encoding="utf-8") as file:
        original_units = json.load(file)

    # Validate data integrity
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
    """Validates the integrity of all loaded data files."""

    # --- units.json ---
    if not isinstance(units, dict) or not units:
        raise DataCorruptedError("'units.json' structure is corrupted!")

    for unit_group in units:
        if not isinstance(units[unit_group], dict):
            raise DataCorruptedError(
                f"'units.json' is corrupted! Group '{unit_group}' should be a dictionary!"
            )
        if unit_group not in base_units:
            raise DataInconsistencyError(
                f"'{unit_group}' exists in 'units.json' but not in 'base_units.json'!"
            )

    # --- base_units.json ---
    if not isinstance(base_units, dict) or not base_units:
        raise DataCorruptedError("'base_units.json' structure is corrupted!")

    for unit_group in units:
        if base_units[unit_group] not in units[unit_group]:
            raise DataInconsistencyError(
                f"'{unit_group}' exists in 'base_units.json' but not in 'units.json'!"
            )

    # --- unit_aliases.json ---
    if not isinstance(unit_aliases, dict) or not unit_aliases:
        raise DataCorruptedError("'unit_aliases.json' structure is corrupted!")

    for unit_group in unit_aliases:
        if unit_group not in units:
            raise DataInconsistencyError(
                f"'{unit_group}' exists in 'unit_aliases.json' but not in 'units.json'!"
            )
        if not isinstance(unit_aliases[unit_group], dict):
            raise DataCorruptedError(
                f"'unit_aliases.json' is corrupted! Group '{unit_group}' should be a dictionary!"
            )

        seen_aliases = set()
        for alias in unit_aliases[unit_group]:
            if alias in seen_aliases:
                raise DataCorruptedError(
                    f"'unit_aliases.json' is corrupted! "
                    f"There are duplicate aliases in group '{unit_group}'!"
                )
            seen_aliases.add(alias)

        for alias, target in unit_aliases[unit_group].items():
            if target not in units[unit_group]:
                raise DataInconsistencyError(
                    f"Alias '{alias}' in group '{unit_group}' points to "
                    f"'{target}', which does not exist in 'units.json'!"
                )

    # --- original_units.json ---
    if not isinstance(original_units, dict) or not original_units:
        raise DataCorruptedError("'original_units.json' structure is corrupted!")

    for unit_group in original_units:
        if not isinstance(original_units[unit_group], dict):
            raise DataCorruptedError(
                f"'original_units.json' is corrupted! Group '{unit_group}' should be a dictionary!"
            )
        if unit_group not in base_units:
            raise DataInconsistencyError(
                f"'{unit_group}' exists in 'original_units.json' but not in 'base_units.json'!"
            )
        if base_units[unit_group] not in original_units[unit_group]:
            raise DataInconsistencyError(
                f"Base unit '{base_units[unit_group]}' for group '{unit_group}' "
                f"is not present in 'original_units.json'!"
            )
        for unit_type in original_units[unit_group]:
            if unit_type not in units[unit_group]:
                raise DataInconsistencyError(
                    f"Type '{unit_type}' exists in 'original_units.json' "
                    f"but not in 'units.json' (group '{unit_group}')!"
                )

    # --- conversion_log.json ---
    if not isinstance(conversion_log, list):
        raise DataCorruptedError("'conversion_log.json' structure is corrupted!")

    # --- month_days.json and month_aliases.json ---
    if not isinstance(month_days, dict) or not month_days:
        raise DataCorruptedError("'month_days.json' structure is corrupted!")

    if not isinstance(month_aliases, dict) or not month_aliases:
        raise DataCorruptedError("'month_aliases.json' structure is corrupted!")


def _save_data(data: Union[dict[Any, Any], list[dict[str, Any]]], file_name: str) -> None:
    """Saves data to the user data directory."""

    _ensure_user_data_dir()

    try:
        with open(USER_DATA_DIR / f"{file_name}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except PermissionError:
        print(f"Error! You don't have permission to write to {file_name}.json!")
        raise
    except Exception as e:
        print(f"Error while saving {file_name}.json: {e}")
        raise


def _add_to_log(
    data: DataStore, conversion_data: ConversionData, is_time_convertion: bool = False
) -> None:
    """Adds a successful conversion to the history log."""

    unit_group: str = conversion_data.unit_group

    if is_time_convertion:
        from_time = conversion_data.from_time
        to_time = conversion_data.to_time
        factor_time = conversion_data.factor_time
        new_time = float(conversion_data.new_time)
        if all(x is None for x in (from_time, to_time, factor_time, new_time)):
            raise InvalidInputError("Missing required arguments!")
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
            raise InvalidInputError("Missing required arguments!")
        entry = {
            "date": datetime.now().isoformat(),
            "unit_group": unit_group,
            "from_type": from_type,
            "to_type": to_type,
            "amount": amount,
            "result": new_value
        }

    data.conversion_log = _clean_history(data)
    data.conversion_log.append(entry)

    try:
        _save_data(data.conversion_log, "conversion_log")
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        raise


def _clean_history(data: DataStore) -> list[dict]:
    """Removes history entries older than 3 days."""

    return [
        entry for entry in data.conversion_log
        if "date" in entry and datetime.now() - datetime.fromisoformat(entry["date"]) <= timedelta(days=3)
    ]


def _reset_user_data() -> bool:
    """
    Resets all user-modifiable data to the original state.

    Deletes the user data directory and recreates it with the original files from the package.
    """

    try:
        if USER_DATA_DIR.exists():
            shutil.rmtree(USER_DATA_DIR)

        _ensure_user_data_dir()
        return True
    except Exception as e:
        return False
