"""Package initializer for backend.api.routes."""
from backend.api.routes.health import router as health_router
from backend.api.routes.upload import router as upload_router
from backend.api.routes.jobs import router as jobs_router
from backend.api.routes.experiments import router as experiments_router
from backend.api.routes.reports import router as reports_router
from backend.api.routes.websocket import router as websocket_router
from backend.api.routes.dashboard import router as dashboard_router
from backend.api.routes.datasets import router as datasets_router

__all__ = [
    "health_router",
    "upload_router",
    "jobs_router",
    "experiments_router",
    "reports_router",
    "websocket_router",
    "dashboard_router",
    "datasets_router",
]


