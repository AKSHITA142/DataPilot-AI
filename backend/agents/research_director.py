from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from backend.schemas.enums import DecisionType
from backend.schemas.evaluation import EvaluationReport, ResearchDirectorDecision
from backend.agents.base import BaseAgent


class ResearchDirectorAgent(BaseAgent):
    """Reasoning agent that reviews EvaluationReports and directs loop iteration or stopping."""

    @property
    def name(self) -> str:
        return "Research Director Agent"

    @property
    def response_model(self) -> Type[BaseModel]:
        return ResearchDirectorDecision

    def format_prompt(self, inputs: Dict[str, Any]) -> str:
        report: Optional[EvaluationReport] = inputs.get("evaluation_report")
        winner = report.winner if report else "none"

        return (
            f"Review the EvaluationReport:\n"
            f"Winner: {winner}\n"
            f"Reasoning: {report.reason if report else ''}\n"
            f"Decide whether to CONTINUE iteration, STOP and report, or EXPLORE alternative strategies."
        )

    def get_fallback_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        report: Optional[EvaluationReport] = inputs.get("evaluation_report")
        should_cont = report.should_continue if report else False

        dec = DecisionType.CONTINUE if should_cont else DecisionType.STOP

        return {
            "decision": dec,
            "confidence": 0.92,
            "knowledge": [f.finding for f in (report.knowledge if report else [])],
            "remaining_questions": [],
            "next_experiments": [],
        }
