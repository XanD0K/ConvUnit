from datetime import datetime
from math import fabs

from .data_manager import _add_to_log, _zero_division_checker
from .data_models import DataStore, ConversionData
from .time_utils import(
    _parse_time_input, _parse_date_input, _get_seconds, _validate_date,
    _get_days_from_month, _get_index_from_month, _resolve_month_aliases
)
from .utils import _resolve_aliases, _format_value

_SECONDS_PER_DAY = 24 * 3600


def _converter_time(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion for time units"""

    # Segregates user's input
    args: list[str] = conversion_data.time_input.split()
    # Specific logic based on user's input
    if len(args) == 2:
        return _converter_time_2args(data, conversion_data)
    elif len(args) == 3:
        return _converter_time_3args(data, conversion_data)
    # E.g. 5 years 10 months 10 days 8 hours 56 minutes seconds
    elif len(args) > 3 and len(args) % 2 != 0:
        return _converter_time_multiple_args(data, conversion_data, args)
    else:
        raise ValueError("Invalid format for date and time conversion!")


def _converter_time_2args(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of 2 arguments expression"""

    _zero_division_checker(
        data.units[conversion_data.unit_group][conversion_data.factor_time]
    )

    # E.g. 17h:28m:36s seconds
    if _is_time(conversion_data.from_time):
        message = _handle_time(data, conversion_data)
    # E.g. JAN minutes
    elif _is_month(data, conversion_data.from_time):
        message = _handle_month(data, conversion_data)
    # E.g. 2019-11-04 days
    elif _is_date(conversion_data.from_time):
        message = _handle_date(data, conversion_data)
    else:
        raise ValueError("Invalid 2-argument time format")

    _add_to_log(data, conversion_data, is_time_convertion=True)
    return message


def _converter_time_3args(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of 3 arguments expression"""

    # Declare variables to reduce code's verbosity
    from_time = conversion_data.from_time
    to_time = conversion_data.to_time

    # E.g. minutes seconds 1
    if _is_time_unit(data, from_time) and _is_time_unit(data, to_time):
        message = _handle_unit_to_unit(data, conversion_data)
    else:
        conversion_data._validate_factor_time(data)
        _zero_division_checker(
            data.units[conversion_data.unit_group][conversion_data.factor_time]
        )

        # E.g. 17h:28m:36s 04h:15m:22s seconds
        if _is_time(from_time) and _is_time(to_time):
            message = _handle_time_to_time(data, conversion_data)
        # E.g. JAN DEC days
        elif _is_month(data, from_time) and _is_month(data, to_time):
            message = _handle_month_to_month(data, conversion_data)
        # E.g. 2019-11-04 2056-04-28 days
        elif _is_date(from_time) and _is_date(to_time):
            message = _handle_date_to_date(data, conversion_data)
        else:
            raise ValueError("Invalid 3-argument time format")

    _add_to_log(data, conversion_data, is_time_convertion=True)
    return message


def _converter_time_multiple_args(
    data: DataStore, conversion_data: ConversionData, args: list[str]
) -> str:
    """Handles conversion of multiple arguments expression"""

    conversion_data.to_time = args[-1]

    _zero_division_checker(
        data.units[conversion_data.unit_group][conversion_data.to_time]
    )

    # Keeps track of every block of (value, unit_type)
    formatted_value: list[tuple[str, str]] = []
    total_seconds: int = 0
    for number, unit in zip(args[0::2], args[1::2]):
        number = float(number)  # type: ignore[assignment]
        unit = _resolve_aliases(data, conversion_data.unit_group, unit)
        total_seconds =  total_seconds + (
            number * data.units[conversion_data.unit_group][unit]
        )
        formatted_value.append((_format_value(number), unit))

    conversion_data.from_time = (
        " ".join(f"{num} {unit}" for num, unit in formatted_value)
    )
    conversion_data.new_time = (
        total_seconds / data.units[conversion_data.unit_group][conversion_data.to_time]
    )

    _add_to_log(data, conversion_data, is_time_convertion=True)
    return (
        f"{' '.join(f'{num} {unit}' for num, unit in formatted_value)} = "
        f"{_format_value(conversion_data.new_time)} {conversion_data.to_time}"
    )


def _is_time(time: str) -> bool:
    """Checks for time format"""

    return any(char in time for char in (":", "h", "m", "s"))


def _is_month(data: DataStore, time: str) -> bool:
    """Checks for month format"""

    return time in data.month_aliases


def _is_date(date: str) -> bool:
    """Checks for date format"""

    return "-" in date


def _is_time_unit(data: DataStore, time: str) -> bool:
    """Checks for time unit format"""

    return time in data.unit_aliases["time"]


def _handle_time(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of single time unit"""

    total_seconds: float = _parse_time_input(conversion_data.from_time)
    conversion_data.new_time = (
        total_seconds / data.units[conversion_data.unit_group][conversion_data.factor_time]
    )

    return (
        f"There are {_format_value(conversion_data.new_time)} "
        f"{conversion_data.factor_time} in {conversion_data.from_time}"
    )


def _handle_month(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of single month unit"""

    from_time = _resolve_month_aliases(data, conversion_data.from_time)
    days: int = _get_days_from_month(data, from_time)
    total_seconds = days * data.units[conversion_data.unit_group]["days"]
    conversion_data.new_time = (
        total_seconds / data.units[conversion_data.unit_group][conversion_data.factor_time]
    )
    return (
        f"There are {_format_value(conversion_data.new_time)} "
        f"{conversion_data.factor_time} in {from_time}"
    )


def _handle_date(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of single date unit"""

    years, months, days = _parse_date_input(conversion_data.from_time)
    total_seconds = _get_seconds(
        data, conversion_data.unit_group, years, months, days
    )
    conversion_data.new_time = (
        total_seconds / data.units[conversion_data.unit_group][conversion_data.factor_time]
    )
    return (
        f"There are {_format_value(conversion_data.new_time)} "
        f"{conversion_data.factor_time} in "
        f"{years} years, {months} months, {days} days"
    )


def _handle_unit_to_unit(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of unit to unit expression"""

    from_time = _resolve_aliases(
        data, conversion_data.unit_group, conversion_data.from_time
    )
    to_time = _resolve_aliases(
        data, conversion_data.unit_group, conversion_data.to_time
    )
    total_seconds: float = (
        conversion_data.factor_time * data.units[conversion_data.unit_group][from_time]
    )
    _zero_division_checker(data.units[conversion_data.unit_group][to_time])
    conversion_data.new_time = (
        total_seconds / data.units[conversion_data.unit_group][to_time]
    )

    return (
        f"{_format_value(conversion_data.factor_time)} {from_time} = "
        f"{_format_value(conversion_data.new_time)} {to_time}"
    )


def _handle_time_to_time(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of time to time expression"""

    new_from_time: int = _parse_time_input(conversion_data.from_time)
    new_to_time: int = _parse_time_input(conversion_data.to_time)
    if new_from_time < _SECONDS_PER_DAY and new_to_time < new_from_time:
        new_to_time += _SECONDS_PER_DAY
    conversion_data.new_time = fabs(
        (new_from_time - new_to_time) / data.units[conversion_data.unit_group][conversion_data.factor_time]
    )
    return (
        f"There are {_format_value(conversion_data.new_time)} "
        f"{conversion_data.factor_time} between {conversion_data.from_time} "
        f"and {conversion_data.to_time}"
    )


def _handle_month_to_month(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of month to month expression"""

    from_month = _resolve_month_aliases(data, conversion_data.from_time)
    to_month = _resolve_month_aliases(data, conversion_data.to_time)

    from_index = _get_index_from_month(data, from_month)
    to_index = _get_index_from_month(data, to_month)
    to_days = _get_days_from_month(data, to_month)

    BASE_YEAR = 1

    from_datetime: datetime = datetime(BASE_YEAR, from_index, 1)
    if to_index >= from_index:
        to_datetime: datetime = datetime(BASE_YEAR, to_index, to_days)
    else:
        to_datetime: datetime  = datetime(BASE_YEAR + 1, to_index, to_days)

    days: float = abs((from_datetime - to_datetime).days) + 1

    if conversion_data.factor_time == "days":
        conversion_data.new_time = days
    else:
        total_seconds = days * data.units[conversion_data.unit_group]["days"]
        _zero_division_checker(
            data.units[conversion_data.unit_group][conversion_data.factor_time]
        )
        conversion_data.new_time = (
            total_seconds / data.units[conversion_data.unit_group][conversion_data.factor_time]
        )

    return (
        f"Between {from_month} and {to_month} there are "
        f"{_format_value(conversion_data.new_time)} {conversion_data.factor_time}"
    )


def _handle_date_to_date(data: DataStore, conversion_data: ConversionData) -> str:
    """Handles conversion of date to date expression"""

    try:
        from_y, from_m, from_d = _parse_date_input(conversion_data.from_time)
        _validate_date(from_y, from_m, from_d)
        to_y, to_m, to_d = _parse_date_input(conversion_data.to_time)
        _validate_date(to_y, to_m, to_d)
    except ValueError as e:
        raise ValueError("Invalid date!") from e

    from_date = datetime(from_y, from_m, from_d)
    to_date = datetime(to_y, to_m, to_d)
    total_days = abs((to_date - from_date).days) + 1

    total_seconds = total_days * data.units[conversion_data.unit_group]["days"]
    conversion_data.new_time = (
        total_seconds / data.units[conversion_data.unit_group][conversion_data.factor_time]
    )
    
    return (
        f"Between {conversion_data.from_time} and {conversion_data.to_time} "
        f"there are {_format_value(conversion_data.new_time)} "
        f"{conversion_data.factor_time}"
    )
