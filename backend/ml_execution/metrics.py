from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    balanced_accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    explained_variance_score,
)

from backend.schemas.experiment import MetricsResult


class MetricEngine:
    """Computes comprehensive evaluation metrics for classification and regression tasks."""

    @classmethod
    def compute_metrics(
        self,
        y_true: Any,
        y_pred: Any,
        y_proba: Any = None,
        task_type: str = "classification",
        cv_scores: list = None,
    ) -> MetricsResult:
        """Calculates evaluation metrics dictionary and wraps in MetricsResult."""
        cv_scores = cv_scores or []
        metrics: Dict[str, float] = {}

        if task_type == "classification":
            acc = float(accuracy_score(y_true, y_pred))
            prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
            rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
            f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
            bal_acc = float(balanced_accuracy_score(y_true, y_pred))

            metrics["accuracy"] = round(acc, 4)
            metrics["precision"] = round(prec, 4)
            metrics["recall"] = round(rec, 4)
            metrics["f1"] = round(f1, 4)
            metrics["f1_score"] = round(f1, 4)
            metrics["balanced_accuracy"] = round(bal_acc, 4)

            # ROC-AUC if proba available or binary
            if y_proba is not None:
                try:
                    if len(np.unique(y_true)) == 2:
                        auc = float(roc_auc_score(y_true, y_proba[:, 1]))
                    else:
                        auc = float(roc_auc_score(y_true, y_proba, multi_class="ovr", average="weighted"))
                    metrics["roc_auc"] = round(auc, 4)
                except Exception:
                    pass

            primary = metrics.get("f1", acc)

        else:
            mae = float(mean_absolute_error(y_true, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
            r2 = float(r2_score(y_true, y_pred))
            evs = float(explained_variance_score(y_true, y_pred))

            metrics["mae"] = round(mae, 4)
            metrics["rmse"] = round(rmse, 4)
            metrics["r2"] = round(r2, 4)
            metrics["explained_variance"] = round(evs, 4)

            primary = metrics.get("r2", -mae)

        return MetricsResult(
            primary_metric=round(primary, 4),
            metrics=metrics,
            cv_scores=[round(s, 4) for s in cv_scores],
        )
