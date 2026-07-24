"""
MuleTrace AI — Custom Domain Exceptions.

Application-specific exception classes for financial crime backend operations.
"""


class MuleTraceException(Exception):
    """Base exception class for MuleTrace AI domain errors."""

    def __init__(self, message: str, error_code: str = "DOMAIN_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class EntityNotFoundError(MuleTraceException):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_name: str, identifier: str) -> None:
        message = f"{entity_name} with identifier '{identifier}' was not found"
        super().__init__(message=message, error_code="ENTITY_NOT_FOUND")


class DuplicateEntityError(MuleTraceException):
    """Raised when attempting to create an entity that already exists."""

    def __init__(self, entity_name: str, identifier: str) -> None:
        message = f"{entity_name} with identifier '{identifier}' already exists"
        super().__init__(message=message, error_code="DUPLICATE_ENTITY")


class ValidationException(MuleTraceException):
    """Raised when domain business rules validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, error_code="VALIDATION_FAILED")


class DatabaseConnectionError(MuleTraceException):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Database connection error") -> None:
        super().__init__(message=message, error_code="DATABASE_ERROR")
