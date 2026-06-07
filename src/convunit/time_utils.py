import calendar
import re

from typing import TYPE_CHECKING

from .errors import InvalidInputError, UnitGroupNotFoundError
from .utils import _print_divider

if TYPE_CHECKING:
    from .data_models import DataStore


__all__ = [
    "_print_time_instructions",
    "_resolve_month_aliases",
    "_parse_time_input",
    "_parse_time_component",
    "_calculate_approximate_seconds",
    "_parse_date_input",
    "_validate_date",
    "_get_days_from_month",
    "_get_index_from_month",
    "_calculate_leap_years",   # Kepts for future usage
    "_is_leap",                # Kepts for future usage
    "_get_days_from_index",    # Kepts for future usage
]

_APPROX_DAYS_PER_YEAR = 365.2425
_APPROX_DAYS_PER_MONTH = 30.436875


def _print_time_instructions() -> None:
    """Prints instructions for supported date and time input formats."""

    print(
        _print_divider("-"),
        "For date-time conversions, you can choose from different formats:",
        " - <unit_type> [unit_type] <amount> → E.g. 'minutes seconds 10",
        " - HH:MM:SS [HH:MM:SS] <unit_type> → E.g. '17h:28m:36s [04h:15m:22s] seconds'",
        " - <month_name> [month_name] <unit_type> →E.g. 'JAN [DEC] days'",
        " - YYYY-MM-DD [YYYY-MM-DD] <unit_type> → E.g. 2019-11-04 [2056-04-28] days",
        " - <amount> <unit_type> [<amount> <unit_type>] <unit_type>"
        " → E.g. 1 century 1 decade 1 month 1 hour seconds",
        sep="\n"
    )


def _resolve_month_aliases(data: "DataStore", month: str) -> str:
    """Resolves a month name or alias to its canonical form."""

    # Checks for literal name
    if month in data.month_aliases:
        return data.month_aliases[month]
    raise InvalidInputError(f"Month '{month}' is not a valid month!")


def _parse_time_input(time_str: str) -> int:
    """Parses a time string (e.g. '17h:28m:36s') and returns total seconds."""

    if matches := re.search(r"^(?:(\d+)h)?(?:(?:\:)?(\d+)m)?(?:(?:\:)?(\d+)s)?$", time_str):
        hours, minutes, seconds = matches.group(1), matches.group(2), matches.group(3)
        hours = _parse_time_component(hours)
        minutes = _parse_time_component(minutes)
        seconds = _parse_time_component(seconds)
        return hours * 3600 + minutes * 60 + seconds
    raise InvalidInputError("Invalid time format!")


def _parse_time_component(time_str: str) -> int:
    """Converts a time component to int. Returns 0 if None or empty."""

    return int(time_str or 0)


def _calculate_approximate_seconds(
    data: "DataStore", unit_group: str, years: int, months: int, days: int
) -> float:
    """Calculates approximate duration in seconds using average year/month lengths."""

    try:
        approx_year_duration: float = (
            _APPROX_DAYS_PER_YEAR * data.units[unit_group]["days"]
        )
        approx_month_duration: float = (
            _APPROX_DAYS_PER_MONTH * data.units[unit_group]["days"]
        )
        days_to_seconds = data.units[unit_group]["days"]
        return (
            years * approx_year_duration +
            months * approx_month_duration +
            days * days_to_seconds
        )
    except KeyError:
        raise UnitGroupNotFoundError(f"'{unit_group}' is not a valid group!")


def _parse_date_input(time_str: str) -> tuple[int, int, int]:
    """Parses a date string in YYYY-MM-DD format and returns (year, month, day)."""

    if matches := re.search(r"^(\d+)-(\d+)-(\d+)$", time_str):
        year, month, day = map(int, matches.groups())
        return year, month, day
    raise InvalidInputError("Invalid date format! Usage: YYYY-MM-DD")


def _validate_date(year: int, month: int, day: int) -> bool:
    """Validates that a year, month, and day form a valid calendar date."""

    if not 1 <= month <= 12:
        raise InvalidInputError(f"Invalid date! '{month}' is not a valid month")
    max_days = calendar.monthrange(year, month)[1]
    if not 1 <= day <= max_days:
        raise InvalidInputError(f"Invalid date! '{day}' is not a valid day for month {month}")
    return True


def _get_days_from_month(data: "DataStore", month: str) -> int:
    """Returns the number of days in a given month name."""

    days = next((value[month] for value in data.month_days.values() if month in value), None)
    if days is None:
        raise InvalidInputError(f"Invalid month: '{month}'")
    return days


def _get_index_from_month(data: "DataStore", month: str) -> int:
    """Returns the numeric index (1-12) of a given month name."""

    index = next((int(index) for index, value in data.month_days.items() if month in value), None)
    if index is None:
        raise InvalidInputError(f"Invalid month: '{month}'")
    return index


# This function is currently not being used, but was kept for future purpose
def _calculate_leap_years(
    from_years: int, from_months: int, to_years: int, to_months: int, to_days: int
) -> int:
    """Calculates the number of leap years from a date range."""

    leap_year_counter = (
        (to_years // 4) - ((from_years-1) // 4) -
        (to_years // 100) - ((from_years-1) // 100) +
        (to_years // 400) - ((from_years-1) // 400)
    )

    if _is_leap(from_years) and from_months > 2:
        leap_year_counter -= 1
    if _is_leap(to_years) and (to_months < 2 or (to_months == 2 and to_days < 29)):
        leap_year_counter -= 1

    return leap_year_counter


# This function is currently not being used, but was kept for future purpose
def _is_leap(year: int) -> bool:
    """Checks if a years is a leap year."""

    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


# This function is currently not being used, but was kept for future purpose
def _get_days_from_index(data: "DataStore", month_index: str) -> int:
    """Returns the number of days for a given month index (kept for future use)."""

    days = next(iter(data.month_days[month_index].values()), None)
    if days is None:
        raise InvalidInputError(f"Invalid index: {month_index}")
    return days
