from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief
from backend.schemas.experiment import ExperimentPlan, ExperimentSpec, ExperimentOperation
from backend.agents.base import BaseAgent


try:
    import xgboost  # type: ignore # noqa: F401
    HAS_XGBOOST = True
except (ImportError, Exception):
    HAS_XGBOOST = False

try:
    import lightgbm  # type: ignore # noqa: F401
    HAS_LIGHTGBM = True
except (ImportError, Exception):
    HAS_LIGHTGBM = False

try:
    import catboost  # type: ignore # noqa: F401
    HAS_CATBOOST = True
except (ImportError, Exception):
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
        mission: Any = inputs.get("mission_brief")
        budget: int = inputs.get("experiment_budget", 3)
        task_type: str = inputs.get("task_type", "classification")

        objective = getattr(mission, "objective", "Tabular Optimization") if mission else "Tabular Optimization"

        if task_type == "regression":
            allowed_models = (
                "RandomForestRegressor, LinearRegression, Ridge, HistGradientBoostingRegressor, "
                "XGBRegressor, LGBMRegressor, CatBoostRegressor, SVR, ExtraTreesRegressor, KNeighborsRegressor"
            )
            strict_instruction = (
                "CRITICAL REQUIREMENT: The user's problem type is strictly REGRESSION. "
                "You MUST ONLY select regression models (ending in Regressor, or LinearRegression/Ridge/SVR). "
                "Do NOT include classification models (like RandomForestClassifier, LogisticRegression, or SVC)."
            )
        else:
            allowed_models = (
                "RandomForestClassifier, LogisticRegression, RidgeClassifier, HistGradientBoostingClassifier, "
                "XGBClassifier, LGBMClassifier, CatBoostClassifier, SVC, ExtraTreesClassifier, KNeighborsClassifier"
            )
            strict_instruction = (
                "CRITICAL REQUIREMENT: The user's problem type is strictly CLASSIFICATION. "
                "You MUST ONLY select classification models (ending in Classifier, or LogisticRegression/RidgeClassifier/SVC). "
                "Do NOT include regression models (like LinearRegression, SVR, or RandomForestRegressor)."
            )

        return (
            f"Generate a batch of {budget} diverse ML experiment specifications.\n"
            f"Mission Objective: {objective}\n"
            f"Task Type: {task_type.upper()}\n"
            f"{strict_instruction}\n"
            f"Allowed Models: {allowed_models}\n"
            f"Select transformers from: imputation (median/mean/constant), encoding (onehot/ordinal/frequency), scaling (standard/robust/minmax)."
        )

    def get_fallback_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        mission: Any = inputs.get("mission_brief")
        obj_text = getattr(mission, "objective", "Tabular Optimization") if mission else "Tabular Optimization"
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

        col_profiles = prof_dict.get("column_profiles", [])
        col_encodings = {}
        col_scalings = {}
        for cp in col_profiles:
            name = cp.get("name") if isinstance(cp, dict) else getattr(cp, "name", None)
            enc_rec = cp.get("encoding_recommendation") if isinstance(cp, dict) else getattr(cp, "encoding_recommendation", None)
            scale_rec = cp.get("scaling_recommendation") if isinstance(cp, dict) else getattr(cp, "scaling_recommendation", None)
            if name and enc_rec:
                col_encodings[name] = enc_rec
            if name and scale_rec:
                col_scalings[name] = scale_rec

        # Remove target column from preprocessing configs — target must never be in X's pipeline
        target_col = target_info.get("target_column")
        if target_col:
            col_encodings.pop(target_col, None)
            col_scalings.pop(target_col, None)

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
                    {"type": "encoding", "method": enc, "params": {"column_encodings": col_encodings}},
                    {"type": "scaling", "method": scale, "params": {"column_scalings": col_scalings}},
                ],
                "model_name": model_name,
            })

        return {
            "mission": f"Optimization for {obj_text}",
            "experiment_budget": budget,
            "experiments": experiments,
        }

    def run(self, inputs: Dict[str, Any]) -> ExperimentPlan:
        plan: ExperimentPlan = super().run(inputs)
        task_type = inputs.get("task_type", "classification")

        MODEL_REG_MAP = {
            "RandomForestClassifier": "RandomForestRegressor",
            "LogisticRegression": "LinearRegression",
            "RidgeClassifier": "Ridge",
            "HistGradientBoostingClassifier": "HistGradientBoostingRegressor",
            "GradientBoostingClassifier": "GradientBoostingRegressor",
            "XGBClassifier": "XGBRegressor",
            "LGBMClassifier": "LGBMRegressor",
            "CatBoostClassifier": "CatBoostRegressor",
            "SVC": "SVR",
            "ExtraTreesClassifier": "ExtraTreesRegressor",
            "KNeighborsClassifier": "KNeighborsRegressor",
            "MLPClassifier": "MLPRegressor",
            "AdaBoostClassifier": "AdaBoostRegressor",
            "DecisionTreeClassifier": "DecisionTreeRegressor",
            "GaussianNB": "LinearRegression",
            "LinearDiscriminantAnalysis": "Ridge",
        }

        MODEL_CLF_MAP = {
            "RandomForestRegressor": "RandomForestClassifier",
            "LinearRegression": "LogisticRegression",
            "Ridge": "RidgeClassifier",
            "HistGradientBoostingRegressor": "HistGradientBoostingClassifier",
            "GradientBoostingRegressor": "GradientBoostingClassifier",
            "XGBRegressor": "XGBClassifier",
            "LGBMRegressor": "LGBMClassifier",
            "CatBoostRegressor": "CatBoostClassifier",
            "SVR": "SVC",
            "ExtraTreesRegressor": "ExtraTreesClassifier",
            "KNeighborsRegressor": "KNeighborsClassifier",
            "MLPRegressor": "MLPClassifier",
            "AdaBoostRegressor": "AdaBoostClassifier",
            "DecisionTreeRegressor": "DecisionTreeClassifier",
            "GaussianProcessRegressor": "RandomForestClassifier",
        }

        # Fallback check: ensure experiments is never empty
        if not plan.experiments:
            fallback_dict = self.get_fallback_data(inputs)
            plan = ExperimentPlan.model_validate(fallback_dict)

        # Filter out any redundant 'model' or 'estimator' operations from operations array
        for exp in plan.experiments:
            exp.operations = [
                op for op in exp.operations 
                if op.type.lower().strip() not in ("model", "modeling", "estimator", "classification", "regression")
            ]

        # Strict post-processing: enforce 100% task_type compliance for every experiment spec
        for exp in plan.experiments:
            m_name = exp.model_name
            if task_type == "regression":
                if m_name in MODEL_REG_MAP:
                    exp.model_name = MODEL_REG_MAP[m_name]
                elif m_name.endswith("Classifier"):
                    exp.model_name = m_name[:-10] + "Regressor"
            else:
                if m_name in MODEL_CLF_MAP:
                    exp.model_name = MODEL_CLF_MAP[m_name]
                elif m_name.endswith("Regressor"):
                    exp.model_name = m_name[:-9] + "Classifier"

        return plan
