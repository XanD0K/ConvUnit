from typing import Optional

from .convert_time import _converter_time
from .data_manager import _add_to_log
from .data_models import DataStore, ConversionData
from .time_utils import _print_time_instructions
from .utils import (
    _get_user_input, _get_unit_group, _get_converter_units,
    _get_amount, _format_value, _ensure_non_zero
)


__all__ = ["_conversion_logic"]


def _conversion_logic(data: DataStore, conversion_data: Optional[ConversionData] = None) -> str:
    """Main entry point for unit conversion logic (interactive and direct)."""

    # Interactive approach
    if conversion_data is None:
        conversion_data = ConversionData(unit_group = _get_unit_group(data))
        if conversion_data.unit_group == "time":
            _print_time_instructions()
            conversion_data.time_input = _get_user_input("Enter time conversion: ")
        else:
            _get_converter_units(data, conversion_data)
            _get_amount(conversion_data)
    # Validates all variables and values
    conversion_data._validate_for_conversion(data)
    # Specific logic for time conversions
    if conversion_data.unit_group == "time":
        return _converter_time(data, conversion_data)
    conversion_data.new_value = _converter_standard_units(data, conversion_data)
    return (
        f"{_format_value(conversion_data.amount)} {conversion_data.from_type} = "
        f"{_format_value(conversion_data.new_value)} {conversion_data.to_type}"
    )


def _converter_standard_units(data: DataStore, conversion_data: ConversionData) -> float:
    """Performs standard (non-time, non-temperature) unit conversion and logs it."""

    unit_group = conversion_data.unit_group
    from_type = conversion_data.from_type
    to_type = conversion_data.to_type
    amount = conversion_data.amount

    # Checks for specific logic for temperature conversions
    if unit_group == "temperature":
        conversion_data.new_value = _converter_temperature(data, conversion_data)
    else:
        _ensure_non_zero(data.units[unit_group][to_type])
        conversion_data.new_value = amount * (
            data.units[unit_group][from_type]/data.units[unit_group][to_type]
        )
        
    # Adds to log file
    _add_to_log(data, conversion_data)
    return conversion_data.new_value


def _converter_temperature(data: DataStore, conversion_data: ConversionData) -> float:
    """Performs temperature conversion using factor and offset."""

    unit_group = conversion_data.unit_group
    from_type = conversion_data.from_type
    to_type = conversion_data.to_type
    amount = conversion_data.amount

    # Gets factor and offset values for temperature conversions
    factor_from, offset_from = data.units[unit_group][from_type]
    factor_to, offset_to = data.units[unit_group][to_type]

    _ensure_non_zero(factor_from)

    # Converts to base unit
    value_in_base = (amount - offset_from) / factor_from

    # Converts to destination unit
    result = (value_in_base * factor_to) + offset_to

    return result
