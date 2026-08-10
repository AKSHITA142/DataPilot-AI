from typing import Optional
from sqlalchemy.orm import Session

from backend.core.exceptions import NotFoundException
from backend.repositories.report_repository import ReportRepository
from backend.models.report import ReportModel


class ReportService:
    """Service layer managing queries for final research reports."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ReportRepository(db)

    def get_report_by_job(self, job_id: str) -> ReportModel:
        """Retrieves completed final report record for a research job."""
        report = self.repository.get_by_job(job_id)
        if not report:
            raise NotFoundException(f"Final report for job '{job_id}' not found or not yet completed.")
        return report
