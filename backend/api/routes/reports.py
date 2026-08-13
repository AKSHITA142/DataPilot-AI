import os
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.services.report_service import ReportService
from backend.services.experiment_service import ExperimentService
from backend.schemas.response import SuccessResponse
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/reports", tags=["Final Reports"])


def _build_recommendation(report_record, db: Session) -> Optional[dict]:
    """
    Builds the nested FinalRecommendation object the frontend expects,
    combining report metadata with the winning experiment's metrics.
    """
    if not report_record.winning_experiment_id:
        return None

    # Try to load the winning experiment for detailed metrics
    exp_service = ExperimentService(db)
    winning_exp = None
    try:
        winning_exp = exp_service.get_experiment_by_code(
            report_record.job_id, report_record.winning_experiment_id
        )
    except Exception:
        pass

    metrics = {}
    model_name = "Unknown"
    pipeline_steps = []
    if winning_exp:
        metrics = winning_exp.metrics or {}
        inner_metrics = metrics.get("metrics", metrics)
        model_name = winning_exp.model_name or "Unknown"
        pipeline_ops = (winning_exp.pipeline or {}).get("operations", [])
        pipeline_steps = [op.get("method", op.get("type", "step")) for op in pipeline_ops]
    else:
        inner_metrics = {}

    # Compute composite score
    available_scores = []
    for key in ("accuracy", "f1_score", "roc_auc", "precision", "recall"):
        val = inner_metrics.get(key)
        if isinstance(val, (int, float)):
            available_scores.append(val)
    composite_score = (sum(available_scores) / len(available_scores)) if available_scores else 0.0

    # Determine primary metric
    primary_metric_value = metrics.get("primary_metric") or (available_scores[0] if available_scores else 0.0)
    primary_metric_name = "Accuracy" if inner_metrics.get("accuracy") is not None else "RMSE"

    # Extract summary data
    summary = report_record.summary
    summary_text = ""
    key_findings = []
    reasoning = ""
    if isinstance(summary, dict):
        summary_text = summary.get("summary", "")
        key_findings = summary.get("key_findings", [])
        reasoning = summary.get("reasoning", summary_text)
    elif isinstance(summary, str):
        summary_text = summary
        reasoning = summary

    return {
        "recommended_model": model_name,
        "recommended_pipeline": pipeline_steps,
        "confidence_score": composite_score,
        "composite_score": composite_score,
        "primary_metric_name": primary_metric_name,
        "primary_metric_value": primary_metric_value,
        "reasoning": reasoning,
        "key_findings": key_findings if key_findings else [summary_text] if summary_text else [],
        "implementation_tips": [],
        "experiment_id": report_record.winning_experiment_id,
    }


@router.get("/{job_id}", response_model=SuccessResponse)
def get_final_report(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the final recommendation report for a completed research job.
    Returns the full Report object with nested FinalRecommendation.
    """
    service = ReportService(db)
    report_record = service.get_report_by_job(job_id)

    recommendation = _build_recommendation(report_record, db)

    return SuccessResponse(
        data={
            "report_id": report_record.id,
            "job_id": report_record.job_id,
            "dataset_id": report_record.job.dataset_id if report_record.job else None,
            "status": "completed",
            "recommendation": recommendation,
            "experiment_count": len(report_record.job.experiments) if report_record.job else 0,
            "knowledge_findings_count": len(report_record.job.knowledge_entries) if report_record.job else 0,
            "markdown_report": None,  # Populated on download
            "created_at": report_record.created_at.isoformat() if report_record.created_at else None,
            "completed_at": report_record.created_at.isoformat() if report_record.created_at else None,
            # Keep original fields for backwards-compat
            "winning_experiment_id": report_record.winning_experiment_id,
            "report_file_path": report_record.report_file_path,
            "summary": report_record.summary,
        },
        message="Final research report retrieved successfully.",
    )


@router.get("/{report_id}/download")
def download_report(
    report_id: str,
    format: str = Query(default="markdown", pattern="^(markdown|html)$"),
    db: Session = Depends(get_db),
):
    """
    Downloads the generated report file as a Markdown or HTML blob.
    Falls back to a plain-text summary if the file does not exist on disk.
    """
    from backend.repositories.report_repository import ReportRepository
    repo = ReportRepository(db)
    report_record = repo.get_by_id(report_id)

    # Also try by job_id in case the frontend passes job_id instead of report_id
    if not report_record:
        report_record = repo.get_by_job(report_id)

    if not report_record:
        raise NotFoundException(f"Report '{report_id}' not found.")

    file_path = report_record.report_file_path

    if file_path and os.path.isfile(file_path):
        media_type = "text/html" if format == "html" else "text/markdown"
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path),
        )

    # File doesn't exist yet — return the summary as plain text
    summary = report_record.summary
    content = ""
    if isinstance(summary, dict):
        content = summary.get("summary", str(summary))
    elif isinstance(summary, str):
        content = summary
    else:
        content = "Report file not yet generated."

    return PlainTextResponse(content=content, media_type="text/markdown")


@router.get("/{job_id}/html")
def get_report_html(job_id: str, db: Session = Depends(get_db)):
    """
    Returns the standalone HTML report string for direct rendering in frontend iframe/preview.
    """
    from backend.repositories.report_repository import ReportRepository
    repo = ReportRepository(db)
    report_record = repo.get_by_job(job_id) or repo.get_by_id(job_id)

    if report_record and report_record.report_file_path and os.path.isfile(report_record.report_file_path):
        with open(report_record.report_file_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(content=f.read(), media_type="text/html")

    html_candidate = f"storage/reports/{job_id}/report.html"
    if os.path.isfile(html_candidate):
        with open(html_candidate, "r", encoding="utf-8") as f:
            return PlainTextResponse(content=f.read(), media_type="text/html")

    fallback_html = f"""<!DOCTYPE html>
<html>
<body style="background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:20px;">
    <h2>DataPilot-AI Report</h2>
    <p>Report is being generated or finalized for job <code>{job_id}</code>...</p>
</body>
</html>"""
    return PlainTextResponse(content=fallback_html, media_type="text/html")


@router.get("/{job_id}/download-dataset")
def download_preprocessed_dataset(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Downloads the preprocessed/cleaned CSV dataset artifact generated for the research job.
    """
    from backend.repositories.job_repository import JobRepository
    from backend.repositories.dataset_repository import DatasetRepository
    from backend.repositories.report_repository import ReportRepository

    job_repo = JobRepository(db)
    job = job_repo.get_by_id(job_id)

    cleaned_csv_path = None

    report_repo = ReportRepository(db)
    report = report_repo.get_by_job(job_id) if job else None

    if report and report.winning_experiment_id:
        candidate_biz = f"storage/artifacts/{report.winning_experiment_id}_business_action.csv"
        candidate_legacy = f"storage/artifacts/{report.winning_experiment_id}_cleaned.csv"
        if os.path.isfile(candidate_biz):
            cleaned_csv_path = candidate_biz
        elif os.path.isfile(candidate_legacy):
            cleaned_csv_path = candidate_legacy

    if not cleaned_csv_path and os.path.isdir("storage/artifacts"):
        for fname in os.listdir("storage/artifacts"):
            if fname.endswith("_business_action.csv") or fname.endswith("_cleaned.csv"):
                cleaned_csv_path = os.path.join("storage/artifacts", fname)
                break

    if not cleaned_csv_path and job:
        ds_repo = DatasetRepository(db)
        dataset = ds_repo.get_by_id(job.dataset_id)
        if dataset and os.path.isfile(dataset.file_path):
            cleaned_csv_path = dataset.file_path

    if not cleaned_csv_path or not os.path.isfile(cleaned_csv_path):
        raise NotFoundException(f"No preprocessed dataset CSV artifact found for job '{job_id}'.")

    filename = f"business_action_dataset_{job_id}.csv"
    return FileResponse(
        path=cleaned_csv_path,
        media_type="text/csv",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{job_id}/download-business-dataset")
def download_business_action_dataset(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Downloads Business Action CSV (IDs, Names, Clean Features, Target, Predictions).
    """
    return download_preprocessed_dataset(job_id=job_id, db=db)


@router.get("/{job_id}/download-ml-feature-matrix")
def download_ml_feature_matrix(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Downloads ML-Ready Feature Matrix CSV (Pure engineered numerical features X and target y).
    """
    from backend.repositories.job_repository import JobRepository
    from backend.repositories.report_repository import ReportRepository

    job_repo = JobRepository(db)
    job = job_repo.get_by_id(job_id)

    ml_csv_path = None
    report_repo = ReportRepository(db)
    report = report_repo.get_by_job(job_id) if job else None

    if report and report.winning_experiment_id:
        candidate = f"storage/artifacts/{report.winning_experiment_id}_ml_ready.csv"
        if os.path.isfile(candidate):
            ml_csv_path = candidate

    if not ml_csv_path and os.path.isdir("storage/artifacts"):
        for fname in os.listdir("storage/artifacts"):
            if fname.endswith("_ml_ready.csv"):
                ml_csv_path = os.path.join("storage/artifacts", fname)
                break

    # Fallback to standard preprocessed dataset if ml_ready artifact doesn't exist
    if not ml_csv_path:
        return download_preprocessed_dataset(job_id=job_id, db=db)

    filename = f"ml_ready_matrix_{job_id}.csv"
    return FileResponse(
        path=ml_csv_path,
        media_type="text/csv",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


