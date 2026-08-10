from typing import Any, Optional, Dict
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin, generate_uuid
from backend.models.base_model import JSONType


class ExperimentModel(Base, TimestampMixin):
    """Individual experiment record database model."""
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    experiment_id_code: Mapped[str] = mapped_column(String(50), nullable=False)
    pipeline: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hyperparameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    runtime_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    artifact_paths: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)

    # Relationships
    job = relationship("JobModel", back_populates="experiments")
