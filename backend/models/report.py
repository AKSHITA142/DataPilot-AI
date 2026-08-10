from typing import Any, Optional, Dict
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin, generate_uuid
from backend.models.base_model import JSONType


class ReportModel(Base, TimestampMixin):
    """Final research report metadata database model."""
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), nullable=False, unique=True)
    winning_experiment_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    report_file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)

    # Relationships
    job = relationship("JobModel", back_populates="report")
