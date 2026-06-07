from typing import Optional

from .data_manager import _save_data
from .data_models import DataStore, ChangeBaseData
from .utils import _get_user_input, _get_unit_group, _ensure_non_zero


__all__ = ["_change_base_unit"]


def _change_base_unit(data: DataStore, change_base_data: Optional[ChangeBaseData] = None) -> str:
    """Changes the base unit of a group and recalculates all values accordingly."""

    # Interactive approach
    if not change_base_data:
        change_base_data = ChangeBaseData(unit_group = _get_unit_group(data), new_base_unit=None)
        print(
            f"All unit types for '{change_base_data.unit_group}' group: " +
            ", ".join(data.units[change_base_data.unit_group].keys())
        )
        change_base_data.new_base_unit = _get_user_input(
            f"Enter new base unit for '{change_base_data.unit_group}' group: "
        )

    # Validates all variables and values
    change_base_data._validate_for_change_base(data)

    # Refactor all values in 'units.json' based on new base unit
    _refactor_value(data, change_base_data.unit_group, change_base_data.new_base_unit)
    # Update 'base_units.json' with new base unit
    data.base_units[change_base_data.unit_group] = change_base_data.new_base_unit

    try:
        # Persist changes
        _save_data(data.units, "units")
        _save_data(data.base_units, "base_units")
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        raise

    return (
        f"Base unit for '{change_base_data.unit_group}' group " 
        f"changed to '{change_base_data.new_base_unit}'!"
    )


def _refactor_value(data: DataStore, unit_group: str, new_base_unit: str) -> None:
    """Recalculates all unit values when the base unit of a group is changed."""

    original = data.original_units[unit_group]
    current = data.units[unit_group]

    if unit_group == "temperature":
        base_factor, base_offset = original[new_base_unit]
        _ensure_non_zero(base_factor)

        for unit_type, (old_factor, old_offset) in original.items():
            new_factor = old_factor / base_factor
            new_offset = old_offset - (old_factor / base_factor) * base_offset

            current[unit_type] = [new_factor, new_offset]

    else:
        base_factor = original[new_base_unit]
        _ensure_non_zero(base_factor)

        for unit_type, value in original.items():
            current[unit_type] = value / base_factor
