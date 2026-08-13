from typing import Any, Dict, List, Optional
from pydantic import Field
from backend.schemas.base import BaseSchema


class ExperimentOperation(BaseSchema):
    """A single preprocessing or feature engineering step in a pipeline."""
    type: str
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)


class ExperimentSpec(BaseSchema):
    """Individual experiment specification created by the Strategy Planner."""
    experiment_id: str
    priority: int = 1
    reason: str = ""
    operations: List[ExperimentOperation] = Field(default_factory=list)
    model_name: str = "RandomForest"


class ExperimentPlan(BaseSchema):
    """Set of prioritized, executable experiments produced by the Strategy Planner."""
    mission: str = ""
    experiment_budget: int = Field(default=10, gt=0)
    experiments: List[ExperimentSpec] = Field(default_factory=list)


class PipelineDefinition(BaseSchema):
    """Execution graph specification for a pipeline."""
    operations: List[ExperimentOperation] = Field(default_factory=list)
    model_name: str = ""


class MetricsResult(BaseSchema):
    """Evaluated metric outputs for an experiment."""
    primary_metric: float = 0.0
    metrics: Dict[str, float] = Field(default_factory=dict)
    cv_scores: List[float] = Field(default_factory=list)


class Artifacts(BaseSchema):
    """Paths or metadata for persistent execution artifacts."""
    model_path: Optional[str] = None
    processed_dataset_path: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    confusion_matrix: Optional[List[List[int]]] = None
    plots: Dict[str, str] = Field(default_factory=dict)
    cleaning_audit: Optional[Dict[str, Any]] = None



class ExperimentResult(BaseSchema):
    """Objective, deterministic output of the ML Execution Engine for a single experiment."""
    experiment_id: str
    pipeline: PipelineDefinition
    model: str
    metrics: MetricsResult
    runtime: float = Field(default=0.0, ge=0.0)
    status: str = "completed"
    artifacts: Optional[Artifacts] = None
    error_message: Optional[str] = None
