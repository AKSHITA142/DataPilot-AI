from typing import Tuple, Optional, Dict, Any, List


class DomainMetricResolver:
    """
    Senior Data Scientist Metric Resolver:
    Dynamically infers problem domain, Type I vs Type II risk costs, and target distribution
    directly from dataset column names, feature statistics, and target semantics — even if the user prompt is vague or missing.
    """

    # Category 1: Communication / Email Spam & Phishing Domain -> PRECISION
    SPAM_DOMAIN_KEYWORDS = {
        "spam", "email", "mail", "inbox", "phishing", "junk", "ham",
        "sender", "subject", "url_count", "has_url", "uppercase_ratio",
        "exclamation_count", "question_count", "body", "email_id", "email_text",
        "email_hour", "has_attachment", "moderation", "ban", "accusation",
        "type1", "false_positive", "precision", "f0.5"
    }

    # Category 2: Medical & Healthcare Diagnosis Domain -> RECALL
    MEDICAL_DOMAIN_KEYWORDS = {
        "medical", "patient", "cancer", "disease", "diagnosis", "glucose",
        "blood", "insulin", "bmi", "biopsy", "radiology", "lesion", "cholesterol",
        "heart", "stroke", "symptom", "hospital", "clinical", "tumor", "icu",
        "survival", "survived", "survive", "mortality", "death", "illness",
        "virus", "infection", "cardiac", "pregnancies", "diabetes", "pedigree"
    }

    # Category 3: Financial Credit & Loan Underwriting Domain -> RECALL
    CREDIT_LOAN_KEYWORDS = {
        "loan", "credit", "default", "approval", "underwriting", "borrower",
        "applicant", "installment", "interest_rate", "debt", "dti", "grade",
        "sub_grade", "revol_bal", "revol_util", "bank", "risk_approval"
    }

    # Category 4: Fraud & Security Domain -> RECALL / F2
    FRAUD_KEYWORDS = {
        "fraud", "is_fraud", "transaction", "chargeback", "unauthorized",
        "suspicious", "card_number", "device_id", "ip_address"
    }

    # Category 5: Customer Churn & Retention Domain -> RECALL
    CHURN_KEYWORDS = {
        "churn", "attrition", "cancellation", "tenure", "monthly_charges",
        "total_charges", "contract", "paperless_billing"
    }

    # Outlier-sensitive regression domains (financial, real estate, pricing) -> MAE
    OUTLIER_REGRESSION_KEYWORDS = {
        "price", "cost", "salary", "income", "valuation", "house", "home",
        "real_estate", "property", "revenue", "fare", "amount", "mae"
    }

    @classmethod
    def resolve_primary_metric(
        cls,
        task_type: str,
        user_goal: str = "",
        target_column: str = "",
        domain: str = "",
        column_names: Optional[List[str]] = None,
        is_imbalanced: bool = False,
        has_proba: bool = True,
    ) -> Tuple[str, str, str]:
        """
        Returns (metric_key, metric_display_name, rationale_explanation).
        Inspects 100% of column names, target column, and domain tokens.
        """
        cols_list = [c.lower().strip() for c in (column_names or [])]
        cols_text = " ".join(cols_list)
        text = f"{user_goal} {target_column} {domain} {cols_text}".lower()

        # ---------------- REGRESSION TASKS ----------------
        if task_type == "regression":
            if any(kw in text for kw in cls.OUTLIER_REGRESSION_KEYWORDS):
                return (
                    "mae",
                    "MAE",
                    "Outlier-sensitive financial/pricing domain detected from column features. Mean Absolute Error (MAE) evaluates average dollar prediction error robustly against extreme outliers."
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
        # Priority 1: Email / Spam & Phishing Domain -> Precision (High Type I Error Risk)
        # Check if email/spam features exist in columns or user goal
        spam_matches = [kw for kw in cls.SPAM_DOMAIN_KEYWORDS if kw in text or any(kw in c for c in cols_list)]
        if spam_matches and not any(kw in text for kw in cls.MEDICAL_DOMAIN_KEYWORDS):
            return (
                "precision",
                "Precision",
                f"Email Spam & Communication Domain detected from dataset features ({', '.join(spam_matches[:3])}). High Type I Error Risk (False Positives): Incorrectly moving legitimate emails to spam causes severe user harm. Precision is selected as the primary metric."
            )

        # Priority 2: Medical & Healthcare Diagnosis Domain -> Recall (High Type II Error Risk)
        med_matches = [kw for kw in cls.MEDICAL_DOMAIN_KEYWORDS if kw in text or any(kw in c for c in cols_list)]
        if med_matches:
            return (
                "recall",
                "Recall",
                f"Healthcare & Medical Diagnosis Domain detected from dataset features ({', '.join(med_matches[:3])}). High Type II Error Risk (False Negatives): Missing a medical condition or disease carries a critical health penalty. Recall is selected as the primary metric."
            )

        # Priority 3: Credit / Loan Underwriting Domain -> Recall
        credit_matches = [kw for kw in cls.CREDIT_LOAN_KEYWORDS if kw in text or any(kw in c for c in cols_list)]
        if credit_matches:
            return (
                "recall",
                "Recall",
                f"Financial Credit & Loan Underwriting Domain detected from dataset features ({', '.join(credit_matches[:3])}). High Type II Error Risk (False Negatives): Approving a defaulting borrower carries a severe financial loss. Recall is selected to minimize missed defaults."
            )

        # Priority 4: Fraud & Cyber-Security Domain -> Recall
        fraud_matches = [kw for kw in cls.FRAUD_KEYWORDS if kw in text or any(kw in c for c in cols_list)]
        if fraud_matches:
            return (
                "recall",
                "Recall",
                f"Fraud & Security Domain detected from dataset features ({', '.join(fraud_matches[:3])}). High Type II Error Risk (False Negatives): Missing a fraudulent transaction results in direct financial liability. Recall is selected to maximize fraud detection."
            )

        # Priority 5: Customer Churn Domain -> Recall
        churn_matches = [kw for kw in cls.CHURN_KEYWORDS if kw in text or any(kw in c for c in cols_list)]
        if churn_matches:
            return (
                "recall",
                "Recall",
                f"Customer Churn & Retention Domain detected from dataset features ({', '.join(churn_matches[:3])}). High Type II Error Risk (False Negatives): Missing an at-risk customer leads to revenue loss. Recall is selected to capture all potential churners."
            )

        # Priority 6: Imbalanced Class Distribution (<20% minority class) with generic feature names
        if is_imbalanced:
            if has_proba:
                return (
                    "roc_auc",
                    "ROC-AUC",
                    "Imbalanced class distribution detected (<20% minority) on generic features. ROC-AUC is selected to evaluate discriminative ranking capability across all decision thresholds without majority-class bias."
                )
            return (
                "balanced_accuracy",
                "Balanced Accuracy",
                "Imbalanced class distribution detected on generic features. Balanced Accuracy evaluates mean recall across all classes."
            )

        # Priority 7: Standard Balanced Classification Default -> F1-Score
        return (
            "f1_score",
            "F1-Score",
            "Harmonic mean of Precision and Recall for balanced multi-class classification performance."
        )
