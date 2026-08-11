import asyncio
import logging
from datetime import datetime, timezone
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


def _now_iso() -> str:
    """Returns the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class JobManager:
    """
    Manager for dispatching long-running research jobs asynchronously,
    updating database records, and broadcasting WebSocket progress events.
    """

    @classmethod
    async def _broadcast(cls, job_id: str, payload: Dict[str, Any]):
        """Broadcasts a WebSocket event with mandatory timestamp and job_id fields."""
        payload.setdefault("job_id", job_id)
        payload.setdefault("timestamp", _now_iso())
        # Ensure data sub-object exists for frontend WSEvent.data mapping
        if "data" not in payload:
            data_fields = {}
            for key in ("status", "stage", "progress_percent", "message", "level",
                        "experiment_id", "finding", "report", "error"):
                if key in payload:
                    data_fields[key] = payload[key]
            payload["data"] = data_fields
        await ws_manager.broadcast_to_job(job_id, payload)

    @classmethod
    async def _broadcast_log(cls, job_id: str, message: str, stage: Optional[str] = None,
                             level: str = "info"):
        """Broadcasts a log.message event for the live execution console terminal."""
        await cls._broadcast(job_id, {
            "event": "log.message",
            "message": message,
            "level": level,
            "stage": stage,
            "progress_percent": None,
        })

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
            await cls._broadcast(job_id, {
                "event": "job.status_changed",
                "status": JobStatus.PROFILING.value,
                "stage": "profiling",
                "progress_percent": 10.0,
            })
            await cls._broadcast_log(job_id, "Starting dataset profiling...", stage="profiling")

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

            await cls._broadcast_log(job_id, "Compiled research graph. Invoking pipeline...",
                                     stage="profiling", level="info")

            # Run compiled graph
            final_state = await asyncio.to_thread(app.invoke, initial_state, config)

            # Check execution outcome
            final_status = final_state.get("job_status")
            if final_status == JobStatus.FAILED.value or final_state.get("error_message"):
                err = final_state.get("error_message") or "Unknown orchestration error."
                job_repo.update_status(job_id, JobStatus.FAILED, error_message=err)
                await cls._broadcast(job_id, {
                    "event": "job.failed",
                    "status": "failed",
                    "message": err,
                    "level": "error",
                    "error": err,
                })
                await cls._broadcast_log(job_id, f"Job failed: {err}", level="error")
                return

            # 3. Persist executed experiments to database
            exp_results = final_state.get("experiment_results") or []
            await cls._broadcast_log(job_id, f"Persisting {len(exp_results)} experiment results...",
                                     stage="evaluating")
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
                            runtime_seconds=exp_dict.get("runtime"),
                            status=exp_dict.get("status", "completed"),
                            artifact_paths=exp_dict.get("artifacts", {}),
                        )
                    )
                # Broadcast individual experiment completion
                await cls._broadcast(job_id, {
                    "event": "experiment.completed",
                    "experiment_id": exp_id,
                    "message": f"Experiment {exp_id} completed ({exp_dict.get('model', 'unknown')})",
                    "stage": "evaluating",
                    "level": "success",
                })

            # 4. Persist knowledge base findings to database
            kb_findings = final_state.get("knowledge_base") or []
            for k_idx, k_dict in enumerate(kb_findings):
                knowledge_repo.create(
                    KnowledgeEntryModel(
                        job_id=job_id,
                        finding=k_dict.get("finding", ""),
                        confidence=k_dict.get("confidence", 0.9),
                        source_experiment_ids=k_dict.get("source_experiment_ids", []),
                    )
                )


            if kb_findings:
                await cls._broadcast(job_id, {
                    "event": "knowledge.updated",
                    "message": f"Discovered {len(kb_findings)} knowledge findings",
                    "stage": "evaluating",
                    "level": "info",
                })

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

            await cls._broadcast_log(job_id, "Final report generated successfully.",
                                     stage="reporting", level="success")

            # 6. Update job status to completed & broadcast
            job_repo.update_status(job_id, JobStatus.COMPLETED, progress_pct=100.0)
            await cls._broadcast(job_id, {
                "event": "job.completed",
                "status": "completed",
                "stage": "reporting",
                "progress_percent": 100.0,
                "winning_experiment_id": winning_id,
                "message": "Research job completed successfully!",
                "level": "success",
            })

            logger.info(f"Research job {job_id} completed successfully!")

        except Exception as e:
            logger.error(f"Error executing background research job {job_id}: {e}", exc_info=True)
            # Rollback any uncommitted transaction to prevent SQLite lock
            try:
                db.rollback()
            except Exception:
                pass
            job_repo.update_status(job_id, JobStatus.FAILED, error_message=str(e))
            await cls._broadcast(job_id, {
                "event": "job.failed",
                "status": "failed",
                "error": str(e),
                "message": f"Job failed: {str(e)}",
                "level": "error",
            })
        finally:
            db.close()

