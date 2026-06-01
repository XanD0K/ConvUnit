# errors.py

class AppError(Exception):
    """Base exception for the entire application"""
    pass


# ====================== DATA ERRORS ======================
class DataError(AppError):
    """Base class for all data-related errors (JSON files)"""
    pass


class DataCorruptedError(DataError):
    """Raised when a JSON file has invalid structure or corrupted content"""
    pass


class DataInconsistencyError(DataError):
    """Raised when there is inconsistency between different data files"""
    pass


# ====================== UNIT ERRORS ======================
class UnitError(AppError):
    """Base class for errors related to units and groups"""
    pass


class UnitNotFoundError(UnitError):
    """Raised when a unit type or alias is not found"""
    pass


class UnitGroupNotFoundError(UnitError):
    """Raised when trying to access a non-existent unit group"""
    pass


class BaseUnitError(UnitError):
    """Raised when there's a problem with the base unit of a group"""
    pass


# ====================== VALIDATION / INPUT ERRORS ======================
class ValidationError(AppError):
    """Base class for validation and input errors"""
    pass


class InvalidInputError(ValidationError):
    """Raised when the user provides invalid input"""
    pass


class DuplicateError(ValidationError):
    """Raised when trying to create something that already exists (e.g. alias, unit, group, type)"""
    pass