import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.core.config import get_settings, Settings
from backend.core.exceptions import NotFoundException
from backend.database.connection import get_db
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=SuccessResponse)
def health_check(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Health check endpoint verifying application status, version, environment, and DB connection.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return SuccessResponse(
        data={
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "status": "healthy" if db_status == "connected" else "degraded",
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.get("/logs", response_model=SuccessResponse)
def get_system_logs(lines: int = 100):
    """
    Returns the latest log lines from backend/logs/datapilot.log for debugging.
    """
    log_file_path = "backend/logs/datapilot.log"
    log_lines = []
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_lines = f.readlines()[-lines:]
    return SuccessResponse(
        data={
            "log_file": log_file_path,
            "total_retrieved": len(log_lines),
            "logs": [l.strip() for l in log_lines],
        }
    )


@router.get("/error-test")
def trigger_test_exception():
    """
    Test endpoint that deliberately raises a NotFoundException to verify the Phase 3 error response gate.
    """
    raise NotFoundException(
        message="Deliberately thrown test exception for Phase 3 gate verification",
        details={"test_key": "gate_passed"}
    )
