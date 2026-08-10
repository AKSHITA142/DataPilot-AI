from backend.core.exceptions import (
    AppException,
    ValidationException,
    NotFoundException,
    ConflictException,
    AuthenticationException,
    AuthorizationException,
    UpstreamException,
)


def test_app_exception_hierarchy():
    """Verify all custom exceptions inherit from AppException and set status/error codes."""
    exc = ValidationException("Invalid field value", details={"field": "email"})
    assert isinstance(exc, AppException)
    assert exc.status_code == 422
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.details == {"field": "email"}

    nf = NotFoundException("Dataset not found")
    assert nf.status_code == 404
    assert nf.error_code == "NOT_FOUND"

    conflict = ConflictException("Duplicate dataset checksum")
    assert conflict.status_code == 409
    assert conflict.error_code == "CONFLICT"

    auth = AuthenticationException("Missing token")
    assert auth.status_code == 401
    assert auth.error_code == "AUTHENTICATION_FAILED"

    forbidden = AuthorizationException("Admin only")
    assert forbidden.status_code == 403
    assert forbidden.error_code == "PERMISSION_DENIED"

    upstream = UpstreamException("Worker timeout")
    assert upstream.status_code == 502
    assert upstream.error_code == "UPSTREAM_ERROR"
