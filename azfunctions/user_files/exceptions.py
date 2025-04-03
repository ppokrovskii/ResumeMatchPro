from typing import Any, Dict, Tuple

from pydantic import ValidationError as PydanticValidationError


class BaseError(Exception):
    """Base class for all custom exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(BaseError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message)


class InternalValidationError(BaseError):
    """Raised when internal data validation fails (e.g. DB to model mapping)."""

    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedError(BaseError):
    """Raised when user is not authorized."""

    def __init__(self, message: str):
        super().__init__(message)


class FileNotFoundError(BaseError):
    """Raised when a file is not found."""

    def __init__(self, message: str):
        super().__init__(message)


class PermissionDeniedError(BaseError):
    """Raised when user doesn't have permission to access a resource."""

    def __init__(self, message: str):
        super().__init__(message)


class BlobStorageError(BaseError):
    """Raised when there's an error with blob storage operations."""

    def __init__(self, message: str):
        super().__init__(message)


def create_error_response(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Create an error response from an exception."""
    if isinstance(error, ValidationError):
        return {"error": str(error)}, 400
    elif isinstance(error, UnauthorizedError):
        return {"error": str(error)}, 401
    elif isinstance(error, FileNotFoundError):
        return {"error": str(error)}, 404
    elif isinstance(error, PermissionDeniedError):
        return {"error": str(error)}, 403
    elif isinstance(error, (BlobStorageError, InternalValidationError)):
        return {"error": str(error)}, 500
    else:
        return {"error": "Internal server error"}, 500
