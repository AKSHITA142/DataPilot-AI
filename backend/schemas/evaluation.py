from typing import Any, Dict, List
from pydantic import Field
from backend.schemas.base import BaseSchema, ConfidenceScoredModel
from backend.schemas.enums import DecisionType
from backend.schemas.experiment import ExperimentSpec


class RankingItem(BaseSchema):
    """Ranked item entry in an evaluation report."""
    rank: int = Field(..., ge=1)
    experiment_id: str
    score: float
    model: str


class KnowledgeFinding(ConfidenceScoredModel):
    """An accumulated finding or insight extracted from experiment outcomes."""
    finding: str
    evidence: Dict[str, Any] = Field(default_factory=dict)


class EvaluationReport(BaseSchema):
    """Judgment produced by the Evaluation Engine over a batch of experiment results."""
    winner: str
    ranking: List[RankingItem] = Field(default_factory=list)
    knowledge: List[KnowledgeFinding] = Field(default_factory=list)
    should_continue: bool = True
    reason: str = ""


class ResearchDirectorDecision(ConfidenceScoredModel):
    """Decision object produced by the Research Director Agent to route the LangGraph orchestrator."""
    decision: DecisionType
    knowledge: List[str] = Field(default_factory=list)
    remaining_questions: List[str] = Field(default_factory=list)
    next_experiments: List[ExperimentSpec] = Field(default_factory=list)
