from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Union, Dict, Any
import logging
import pandas as pd
import numpy as np

from backend.schemas.experiment import (
    ExperimentPlan,
    ExperimentSpec,
    ExperimentResult,
    PipelineDefinition,
    Artifacts,
)
from backend.schemas.mission_brief import MissionBrief
from backend.ml_execution.validator import ExperimentValidator
from backend.ml_execution.pipeline_builder import PipelineBuilder
from backend.ml_execution.cross_validation import CrossValidationRunner
from backend.ml_execution.metrics import MetricEngine
from backend.ml_execution.logger import ExperimentLogger

logger = logging.getLogger("datapilot.ml_execution.executor")


class MLExecutionEngine:
    """Deterministic ML Execution Engine that executes experiment batches starting from original data."""

    def __init__(self, max_workers: int = 4, n_splits: int = 5, random_state: int = 42):
        self.max_workers = max_workers
        self.n_splits = n_splits
        self.random_state = random_state
        self.validator = ExperimentValidator()
        self.pipeline_builder = PipelineBuilder()
        self.cv_runner = CrossValidationRunner(n_splits=self.n_splits, random_state=self.random_state)

    def execute_single_experiment(
        self,
        spec: ExperimentSpec,
        df: pd.DataFrame,
        target_column: str,
        task_type: str = "classification",
        mission_brief: Optional[MissionBrief] = None,
    ) -> ExperimentResult:
        """Executes a single experiment spec starting from the original, unmodified dataset."""
        logger_inst = ExperimentLogger(spec.experiment_id)
        logger_inst.start()

        # Create fresh copy of original dataset for complete isolation
        df_copy = df.copy()

        try:
            # 1. Validation
            self.validator.validate_spec(spec, df_copy, target_column, mission_brief)

            # Separate features X and target y
            X = df_copy.drop(columns=[target_column])
            y = df_copy[target_column]

            # For classification, clean NaNs in y and encode string targets
            if task_type == "classification":
                from sklearn.preprocessing import LabelEncoder
                valid_mask = y.notna()
                X = X[valid_mask]
                y = y[valid_mask]

                if y.dtype == object or isinstance(y.iloc[0], str) or str(y.dtype) in ("category", "string"):
                    le = LabelEncoder()
                    y = pd.Series(le.fit_transform(y.astype(str)), index=y.index)

            # 2. Build Pipeline
            pipeline = self.pipeline_builder.build_pipeline(
                spec=spec,
                task_type=task_type,
                random_state=self.random_state,
            )

            # 3. Cross-Validation & Fit
            cv_scores, fitted_pipeline = self.cv_runner.run_cv(
                pipeline=pipeline,
                X=X,
                y=y,
                task_type=task_type,
            )

            # 4. Predict for metric calculation
            y_pred = fitted_pipeline.predict(X)
            y_proba = None
            if task_type == "classification" and hasattr(fitted_pipeline, "predict_proba"):
                try:
                    y_proba = fitted_pipeline.predict_proba(X)
                except Exception:
                    pass

            # 5. Compute Metrics
            metrics_result = MetricEngine.compute_metrics(
                y_true=y,
                y_pred=y_pred,
                y_proba=y_proba,
                task_type=task_type,
                cv_scores=cv_scores,
            )

            # 6. Extract Feature Importances if available
            feature_importance: Optional[Dict[str, float]] = None
            try:
                model_step = fitted_pipeline.named_steps.get("model")
                if hasattr(model_step, "feature_importances_"):
                    # Use feature names from previous steps if available
                    importances = model_step.feature_importances_
                    feature_importance = {f"feature_{i}": float(val) for i, val in enumerate(importances)}
                elif hasattr(model_step, "coef_"):
                    coefs = np.abs(model_step.coef_).flatten()
                    feature_importance = {f"feature_{i}": float(val) for i, val in enumerate(coefs)}
            except Exception:
                pass

            artifacts = Artifacts(feature_importance=feature_importance)
            runtime = logger_inst.finish(status="completed", metrics=metrics_result.metrics)

            pipeline_def = PipelineDefinition(
                operations=spec.operations,
                model_name=spec.model_name,
            )

            return ExperimentResult(
                experiment_id=spec.experiment_id,
                pipeline=pipeline_def,
                model=spec.model_name,
                metrics=metrics_result,
                runtime=runtime,
                status="completed",
                artifacts=artifacts,
            )

        except Exception as e:
            runtime = logger_inst.finish(status="failed")
            logger_inst.log_error(e)

            pipeline_def = PipelineDefinition(
                operations=spec.operations,
                model_name=spec.model_name,
            )

            return ExperimentResult(
                experiment_id=spec.experiment_id,
                pipeline=pipeline_def,
                model=spec.model_name,
                metrics=MetricEngine.compute_metrics([], [], task_type=task_type),
                runtime=runtime,
                status="failed",
                error_message=str(e),
            )

    def execute_plan(
        self,
        plan: ExperimentPlan,
        dataset: Union[pd.DataFrame, str],
        target_column: str,
        task_type: str = "classification",
        mission_brief: Optional[MissionBrief] = None,
    ) -> List[ExperimentResult]:
        """Executes a batch ExperimentPlan in parallel starting from the original dataset."""
        # Load dataset if CSV file path provided
        if isinstance(dataset, str):
            df = pd.read_csv(dataset)
        else:
            df = dataset.copy()

        # Validate entire plan
        self.validator.validate_plan(plan, df, target_column, mission_brief)

        results: List[ExperimentResult] = []

        # Run experiments in parallel
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(plan.experiments))) as executor:
            future_to_spec = {
                executor.submit(
                    self.execute_single_experiment,
                    spec,
                    df,
                    target_column,
                    task_type,
                    mission_brief,
                ): spec
                for spec in plan.experiments
            }

            for future in as_completed(future_to_spec):
                spec = future_to_spec[future]
                try:
                    res = future.result()
                    results.append(res)
                except Exception as exc:
                    logger.error(f"Experiment {spec.experiment_id} generated an exception: {exc}")
                    pipeline_def = PipelineDefinition(operations=spec.operations, model_name=spec.model_name)
                    results.append(
                        ExperimentResult(
                            experiment_id=spec.experiment_id,
                            pipeline=pipeline_def,
                            model=spec.model_name,
                            metrics=MetricEngine.compute_metrics([], [], task_type=task_type),
                            runtime=0.0,
                            status="failed",
                            error_message=str(exc),
                        )
                    )

        # Sort results by experiment priority / ID
        results.sort(key=lambda r: r.experiment_id)
        return results
