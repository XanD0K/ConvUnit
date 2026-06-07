"""
Custom exception hierarchy for ConvUnit.

All exceptions inherit from AppError, allowing broad or specific error handling.
"""

__all__ = [
    # Base
    "AppError",
    # Data errors
    "DataError",
    "DataCorruptedError",
    "DataInconsistencyError",
    # Unit errors
    "UnitError",
    "UnitNotFoundError",
    "UnitGroupNotFoundError",
    "BaseUnitError",
    # Validation / Input errors
    "ValidationError",
    "InvalidInputError",
    "DuplicateError",
]

class AppError(Exception):
    """Base exception for all ConvUnit errors"""
    pass


# ====================== DATA ERRORS ======================
class DataError(AppError):
    """Base class for errors related to data files (JSON)"""
    pass


class DataCorruptedError(DataError):
    """Raised when a data file has invalid structure or corrupted content"""
    pass


class DataInconsistencyError(DataError):
    """Raised when there is inconsistency between different data files"""
    pass


# ====================== UNIT ERRORS ======================
class UnitError(AppError):
    """Base class for errors related to units, groups and aliases"""
    pass


class UnitNotFoundError(UnitError):
    """Raised when a unit type or alias is not found in the specified group"""
    pass


class UnitGroupNotFoundError(UnitError):
    """Raised when trying to access a unit group that does not exist"""
    pass


class BaseUnitError(UnitError):
    """Raised when there is a problem related to the base unit of a group"""
    pass


# ====================== VALIDATION / INPUT ERRORS ======================
class ValidationError(AppError):
    """Base class for validation and user input errors"""
    pass


class InvalidInputError(ValidationError):
    """Raised when the user provides invalid or malformed input"""
    pass


class DuplicateError(ValidationError):
    """Raised when trying to create a duplicate (e.g. alias, unit type, group)"""
    pass
