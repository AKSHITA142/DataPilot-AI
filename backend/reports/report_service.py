import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.schemas.report import FinalRecommendation
from backend.schemas.evaluation import EvaluationReport
from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief
from backend.reports.markdown_generator import MarkdownReportGenerator
from backend.reports.html_generator import HTMLReportGenerator
from backend.reports.exporter import ArtifactExporter
from backend.repositories.report_repository import ReportRepository

logger = logging.getLogger("datapilot.reports.service")


class ReportService:
    """Service orchestrating report generation, artifact export, and database persistence."""

    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.report_repo = ReportRepository(db_session) if db_session else None

    def generate_and_export_report(
        self,
        job_id: str,
        recommendation: FinalRecommendation,
        evaluation_report: Optional[EvaluationReport] = None,
        profile: Optional[SemanticProfile] = None,
        mission: Optional[MissionBrief] = None,
        storage_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates Markdown + HTML reports, exports files, persists DB record, and returns payload."""
        logger.info(f"Generating reports for job {job_id} (Winner: {recommendation.winning_experiment_id})")

        # 1. Render Markdown & HTML Reports
        md_text = MarkdownReportGenerator.generate_markdown(
            recommendation=recommendation,
            evaluation_report=evaluation_report,
            profile=profile,
            mission=mission,
        )

        html_text = HTMLReportGenerator.generate_html(
            recommendation=recommendation,
            evaluation_report=evaluation_report,
            profile=profile,
            mission=mission,
        )

        # 2. Export Artifacts to disk
        exported_paths = ArtifactExporter.export_report_files(
            html_content=html_text,
            md_content=md_text,
            job_id=job_id,
            storage_dir=storage_dir,
        )

        # Update recommendation object with exported artifact paths
        recommendation.exported_artifacts.update(exported_paths)

        # 3. Persist to Database if DB session present
        if self.report_repo:
            try:
                self.report_repo.create_report(
                    job_id=job_id,
                    winner_experiment_id=recommendation.winning_experiment_id,
                    summary=recommendation.summary,
                    recommendation_data=recommendation.model_dump(),
                )
                logger.info(f"Successfully persisted ReportModel in DB for job {job_id}")
            except Exception as e:
                logger.warning(f"Database report persistence warning for job {job_id}: {e}")

        return {
            "job_id": job_id,
            "recommendation": recommendation,
            "markdown_content": md_text,
            "html_content": html_text,
            "artifacts": exported_paths,
        }
