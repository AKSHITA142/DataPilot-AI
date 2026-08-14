from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline


class CrossValidationRunner:
    """Executes cross-validation over dataset features and target."""

    def __init__(self, n_splits: int = 5, random_state: int = 42):
        self.n_splits = n_splits
        self.random_state = random_state

    def run_cv(
        self,
        pipeline: Pipeline,
        X: pd.DataFrame,
        y: pd.Series,
        task_type: str = "classification",
    ) -> Tuple[List[float], Any]:
        """Runs K-Fold cross-validation and returns fold scores and the pipeline.

        IMPORTANT: Labels in y must already be encoded as integers [0..K-1]
        by the caller (executor). This method does NOT re-encode labels.
        """
        n_samples = len(X)
        if n_samples < 2:
            pipeline.fit(X, y)
            score = float(pipeline.score(X, y))
            return [score], pipeline

        # Adapt n_splits dynamically based on sample size
        effective_splits = min(self.n_splits, n_samples)

        if task_type == "classification" and len(np.unique(y)) > 1:
            class_counts = pd.Series(y).value_counts()
            min_class_count = class_counts.min()
            if min_class_count < 2 or len(class_counts) > n_samples * 0.5:
                # Fall back to standard KFold if any class has 1 sample or target is near-continuous
                cv = KFold(n_splits=max(2, effective_splits), shuffle=True, random_state=self.random_state)
            else:
                effective_splits = max(2, min(effective_splits, int(min_class_count)))
                cv = StratifiedKFold(n_splits=effective_splits, shuffle=True, random_state=self.random_state)
        else:
            effective_splits = max(2, effective_splits)
            cv = KFold(n_splits=effective_splits, shuffle=True, random_state=self.random_state)

        scores: List[float] = []

        for train_idx, val_idx in cv.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            if task_type == "classification":
                from sklearn.preprocessing import LabelEncoder
                fold_le = LabelEncoder()
                y_train = pd.Series(fold_le.fit_transform(y_train), index=y_train.index)
                known_classes = set(fold_le.classes_)
                y_val = pd.Series(y_val.map(lambda c: fold_le.transform([c])[0] if c in known_classes else 0), index=y_val.index)

            pipeline.fit(X_train, y_train)
            score = pipeline.score(X_val, y_val)
            scores.append(float(score))

        return scores, pipeline


