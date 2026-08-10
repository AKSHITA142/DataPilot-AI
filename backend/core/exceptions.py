from typing import Optional, Dict, Any


class AppException(Exception):
    """
    Base custom application exception.
    All domain and service exceptions inherit from this class to guarantee uniform error responses.
    """
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class ValidationException(AppException):
    """Raised when data validation fails at the domain layer."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Requested resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ConflictException(AppException):
    """Raised when a resource conflict occurs (e.g. duplicate unique key)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class AuthenticationException(AppException):
    """Raised when authentication fails or credentials are invalid."""
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details,
        )


class AuthorizationException(AppException):
    """Raised when an authenticated user lacks permission."""
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=403,
            details=details,
        )


class UpstreamException(AppException):
    """Raised when an upstream dependency (worker, database, LLM API) fails."""
    def __init__(self, message: str = "Upstream service failure", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="UPSTREAM_ERROR",
            status_code=502,
            details=details,
        )
