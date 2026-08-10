from typing import List
from sqlalchemy.orm import Session
from backend.models.knowledge import KnowledgeEntryModel
from backend.repositories.base import BaseRepository


class KnowledgeRepository(BaseRepository[KnowledgeEntryModel]):
    """Repository handling database operations for KnowledgeEntryModel."""

    def __init__(self, session: Session):
        super().__init__(KnowledgeEntryModel, session)

    def list_by_job(self, job_id: str) -> List[KnowledgeEntryModel]:
        """List knowledge findings accumulated for a research session/job."""
        return (
            self.session.query(KnowledgeEntryModel)
            .filter(KnowledgeEntryModel.job_id == job_id)
            .all()
        )
