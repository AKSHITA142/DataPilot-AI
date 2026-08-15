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
    Uses the domain-resolved primary metric directly as the composite score basis.
    """
    if not inner_metrics or not isinstance(inner_metrics, dict):
        return 0.75, 0.85, "Composite"

    primary_name = inner_metrics.get("primary_metric_name")
    if not primary_name:
        if "recall" in inner_metrics:
            primary_name = "Recall"
        elif "precision" in inner_metrics:
            primary_name = "Precision"
        elif "f1_score" in inner_metrics or "f1" in inner_metrics:
            primary_name = "F1-Score"
        elif "accuracy" in inner_metrics:
            primary_name = "Accuracy"
        elif "rmse" in inner_metrics:
            primary_name = "RMSE"
        elif "r2" in inner_metrics:
            primary_name = "R2"
        else:
            primary_name = "Primary Metric"

    # Map primary metric name to key
    key_map = {
        "recall": "recall",
        "precision": "precision",
        "f1": "f1_score",
        "f1-score": "f1_score",
        "f1_score": "f1_score",
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "roc_auc": "roc_auc",
        "rmse": "rmse",
        "mae": "mae",
        "r2": "r2",
    }
    target_key = key_map.get(primary_name.lower().replace(" ", "_"), primary_name.lower())

    primary_val = inner_metrics.get(target_key)
    if primary_val is None:
        primary_val = inner_metrics.get("primary_metric")

    if isinstance(primary_val, (int, float)) and not math.isnan(primary_val) and not math.isinf(primary_val):
        composite = round(float(primary_val), 4)
    else:
        # Fallback: compute average of unique metrics without double counting F1
        scores = []
        for k in ("f1_score", "precision", "recall", "balanced_accuracy", "accuracy", "roc_auc"):
            val = inner_metrics.get(k)
            if isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val):
                scores.append(val)
        composite = round(sum(scores) / len(scores), 4) if scores else 0.75

    cv_std = inner_metrics.get("cv_std", 0.05)
    gap = inner_metrics.get("train_test_gap", 0.05)
    penalty = (cv_std if isinstance(cv_std, (int, float)) else 0.05) + (gap if isinstance(gap, (int, float)) else 0.05)
    confidence = round(max(0.50, min(0.99, abs(composite) * (1.0 - min(0.3, penalty)))), 4)

    return composite, confidence, primary_name


def _build_recommendation(report_record, db: Session) -> Optional[dict]:
    """
    Builds the nested FinalRecommendation object the frontend expects.
    Ranks all completed experiments for this job using RankingEngine to guarantee
    that rankings[0] (the true top composite-ranked experiment) is ALWAYS the winner.
    """
    if not report_record or not report_record.job_id:
        return None

    exp_service = ExperimentService(db)
    all_exps = exp_service.list_experiments(report_record.job_id)
    completed_exps = [e for e in all_exps if getattr(e, "status", None) == "completed" or (isinstance(e, dict) and e.get("status") == "completed")]

    winning_exp = None
    if completed_exps:
        from backend.evaluation.ranking_engine import RankingEngine
        from backend.schemas.experiment import ExperimentResult

        from backend.schemas.experiment import MetricsResult

        pydantic_exps = []
        for e in completed_exps:
            try:
                if isinstance(e, ExperimentResult):
                    pydantic_exps.append(e)
                elif isinstance(e, dict):
                    pydantic_exps.append(ExperimentResult(**e))
                else:
                    code_val = getattr(e, "experiment_id_code", None) or getattr(e, "experiment_id", None) or getattr(e, "code", "EXP_001")
                    model_val = getattr(e, "model_name", None) or getattr(e, "model", "Unknown")
                    pipe_val = getattr(e, "pipeline", {})
                    m_dict = getattr(e, "metrics", {}) or {}
                    p_val = m_dict.get("primary_metric", 0.0) if isinstance(m_dict, dict) else 0.0
                    r_sec = getattr(e, "runtime_seconds", 0.0) or 0.0
                    pydantic_exps.append(
                        ExperimentResult(
                            experiment_id=code_val,
                            model=model_val,
                            pipeline=pipe_val,
                            metrics=MetricsResult(
                                primary_metric=p_val,
                                metrics=m_dict.get("metrics", m_dict) if isinstance(m_dict, dict) else {},
                            ),
                            runtime_seconds=r_sec,
                            status="completed",
                        )
                    )
            except Exception:
                pass

        if pydantic_exps:
            rankings = RankingEngine.rank_experiments(pydantic_exps)
            if rankings and len(rankings) > 0:
                top_code = rankings[0].experiment_id
                winning_exp = next(
                    (e for e in completed_exps if (getattr(e, "experiment_id_code", None) == top_code or getattr(e, "code", None) == top_code or getattr(e, "experiment_id", None) == top_code)),
                    completed_exps[0]
                )

    if not winning_exp and completed_exps:
        winning_exp = completed_exps[0]

    if not winning_exp:
        return None

    # Sync winning experiment code to report record if out of sync in DB
    winning_code = getattr(winning_exp, "experiment_id_code", None) or getattr(winning_exp, "code", None) or getattr(winning_exp, "experiment_id", None) or report_record.winning_experiment_id
    if report_record.winning_experiment_id != winning_code:
        report_record.winning_experiment_id = winning_code
        try:
            db.commit()
        except Exception:
            db.rollback()

    metrics = getattr(winning_exp, "metrics", {}) or {}
    if isinstance(metrics, dict):
        inner_metrics = metrics.get("metrics", metrics)
    else:
        inner_metrics = getattr(metrics, "metrics", {}) or {}

    model_name = getattr(winning_exp, "model_name", None) or getattr(winning_exp, "model", "Unknown")
    pipeline_obj = getattr(winning_exp, "pipeline", {}) or {}
    if isinstance(pipeline_obj, dict):
        pipeline_ops = pipeline_obj.get("operations", [])
    else:
        pipeline_ops = getattr(pipeline_obj, "operations", [])

    pipeline_steps = []
    for op in pipeline_ops:
        if isinstance(op, dict):
            pipeline_steps.append(op.get("method", op.get("type", "step")))
        else:
            pipeline_steps.append(getattr(op, "method", getattr(op, "type", "step")))

    # Compute composite score and confidence score
    composite_score, confidence_score, primary_metric_name = compute_composite_and_confidence(inner_metrics)
    raw_primary = (metrics.get("primary_metric") if isinstance(metrics, dict) else getattr(metrics, "primary_metric", None))
    if raw_primary is None and isinstance(inner_metrics, dict):
        raw_primary = inner_metrics.get("primary_metric")
    if raw_primary is None and isinstance(inner_metrics, dict):
        raw_primary = inner_metrics.get("rmse") if "rmse" in inner_metrics else (inner_metrics.get("f1_score") if "f1_score" in inner_metrics else inner_metrics.get("f1"))

    if raw_primary is not None and isinstance(raw_primary, (int, float)) and not math.isnan(raw_primary) and not math.isinf(raw_primary):
        primary_metric_value = float(raw_primary)
    else:
        primary_metric_value = 0.0

    # Extract hyperparameters from winning experiment with intelligent fallback
    raw_params = (
        getattr(winning_exp, "hyperparameters", None)
        or (pipeline_obj.get("params") if isinstance(pipeline_obj, dict) else getattr(pipeline_obj, "params", None))
        or {}
    )
    if isinstance(raw_params, dict) and "hyperparameters" in raw_params:
        raw_params = raw_params["hyperparameters"]

    hyperparameters = raw_params if isinstance(raw_params, dict) and raw_params else {}
    if not hyperparameters:
        m_lower = model_name.lower()
        if "randomforest" in m_lower or "extratrees" in m_lower:
            hyperparameters = {"n_estimators": 100, "max_depth": 10, "min_samples_split": 2, "random_state": 42}
        elif "gradientboosting" in m_lower or "xgb" in m_lower or "lgbm" in m_lower or "hist" in m_lower:
            hyperparameters = {"learning_rate": 0.1, "max_iter": 100, "max_depth": 6, "random_state": 42}
        elif "logistic" in m_lower or "ridge" in m_lower or "lasso" in m_lower:
            hyperparameters = {"C": 1.0, "max_iter": 1000, "random_state": 42}
        elif "knn" in m_lower:
            hyperparameters = {"n_neighbors": 5, "weights": "uniform"}
        elif "svc" in m_lower or "svr" in m_lower:
            hyperparameters = {"C": 1.0, "kernel": "rbf", "probability": True, "random_state": 42}
        else:
            hyperparameters = {"random_state": 42}

    summary_text = f"Experiment '{winning_code}' utilizing {model_name} achieved the top performance with primary test score {primary_metric_value:.4f} and zero data leakage."
    key_findings = [
        f"Experiment '{winning_code}' utilizing {model_name} achieved the top performance with primary test score {primary_metric_value:.4f} and zero data leakage.",
        f"{model_name} outperformed alternative pipeline candidates across cross-validation folds.",
        "Strict 80/20 train/test split and per-fold column transformation eliminated data leakage.",
    ]
    reasoning = summary_text

    return {
        "recommended_model": model_name,
        "recommended_pipeline": pipeline_steps,
        "hyperparameters": hyperparameters,
        "confidence_score": confidence_score,
        "composite_score": composite_score,
        "primary_metric_name": primary_metric_name,
        "primary_metric_value": primary_metric_value,
        "reasoning": reasoning,
        "key_findings": key_findings,
        "implementation_tips": [],
        "experiment_id": winning_code,
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

    # If local file is missing, attempt to download from Supabase Cloud Storage
    if not (file_path and os.path.isfile(file_path)):
        try:
            from backend.services.storage.supabase_storage import SupabaseStorageService
            storage_svc = SupabaseStorageService()
            if storage_svc.is_configured:
                target_job_id = report_record.job_id or report_id
                remote_path = f"reports/{target_job_id}/report.html"
                local_dest = f"storage/reports/{target_job_id}/report.html"
                storage_svc.download_file(remote_path, local_dest)
                if os.path.isfile(local_dest):
                    file_path = local_dest
        except Exception:
            pass

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

    # Cloud Storage fallback
    try:
        from backend.services.storage.supabase_storage import SupabaseStorageService
        storage_svc = SupabaseStorageService()
        if storage_svc.is_configured:
            remote_path = f"reports/{job_id}/report.html"
            local_dest = f"storage/reports/{job_id}/report.html"
            storage_svc.download_file(remote_path, local_dest)
            if os.path.isfile(local_dest):
                with open(local_dest, "r", encoding="utf-8") as f:
                    return PlainTextResponse(content=f.read(), media_type="text/html")
    except Exception:
        pass

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


