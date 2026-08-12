import os
import sys
import logging
from datetime import datetime
from typing import Optional

from backend.core.config import get_settings

class DailyDateFileHandler(logging.Handler):
    """
    Custom Logging Handler that dynamically writes log records into daily dated log files:
    e.g., storage/logs/2026-08-12.log
    """

    def __init__(self, log_dir: str):
        super().__init__()
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self._current_date_str: Optional[str] = None
        self._file_handler: Optional[logging.FileHandler] = None

    def _get_file_handler(self) -> logging.FileHandler:
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str != self._current_date_str or self._file_handler is None:
            if self._file_handler:
                self._file_handler.close()
            self._current_date_str = today_str
            file_path = os.path.join(self.log_dir, f"{today_str}.log")
            self._file_handler = logging.FileHandler(file_path, encoding="utf-8")
            self._file_handler.setFormatter(self.formatter)
        return self._file_handler

    def emit(self, record: logging.LogRecord) -> None:
        try:
            handler = self._get_file_handler()
            handler.emit(record)
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        if self._file_handler:
            self._file_handler.close()
        super().close()


def setup_logging() -> logging.Logger:
    """Configures system-wide logging with Console output and Daily Dated Log Files."""
    settings = get_settings()
    log_dir = os.path.join(settings.storage_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    formatter = logging.Formatter(log_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Clear existing handlers to prevent duplicate log entries
    root_logger.handlers.clear()

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Daily Dated File Handler (storage/logs/YYYY-MM-DD.log)
    daily_handler = DailyDateFileHandler(log_dir=log_dir)
    daily_handler.setFormatter(formatter)
    root_logger.addHandler(daily_handler)

    logger = logging.getLogger("datapilot")
    
    # Session Startup Banner
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banner = f"\n{'='*80}\n>>> NEW DATAPILOT-AI SESSION STARTED AT {now_str} <<<\n{'='*80}"
    logger.info(banner)

    return logger


def log_phase_banner(phase_name: str, phase_description: str = "") -> None:
    """Logs a prominent Phase Header Banner across console and daily log files."""
    logger = logging.getLogger("datapilot.phase")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banner = (
        f"\n{'='*80}\n"
        f"  🚀 ENTERING PHASE: {phase_name.upper()}\n"
        f"  ⏰ TIMESTAMP: {now_str}\n"
        f"  📝 DESCRIPTION: {phase_description}\n"
        f"{'='*80}"
    )
    logger.info(banner)
