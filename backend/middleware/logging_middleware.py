import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("datapilot.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware class logging every HTTP request/response pair.
    Attaches a unique X-Correlation-ID header to every request.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        return await logging_middleware_fn(request, call_next)


async def logging_middleware_fn(request: Request, call_next) -> Response:
    """
    HTTP middleware function for request tracing and correlation ID tracking.
    """
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    response.headers["X-Correlation-ID"] = correlation_id
    
    logger.info(
        f"[{correlation_id}] {request.method} {request.url.path} - "
        f"Status: {response.status_code} ({duration_ms:.2f}ms)"
    )
    return response
