from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.services.experiment_service import ExperimentService
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/experiments", tags=["Experiments Explorer"])


def _experiment_to_frontend(exp, job_id: str) -> dict:
    """
    Converts an ExperimentModel row into the flattened dictionary shape
    the frontend `ExperimentResult` type expects.

    Frontend needs top-level metric fields (accuracy, f1_score, composite_score, etc.)
    instead of a nested `metrics: {}` object.
    """
    metrics = exp.metrics or {}
    # Extract nested metrics (could be {primary_metric, metrics: {acc, f1}, cv_scores}
    # or flat {accuracy, f1_score, ...})
    inner_metrics = metrics.get("metrics", metrics)

    # Compute composite_score as the average of available classification metrics
    available_scores = []
    for key in ("accuracy", "f1_score", "roc_auc", "precision", "recall"):
        val = inner_metrics.get(key)
        if isinstance(val, (int, float)):
            available_scores.append(val)
    composite_score = (sum(available_scores) / len(available_scores)) if available_scores else None

    # Determine primary metric
    primary_metric_value = metrics.get("primary_metric") or (available_scores[0] if available_scores else None)
    primary_metric_name = None
    if inner_metrics.get("accuracy") is not None:
        primary_metric_name = "Accuracy"
    elif inner_metrics.get("rmse") is not None:
        primary_metric_name = "RMSE"

    # Build pipeline name from operations or model name
    pipeline_ops = exp.pipeline or {}
    operations = pipeline_ops.get("operations", [])
    if operations:
        step_names = [op.get("method", op.get("type", "step")) for op in operations]
        pipeline_name = " → ".join(step_names) + f" → {exp.model_name}"
    else:
        pipeline_name = exp.model_name or "Unknown Pipeline"

    return {
        "experiment_id": exp.experiment_id_code,
        "job_id": job_id,
        "pipeline_name": pipeline_name,
        "model_name": exp.model_name,
        "model_type": exp.model_name,
        "status": exp.status or "completed",
        "primary_metric_name": primary_metric_name,
        "primary_metric_value": primary_metric_value,
        "composite_score": composite_score,
        # Flatten individual metrics to top-level
        "accuracy": inner_metrics.get("accuracy"),
        "precision": inner_metrics.get("precision"),
        "recall": inner_metrics.get("recall"),
        "f1_score": inner_metrics.get("f1_score"),
        "roc_auc": inner_metrics.get("roc_auc"),
        "rmse": inner_metrics.get("rmse"),
        "mae": inner_metrics.get("mae"),
        "r2": inner_metrics.get("r2"),
        "runtime_seconds": exp.runtime_seconds,
        "feature_importance": (exp.artifact_paths or {}).get("feature_importance"),
        "pipeline_steps": [op.get("method", "") for op in operations] if operations else None,
        "error_message": None,
        "created_at": exp.created_at.isoformat() if exp.created_at else None,
        "completed_at": None,
        # Keep original nested format for backwards-compatibility
        "pipeline": exp.pipeline,
        "metrics": exp.metrics,
        "artifact_paths": exp.artifact_paths,
    }


@router.get("/{job_id}", response_model=SuccessResponse)
def list_job_experiments(job_id: str, db: Session = Depends(get_db)):
    """
    Lists all executed experiment results and metrics for a research job.
    """
    service = ExperimentService(db)
    experiments = service.list_experiments(job_id)

    exp_data = [_experiment_to_frontend(exp, job_id) for exp in experiments]

    return SuccessResponse(
        data=exp_data,
        message=f"Retrieved {len(exp_data)} experiments for job '{job_id}'.",
    )


@router.get("/detail/{experiment_id}", response_model=SuccessResponse)
def get_experiment_detail(experiment_id: str, db: Session = Depends(get_db)):
    """
    Retrieves a single experiment by its database ID.
    """
    service = ExperimentService(db)
    # Search across all jobs for this experiment DB id
    from backend.repositories.experiment_repository import ExperimentRepository
    repo = ExperimentRepository(db)
    exp = repo.get_by_id(experiment_id)
    if not exp:
        from backend.core.exceptions import NotFoundException
        raise NotFoundException(f"Experiment '{experiment_id}' not found.")

    return SuccessResponse(
        data=_experiment_to_frontend(exp, exp.job_id),
        message="Experiment detail retrieved successfully.",
    )
