from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Union, Dict, Any, Tuple
import logging

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline


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

    @staticmethod
    def _extract_meta_and_features(df: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Separates non-predictive identifier/metadata columns (id, name, uuid, *_id)
        from ML feature columns X to prevent target memorization and preserve ID columns in export.
        """
        meta_cols = []
        n_rows = len(df)
        for col in df.columns:
            if col == target_column:
                continue
            col_lower = col.lower().strip()
            if col_lower in ("id", "name", "uuid", "row_id", "user_id", "customer_id", "index"):
                meta_cols.append(col)
            elif col_lower.endswith("_id") or col_lower.startswith("id_"):
                meta_cols.append(col)
            elif df[col].dtype == object and df[col].nunique() == n_rows and n_rows > 5:
                meta_cols.append(col)

        meta_df = df[meta_cols].copy()
        feature_cols = [c for c in df.columns if c not in meta_cols and c != target_column]
        features_df = df[feature_cols].copy()
        return meta_df, features_df

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

        logger.info(f"[ML EXECUTION: {spec.experiment_id}] Target Column: '{target_column}' | Task: {task_type} | Algorithm: {spec.model}")
        df_copy = df.copy()

        try:
            # 1. Validation
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 1/7: Validating experiment spec parameters...")
            self.validator.validate_spec(spec, df_copy, target_column, mission_brief)

            # Separate metadata (id, name), features X, and target y
            meta_df, X = self._extract_meta_and_features(df_copy, target_column)
            y = df_copy[target_column]
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 2/7: Isolated {len(meta_df.columns)} meta/ID columns {list(meta_df.columns)}. Remaining features X: {len(X.columns)} columns.")

            # For classification, clean NaNs in y and encode string targets
            if task_type == "classification":
                from sklearn.preprocessing import LabelEncoder
                valid_mask = y.notna()
                meta_df = meta_df[valid_mask]
                X = X[valid_mask]
                y = y[valid_mask]

                if y.dtype == object or isinstance(y.iloc[0], str) or str(y.dtype) in ("category", "string"):
                    le = LabelEncoder()
                    y = pd.Series(le.fit_transform(y.astype(str)), index=y.index)
                    logger.info(f"[ML EXECUTION: {spec.experiment_id}] Label-encoded string target classes: {list(le.classes_)}")

            # 2. Build Pipeline
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 3/7: Building scikit-learn pipeline for model '{spec.model}'...")
            pipeline = self.pipeline_builder.build_pipeline(
                spec=spec,
                task_type=task_type,
                random_state=self.random_state,
            )
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Pipeline steps built: {list(pipeline.named_steps.keys())}")

            # 3. Cross-Validation & Fit
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 4/7: Executing adaptive cross-validation ({self.n_splits} folds)...")
            cv_scores, fitted_pipeline = self.cv_runner.run_cv(
                pipeline=pipeline,
                X=X,
                y=y,
                task_type=task_type,
            )
            mean_cv = float(np.mean(cv_scores)) if cv_scores else 0.0
            std_cv = float(np.std(cv_scores)) if cv_scores else 0.0
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 4/7: CV Completed. Fold Scores: {[round(s, 4) for s in cv_scores]} | Mean: {mean_cv:.4f} (+/- {std_cv:.4f})")

            # 4. Predict for metric calculation
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 5/7: Generating predictions for full metric calculation...")
            y_pred = fitted_pipeline.predict(X)
            y_proba = None
            if task_type == "classification" and hasattr(fitted_pipeline, "predict_proba"):
                try:
                    y_proba = fitted_pipeline.predict_proba(X)
                except Exception as pe:
                    logger.debug(f"predict_proba skipped: {pe}")

            # 5. Compute Metrics
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 6/7: Computing performance metrics via MetricEngine...")
            metrics_result = MetricEngine.compute_metrics(
                y_true=y,
                y_pred=y_pred,
                y_proba=y_proba,
                task_type=task_type,
                cv_scores=cv_scores,
            )
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 6/7: Computed metrics: {metrics_result.metrics}")

            # 6. Extract Feature Importances if available
            feature_importance: Optional[Dict[str, float]] = None
            try:
                model_step = fitted_pipeline.named_steps.get("model")
                if hasattr(model_step, "feature_importances_"):
                    importances = model_step.feature_importances_
                    feature_importance = {f"feature_{i}": float(val) for i, val in enumerate(importances)}
                elif hasattr(model_step, "coef_"):
                    coefs = np.abs(model_step.coef_).flatten()
                    feature_importance = {f"feature_{i}": float(val) for i, val in enumerate(coefs)}
            except Exception:
                pass

            # 7. Generate and save preprocessed dataset CSV artifact
            logger.info(f"[ML EXECUTION: {spec.experiment_id}] Step 7/7: Exporting preprocessed cleaned CSV artifact...")
            processed_csv_path: Optional[str] = None
            try:
                import os
                if len(fitted_pipeline.steps) > 1:
                    preproc_pipe = Pipeline(fitted_pipeline.steps[:-1])
                    X_trans = preproc_pipe.transform(X)
                    if isinstance(X_trans, pd.DataFrame):
                        clean_features_df = X_trans.copy()
                    else:
                        if hasattr(X_trans, "toarray"):
                            X_trans = X_trans.toarray()
                        clean_features_df = pd.DataFrame(X_trans, index=X.index)
                else:
                    clean_features_df = X.copy()

                # Re-attach metadata columns (id, name, etc.) and target column
                clean_df = pd.concat([meta_df.reset_index(drop=True), clean_features_df.reset_index(drop=True)], axis=1)
                clean_df[target_column] = y.values

                os.makedirs("storage/artifacts", exist_ok=True)
                processed_csv_path = f"storage/artifacts/{spec.experiment_id}_cleaned.csv"
                clean_df.to_csv(processed_csv_path, index=False)
                logger.info(f"[ML EXECUTION: {spec.experiment_id}] Saved preprocessed dataset ({len(clean_df)} rows, {len(clean_df.columns)} cols) to {processed_csv_path}")
            except Exception as pe:
                logger.warning(f"Could not export preprocessed dataset CSV: {pe}")

            artifacts = Artifacts(
                processed_dataset_path=processed_csv_path,
                feature_importance=feature_importance,
            )
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
