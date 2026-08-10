from typing import Any, Dict, List
from pydantic import Field
from backend.schemas.base import BaseSchema


class MissionConstraints(BaseSchema):
    """User-specified or inferred constraints on dataset processing."""
    max_row_loss: float = Field(default=0.05, ge=0.0, le=1.0)
    use_only_open_source_models: bool = True
    training_time_limit_minutes: int = Field(default=30, gt=0)
    forbidden_operations: List[str] = Field(default_factory=list)
    custom_constraints: Dict[str, Any] = Field(default_factory=dict)


class DatasetCharacteristics(BaseSchema):
    """Semantic context of the dataset domain and complexity."""
    domain: str = "General"
    risk_level: str = "Low"
    complexity: str = "Medium"


class MissionBrief(BaseSchema):
    """Canonical objective and constraint payload derived by the Dataset Understanding Agent."""
    objective: str
    constraints: MissionConstraints = Field(default_factory=MissionConstraints)
    dataset_characteristics: DatasetCharacteristics = Field(default_factory=DatasetCharacteristics)
    success_metrics: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
