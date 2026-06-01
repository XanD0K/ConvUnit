# TODO


## New features


## Refactoring tasks
- Improve error messages and code errors


## Testing


## BACKLOG


## DONE
- [x] Implement a functional `converter` function
- [x] Improve Errors checking
- [x] Centralize try-except block in `main`, making functions to just raise the exception
- [x] Keep users inside program with `while` loop, until he decides to quit
- [x] Allow users to modify the unit's dictionary by adding new `groups`/`types` (modifies `units.json` and `base_units.json`)
- [x] Move `units` dictionary to another file to keep `project.py` cleaner
- [x] Use `json` library to open/save/close that new dictionary file, so that changes won't be lost
- [x] Remove abrupt ending with `sys.exit` by adding `while` logic
- [x] Remove actions' logic from `main` to keep it cleaner
- [x] Fix message that outputs dictionary's keys
- [x] Create separate functions for each action
- [x] Modify "add" action by adding more logic and validation checks to new groups (e.g. base unit, valid number)
- [x] When adding new group/type, display base unit of that type so that users know in ehich unit he should calculate the conversion factor
- [x] Add separate logic for temperature (for converting units and for adding new `types`)
- [x] Fix converted value that always has 5 decimal values, even if all zeroes
- [x] Improve inputs validation based on unit group
- [x] Validate dictionary after importing/using it
- [x] Verify both dictionaries matches
- [x] Allow users to run the program through command lines
- [x] Add `groups` and `types` functions to also be used with comman-line arguments
- [x] Implement comman-line arguments to "add" action
- [x] Add aliases to all command lines to improve UX (e.g "convert" and "c" will both be used to convert units)
- [x] Modify argument's name to keep consistency throughout the code
- [x] Add log file, keeping track of user's previous actions
- [x] Add temperature conversions to history log
- [x] Improve time conversion with `datetime` library
- [x] Allow time conversion between units (e.g. 5 hours to minutes) and between dates given a specified unit (e.g. 2023-12-17 2024-12-01 minutes)
- [x] Improve converted output
- [x] Changed `add_to_log` function to accept new logic for date time unit conversion
- [x] Changed `print_history` function also print new
- [x] Add new date and time conversion logic to be handled through command-line commands
- [x] Add aliases to unit types (e.g. "km" for "kilometer", "ft" for "feet", "min" for "minute")
- [x] Remove `while` loops from inner functions
- [x] Allow users to remove unit type (except base unit)
- [x] Allow users to change base unit
- [x] Allow users to calculate more complex date and time conversions
- [x] Change `month`'s dictionaries structure
- [x] Automatically delete data in `change_log.json` file after some time
- [x] Moved all `.json` files into `data` directory 
- [x] Moved data manager functions and helper function into their own files
- [x] Refactore all functions' arguments, reducing their numbers, making code cleaner and easier to read
- [x] Move variables' validation from multiple functions, centralizing them on `UnitData` class
- [x] Allow users to remove unit_group
- [x] Segregate `UnitData` class into multiple classes
- [x] Add a class that encapsulates all program's logic, allowing users to also access it's features throughout an Class's object
- [x] Add remmaining comments throughout the codebase
- [x] Add remmaining type hints throughout the codebase
- [x] Clean program by removing multiple repetitive logic throught the codebase and transforming it into a single function
- [x] Implement a test suite (`test_project.py`)
- [x] Implement test files for all other files (`test_utils.py`, `test_data_models.py`, `test_data_manager.py` and `test_api.py`)
- [-] Use `inflect` library to customize output message
- [x] Add style to introductory messages and instruction messages and add separator (e.g. with `-`, `=` or `_`)
- [x] Test corner cases (e.g. lower/uper case, invalid values, empty values)
- [x] Validade type checking (by using `mypy`)
- [x] Polish code, improving readability
- [x] Reestructure `project.py` file into multiple files to keep program cleaner
- [x] Reestructure `final-project` directory
- [x] Refactor `project.py` into multiple files, segregating CLI and interactive approaches
- [x] Clean files and improve code before conversion into a package
- [x] Changed program's intern functions to be displayed as hidden (with a `_` in the beggining of their names)
- [x] Improve code structure to allow it's conversion into a package
- [x] Refactored and cleaned all features
- [x] Allow reset of unit's data (`JSON` files)
- [x] Improved `change_base` and `manage_type`, fixing both features when group is "temperature"
