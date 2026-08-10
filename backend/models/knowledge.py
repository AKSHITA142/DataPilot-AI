from typing import Any, Optional, List
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin, generate_uuid
from backend.models.base_model import JSONType


class KnowledgeEntryModel(Base, TimestampMixin):
    """Accumulated Knowledge Base findings database model."""
    __tablename__ = "knowledge_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    finding: Mapped[str] = mapped_column(String(2048), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    source_experiment_ids: Mapped[Optional[List[str]]] = mapped_column(JSONType, nullable=True)

    # Relationships
    job = relationship("JobModel", back_populates="knowledge_entries")
