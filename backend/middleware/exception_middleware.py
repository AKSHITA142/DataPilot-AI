import logging
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.exceptions import AppException
from backend.schemas.response import ErrorResponse

logger = logging.getLogger("datapilot.exception")


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application instance."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(f"AppException caught: [{exc.error_code}] {exc.message}")
        error_payload = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Validation error: {exc.errors()}")
        details = {"errors": exc.errors()}
        error_payload = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request body or query parameter validation failed",
            details=details,
        )
        return JSONResponse(
            status_code=422,
            content=error_payload.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        error_payload = ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            details={},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled server error: {exc}", exc_info=True)
        error_payload = ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred",
            details={"error_type": exc.__class__.__name__},
        )
        return JSONResponse(
            status_code=500,
            content=error_payload.model_dump(),
        )
