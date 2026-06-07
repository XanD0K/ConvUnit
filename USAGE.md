# ConvUnit - Detailed Usage Guide

This document provides complete instructions, explanations, and examples for all features and usage modes of ConvUnit.

---

## Table of Contents

- [1. Interactive Mode](#1-interactive-mode)
- [2. Command Line Interface (CLI) Mode](#2-command-line-interface-cli-mode)
- [3. Python API Mode](#3-python-api-mode)
- [4. Date & Time Conversion](#4-date--time-conversion)
- [5. Managing Units and Groups](#5-managing-units-and-groups)
- [6. Conversion History](#6-conversion-history)
- [7. Important Notes and Behaviors](#7-important-notes-and-behaviors)
- [8. Troubleshooting](#8-troubleshooting)

---

## 1. Interactive Mode

The interactive mode provides a guided, menu-driven experience. It is ideal for exploration and when you prefer not to remember command syntax.

### Starting Interactive Mode

```bash
python -m src.convunit
```

Once inside, type any available command and follow the prompts.  
Type `quit` (`q`) or `exit` (`e`) to exit the program at any time.

### Available Commands

| Command            | Alias | Description                                                                 |
|--------------------|-------|-----------------------------------------------------------------------------|
| `convert`          | `c`   | Convert between units or perform time/date calculations                     |
| `groups`           | `g`   | List all available unit groups                                              |
| `types`            | `t`   | Show all unit types (and their aliases) within a group                      |
| `base`             | `b`   | Show the current base unit of a group                                       |
| `history`          | `h`   | View recent conversion history                                              |
| `manage-group`     | `mg`  | Add or remove custom unit groups                                            |
| `manage-type`      | `mt`  | Add or remove unit types inside a group                                     |
| `aliases`          | `a`   | Add or remove aliases for existing unit types                               |
| `change-base`      | `cb`  | Change the base unit of any group                                           |

> **Note:** The commands above are the same for both Interactive and CLI modes. Some CLI commands have additional flags (documented in the CLI section).

### Example Flow

```
$ python -m src.convunit

> convert
> length
> meters
> feet
> 10

Result: 10 meters = 32.8084 feet

> groups
> types length
> history
> quit
```

---

## 2. Command Line Interface (CLI) Mode

The CLI mode allows you to run commands directly from the terminal. It is best suited for scripting, automation, and quick conversions.

### Basic Usage

All commands follow this pattern:

```bash
python -m src.convunit <command> [arguments] [options]
```

Use `--help` with any command to see its specific options:

```bash
python -m src.convunit convert --help
python -m src.convunit history --help
```

### Available Commands

#### `convert` (or `c`)

Converts a value from one unit to another.

**Usage:**
```bash
python -m src.convunit convert <group> <from_type> <to_type> [amount]
python -m src.convunit convert time <time_input...>
```

**Behavior:**
- For most groups: expects `from_type`, `to_type`, and optionally an `amount` (default = 1).
- For the `time` group: accepts flexible time/date formats (see section 4 - [Date & Time Conversion](#4-date--time-conversion)).

**Examples:**
```bash
python -m src.convunit convert length meters feet 10
python -m src.convunit convert mass kg g 5
python -m src.convunit c time minutes seconds 90
python -m src.convunit c time 5 years 10 months 10 days hours
```

#### `groups` (or `g`)

Lists all available unit groups.

```bash
python -m src.convunit groups
```

#### `types` (or `t`)

Shows all unit types within a group (including aliases).

```bash
python -m src.convunit types length
python -m src.convunit types --all          # Show types from all groups
```

**Flag:**
- `--all`, `-a`: Show types for all groups at once.

#### `base` (or `b`)

Shows the current base unit of a group.

```bash
python -m src.convunit base length
python -m src.convunit base --all           # Show base units for all groups
```

**Flag:**
- `--all`, `-a`: Show base units for all groups at once.

#### `history` (or `h`)

Displays recent conversions (default: last 10 entries).

```bash
python -m src.convunit history
python -m src.convunit history --limit 30
```

**Flags:**
- `--limit`, `-l <N>`: Limit the number of entries shown (default = 10).
- `--reset`, `-r`: Clear the entire conversion history.

#### `manage-group` (or `mg`)

Add or remove custom unit groups.

```bash
python -m src.convunit manage-group weight add kilogram
python -m src.convunit manage-group weight remove
```

> When creating a new group, the unit provided (`kilogram` in the example) automatically becomes the `base_unit` of that group.

#### `manage-type` (or `mt`)

Add or remove unit types inside an existing group.

```bash
python -m src.convunit manage-type length kilometer add 1000
python -m src.convunit manage-type length kilometer remove
```

**Flags (for temperature):**
- `--factor`: Conversion factor to the temperature base unit.
- `--offset`: Offset value for temperature conversions.

> For non-temperature units, provide the conversion factor as a positional argument. For temperature, use `--factor` and `--offset`.

#### `aliases` (or `a`)

Add or remove aliases for unit types.

```bash
python -m src.convunit aliases length meter add mtr
python -m src.convunit aliases length meter remove mtr
```

#### `change-base` (or `cb`)

Changes the base unit of a group. All other units are recalculated relative to the new base.

```bash
python -m src.convunit change-base length kilometer
```

> **Warning:** This is a structural change. It affects internal storage but does not break existing conversions.

---

## 3. Python API Mode

You can use ConvUnit programmatically in your own Python code. This is useful for building applications, scripts, or integrating conversions into larger systems.

### Basic Setup

```python
from convunit import Converter

converter = Converter()
```

### Available Methods

| Method                              | Description                                                                 | Example |
|-------------------------------------|-----------------------------------------------------------------------------|---------|
| `convert(group, from_unit, to_unit, value)` | Convert a value between two units                                      | `converter.convert("length", "meters", "feet", 10)` |
| `groups()`                          | Return list of all unit groups                                              | `converter.groups()` |
| `types(group=None)`                 | Return unit types for a group. If no group is given, returns all types      | `converter.types("length")` or `converter.types()` |
| `base(group=None)`                  | Return base unit of a group. If no group is given, returns all base units   | `converter.base("length")` or `converter.base()` |
| `history(limit=10)`                 | Return recent conversion history                                            | `converter.history(20)` |
| `reset_history()`                   | Clear all conversion history                                                | `converter.reset_history()` |
| `manage_group(group, action, unit)` | Add or remove a unit group                                                  | `converter.manage_group("weight", "kilogram", "add")` |
| `manage_type(...)`                  | Add or remove a unit type (supports factor/offset for temperature)          | `converter.manage_type("length", "kilometer", "add", 1000)` |
| `aliases(group, unit_type, action, alias)` | Add or remove an alias for a unit type                                | `converter.aliases("length", "meter", "add", "mtr")` |
| `change_base(group, new_base)`      | Change the base unit of a group                                             | `converter.change_base("length", "kilometer")` |
| `reset()`                           | Reset all user data to original state                                       | `converter.reset()` |

> **Note:** Calling `types()` or `base()` without arguments returns data for all groups (same behavior as `all_types()` / `all_bases()`).

### Method Aliases (Shortcuts)

For convenience, the following aliases are available:

| Alias     | Full Method          |
|-----------|----------------------|
| `g`       | `groups()`           |
| `h`       | `history()`          |
| `c`       | `convert()`          |
| `mg`      | `manage_group()`     |
| `mt`      | `manage_type()`      |
| `a`       | `aliases()`          |
| `cb`      | `change_base()`      |
| `all_t`   | `all_types()`        |
| `all_b`   | `all_bases()`        |
| `reset_h` | `reset_history()`    |

### Example Usage

```python
from convunit import Converter

converter = Converter()

# Basic conversion
result = converter.convert("length", "meters", "feet", 10)
print(result)   # 32.8084

# List groups and types
print(converter.groups())
print(converter.types("time"))

# Work with history
print(converter.history(limit=5))
converter.reset_history()

# Custom management
converter.manage_group("weight", "add", "kilogram")
converter.manage_type("length", "kilometer", "add", 1000)
converter.aliases("length", "meter", "add", "mtr")
converter.change_base("length", "kilometer")

# Reset everything to factory defaults
converter.reset()
```

> **Note:** When using the API, custom changes (groups, types, aliases, base units) are persisted to the JSON data files, just like in Interactive and CLI modes.

---

## 4. Date & Time Conversion

ConvUnit has a powerful and flexible system for handling dates, times, months, and durations. It supports many input formats and can calculate differences between dates or sum multiple time units.

### Supported Formats

The system accepts several input styles:

| Format                        | Example                                      | Description |
|-------------------------------|----------------------------------------------|-----------|
| Simple unit conversion        | `minutes seconds 10`                         | Convert between time units |
| Time string                   | `17h:28m:36s seconds`                        | Convert a time expression |
| Flexible time string          | `50h:350m:780s seconds`                      | Accepts non-standard values (e.g. 350 minutes) |
| Month name                    | `JAN days` or `January seconds`              | Convert a month to a unit |
| Single date                   | `2019-11-04 days`                            | Convert a date to a unit (approximate) |
| Flexible date                 | `5402-555-70 days`                           | Accepts large or unusual year/month/day values |
| Date difference               | `2019-11-04 2056-04-28 days`                 | Accurate difference between two dates |
| Multiple units                | `5 years 10 months 10 days hours`            | Sum several units into one result |

### How It Works

- **Date differences** use Python’s `datetime` module and correctly handle leap years.
- **Single date / month conversions** use average values (1 year ≈ 365.2425 days, 1 month ≈ 30.436875 days).
- Time-of-day calculations (`17h:28m:36s`) are precise to the second.
- The parser for single time and single date formats is quite flexible. It accepts non-standard values such as:
  - `50h:350m:780s seconds`
  - `5402-555-70 days`


**Examples:**

```bash
python -m src.convunit convert time 50h:350m:780s seconds
# Result: There are 201,780.0 seconds in 50h:350m:780s

python -m src.convunit convert time 5402-555-70 days
# Result: There are 1,990,002.45063 days in 5402 years, 555 months, 70 days
```

### Usage by Mode

**Interactive Mode:**
```
convert
time
5 years 10 months 10 days hours
```

**CLI Mode:**
```bash
python -m src.convunit convert time 5 years 10 months 10 days hours
python -m src.convunit convert time 2019-11-04 2056-04-28 days
python -m src.convunit convert time JAN DEC days
```

**API Mode:**
```python
result = converter.convert("time", time_input="5 years 10 months 10 days hours")
result = converter.convert("time", time_input="2019-11-04 2056-04-28 days")
```

> **Tip:** You can mix multiple units in a single input when using the "Multiple units sum" format.

---

## 5. Managing Units and Groups

ConvUnit allows you to extend the system with custom groups and units. All changes are persisted in JSON files.

### What You Can Do

- Create new unit groups (`manage-group`)
- Add new unit types inside existing groups (`manage-type`)
- Create aliases (shortcuts) for units (`aliases`)
- Change the base unit of any group (`change-base`)

When you create a new group using `manage-group <group> add <base_unit>`, the provided unit automatically becomes the base unit of that group.

When changing the base unit of a group, all other units are automatically recalculated relative to the new base.

All custom data is shared between Interactive, CLI, and API modes.

---

## 6. Conversion History

Every conversion performed (in any mode) is logged with a timestamp. History is kept for the last **3 days** only.

### Viewing History

```bash
python -m src.convunit history
python -m src.convunit history --limit 30
```

In the API:
```python
converter.history(limit=30)
```

### Clearing History

```bash
python -m src.convunit history --reset
```

Or in the API:
```python
converter.reset_history()
```

> **Note:** History is stored in `data/conversion_log.json`. Old entries (older than 3 days) are automatically ignored.

---

## 7. Important Notes and Behaviors

- **Persistence**: All custom groups, types, aliases, and base unit changes are saved to JSON files in the `data/` folder. They persist across sessions.
- **Shared data**: Changes made in any mode (Interactive, CLI, or API) are immediately visible in the others.
- **Error handling**: Invalid units, unknown groups, or malformed inputs raise clear error messages in all modes.
- **Date calculations**: Date differences are accurate (including leap years). Single-date conversions use average year/month lengths.
- **No external dependencies**: The project uses only Python’s standard library.

---

## 8. Troubleshooting

### Common Issues

| Problem                              | Possible Cause                                      | Solution |
|--------------------------------------|-----------------------------------------------------|----------|
| `ModuleNotFoundError`                | Running `python src/convunit/main.py` directly | Always use `python -m src.convunit` |
| Custom units not appearing           | Running from a different working directory          | Run from the project root |
| Strange results after `change-base`  | Expecting old base unit values                      | All conversions remain mathematically correct |
| Date difference seems wrong          | Using single date format instead of two dates       | Use two dates for accurate difference |
| Aliases not working                  | Alias added to wrong group or unit                  | Check with `types <group>` |

### Getting Help

- In Interactive mode, most commands provide contextual guidance.
- See the main [README.md](../README.md) for installation and quick start.

---