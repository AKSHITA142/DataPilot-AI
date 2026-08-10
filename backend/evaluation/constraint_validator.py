from typing import Dict, List, Optional
from backend.schemas.experiment import ExperimentResult
from backend.schemas.mission_brief import MissionBrief


class ConstraintValidator:
    """Validates experiments against MissionBrief runtime and model constraints."""

    INTERPRETABLE_MODELS = {
        "logisticregression",
        "linearregression",
        "ridge",
        "lasso",
        "elasticnet",
        "decisiontreeclassifier",
        "decisiontreeregressor",
        "gaussiannb",
    }

    @classmethod
    def validate_constraints(
        cls,
        result: ExperimentResult,
        mission_brief: Optional[MissionBrief] = None,
    ) -> bool:
        """Returns True if experiment complies with all business and mission constraints."""
        if result.status != "completed":
            return False

        if not mission_brief or not mission_brief.constraints:
            return True

        constraints = mission_brief.constraints

        # 1. Training Time Limit Constraint (convert minutes to seconds)
        if constraints.training_time_limit_minutes and result.runtime:
            max_sec = constraints.training_time_limit_minutes * 60.0
            if result.runtime > max_sec:
                return False

        # 2. Interpretability Constraint (check custom_constraints if specified)
        if constraints.custom_constraints and constraints.custom_constraints.get("prefer_interpretable_models"):
            model_name_clean = result.model.lower().replace(" ", "").replace("_", "")
            if model_name_clean not in cls.INTERPRETABLE_MODELS:
                return False

        # 3. Forbidden Operations Constraint
        if constraints.forbidden_operations and result.pipeline:
            forbidden = set(constraints.forbidden_operations)
            for op in result.pipeline.operations:
                if op.method in forbidden or op.type in forbidden:
                    return False

        return True

    @classmethod
    def validate_batch(
        cls,
        results: List[ExperimentResult],
        mission_brief: Optional[MissionBrief] = None,
    ) -> Dict[str, bool]:
        """Returns dictionary mapping experiment_id -> compliance bool."""
        return {r.experiment_id: cls.validate_constraints(r, mission_brief) for r in results}
