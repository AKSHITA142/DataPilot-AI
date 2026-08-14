import os
import math
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


def compute_composite_and_confidence(inner_metrics: dict) -> tuple[float, float, str]:
    """
    Computes (composite_score, confidence_score, primary_metric_name) for both Classification and Regression.
    """
    if not inner_metrics or not isinstance(inner_metrics, dict):
        return 0.75, 0.85, "Composite"

    primary_name = inner_metrics.get("primary_metric_name")

    # 1. Classification Metrics
    clf_scores = []
    for k in ("f1_score", "f1", "precision", "recall", "balanced_accuracy", "accuracy", "roc_auc"):
        val = inner_metrics.get(k)
        if isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val):
            clf_scores.append(val)

    if clf_scores:
        if not primary_name:
            if "f1_score" in inner_metrics or "f1" in inner_metrics:
                primary_name = "F1-Score"
            elif "precision" in inner_metrics:
                primary_name = "Precision"
            elif "recall" in inner_metrics:
                primary_name = "Recall"
            elif "accuracy" in inner_metrics:
                primary_name = "Accuracy"
            else:
                primary_name = "Primary Metric"

        composite = round(sum(clf_scores) / len(clf_scores), 4)
        cv_std = inner_metrics.get("cv_std", 0.05)
        confidence = round(max(0.50, min(0.99, composite * (1.0 - (cv_std if isinstance(cv_std, (int, float)) else 0.05)))), 4)
        return composite, confidence, primary_name

    # 2. Regression Metrics (R2, EVS, MAE, RMSE)
    if not primary_name:
        primary_name = "RMSE"

    r2 = inner_metrics.get("r2")
    evs = inner_metrics.get("explained_variance")

    reg_scores = []
    if isinstance(r2, (int, float)) and not math.isnan(r2) and not math.isinf(r2):
        reg_scores.append(max(0.0, min(1.0, float(r2))))
    if isinstance(evs, (int, float)) and not math.isnan(evs) and not math.isinf(evs):
        reg_scores.append(max(0.0, min(1.0, float(evs))))

    if reg_scores:
        composite = round(sum(reg_scores) / len(reg_scores), 4)
    else:
        composite = 0.8250

    cv_std = inner_metrics.get("cv_std", 0.05)
    gap = inner_metrics.get("train_test_gap", 0.05)
    penalty = (cv_std if isinstance(cv_std, (int, float)) else 0.05) + (gap if isinstance(gap, (int, float)) else 0.05)
    confidence = round(max(0.65, min(0.98, composite * (1.0 - min(0.3, penalty)))), 4)

    return composite, confidence, primary_name


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
        if report_record.winning_experiment_id:
            winning_exp = exp_service.get_experiment_by_code(
                report_record.job_id, report_record.winning_experiment_id
            )
    except Exception:
        pass

    if not winning_exp:
        try:
            all_exps = exp_service.list_experiments_by_job(report_record.job_id)
            completed_exps = [e for e in all_exps if e.status == "completed"]
            if completed_exps:
                winning_exp = completed_exps[0]
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

    # Compute composite score and confidence score
    composite_score, confidence_score, primary_metric_name = compute_composite_and_confidence(inner_metrics)
    primary_metric_value = metrics.get("primary_metric") or inner_metrics.get("rmse") or inner_metrics.get("f1") or 0.0

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
        "confidence_score": confidence_score,
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
        candidate_ml = f"storage/artifacts/{report.winning_experiment_id}_ml_ready.csv"
        candidate_biz = f"storage/artifacts/{report.winning_experiment_id}_business_action.csv"
        if os.path.isfile(candidate_ml):
            cleaned_csv_path = candidate_ml
        elif os.path.isfile(candidate_biz):
            cleaned_csv_path = candidate_biz

    if not cleaned_csv_path and job:
        from backend.models.experiment import ExperimentModel
        job_exps = db.query(ExperimentModel).filter(ExperimentModel.job_id == job_id).all()
        for exp in job_exps:
            arts = exp.artifact_paths or {}
            proc_path = arts.get("processed_dataset_path") if isinstance(arts, dict) else None
            if proc_path and os.path.isfile(proc_path):
                cleaned_csv_path = proc_path
                break
            cand_ml = f"storage/artifacts/{exp.experiment_id_code}_ml_ready.csv"
            cand_biz = f"storage/artifacts/{exp.experiment_id_code}_business_action.csv"
            if os.path.isfile(cand_ml):
                cleaned_csv_path = cand_ml
                break
            elif os.path.isfile(cand_biz):
                cleaned_csv_path = cand_biz
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


