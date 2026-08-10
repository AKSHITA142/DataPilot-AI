from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief, DatasetCharacteristics, MissionConstraints
from backend.agents.base import BaseAgent


class DatasetUnderstandingAgent(BaseAgent):
    """Reasoning agent that converts dataset profile and user goal into a MissionBrief."""

    @property
    def name(self) -> str:
        return "Dataset Understanding Agent"

    @property
    def response_model(self) -> Type[BaseModel]:
        return MissionBrief

    def format_prompt(self, inputs: Dict[str, Any]) -> str:
        profile: Optional[SemanticProfile] = inputs.get("semantic_profile")
        user_goal: str = inputs.get("user_goal", "Optimize machine learning model performance.")
        target_col: str = inputs.get("target_column", "target")

        rows = profile.dataset_summary.get("rows", 0) if profile else 0
        cols = profile.dataset_summary.get("columns", 0) if profile else 0

        return (
            f"Analyze the dataset profile and user goal to form a MissionBrief:\n"
            f"User Goal: {user_goal}\n"
            f"Target Column: {target_col}\n"
            f"Dataset Size: {rows} rows, {cols} columns.\n"
            f"Formulate domain, task type, constraints, and success metrics."
        )

    def get_fallback_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_goal = inputs.get("user_goal", "Maximize model predictive accuracy")
        target_col = inputs.get("target_column", "target")

        return {
            "objective": user_goal,
            "constraints": {
                "max_row_loss": 0.05,
                "use_only_open_source_models": True,
                "training_time_limit_minutes": 30,
                "forbidden_operations": [],
                "custom_constraints": {},
            },
            "dataset_characteristics": {
                "domain": "General Tabular Data",
                "risk_level": "Low",
                "complexity": "Medium",
            },
            "success_metrics": ["f1", "accuracy", "roc_auc"],
            "avoid": ["data_leakage", "severe_overfitting"],
        }
