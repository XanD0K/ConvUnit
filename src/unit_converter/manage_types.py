from typing import Optional

from .data_manager import _save_data, _zero_division_checker
from .data_models import DataStore, ManageTypeData
from .utils import _get_users_input, _get_unit_group


def _manage_type(data: DataStore, manage_type_data: Optional[ManageTypeData]=None) -> str:
    """Handles all logic of adding and removing unit types"""

    # Interactive approach
    if manage_type_data is None:
        manage_type_data = ManageTypeData(unit_group = _get_unit_group(data))

        manage_type_data.action = _get_users_input(
            f"Existed types for '{manage_type_data.unit_group}' group: "
            f"{data.units[manage_type_data.unit_group]}. "
            f"What do you want to do ('add' or 'remove')? "
        )
        manage_type_data._validate_action()

        if manage_type_data.action == "add":
            manage_type_data.unit_type = _get_users_input(
                f"Enter new type for '{manage_type_data.unit_group}' group: "
            )
            manage_type_data._validate_add_action(data)

            curr_base = data.base_units[manage_type_data.unit_group]
            print(f"Current base unit for '{manage_type_data.unit_group}' is: {curr_base}")

            if manage_type_data.unit_group == "temperature":
                print(
                    f"\nYou will enter factor and offset so that:"
                    f"    new_unit_value = factor × {curr_base} + offset\n"
                )
                manage_type_data.factor = _get_users_input(
                    f"Enter conversion factor for '{manage_type_data.unit_type}': "
                )
                manage_type_data.offset = _get_users_input(
                    f"Enter conversion offset for '{manage_type_data.unit_type}': "
                )
            else:
                manage_type_data.value = _get_users_input(
                    f"Enter conversion factor to base unit "
                    f"'{curr_base}' of '{manage_type_data.unit_group}' group: "
                )

        elif manage_type_data.action == "remove":
            manage_type_data.unit_type = _get_users_input(
                f"Enter type to remove from '{manage_type_data.unit_group}' group: "
            )

    # Validates all variables and values
    manage_type_data._validate_for_manage_type(data)

    unit_group = manage_type_data.unit_group
    unit_type = manage_type_data.unit_type

    curr_base = data.base_units[unit_group]

    # Changes respective '.json' files
    if manage_type_data.action == "add":
        if unit_group == "temperature":
            user_factor = float(manage_type_data.factor)
            user_offset = float(manage_type_data.offset)

            # Gets value based on original base_unit (for original_units.json)
            canonical = _get_canonical_value(data, unit_group, [user_factor, user_offset])

            data.units[unit_group][unit_type] = [user_factor, user_offset]
            data.original_units[unit_group][unit_type] = canonical
        else:
            user_value = float(manage_type_data.value)

            # Gets value based on original base_unit (for original_units.json)
            canonical = _get_canonical_value(data, unit_group, user_value)

            data.units[unit_group][unit_type] = user_value
            data.original_units[unit_group][unit_type] = canonical

        data.unit_aliases[unit_group][unit_type] = unit_type
        message = f"'{unit_type}' was added to '{unit_group}'"
    elif manage_type_data.action == "remove":
        data.units[unit_group].pop(unit_type, None)
        data.original_units[unit_group].pop(unit_type, None)
        aliases_to_remove = [
            alias for alias, unit in data.unit_aliases[unit_group].items()
            if unit == unit_type
        ]
        for alias in aliases_to_remove:
            data.unit_aliases[unit_group].pop(alias, None)

        message = f"'{unit_type}' was removed from '{unit_group}'"

    try:
        # Persist changes
        _save_data(data.units, "units")
        _save_data(data.original_units, "original_units")
        _save_data(data.unit_aliases, "unit_aliases")
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        raise

    return message


def _get_canonical_value(data: DataStore, unit_group: str, value: float | list) -> float | list:
    """
    Converts value of new type to original base unit saved in original_units.json
    Prevents inconsistency when adding new type with base_unit is different from the original one
    """

    curr_base = data.base_units[unit_group]
    original = data.original_units[unit_group]

    if unit_group == "temperature":
        user_factor, user_offset = value
        curr_factor, curr_offset = original[curr_base]

        new_factor = user_factor * curr_factor
        new_offset = user_offset + (user_factor * curr_offset)

        return [new_factor, new_offset]

    else:
        # Grupos normais (multiplicativos)
        curr_factor = original[curr_base]
        _zero_division_checker(curr_factor)
        return value * curr_factor
