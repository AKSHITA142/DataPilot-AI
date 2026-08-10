from typing import Any, Dict, Type
from pydantic import BaseModel

from backend.schemas.mission_brief import MissionConstraints
from backend.agents.base import BaseAgent


class ConstraintGoalAnalyzer(BaseAgent):
    """Reasoning agent that converts user natural language constraints into structured MissionConstraints."""

    @property
    def name(self) -> str:
        return "Constraint & Goal Analyzer"

    @property
    def response_model(self) -> Type[BaseModel]:
        return MissionConstraints

    def format_prompt(self, inputs: Dict[str, Any]) -> str:
        user_instructions: str = inputs.get("user_instructions", "")
        return (
            f"Extract structured constraints from user instructions:\n"
            f"User Instructions: '{user_instructions}'\n"
            f"Extract max_row_loss, training_time_limit_minutes, prefer_interpretable_models, forbidden_operations."
        )

    def get_fallback_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        instructions = str(inputs.get("user_instructions", "")).lower()
        prefer_interpretable = "interpretable" in instructions or "explainable" in instructions or "simple" in instructions

        return {
            "max_row_loss": 0.05,
            "use_only_open_source_models": True,
            "training_time_limit_minutes": 30,
            "forbidden_operations": [],
            "custom_constraints": {"prefer_interpretable_models": prefer_interpretable},
        }
