from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.services.experiment_service import ExperimentService
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/experiments", tags=["Experiments Explorer"])


@router.get("/{job_id}", response_model=SuccessResponse)
def list_job_experiments(job_id: str, db: Session = Depends(get_db)):
    """
    Lists all executed experiment results and metrics for a research job.
    """
    service = ExperimentService(db)
    experiments = service.list_experiments(job_id)

    exp_data = [
        {
            "id": exp.id,
            "experiment_id": exp.experiment_id_code,
            "pipeline": exp.pipeline,
            "model_name": exp.model_name,
            "metrics": exp.metrics,
            "artifact_paths": exp.artifact_paths,
            "created_at": exp.created_at.isoformat() if exp.created_at else None,
        }
        for exp in experiments
    ]

    return SuccessResponse(
        data=exp_data,
        message=f"Retrieved {len(exp_data)} experiments for job '{job_id}'.",
    )
