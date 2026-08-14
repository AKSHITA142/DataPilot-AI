from typing import Tuple, Optional, Dict, Any


class DomainMetricResolver:
    """
    Senior Data Scientist Metric Resolver:
    Dynamically determines the optimal evaluation metric based on problem domain,
    Type I (False Positive) vs Type II (False Negative) risk costs, and class imbalance.
    """

    HIGH_PRECISION_KEYWORDS = {
        "loan", "credit", "fraud", "default", "approval", "spam",
        "financial", "transaction", "bank", "risk_approval", "underwriting",
        "precision", "type1", "false_positive"
    }

    HIGH_RECALL_KEYWORDS = {
        "health", "healthcare", "medical", "disease", "patient", "cancer",
        "diagnosis", "air", "air_quality", "aqi", "pollution", "hazard",
        "danger", "churn", "attrition", "safety", "inspection", "alert", "warning",
        "recall", "type2", "false_negative"
    }

    @classmethod
    def resolve_primary_metric(
        cls,
        task_type: str,
        user_goal: str = "",
        domain: str = "",
        is_imbalanced: bool = False,
    ) -> Tuple[str, str, str]:
        """
        Returns (metric_key, metric_display_name, rationale_explanation).

        - High Type I Error Cost (False Positives) -> Precision
        - High Type II Error Cost (False Negatives) -> Recall
        - Imbalanced Dataset (<25% minority) -> F1-Score / Balanced Accuracy
        - General Classification -> F1-Score
        - Regression -> RMSE
        """
        if task_type == "regression":
            return "rmse", "RMSE", "Root Mean Squared Error measures prediction variance on continuous targets."

        text = f"{user_goal} {domain}".lower()

        # 1. Check High Type I Error Penalty (False Positives -> Precision)
        if any(kw in text for kw in cls.HIGH_PRECISION_KEYWORDS):
            return (
                "precision",
                "Precision",
                "High Type I error cost (False Positives). Precision optimizes against false approvals."
            )

        # 2. Check High Type II Error Penalty (False Negatives -> Recall)
        if any(kw in text for kw in cls.HIGH_RECALL_KEYWORDS):
            return (
                "recall",
                "Recall",
                "High Type II error cost (False Negatives). Recall optimizes against missed critical alerts."
            )

        # 3. Check Imbalanced Datasets (F1-Score / Balanced Accuracy)
        if is_imbalanced:
            return (
                "f1_score",
                "F1-Score",
                "Imbalanced class distribution detected. F1-Score balances Precision and Recall."
            )

        # 4. Standard Classification Default -> F1-Score
        return (
            "f1_score",
            "F1-Score",
            "Harmonic mean of Precision and Recall for balanced classification performance."
        )
