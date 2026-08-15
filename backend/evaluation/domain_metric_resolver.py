from typing import Tuple, Optional, Dict, Any


class DomainMetricResolver:
    """
    Senior Data Scientist Metric Resolver:
    Dynamically determines the optimal evaluation metric based on problem domain,
    Type I (False Positive) vs Type II (False Negative) risk costs, class imbalance, and target statistics.
    """

    # Type II Error Penalty: False Negatives carry high cost (Missing a risk/default/disease)
    HIGH_TYPE2_KEYWORDS = {
        "loan", "credit", "default", "approval", "underwriting", "borrower",
        "fraud", "medical", "disease", "patient", "cancer", "diagnosis", "outcome",
        "health", "healthcare", "hospital", "clinical", "tumor", "blood", "heart",
        "stroke", "diabetes", "glucose", "insulin", "bmi", "biopsy", "radiology",
        "lesion", "icu", "survival", "survived", "survive", "mortality", "death",
        "illness", "symptom", "virus", "infection", "cardiac", "churn", "attrition",
        "hazard", "danger", "safety", "alert", "recall", "type2", "false_negative", "f2"
    }

    # Type I Error Penalty: False Positives carry high cost (False Alarm / Wrong Accusation)
    HIGH_TYPE1_KEYWORDS = {
        "spam", "moderation", "ban", "penalty", "accusation",
        "precision", "type1", "false_positive", "f0.5"
    }

    # Outlier-sensitive regression domains (financial, real estate, pricing)
    OUTLIER_REGRESSION_KEYWORDS = {
        "price", "cost", "salary", "income", "valuation", "house", "home",
        "real_estate", "property", "mae"
    }

    @classmethod
    def resolve_primary_metric(
        cls,
        task_type: str,
        user_goal: str = "",
        target_column: str = "",
        domain: str = "",
        column_names: Optional[list] = None,
        is_imbalanced: bool = False,
        has_proba: bool = True,
    ) -> Tuple[str, str, str]:
        """
        Returns (metric_key, metric_display_name, rationale_explanation).
        """
        cols_text = " ".join(column_names) if column_names else ""
        text = f"{user_goal} {target_column} {domain} {cols_text}".lower()

        # ---------------- REGRESSION TASKS ----------------
        if task_type == "regression":
            if any(kw in text for kw in cls.OUTLIER_REGRESSION_KEYWORDS):
                return (
                    "mae",
                    "MAE",
                    "Outlier-sensitive financial/pricing domain detected. Mean Absolute Error (MAE) evaluates average prediction error robustly against extreme outliers."
                )
            if "r2" in text or "variance" in text:
                return (
                    "r2",
                    "R² Score",
                    "Explained variance (R²) selected to evaluate goodness of fit and proportion of variance explained by the model."
                )
            return (
                "rmse",
                "RMSE",
                "Root Mean Squared Error (RMSE) measures prediction error variance on continuous numeric targets."
            )

        # ---------------- CLASSIFICATION TASKS ----------------
        # 1. Type II Risk (False Negatives: Loan Default, Medical, Fraud, Churn)
        if any(kw in text for kw in cls.HIGH_TYPE2_KEYWORDS):
            return (
                "recall",
                "Recall",
                "High Type II Error Risk (False Negatives): In loan underwriting, risk assessment, and medical screening, approving a defaulting borrower or missing a critical risk carries a severe financial/safety penalty. Recall is selected as the primary metric to minimize missed risk cases."
            )

        # 2. Type I Risk (False Positives: Spam, Moderation, False Alarms)
        if any(kw in text for kw in cls.HIGH_TYPE1_KEYWORDS):
            return (
                "precision",
                "Precision",
                "High Type I Error Risk (False Positives): Incorrectly flagging legitimate items causes severe user friction. Precision is selected as the primary metric to ensure high confidence in positive alerts."
            )

        # 3. Imbalanced Class Distribution (<20% minority class)
        if is_imbalanced:
            if has_proba:
                return (
                    "roc_auc",
                    "ROC-AUC",
                    "Imbalanced class distribution detected (<20% minority). ROC-AUC is selected to evaluate discriminative ranking capability across all decision thresholds without majority-class bias."
                )
            return (
                "balanced_accuracy",
                "Balanced Accuracy",
                "Imbalanced class distribution detected. Balanced Accuracy evaluates mean recall across all classes."
            )

        # 4. Standard Balanced Classification Default -> F1-Score
        return (
            "f1_score",
            "F1-Score",
            "Harmonic mean of Precision and Recall for balanced multi-class classification performance."
        )
