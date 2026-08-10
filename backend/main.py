import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.database.connection import init_db
from backend.middleware.logging_middleware import logging_middleware_fn
from backend.middleware.auth_middleware import auth_middleware_fn
from backend.middleware.exception_middleware import register_exception_handlers
from backend.api.routes import (
    health_router,
    upload_router,
    jobs_router,
    experiments_router,
    reports_router,
    websocket_router,
)

settings = get_settings()

# Setup logging configuration
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("datapilot.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for FastAPI application startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version} ({settings.environment})")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="DataPilot-AI API Gateway - AI-Powered Data Quality & Preprocessing Copilot",
    lifespan=lifespan,
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. HTTP Custom Middlewares
@app.middleware("http")
async def custom_auth_middleware(request: Request, call_next):
    return await auth_middleware_fn(request, call_next)


@app.middleware("http")
async def custom_logging_middleware(request: Request, call_next):
    return await logging_middleware_fn(request, call_next)


# 3. Exception Handlers
register_exception_handlers(app)

# 4. Include API Routers (both un-prefixed and /api/v1 prefixed for compatibility)
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(experiments_router)
app.include_router(reports_router)

api_prefix = "/api/v1"
app.include_router(upload_router, prefix=api_prefix)
app.include_router(jobs_router, prefix=api_prefix)
app.include_router(experiments_router, prefix=api_prefix)
app.include_router(reports_router, prefix=api_prefix)
app.include_router(websocket_router, prefix=api_prefix)


@app.get("/", tags=["Root"])
def root():
    """Root entry point directing to API docs."""
    return {
        "message": f"Welcome to {settings.app_name} API Gateway",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/health",
    }
