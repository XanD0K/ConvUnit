from typing import Optional

from .convert_time import _converter_time
from .data_manager import _add_to_log, _zero_division_checker
from .data_models import DataStore, ConversionData
from .time_utils import _print_time_instructions
from .utils import (
    _get_users_input, _get_unit_group, _get_converter_units,
    _get_amount, _format_value
)


def _conversion_logic(
    data: DataStore, conversion_data: Optional[ConversionData]=None
) -> str:
    """Handles all logic of unit conversion"""

    # Interactive approach
    if conversion_data is None:
        conversion_data = ConversionData(unit_group = _get_unit_group(data))
        if conversion_data.unit_group == "time":
            _print_time_instructions()
            conversion_data.time_input = _get_users_input("Enter time conversion: ")
        else:
            _get_converter_units(data, conversion_data)
            _get_amount(conversion_data)
    # Validates all variables and values
    conversion_data._validate_for_conversion(data)
    # Specific logic for time conversions
    if conversion_data.unit_group == "time":
        return _converter_time(data, conversion_data)
    conversion_data.new_value = _converter_standard(data, conversion_data)
    return (
        f"{_format_value(conversion_data.amount)} {conversion_data.from_type} = "
        f"{_format_value(conversion_data.new_value)} {conversion_data.to_type}"
    )


def _converter_standard(data: DataStore, conversion_data:ConversionData) -> float:
    """Handles conversions for non-time units"""

    unit_group = conversion_data.unit_group
    from_type = conversion_data.from_type
    to_type = conversion_data.to_type
    amount = conversion_data.amount

    # Checks for specific logic for temperature conversions
    if unit_group == "temperature":
        conversion_data.new_value = _converter_temp(data, conversion_data)
    else:
        _zero_division_checker(data.units[unit_group][to_type])
        conversion_data.new_value = amount * (
            data.units[unit_group][from_type]/data.units[unit_group][to_type]
        )
        
    # Adds to log file
    _add_to_log(data, conversion_data)
    return conversion_data.new_value


def _converter_temp(data: DataStore, conversion_data: ConversionData) -> float:
    """Handles conversion for temperature units"""

    unit_group = conversion_data.unit_group
    from_type = conversion_data.from_type
    to_type = conversion_data.to_type
    amount = conversion_data.amount

    # Gets factor and offset values for temperature conversions
    factor_from, offset_from = data.units[unit_group][from_type]
    factor_to, offset_to = data.units[unit_group][to_type]

    _zero_division_checker(factor_from)

    # Converts to base unit
    value_in_base = (amount - offset_from) / factor_from

    # Converts to destination unit
    result = (value_in_base * factor_to) + offset_to

    return result
