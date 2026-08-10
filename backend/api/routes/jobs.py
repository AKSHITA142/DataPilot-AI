from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.services.job_service import JobService
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/jobs", tags=["Research Jobs"])


class StartJobRequest(BaseModel):
    dataset_id: str
    user_goal: Optional[str] = None


@router.post("/start", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED)
def start_research_job(
    payload: StartJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Triggers an automated research job asynchronously for a dataset.
    Returns immediately with job_id and queued status.
    """
    service = JobService(db)
    job_record = service.start_job(
        dataset_id=payload.dataset_id,
        user_goal=payload.user_goal,
        background_tasks=background_tasks,
    )

    return SuccessResponse(
        data={
            "job_id": job_record.id,
            "dataset_id": job_record.dataset_id,
            "status": job_record.status,
            "progress_pct": job_record.progress_pct,
            "objective": job_record.objective,
        },
        message="Research job queued and started in background worker.",
    )


@router.get("/{job_id}", response_model=SuccessResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Queries real-time status and progress percentage for a research job.
    """
    service = JobService(db)
    job_record = service.get_job(job_id)

    return SuccessResponse(
        data={
            "job_id": job_record.id,
            "dataset_id": job_record.dataset_id,
            "status": job_record.status,
            "progress_pct": job_record.progress_pct,
            "objective": job_record.objective,
            "created_at": job_record.created_at.isoformat() if job_record.created_at else None,
            "updated_at": job_record.updated_at.isoformat() if job_record.updated_at else None,
        },
        message="Job status retrieved successfully.",
    )


@router.post("/{job_id}/cancel", response_model=SuccessResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """
    Requests cancellation of a running or queued research job.
    """
    service = JobService(db)
    job_record = service.cancel_job(job_id)

    return SuccessResponse(
        data={
            "job_id": job_record.id,
            "status": job_record.status,
        },
        message="Job cancellation requested successfully.",
    )
