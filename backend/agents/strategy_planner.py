from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief
from backend.schemas.experiment import ExperimentPlan, ExperimentSpec, ExperimentOperation
from backend.agents.base import BaseAgent


class StrategyPlannerAgent(BaseAgent):
    """Reasoning agent that formulates prioritized ExperimentPlans using supported Phase 4 strategies."""

    @property
    def name(self) -> str:
        return "Strategy Planner Agent"

    @property
    def response_model(self) -> Type[BaseModel]:
        return ExperimentPlan

    def format_prompt(self, inputs: Dict[str, Any]) -> str:
        profile: Optional[SemanticProfile] = inputs.get("semantic_profile")
        mission: Optional[MissionBrief] = inputs.get("mission_brief")
        budget: int = inputs.get("experiment_budget", 3)

        return (
            f"Generate a batch of {budget} diverse ML experiment specifications.\n"
            f"Mission Objective: {mission.objective if mission else 'Classification'}\n"
            f"Select from supported models (RandomForest, LogisticRegression, XGBoost, LightGBM, CatBoost, SVC, LinearRegression, Ridge) "
            f"and transformers (imputation: median/mean/constant, encoding: onehot/ordinal/frequency, scaling: standard/robust/minmax)."
        )

    def get_fallback_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        mission: Optional[MissionBrief] = inputs.get("mission_brief")
        obj_text = mission.objective if mission else "Tabular Optimization"
        budget = inputs.get("experiment_budget", 3)

        task_type = inputs.get("task_type", "classification")

        if task_type == "regression":
            m1, m2, m3 = "RandomForestRegressor", "LinearRegression", "Ridge"
        else:
            m1, m2, m3 = "RandomForestClassifier", "LogisticRegression", "HistGradientBoostingClassifier"

        experiments = [
            {
                "experiment_id": "EXP_001",
                "operations": [
                    {"type": "imputation", "method": "median"},
                    {"type": "encoding", "method": "onehot"},
                    {"type": "scaling", "method": "standard"},
                ],
                "model_name": m1,
            },
            {
                "experiment_id": "EXP_002",
                "operations": [
                    {"type": "imputation", "method": "mean"},
                    {"type": "encoding", "method": "ordinal"},
                    {"type": "scaling", "method": "robust"},
                ],
                "model_name": m2,
            },
            {
                "experiment_id": "EXP_003",
                "operations": [
                    {"type": "imputation", "method": "median"},
                    {"type": "encoding", "method": "frequency"},
                    {"type": "scaling", "method": "minmax"},
                ],
                "model_name": m3,
            },
        ]

        return {
            "mission": f"Optimization for {obj_text}",
            "experiment_budget": budget,
            "experiments": experiments[:budget],
        }
