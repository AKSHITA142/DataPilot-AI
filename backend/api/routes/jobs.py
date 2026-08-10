from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/jobs", tags=["Research Jobs"])


@router.get("", response_model=SuccessResponse)
def list_jobs(db: Session = Depends(get_db)):
    """List research jobs (skeleton route)."""
    return SuccessResponse(data={"jobs": []})


@router.get("/{job_id}", response_model=SuccessResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get research job status and details (skeleton route)."""
    return SuccessResponse(data={"job_id": job_id, "status": "queued", "progress_pct": 0.0})
