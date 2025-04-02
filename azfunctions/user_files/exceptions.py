import logging
import uuid
from typing import Optional

from azure.functions import HttpRequest


class UserFilesError(Exception):
    """Base exception for user files module"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error
        self.error_id = str(uuid.uuid4())


class UnauthorizedError(UserFilesError):
    """Raised when user authentication fails"""

    pass


class FileNotFoundError(UserFilesError):
    """Raised when requested file is not found"""

    pass


class PermissionDeniedError(UserFilesError):
    """Raised when user doesn't have required permissions"""

    pass


class ValidationError(UserFilesError):
    """Raised when request validation fails"""

    pass


class BlobStorageError(UserFilesError):
    """Raised when blob storage operations fail"""

    pass


def get_request_id(req: HttpRequest) -> str:
    """Extract or generate request ID for tracking"""
    return req.headers.get("X-Request-ID") or str(uuid.uuid4())


def get_logger_with_context(request_id: str) -> logging.Logger:
    """Get a logger with request context"""
    logger = logging.getLogger(__name__)
    return logging.LoggerAdapter(logger, {"request_id": request_id})


def create_error_response(error: Exception, status_code: int = 500) -> dict:
    """Create standardized error response"""
    error_mapping = {
        UnauthorizedError: 401,
        FileNotFoundError: 404,
        PermissionDeniedError: 403,
        ValidationError: 400,
        BlobStorageError: 500,
    }

    status = error_mapping.get(type(error), status_code)

    error_body = {
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "code": status,
            "id": error.error_id,
        }
    }

    return error_body, status
