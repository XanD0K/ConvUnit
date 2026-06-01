import argparse
import sys

from .aliases import _manage_aliases
from .change_base import _change_base_unit
from .convert import _conversion_logic
from .data_models import (
    DataStore, ConversionData, ManageGroupData,
    ManageTypeData, AliasesData, ChangeBaseData
)
from .display import (
    _print_groups, _print_history, _reset_history,
    _print_types, _validate_for_history, _print_base
)
from .groups import _manage_group
from .manage_types import _manage_type
from .utils import _validate_unit_group


# CLI approach
def _handle_cli(data: DataStore, args: list[str]) -> None:
    """Handles command-line interface (CLI)"""

    # Creates a shallow copy of all command-line arguments
    formatted_args: list[str] = args[:]

    # Adds description to program
    parser = argparse.ArgumentParser(
        prog="Unit Converter", description="Convert multiple types of units"
    )

    # Defines subparser to handle multiple commands
    subparser = parser.add_subparsers(dest="command", help="Available commands")

    # 'groups' command
    subparser.add_parser("groups", aliases=["g"], help="List all unit groups")
    # 'history' command
    history_parser = subparser.add_parser(
        "history", aliases=["h"], help="Displays conversion history (default=10)"
    )
    history_parser.add_argument(
        "--limit", "-l", type=int, default=10, help="Number of entries to be printed"
    )
    history_parser.add_argument(
        "--reset", "-r", action="store_true", help="Resets history log"
    )
    # 'types' command
    types_parser = subparser.add_parser(
        "types", aliases=["t"], help="Displays all unit types in a group"
    )
    types_parser.add_argument(
        "unit_group", nargs="?", help="Unit group (use --all|-a to show all groups)"
    )
    types_parser.add_argument(
        "--all", "-a", action="store_true", help="Shows types for all groups"
    )
    # 'convert' command 
    convert_parser = subparser.add_parser(
        "convert", aliases=["c"], help="Converts values"
    )
    convert_parser.add_argument("unit_group", help="Unit group")
    convert_parser.add_argument("args", nargs="+", help="Source unit type")
    # 'manage-group' command
    manage_group_parser = subparser.add_parser(
        "manage-group", aliases=["mg"], help="Add new unit group"
    )
    manage_group_parser.add_argument("action", help="Action to perform")
    manage_group_parser.add_argument("unit_group", help="Unit group")    
    manage_group_parser.add_argument(
        "new_base_unit", nargs="?", help="New base unit"
    )
    # 'manage-type' command
    manage_type_parser = subparser.add_parser(
        "manage-type", aliases=["mt"], help="Add new unit type"
    )
    manage_type_parser.add_argument("unit_group", help="Unit group")
    manage_type_parser.add_argument("action", help="Action to perform")
    manage_type_parser.add_argument("unit_type", help="Unit type to be added")
    manage_type_parser.add_argument(
        "value", nargs="?", 
        help="Conversion factor to base unit (not used for temperature)"
    )
    manage_type_parser.add_argument(
        "--factor", help="Conversion factor to temperature's base unit"
    )
    manage_type_parser.add_argument("--offset", help="Offset to temperature")
    # 'aliases' command
    aliases_parser = subparser.add_parser(
        "aliases", aliases=["a"], help="Manage unit's aliases"
    )
    aliases_parser.add_argument("unit_group", help="Unit group")
    aliases_parser.add_argument("unit_type", help="Unit type")
    aliases_parser.add_argument("action", help="Action to perform")
    aliases_parser.add_argument(
        "alias", help="Alias used to add/remove to/from an unit"
    )
    # 'base' command
    base_parser = subparser.add_parser(
        "base", aliases=["b"], help="Displays base unit"
    )
    base_parser.add_argument(
        "unit_group", nargs="?", help="Unit group (use --all|-a to show base unit for all groups)"
    )
    base_parser.add_argument(
        "--all", "-a", action="store_true", help="Shows base unit for all groups"
    )
    # 'change-base' command
    change_base_parser = subparser.add_parser(
        "change-base", aliases=["cb"], help="Change unit base for a group"
    )
    change_base_parser.add_argument("unit_group", help="Unit group")
    change_base_parser.add_argument("new_base_unit", help="New base unit")

    # Parses arguments and calls its respective function
    parsed_args: argparse.Namespace = parser.parse_args(formatted_args[1:])
    match parsed_args.command:
        # 'groups' command
        case "groups" | "g":
            message = _print_groups(data)
        # 'history command
        case "history" | "h":
            if parsed_args.reset:
                message = (
                    "History log successfully reseted!"
                    if _reset_history(data)
                    else "Error: Failed to reset history")
            else:
                limit: int = parsed_args.limit
                _validate_for_history(data, limit)
                message = _print_history(data, limit)
        # 'types' command
        case "types" | "t":
            if parsed_args.all:
                message = _print_types(data, unit_group="all")
            else:
                unit_group = parsed_args.unit_group.lower()
                _validate_unit_group(unit_group, data)
                message = _print_types(data, unit_group)
        # 'convert' command
        case "convert" | "c":
            _validate_unit_group(parsed_args.unit_group.lower(), data)
            conversion_data: ConversionData = ConversionData(
                unit_group=parsed_args.unit_group.lower()
            )
            if conversion_data.unit_group == "time":
                conversion_data.time_input = " ".join(
                    arg.lower() for arg in parsed_args.args)
            else:
                if len(parsed_args.args) not in [2, 3]:
                    raise ValueError(
                        "Invalid format for non-time conversion! "
                        "Usage: <from_type> <to_type> [amount]"
                    )
                conversion_data.from_type = parsed_args.args[0].lower()
                conversion_data.to_type = parsed_args.args[1].lower()
                conversion_data.amount = (
                    float(parsed_args.args[2])
                    if len(parsed_args.args) == 3
                    else 1.0
                )
            message = _conversion_logic(data, conversion_data)
        # 'manage-group' command
        case "manage-group" | "mg":
            manage_group_data: ManageGroupData = ManageGroupData(
                unit_group = parsed_args.unit_group.lower(),
                action = parsed_args.action.lower(),
                new_base_unit = (parsed_args.new_base_unit.lower()
                                 if parsed_args.new_base_unit
                                 else None)
            )
            message = _manage_group(data, manage_group_data)
        # 'manage-type' command
        case "manage-type" | "mt":
            _validate_unit_group(parsed_args.unit_group.lower(), data)
            manage_type_data: ManageTypeData = ManageTypeData(
                unit_group = parsed_args.unit_group.lower(),
                unit_type = parsed_args.unit_type.lower(),
                action = parsed_args.action.lower(),
                value = parsed_args.value,
                factor = parsed_args.factor,
                offset = parsed_args.offset
            )
            message = _manage_type(data, manage_type_data)
        # 'aliases' command
        case "aliases" | "a":
            _validate_unit_group(parsed_args.unit_group.lower(), data)
            aliases_data: AliasesData = AliasesData(
                unit_group = parsed_args.unit_group.lower(),
                unit_type = parsed_args.unit_type.lower(),
                action = parsed_args.action.lower(),
                alias = parsed_args.alias.lower()
            )
            message = _manage_aliases(data, aliases_data)
        # 'base' command
        case "base" | "b":
            if parsed_args.all:
                message = _print_base(data, unit_group="all")
            else:
                unit_group = parsed_args.unit_group.lower()
                _validate_unit_group(unit_group, data)
                message = _print_base(data, unit_group)
        # 'change-base' command
        case "change-base" | "cb":
            _validate_unit_group(parsed_args.unit_group.lower(), data)
            change_base_data: ChangeBaseData = ChangeBaseData(
                unit_group=parsed_args.unit_group.lower(),
                new_base_unit = parsed_args.new_base_unit.lower()
            )
            message = _change_base_unit(data, change_base_data)
        case _:
            parser.print_help()
            sys.exit(1)
            
    print(message)
