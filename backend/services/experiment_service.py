from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.exceptions import NotFoundException
from backend.repositories.experiment_repository import ExperimentRepository
from backend.models.experiment import ExperimentModel


class ExperimentService:
    """Service layer managing queries for executed experiments."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ExperimentRepository(db)

    def list_experiments(self, job_id: str) -> List[ExperimentModel]:
        """Lists all executed experiments for a job."""
        return self.repository.list_by_job(job_id)

    def get_experiment_by_code(self, job_id: str, experiment_code: str) -> ExperimentModel:
        """Retrieves a single experiment record by job ID and experiment code."""
        exp = self.repository.get_by_code(job_id, experiment_code)
        if not exp:
            raise NotFoundException(f"Experiment '{experiment_code}' not found for job '{job_id}'.")
        return exp
