import os
import pickle
from typing import Dict, Any, Optional
import pandas as pd

from backend.core.config import get_settings


class ArtifactExporter:
    """Exports dataset CSVs, trained model pickles, and report files to disk storage."""

    @classmethod
    def export_cleaned_dataset(cls, df: pd.DataFrame, job_id: str, storage_dir: Optional[str] = None) -> str:
        """Saves processed cleaned dataset CSV to storage/datasets/."""
        base_dir = storage_dir or get_settings().storage_dir
        datasets_dir = os.path.join(base_dir, "datasets")
        os.makedirs(datasets_dir, exist_ok=True)

        path = os.path.join(datasets_dir, f"cleaned_{job_id}.csv")
        df.to_csv(path, index=False)
        return path

    @classmethod
    def export_model_artifact(cls, fitted_pipeline: Any, job_id: str, storage_dir: Optional[str] = None) -> str:
        """Serializes trained scikit-learn pipeline to storage/models/."""
        base_dir = storage_dir or get_settings().storage_dir
        models_dir = os.path.join(base_dir, "models")
        os.makedirs(models_dir, exist_ok=True)

        path = os.path.join(models_dir, f"model_{job_id}.pkl")
        with open(path, "wb") as f:
            pickle.dump(fitted_pipeline, f)
        return path

    @classmethod
    def export_report_files(
        cls,
        html_content: str,
        md_content: str,
        job_id: str,
        storage_dir: Optional[str] = None,
    ) -> Dict[str, str]:
        """Saves HTML and Markdown report files to storage/reports/."""
        base_dir = storage_dir or get_settings().storage_dir
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        html_path = os.path.join(reports_dir, f"report_{job_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        md_path = os.path.join(reports_dir, f"report_{job_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return {
            "html": html_path,
            "markdown": md_path,
        }
