from typing import List, Optional
from pydantic import Field
from backend.schemas.base import BaseSchema
from backend.schemas.enums import JobStatus
from backend.schemas.evaluation import EvaluationReport, KnowledgeFinding, ResearchDirectorDecision
from backend.schemas.experiment import ExperimentPlan, ExperimentResult
from backend.schemas.mission_brief import MissionBrief
from backend.schemas.report import FinalRecommendation
from backend.schemas.semantic_profile import SemanticProfile


class WorkflowState(BaseSchema):
    """Canonical contract for the shared state object passed between every LangGraph node."""
    dataset_id: str
    job_status: JobStatus = JobStatus.QUEUED
    user_goal: Optional[str] = None
    semantic_profile: Optional[SemanticProfile] = None
    mission_brief: Optional[MissionBrief] = None
    experiment_plan: Optional[ExperimentPlan] = None
    experiment_results: List[ExperimentResult] = Field(default_factory=list)
    evaluation_report: Optional[EvaluationReport] = None
    knowledge_base: List[KnowledgeFinding] = Field(default_factory=list)
    decision: Optional[ResearchDirectorDecision] = None
    final_report: Optional[FinalRecommendation] = None
    error_message: Optional[str] = None
