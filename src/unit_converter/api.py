from .aliases import _manage_aliases
from .change_base import _change_base_unit
from .convert import _conversion_logic
from .data_manager import _load_data
from .data_models import (
    DataStore, ConversionData, ManageGroupData,
    ManageTypeData, AliasesData, ChangeBaseData
)
from .display import (
    _print_groups, _print_history, _reset_history, _print_types, _print_base
)
from .groups import _manage_group as mg_action
from .manage_types import _manage_type as mt_action
from .utils import _validate_unit_group


class Converter():
    def __init__(self):
        try:
            # Initiates data variables related to all '.json' files
            (units, base_units, conversion_log, unit_aliases,
             month_days, original_units, month_aliases) = _load_data()
            self._data = DataStore(
                units, base_units,conversion_log,unit_aliases,
                month_days, original_units, month_aliases
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Converter: {e}") from e
    
    # ===================== READ OPERATIONS ======================
    def groups(self) -> str:
        """Returns all available unit groups"""

        return _print_groups(self._data)

    def history(self, limit: int=10) -> str:
        """Returns the last conversion entries (default = 10)"""

        try:
            return _print_history(self._data, limit)
        except Exception as e:
            return f"Error: {e}"
    
    def reset_history(self) -> bool:
        """Clears the conversion history log. Returns True on success."""
        
        return _reset_history(self._data)

    def types(self, unit_group: str) -> str:
        """Returns all unit types for a specific group"""

        try:
            _validate_unit_group(unit_group.lower(), self._data)
            return _print_types(self._data, unit_group.lower())
        except Exception as e:
            return f"Error: {e}"
    
    def all_types(self) -> str:
        """Returns all unit types for all groups"""

        try:
            return _print_types(self._data, "all")
        except Exception as e:
            return f"Error: {e}"
    
    def base(self, unit_group: str) -> str:
        """Returns the base unit for a specific group"""

        try:
            if unit_group is None:
                return _print_base(self._data, "all")
            
            _validate_unit_group(unit_group.lower(), self._data)
            return _print_base(self._data, unit_group.lower())
        except Exception as e:
            return f"Error: {e}"
    
    def all_bases(self) -> str:
        """Returns the base unit for all group"""

        return _print_base(self._data, "all")

    # ======================== CONVERSION ========================
    def convert(
        self, unit_group: str, from_type: str = None, to_type: str = None,
        amount: float = 1.0, time_input: str = None
    ) -> float | str:
        """Performs unit conversion"""

        try:
            _validate_unit_group(unit_group.lower(), self._data)
            conversion_data = ConversionData(
                unit_group=unit_group.lower(),
                time_input=time_input.lower() if time_input else None,
                from_type=from_type.lower() if from_type else None,
                to_type=to_type.lower() if to_type else None,
                amount=amount
            )

            _conversion_logic(self._data, conversion_data)
            return (conversion_data.new_time
                    if unit_group == "time"
                    else conversion_data.new_value
            )
        except Exception as e:
            return f"Error: {e}"

    # ================== MANAGEMENT OPERATIONS ===================
    def manage_group(self, unit_group: str, action: str, new_base_unit: str = None):
        """Adds or removes a unit group"""

        try:
            manage_group_data = ManageGroupData(
                unit_group=unit_group.lower(),
                action=action.lower(),
                new_base_unit=new_base_unit.lower() if new_base_unit else None
            )

            mg_action(self._data, manage_group_data)
            return True
        except Exception as e:
            return f"Error: {e}"

    def manage_type(
        self, unit_group: str, unit_type: str, action: str,
        value: float = None, factor: float = None, offset: float = None
    ) -> bool:
        """Adds or removes a unit type"""

        try:
            _validate_unit_group(unit_group.lower(), self)
            manage_type_data = ManageTypeData(
                unit_group=unit_group.lower(),
                action=action.lower(),
                unit_type=unit_type.lower(),
                value=value,
                factor=factor,
                offset=offset
            )

            mt_action(self._data, manage_type_data)
            return True
        except Exception as e:
            return f"Error: {e}"

    def aliases(self, unit_group: str, unit_type: str, action: str, alias: str):
        """Adds or removes an alias for a unit type"""

        try:
            _validate_unit_group(unit_group.lower(), self)
            aliases_data = AliasesData(
                unit_group=unit_group.lower(),
                unit_type=unit_type.lower(),
                action=action.lower(),
                alias=alias.lower()
            )

            _manage_aliases(self._data, aliases_data)
            return True
        except Exception as e:
            return f"Error: {e}"

    def change_base(self, unit_group: str, new_base_unit: str):
        """Changes the base unit for a group"""

        try:
            _validate_unit_group(unit_group.lower(), self)
            change_base_data = ChangeBaseData(
                unit_group=unit_group.lower(),
                new_base_unit=new_base_unit.lower()
            )

            _change_base_unit(self._data, change_base_data)
            return True
        except Exception as e:
            return f"Error: {e}"

    # ====================== METHOD ALIASES ======================
    g = groups
    h = history
    t = types
    c = convert
    mg = manage_group
    mt = manage_type
    a = aliases
    cb = change_base
