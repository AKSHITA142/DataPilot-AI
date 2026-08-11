import asyncio
import logging
import uuid
from typing import Optional, Dict, Any, List
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from backend.core.exceptions import NotFoundException, ValidationException, ConflictException
from backend.repositories.job_repository import JobRepository
from backend.repositories.dataset_repository import DatasetRepository
from backend.models.job import JobModel
from backend.schemas.enums import JobStatus
from backend.services.job_manager import JobManager

logger = logging.getLogger("datapilot.services.job_service")


def _run_job_in_background(job_id: str, dataset_id: str, file_path: str, user_goal: Optional[str] = None):
    """
    Sync wrapper that safely schedules the async JobManager coroutine
    onto the already-running FastAPI event loop.

    CRITICAL FIX: asyncio.run() cannot be called from within a running event loop
    (which FastAPI always has). Using loop.create_task() instead.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            JobManager.run_job_async(
                job_id=job_id,
                dataset_id=dataset_id,
                file_path=file_path,
                user_goal=user_goal,
            )
        )
    except RuntimeError:
        # No running loop (shouldn't happen in FastAPI, but handle gracefully)
        logger.warning(f"No running event loop found for job {job_id}; creating new loop")
        asyncio.run(
            JobManager.run_job_async(
                job_id=job_id,
                dataset_id=dataset_id,
                file_path=file_path,
                user_goal=user_goal,
            )
        )


class JobService:
    """Service layer managing research job creation, status querying, and cancellation."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = JobRepository(db)
        self.dataset_repository = DatasetRepository(db)

    def start_job(
        self,
        dataset_id: str,
        user_goal: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> JobModel:
        """
        Creates a new Job record and dispatches background execution worker.
        """
        dataset = self.dataset_repository.get_by_id(dataset_id)
        if not dataset:
            raise NotFoundException(f"Dataset with ID '{dataset_id}' not found.")

        job_id = f"job_{uuid.uuid4().hex[:8]}"

        # Create Job DB record
        job_record = self.repository.create(
            JobModel(
                id=job_id,
                dataset_id=dataset_id,
                status=JobStatus.QUEUED.value,
                objective=user_goal or "Automated ML Research & Preprocessing Optimization",
                progress_pct=0.0,
            )
        )

        # Dispatch background worker using safe async scheduling
        if background_tasks:
            background_tasks.add_task(
                _run_job_in_background,
                job_id=job_id,
                dataset_id=dataset_id,
                file_path=dataset.file_path,
                user_goal=user_goal,
            )
        else:
            # Direct dispatch on running event loop
            _run_job_in_background(
                job_id=job_id,
                dataset_id=dataset_id,
                file_path=dataset.file_path,
                user_goal=user_goal,
            )

        return job_record

    def get_job(self, job_id: str) -> JobModel:
        """Retrieves job record by ID."""
        job = self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Research job with ID '{job_id}' not found.")
        return job

    def cancel_job(self, job_id: str) -> JobModel:
        """Requests cancellation for a running or queued job."""
        job = self.get_job(job_id)

        if job.status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
            raise ConflictException(f"Cannot cancel job {job_id} in status '{job.status}'.")

        updated_job = self.repository.update_status(job_id, JobStatus.CANCELLED)
        return updated_job
