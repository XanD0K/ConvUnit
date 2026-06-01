from typing import Optional

from .data_manager import _save_data
from .data_models import DataStore, ManageGroupData
from .utils import _get_users_input, _get_unit_group


def _manage_group(
    data: DataStore, manage_group_data: Optional[ManageGroupData]=None
) -> str:
    """Handles all logic of adding and removing unit groups"""

    # Interactive approach
    if manage_group_data is None:
        manage_group_data = ManageGroupData(unit_group=None, action=None, new_base_unit=None)

        manage_group_data.action = _get_users_input(
            f"Existed groups: {", ".join(data.units.keys())}. "
            f"What do you want to do? ('add' or 'remove') "
        )
        manage_group_data._validate_action()

        if manage_group_data.action == "add":
            manage_group_data.unit_group = _get_users_input(f"New unit group: ")
            manage_group_data._validate_add_action(data)

            manage_group_data.new_base_unit = _get_users_input(
                f"You are creating '{manage_group_data.unit_group}' group. "
                f"Enter the base unit for that group: "
            )

        elif manage_group_data.action == "remove":
            manage_group_data.unit_group = _get_unit_group(data)

    # Validates all variables and values    
    manage_group_data._validate_for_manage_group(data)

    unit_group = manage_group_data.unit_group
    new_base_unit = manage_group_data.new_base_unit

    # Changes respective '.json' files
    if manage_group_data.action == "add":
        data.units[unit_group] = {new_base_unit: 1.0}
        data.original_units[unit_group] = {new_base_unit: 1.0}
        data.base_units[unit_group] = new_base_unit
        data.unit_aliases[unit_group] = {new_base_unit: new_base_unit}

        message = (
            f"You've just created a '{unit_group}' group, "
            f"with '{new_base_unit}' as its base unit!"
        )

    elif manage_group_data.action == "remove":
        data.units.pop(unit_group)
        data.original_units.pop(unit_group)
        data.base_units.pop(unit_group)
        data.unit_aliases.pop(unit_group)

        message = f"Group '{unit_group}' successfully removed!"

    try:
        # Persist changes
        _save_data(data.units, "units")
        _save_data(data.original_units, "original_units")
        _save_data(data.base_units, "base_units")
        _save_data(data.unit_aliases, "unit_aliases")
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        raise

    return message
