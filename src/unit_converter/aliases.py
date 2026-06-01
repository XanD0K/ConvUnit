from typing import Optional

from .data_manager import _save_data
from .data_models import DataStore, AliasesData
from .utils import _get_users_input, _get_unit_group


def _manage_aliases(
    data: DataStore, aliases_data: Optional[AliasesData]=None
) -> str:
    """Handles aliases, allowing users to add or remove aliases to/from an unit type"""

    # Interactive approach
    if aliases_data is None:
        aliases_data = AliasesData(unit_group = _get_unit_group(data))

        aliases_data.unit_type = _get_users_input(
            f"Enter unit type for '{aliases_data.unit_group}' group: "
        )
        aliases_data._validate_unit_type(data)

        existing_aliases = [
            alias for alias, target in data.unit_aliases[aliases_data.unit_group].items()
            if target == aliases_data.unit_type and alias != aliases_data.unit_type
        ]
        if not existing_aliases:
            aliases_data.action = "add"
            prompt = f"'{aliases_data.unit_type}' has no alias. Enter new alias: "
        else:
            aliases_data.action = _get_users_input(
                f"Existed aliases for '{aliases_data.unit_type}': {existing_aliases}. "
                f"What do you want to do? ('add' or 'remove') "
            )
            aliases_data._validate_action()

            verb = "to" if aliases_data.action == "add" else "from"
            prompt = (
                f"Which alias do you want to {aliases_data.action} "
                f"{verb} '{aliases_data.unit_type}'? "
            )

        aliases_data.alias = _get_users_input(prompt)

    # Validates all variables and values
    aliases_data._validate_for_aliases(data)

    unit_group = aliases_data.unit_group
    alias = aliases_data.alias

    # Changes respective '.json' files
    if aliases_data.action == "add":
        data.unit_aliases[unit_group][alias] = aliases_data.unit_type
        message = f"Alias {alias} successfully added!"
    elif aliases_data.action == "remove":
        data.unit_aliases[unit_group].pop(alias) 
        message = f"Alias '{alias}' successfully removed!"

    try:
        # Persist changes
        _save_data(data.unit_aliases, "unit_aliases")
    except Exception:
        print("Warning: Changes were applied in memory, but could not be saved to disk.")
        raise 

    return message
