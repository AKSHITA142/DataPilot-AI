from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief
from backend.schemas.experiment import ExperimentPlan, ExperimentSpec, ExperimentOperation
from backend.agents.base import BaseAgent


try:
    import xgboost
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import catboost
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False


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
        budget: int = inputs.get("experiment_budget", 3)

        # Parse profile for row_count and task_type
        profile = inputs.get("semantic_profile")
        if isinstance(profile, SemanticProfile):
            prof_dict = profile.model_dump()
        elif isinstance(profile, dict):
            prof_dict = profile
        else:
            prof_dict = {}

        ds_summary = prof_dict.get("dataset_summary", {})
        row_count = ds_summary.get("row_count") or 1000
        target_info = ds_summary.get("target", {})
        task_type = inputs.get("task_type") or target_info.get("task_type") or "classification"

        # Tiered candidate model pool construction
        candidate_models = []

        if task_type == "regression":
            # Tier 1 (Always included - Linear, Tree, Boosting)
            candidate_models.extend(["RandomForestRegressor", "LinearRegression", "HistGradientBoostingRegressor"])

            # Tier 2 (Budget >= 5)
            if budget >= 5:
                candidate_models.append("ExtraTreesRegressor")
                candidate_models.append("Ridge")
                if HAS_XGBOOST:
                    candidate_models.append("XGBRegressor")
                elif HAS_LIGHTGBM:
                    candidate_models.append("LGBMRegressor")
                elif HAS_CATBOOST:
                    candidate_models.append("CatBoostRegressor")
                else:
                    candidate_models.append("GradientBoostingRegressor")

            # Tier 3 (Budget >= 8)
            if budget >= 8:
                if row_count < 5000:
                    candidate_models.append("SVR")
                candidate_models.append("MLPRegressor")
                candidate_models.append("AdaBoostRegressor")
                candidate_models.append("DecisionTreeRegressor")

            # Tier 4 (Fit-based Data Conditions)
            if len(candidate_models) < budget:
                candidate_models.append("KNeighborsRegressor")
                if row_count < 1000:
                    candidate_models.append("GaussianProcessRegressor")

        else:
            # Classification
            # Tier 1 (Always included - Tree, Linear, Boosting)
            candidate_models.extend(["RandomForestClassifier", "LogisticRegression", "HistGradientBoostingClassifier"])

            # Tier 2 (Budget >= 5)
            if budget >= 5:
                candidate_models.append("ExtraTreesClassifier")
                candidate_models.append("RidgeClassifier")
                if HAS_XGBOOST:
                    candidate_models.append("XGBClassifier")
                elif HAS_LIGHTGBM:
                    candidate_models.append("LGBMClassifier")
                elif HAS_CATBOOST:
                    candidate_models.append("CatBoostClassifier")
                else:
                    candidate_models.append("GradientBoostingClassifier")

            # Tier 3 (Budget >= 8)
            if budget >= 8:
                if row_count < 5000:
                    candidate_models.append("SVC")
                candidate_models.append("MLPClassifier")
                candidate_models.append("AdaBoostClassifier")
                candidate_models.append("DecisionTreeClassifier")

            # Tier 4 (Fit-based Data Conditions)
            if len(candidate_models) < budget:
                candidate_models.append("KNeighborsClassifier")
                candidate_models.append("GaussianNB")
                candidate_models.append("LinearDiscriminantAnalysis")

        # Select budget number of distinct models
        selected_models = candidate_models[:budget]

        imputations = ["median", "mean", "median", "mean", "constant"]
        encodings = ["onehot", "ordinal", "frequency", "onehot", "ordinal"]
        scalings = ["standard", "robust", "minmax", "standard", "robust"]

        experiments = []
        for idx, model_name in enumerate(selected_models):
            imp = imputations[idx % len(imputations)]
            enc = encodings[idx % len(encodings)]
            scale = scalings[idx % len(scalings)]

            # MLP and Distance models mandate scaling
            if "mlp" in model_name.lower() or "svc" in model_name.lower() or "svr" in model_name.lower() or "knn" in model_name.lower():
                scale = "standard"

            experiments.append({
                "experiment_id": f"EXP_{idx + 1:03d}",
                "operations": [
                    {"type": "imputation", "method": imp},
                    {"type": "encoding", "method": enc},
                    {"type": "scaling", "method": scale},
                ],
                "model_name": model_name,
            })

        return {
            "mission": f"Optimization for {obj_text}",
            "experiment_budget": budget,
            "experiments": experiments,
        }
