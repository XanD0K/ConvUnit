from typing import Optional

from .errors import InvalidInputError, DuplicateError, UnitNotFoundError,UnitGroupNotFoundError
from .time_utils import _parse_date_input, _validate_date
from .utils import _validate_unit_group, _resolve_aliases


__all__ = [
    "DataStore",
    "ConversionData",
    "ManageGroupData",
    "ManageTypeData",
    "AliasesData",
    "ChangeBaseData",
]


class DataStore:
    """Container for all data loaded from JSON files."""

    def __init__(
        self, units: dict, base_units: dict, conversion_log: list,
        unit_aliases: dict, month_days: dict, original_units: dict,
        month_aliases: dict
    ):
        self.units = units
        self.base_units = base_units
        self.conversion_log = conversion_log
        self.unit_aliases = unit_aliases
        self.month_days = month_days
        self.original_units = original_units
        self.month_aliases = month_aliases

class ConversionData:
    """Holds input and output data for a conversion operation."""

    def __init__(
        self, unit_group: str, from_type: str = None, to_type: str = None,
        amount: float | str = None, new_value: float = None, time_input: str = None,
        from_time: str = None, to_time: str = None, factor_time: str | float = None,
        new_time: float = None
    ):
        self.unit_group = unit_group
        self.from_type = from_type
        self.to_type = to_type
        self.amount = amount
        self.new_value = new_value
        self.time_input = time_input
        self.from_time = from_time
        self.to_time = to_time
        self.factor_time = factor_time
        self.new_time = new_time

    def _resolve_and_validate_type(self, data: DataStore, value: str) -> str:
        if value in data.unit_aliases[self.unit_group]:
            value = _resolve_aliases(data, self.unit_group, value)
        
        if value not in data.units[self.unit_group]:
            raise UnitNotFoundError(f"'{value}' is not a valid type for '{self.unit_group}'!")
    
        return value

    def _validate_from_type(self, data: DataStore) -> None:
        if not self.from_type:
            raise InvalidInputError("'unit_type' cannot be empty!")
        
        self.from_type = self._resolve_and_validate_type(data, self.from_type)

    def _validate_to_type(self, data: DataStore) -> None:
        if not self.to_type:
            raise InvalidInputError("'unit_type' cannot be empty!")
        
        self.to_type = self._resolve_and_validate_type(data, self.to_type)

    def _validate_amount(self) -> None:
        if self.amount is None:
            raise InvalidInputError("'amount' cannot be empty")
        
        try:
            self.amount = float(self.amount)
        except (ValueError, TypeError):
            raise InvalidInputError("Amount must be a number.")     
          
        # Prevents negative value for "Kelvin"
        if (self.amount < 0 and self.unit_group == "temperature" and self.from_type == "kelvin"):
            raise InvalidInputError("Kelvin temperature cannot be negative!")

    def _validate_time_input(self) -> None:
        if not self.time_input:
            raise InvalidInputError("Time conversion cannot be empty!")
        if len(self.time_input.split()) < 2:
            raise InvalidInputError("Invalid time conversion format!")
           
    def _validate_from_time(self, data: DataStore) -> None:
        if not self.from_time:
            raise InvalidInputError("'from_time' cannot be empty!")

        elif (self.from_time in data.unit_aliases[self.unit_group]):
            self.from_time = _resolve_aliases(data, self.unit_group, self.from_time)

        elif any(char in self.from_time for char in (":", "h", "m", "s")):
            pass
        elif self.from_time in data.month_aliases:
            pass
        elif "-" in self.from_time:
            years, months, days = _parse_date_input(self.from_time) 
            if self.to_time:
                _validate_date(years, months, days)
        else:
            raise InvalidInputError(f"Invalid 'from_time': '{self.from_time}'")

    def _validate_to_time(self, data: DataStore) -> None:
        if not self.to_time:
            raise InvalidInputError("'to_time' cannot be empty!")

        elif (self.to_time in data.unit_aliases[self.unit_group]):
            self.to_time = _resolve_aliases(data, self.unit_group, self.to_time)

        elif any(char in self.to_time for char in (":", "h", "m", "s")):
            pass
        elif self.to_time in data.month_aliases:
            pass
        elif "-" in self.to_time:
            years, months, days = _parse_date_input(self.to_time)
            _validate_date(years, months, days)
        else:
            raise InvalidInputError(f"Invalid 'to_time': '{self.to_time}'")

    def _validate_factor_time(self, data: DataStore) -> None:
        if not self.factor_time:
            raise InvalidInputError("'factor_time' cannot be empty!")
        
        try:
            self.factor_time = float(self.factor_time)
        except (ValueError, TypeError):
            if (self.factor_time in data.unit_aliases[self.unit_group]):
                self.factor_time = _resolve_aliases(data, self.unit_group, str(self.factor_time))

            if self.factor_time not in data.units[self.unit_group]:
                raise UnitNotFoundError(
                    f"Factor time '{self.factor_time}' not found in '{self.unit_group}' group!"
                )
    
    def _validate_multiple_time_args(self, data: DataStore, args: list[str]) -> None:
        for number, unit in zip(args[0::2], args[1::2]):
            try:
                float(number)
            except (ValueError, TypeError):
                raise InvalidInputError(f"'{number}' is an invalid amount!")

            try:
                resolved_unit = _resolve_aliases(data, self.unit_group, unit)
            except (ValueError, TypeError):
                raise InvalidInputError(f"'{unit}' is an invalid unit type!")

            if resolved_unit not in data.units[self.unit_group]:
                raise InvalidInputError(
                    f"'{resolved_unit}' is not a type for '{self.unit_group}' group!"
                )

    def _validate_time_args(self, data: DataStore) -> None:
        args: list[str] = self.time_input.split()

        if len(args) == 2:
            self.from_time, self.factor_time = args
        elif len(args) == 3:
            self.from_time, self.to_time, self.factor_time = args
        elif len(args) > 3 and len(args) % 2 != 0:
            self.to_time = args[-1]
            self._validate_multiple_time_args(data, args)
        else:
            raise InvalidInputError("Invalid time conversion format!")
        if self.from_time:
            self._validate_from_time(data)
        if self.to_time:
            self._validate_to_time(data)
        if self.factor_time:
            self._validate_factor_time(data)

    def _validate_for_conversion(self, data: DataStore) -> None:
        _validate_unit_group(self.unit_group, data)
        if self.unit_group == "time":
            self._validate_time_input()
            self._validate_time_args(data)
        else:   
            if (self.from_type is None and self.to_type is None and self.amount is None):
                raise InvalidInputError("Invalid conversion format!")
            self._validate_from_type(data)
            self._validate_to_type(data)
            self._validate_amount()


class ManageGroupData:
    """Holds data and validation logic for managing unit groups."""

    def __init__(
        self, unit_group: str|None, action: Optional[str] = None,
        new_base_unit: Optional[str] = None
    ):
    
        self.unit_group = unit_group
        self.action = action
        self.new_base_unit = new_base_unit

    def _validate_action(self) -> None:
        if not self.action:
            raise InvalidInputError("'action' cannot be empty!")
        if self.action not in ["add", "remove"]:
            raise InvalidInputError(f"Invalid action: '{self.action}'")

    def _validate_add_action(self, data: DataStore) -> None:
        if self.unit_group in data.units:
            raise DuplicateError(f"'{self.unit_group}' already exists!")
           
    def _validate_remove_action(self,data: DataStore) -> None:
        if self.unit_group not in data.units:
            raise UnitGroupNotFoundError(f"'{self.unit_group}' does not exist!")
        if self.new_base_unit:
            raise InvalidInputError("Incorrect usage! Use: <unit_group> remove")
        
    def _validate_new_base_unit(self, data: DataStore) -> None:
        if not self.new_base_unit:
            raise InvalidInputError("'new_base_unit' cannot be empty")
        if self.new_base_unit in data.units:
            raise DuplicateError(f"'{self.new_base_unit}' is already a group name!")
        if self.new_base_unit == self.unit_group:
            raise InvalidInputError(f"'new_base_unit' cannot have the same name as 'unit_group'")

    def _validate_for_manage_group(self, data: DataStore) -> None:
        self._validate_action()
        if self.action == "add":
            self._validate_add_action(data)
            self._validate_new_base_unit(data)
        elif self.action == "remove":
            _validate_unit_group(self.unit_group, data)
            self._validate_remove_action(data)


class ManageTypeData:
    """Holds data for managing unit types."""

    def __init__(
        self, unit_group: str, unit_type: Optional[str] = None,
        action: Optional[str] = None, value: Optional[str|float] = None,
        factor: Optional[str|float] = None, offset: Optional[str|float] = None
    ):
        self.unit_group = unit_group
        self.unit_type = unit_type
        self.action = action
        self.value = value
        self.factor = factor
        self.offset = offset

    def _validate_action(self) -> None:
        if not self.action:
            raise InvalidInputError("'action' cannot be empty!")
        if self.action not in ["add", "remove"]:
            raise InvalidInputError(f"Invalid action: '{self.action}'")

    def _validate_add_action(self, data: DataStore) -> None:
        if not self.unit_type:
            raise InvalidInputError("'unit_type' cannot be empty!")
        if self.unit_type in data.unit_aliases[self.unit_group]:
            raise DuplicateError(f"'{self.unit_type}' already exists in '{self.unit_group}'!")

    def _validate_remove_action(self, data: DataStore) -> None:
        if not self.unit_type:
            raise InvalidInputError("'unit_type' cannot be empty!")
        
        if self.unit_type in data.unit_aliases[self.unit_group]:
            self.unit_type = _resolve_aliases(data, self.unit_group, self.unit_type)

        if self.unit_type not in data.units[self.unit_group]:
            raise UnitNotFoundError(f"'{self.unit_type}' does not exist in '{self.unit_group}'!")
        if self.unit_type == data.base_units[self.unit_group]:
            raise InvalidInputError("Cannot remove the base unit!")
        if self.value or self.factor or self.offset:
            raise InvalidInputError(
                "Incorrect usage when removing a type! "
                "Usage: <unit_group> remove <unit_type>"
            )

    def _validate_value(self) -> None:
        if not self.value:
            raise InvalidInputError("'value' cannot be empty!")
        try:
            self.value = float(self.value)
        except (ValueError, TypeError):
            raise InvalidInputError("Invalid conversion factor!")

    def _validate_factor(self) -> None:
        if not self.factor:
            raise InvalidInputError("'factor' cannot be empty!")
        try:
            self.factor = float(self.factor)
        except (ValueError, TypeError):
            raise InvalidInputError("Invalid conversion factor!")
        if self.unit_group == "temperature":
            if self.factor == 0:
                raise InvalidInputError("Conversion factor cannot be zero for temperature!")
        else:
            if self.factor <= 0:
                raise InvalidInputError("Conversion factor must be positive!")
            

    def _validate_offset(self) -> None:
        if not self.offset:
            raise InvalidInputError("'offset' cannot be empty!")
        try:
            self.offset = float(self.offset)
        except (ValueError, TypeError):
            raise InvalidInputError("Invalid conversion offset!")

    def _validate_for_manage_type(self, data: DataStore) -> None:
        _validate_unit_group(self.unit_group, data)
        self._validate_action()
        if self.action == "add":
            self._validate_add_action(data)
            if self.unit_group == "temperature":
                self._validate_factor()
                self._validate_offset()
            else:
                self._validate_value()
        elif self.action == "remove":
            self._validate_remove_action(data)


class AliasesData:
    """Holds data for managing aliases."""

    def __init__(
        self, unit_group: str, unit_type: Optional[str] = None,
        action: Optional[str] = None, alias: Optional[str] = None
    ):
        self.unit_group = unit_group
        self.unit_type = unit_type
        self.action = action
        self.alias = alias

    def _validate_unit_type(self, data: DataStore) -> None:
        if not self.unit_type:
            raise InvalidInputError("'unit_type' cannot be empty!")
        
        if self.unit_type in data.unit_aliases[self.unit_group]:
            self.unit_type = _resolve_aliases(data, self.unit_group, self.unit_type)

        if self.unit_type not in data.units[self.unit_group]:
            raise UnitNotFoundError(
                f"'{self.unit_type}' is not a valid unit type in '{self.unit_group}'!"
            )

    def _validate_action(self) -> None:
        if not self.action:
            raise InvalidInputError("'action' cannot be empty!")        
        if self.action not in ["add", "remove"]:
            raise InvalidInputError(f"Invalid action: '{self.action}'")

    def _validate_alias(self, data: DataStore) -> None:
        if not self.alias:
            raise InvalidInputError("'alias' cannot be empty!")
        
        aliases: list[str] = [
            alias for alias in data.unit_aliases[self.unit_group]
            if alias != self.unit_type
        ]

        if self.action == "add":
            if self.alias in aliases:
                raise DuplicateError(f"'{self.alias}' already exists!")            
            if self.alias in data.base_units:
                raise DuplicateError(f"'{self.alias}' is already a unit group!")            
            if self.alias in data.units[self.unit_group]:
                raise DuplicateError(f"'{self.alias}' is already a unit type!")            
        else:
            if self.alias not in aliases:
                raise InvalidInputError(f"'{self.alias}' does not exist!")            
            if data.unit_aliases[self.unit_group].get(self.alias) != self.unit_type:
                raise InvalidInputError(f"'{self.alias}' does not belong to '{self.unit_type}'!")

    def _validate_for_aliases(self, data: DataStore) -> None:
        _validate_unit_group(self.unit_group, data)
        self._validate_unit_type(data)
        self._validate_action()
        self._validate_alias(data)


class ChangeBaseData:
    """Holds data for changing base unit."""

    def __init__(self, unit_group: str, new_base_unit:str | None):
        self.unit_group = unit_group
        self.new_base_unit = new_base_unit

    def _validate_for_change_base(self, data: DataStore) -> None:
        _validate_unit_group(self.unit_group, data)

        if not self.new_base_unit:
            raise InvalidInputError("'new_base_unit' cannot be empty!")       

        if self.new_base_unit in data.unit_aliases[self.unit_group]:
            self.new_base_unit = _resolve_aliases(data, self.unit_group, self.new_base_unit)

        if self.new_base_unit not in data.units[self.unit_group]:
            raise UnitNotFoundError(f"'{self.new_base_unit}' is not a valid unit type!")
        if self.new_base_unit == data.base_units[self.unit_group]:
            raise InvalidInputError(f"'{self.new_base_unit}' is already the base unit!")
