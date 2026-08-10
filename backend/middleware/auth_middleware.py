from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware class.
    Extracts Bearer token from Authorization header when auth is enabled.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        return await auth_middleware_fn(request, call_next)


async def auth_middleware_fn(request: Request, call_next) -> Response:
    """
    Authentication middleware function for FastAPI @app.middleware("http").
    Safely initializes request.state.token and request.state.user.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        request.state.token = token
        request.state.user = {"id": "dev_user", "authenticated": True}
    else:
        request.state.token = None
        request.state.user = None

    return await call_next(request)
