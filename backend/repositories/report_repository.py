from typing import Optional
from sqlalchemy.orm import Session
from backend.models.report import ReportModel
from backend.repositories.base import BaseRepository


class ReportRepository(BaseRepository[ReportModel]):
    """Repository handling database operations for ReportModel."""

    def __init__(self, session: Session):
        super().__init__(ReportModel, session)

    def get_by_job(self, job_id: str) -> Optional[ReportModel]:
        """Fetch final report metadata for a specific research job."""
        return (
            self.session.query(ReportModel)
            .filter(ReportModel.job_id == job_id)
            .first()
        )
