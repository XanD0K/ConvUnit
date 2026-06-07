from .aliases import _manage_aliases
from .change_base import _change_base_unit
from .convert import _conversion_logic
from .data_manager import _load_data, _reset_user_data
from .data_models import (
    DataStore, ConversionData, ManageGroupData,
    ManageTypeData, AliasesData, ChangeBaseData
)
from .display import _print_groups, _print_history, _reset_history, _print_types, _print_base
from .errors import AppError
from .groups import _manage_group as mg_action
from .manage_types import _manage_type as mt_action
from .utils import _validate_unit_group


__all__ = ["Converter"]


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
        """Returns a formatted string with all available unit groups."""

        return _print_groups(self._data)

    def history(self, limit: int = 10) -> str:
        """Returns the last conversion entries (default = 10)."""

        try:
            return _print_history(self._data, limit)
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def reset_history(self) -> bool:
        """Clears the conversion history log. Returns True on success."""
        
        return _reset_history(self._data)

    def types(self, unit_group: str | None = None) -> str:
        """Returns all unit types for a specific group."""

        try:
            if unit_group is None:
                return _print_types(self._data, "all")

            _validate_unit_group(unit_group.lower(), self._data)
            return _print_types(self._data, unit_group.lower())
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def all_types(self) -> str:
        """Returns all unit types for all groups."""

        try:
            return _print_types(self._data, "all")
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def base(self, unit_group: str | None = None) -> str:
        """Returns the base unit for a specific group."""

        try:
            if unit_group is None:
                return _print_base(self._data, "all")
            
            _validate_unit_group(unit_group.lower(), self._data)
            return _print_base(self._data, unit_group.lower())
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def all_bases(self) -> str:
        """Returns the base unit for all group."""

        return _print_base(self._data, "all")

    # ======================== CONVERSION ========================
    def convert(
        self, unit_group: str, from_type: str = None, to_type: str = None,
        amount: float = 1.0, time_input: str = None
    ) -> float | str:
        """
        Performs a unit conversion and returns the result.
        
        Supports both regular units and complex time/date conversions.
        """

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
            return (
                conversion_data.new_time
                if unit_group == "time"
                else conversion_data.new_value
            )
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    # ================== MANAGEMENT OPERATIONS ===================
    def manage_group(self, unit_group: str, action: str, new_base_unit: str = None) -> bool | str:
        """
        Adds or removes a custom unit group.

        Returns True on success or an error message on failure.
        """

        try:
            manage_group_data = ManageGroupData(
                unit_group=unit_group.lower(),
                action=action.lower(),
                new_base_unit=new_base_unit.lower() if new_base_unit else None
            )

            mg_action(self._data, manage_group_data)
            return True
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def manage_type(
        self, unit_group: str, unit_type: str, action: str,
        value: float = None, factor: float = None, offset: float = None
    ) -> bool:
        """
        Adds or removes a unit type.

        Returns True on success or an error message on failure.
        """

        try:
            _validate_unit_group(unit_group.lower(), self._data)
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
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def aliases(self, unit_group: str, unit_type: str, action: str, alias: str) -> bool | str:
        """Adds or removes an alias for a unit type."""

        try:
            _validate_unit_group(unit_group.lower(), self._data)
            aliases_data = AliasesData(
                unit_group=unit_group.lower(),
                unit_type=unit_type.lower(),
                action=action.lower(),
                alias=alias.lower()
            )

            _manage_aliases(self._data, aliases_data)
            return True
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def change_base(self, unit_group: str, new_base_unit: str) -> bool | str:
        """Changes the base unit for a group."""

        try:
            _validate_unit_group(unit_group.lower(), self._data)
            change_base_data = ChangeBaseData(
                unit_group=unit_group.lower(),
                new_base_unit=new_base_unit.lower()
            )

            _change_base_unit(self._data, change_base_data)
            return True
        except AppError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    # ===================== DATA MANAGEMENT ======================
    def reset(self) -> str:
        """Reset data files."""

        try:
            success = _reset_user_data()
            if success:
                return "Data files successfully reset to original state."
            else:
                return "Error: Failed to reset data files."
        except Exception as e:
            return f"Unexpected error while resetting data: {e}"

    # ====================== METHOD ALIASES ======================
    a = aliases
    cb = change_base
    b = base
    all_b = all_bases
    c = convert
    g = groups
    h = history
    mg = manage_group
    mt = manage_type
    t = types
    all_t = all_types
    reset_h = reset_history
