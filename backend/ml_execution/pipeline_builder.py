from typing import Any, Dict, List, Optional
import pandas as pd
from sklearn.pipeline import Pipeline

from backend.schemas.experiment import ExperimentOperation, ExperimentSpec
from backend.ml_execution.transformers import (
    ImputerTransformer,
    CategoricalEncoderTransformer,
    FeatureScalerTransformer,
)
from backend.ml_execution.feature_engineering import (
    LogTransformTransformer,
    InteractionFeaturesTransformer,
    PolynomialFeaturesTransformer,
    DatetimeDecompositionTransformer,
)
from backend.ml_execution.trainer import ModelTrainerFactory


class PipelineBuilder:
    """Constructs executable scikit-learn Pipelines in strict structural order."""

    STRUCTURAL_ORDER = [
        "datetime_decomposition",
        "imputation",
        "encoding",
        "scaling",
        "feature_engineering",
    ]

    def build_pipeline(
        self,
        spec: ExperimentSpec,
        task_type: str = "classification",
        random_state: int = 42,
    ) -> Pipeline:
        """Assembles a scikit-learn Pipeline from ExperimentSpec operations and model choice."""
        steps: List[tuple] = []

        # Always decompose datetime columns first if present
        steps.append(("datetime_decomp", DatetimeDecompositionTransformer()))

        # Categorize operations by structural type
        ops_by_type: Dict[str, ExperimentOperation] = {}
        for op in spec.operations:
            ops_by_type[op.type] = op

        # 1. Imputation step
        if "imputation" in ops_by_type:
            imp_op = ops_by_type["imputation"]
            steps.append(("imputer", ImputerTransformer(strategy=imp_op.method)))
        else:
            steps.append(("default_imputer", ImputerTransformer(strategy="median")))

        # 2. Categorical Encoding step
        if "encoding" in ops_by_type:
            enc_op = ops_by_type["encoding"]
            steps.append(("encoder", CategoricalEncoderTransformer(method=enc_op.method)))
        else:
            steps.append(("default_encoder", CategoricalEncoderTransformer(method="onehot")))

        # 3. Feature Scaling step
        if "scaling" in ops_by_type:
            scale_op = ops_by_type["scaling"]
            steps.append(("scaler", FeatureScalerTransformer(method=scale_op.method)))

        # 4. Feature Engineering step
        if "feature_engineering" in ops_by_type:
            fe_op = ops_by_type["feature_engineering"]
            if fe_op.method == "log":
                steps.append(("fe_log", LogTransformTransformer()))
            elif fe_op.method == "interaction":
                steps.append(("fe_interaction", InteractionFeaturesTransformer()))
            elif fe_op.method == "polynomial":
                steps.append(("fe_poly", PolynomialFeaturesTransformer()))

        # 5. Model Estimator step
        model_estimator = ModelTrainerFactory.get_estimator(
            model_name=spec.model_name,
            task_type=task_type,
            random_state=random_state,
        )
        steps.append(("model", model_estimator))

        return Pipeline(steps=steps)
