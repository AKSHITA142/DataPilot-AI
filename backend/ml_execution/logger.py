import time
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("datapilot.ml_execution")


class ExperimentLogger:
    """Logs structured experiment run metrics, runtime, and diagnostic outputs."""

    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def start(self) -> None:
        """Marks the start of experiment execution."""
        self.start_time = time.time()
        logger.info(f"Starting execution for Experiment ID: {self.experiment_id}")

    def finish(self, status: str = "completed", metrics: Optional[Dict[str, Any]] = None) -> float:
        """Marks the completion of experiment execution and records runtime."""
        self.end_time = time.time()
        runtime = round(self.end_time - self.start_time, 4)
        logger.info(
            f"Finished Experiment ID: {self.experiment_id} | Status: {status} | "
            f"Runtime: {runtime}s | Metrics: {metrics or {}}"
        )
        return runtime

    def log_error(self, error: Exception) -> None:
        """Logs an execution failure."""
        logger.error(f"Experiment ID: {self.experiment_id} failed with error: {error}", exc_info=True)
