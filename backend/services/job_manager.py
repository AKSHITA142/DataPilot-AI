import asyncio
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.schemas.enums import JobStatus
from backend.database.connection import SessionLocal
from backend.repositories.job_repository import JobRepository
from backend.repositories.experiment_repository import ExperimentRepository
from backend.repositories.report_repository import ReportRepository
from backend.repositories.knowledge_repository import KnowledgeRepository
from backend.models.job import JobModel
from backend.models.experiment import ExperimentModel
from backend.models.report import ReportModel
from backend.models.knowledge import KnowledgeEntryModel
from backend.graph import compile_graph, create_initial_state
from backend.api.websocket_manager import ws_manager

logger = logging.getLogger("datapilot.services.job_manager")


class JobManager:
    """
    Manager for dispatching long-running research jobs asynchronously,
    updating database records, and broadcasting WebSocket progress events.
    """

    @classmethod
    async def run_job_async(cls, job_id: str, dataset_id: str, file_path: str, user_goal: Optional[str] = None):
        """Asynchronous worker executing the compiled LangGraph state machine."""
        db: Session = SessionLocal()
        job_repo = JobRepository(db)
        exp_repo = ExperimentRepository(db)
        report_repo = ReportRepository(db)
        knowledge_repo = KnowledgeRepository(db)

        try:
            # 1. Update status to profiling & broadcast
            job_repo.update_status(job_id, JobStatus.PROFILING, progress_pct=10.0)
            await ws_manager.broadcast_to_job(job_id, {
                "event": "job.status_changed",
                "job_id": job_id,
                "status": JobStatus.PROFILING.value,
                "progress": 10.0,
            })

            # 2. Compile LangGraph workflow
            app = compile_graph()
            initial_state = create_initial_state(
                dataset_id=dataset_id,
                job_id=job_id,
                file_path=file_path,
                user_goal=user_goal,
                max_iterations=3,
            )

            config = {"configurable": {"thread_id": f"thread_{job_id}"}}

            # Run compiled graph
            final_state = await asyncio.to_thread(app.invoke, initial_state, config)

            # Check execution outcome
            final_status = final_state.get("job_status")
            if final_status == JobStatus.FAILED.value or final_state.get("error_message"):
                err = final_state.get("error_message") or "Unknown orchestration error."
                job_repo.update_status(job_id, JobStatus.FAILED, error_message=err)
                await ws_manager.broadcast_to_job(job_id, {
                    "event": "job.failed",
                    "job_id": job_id,
                    "error": err,
                })
                return

            # 3. Persist executed experiments to database
            exp_results = final_state.get("experiment_results") or []
            for idx, exp_dict in enumerate(exp_results):
                exp_id = exp_dict.get("experiment_id") or f"exp_{job_id}_{idx}"
                existing_exp = exp_repo.get_by_code(job_id, exp_id)
                if not existing_exp:
                    exp_repo.create(
                        ExperimentModel(
                            id=f"exp_db_{job_id}_{idx}",
                            job_id=job_id,
                            experiment_id_code=exp_id,
                            pipeline=exp_dict.get("pipeline", {}),
                            model_name=exp_dict.get("model", "xgboost"),
                            metrics=exp_dict.get("metrics", {}),
                            artifact_paths=exp_dict.get("artifacts", {}),
                        )
                    )

            # 4. Persist knowledge base findings to database
            kb_findings = final_state.get("knowledge_base") or []
            for k_idx, k_dict in enumerate(kb_findings):
                knowledge_repo.create(
                    KnowledgeEntryModel(
                        id=f"k_{job_id}_{k_idx}",
                        job_id=job_id,
                        finding=k_dict.get("finding", ""),
                        confidence=k_dict.get("confidence", 0.9),
                        source_experiment_ids=k_dict.get("source_experiment_ids", []),
                    )
                )

            # 5. Persist final report to database
            final_report_dict = final_state.get("final_report") or {}
            winning_id = final_report_dict.get("winning_experiment_id") or "exp_1"
            
            existing_report = report_repo.get_by_job(job_id)
            if not existing_report:
                report_repo.create(
                    ReportModel(
                        id=f"rep_{job_id}",
                        job_id=job_id,
                        winning_experiment_id=winning_id,
                        report_file_path=f"storage/reports/{job_id}/report.md",
                        summary=final_report_dict.get("summary") or "Final research report completed.",
                    )
                )

            # 6. Update job status to completed & broadcast
            job_repo.update_status(job_id, JobStatus.COMPLETED, progress_pct=100.0)
            await ws_manager.broadcast_to_job(job_id, {
                "event": "job.completed",
                "job_id": job_id,
                "winning_experiment_id": winning_id,
                "progress": 100.0,
            })

            logger.info(f"Research job {job_id} completed successfully!")

        except Exception as e:
            logger.error(f"Error executing background research job {job_id}: {e}", exc_info=True)
            job_repo.update_status(job_id, JobStatus.FAILED, error_message=str(e))
            await ws_manager.broadcast_to_job(job_id, {
                "event": "job.failed",
                "job_id": job_id,
                "error": str(e),
            })
        finally:
            db.close()
