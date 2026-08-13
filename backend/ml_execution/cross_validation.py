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
        """Runs K-Fold cross-validation and returns fold scores and fitted pipeline."""
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
                # Fall back to standard KFold if any class has 1 sample or target is continuous floats
                cv = KFold(n_splits=max(2, effective_splits), shuffle=True, random_state=self.random_state)
            else:
                effective_splits = max(2, min(effective_splits, int(min_class_count)))
                cv = StratifiedKFold(n_splits=effective_splits, shuffle=True, random_state=self.random_state)
        else:
            effective_splits = max(2, effective_splits)
            cv = KFold(n_splits=effective_splits, shuffle=True, random_state=self.random_state)

        scores: List[float] = []

        from sklearn.preprocessing import LabelEncoder

        for train_idx, val_idx in cv.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            if task_type == "classification":
                le_fold = LabelEncoder()
                y_train = pd.Series(le_fold.fit_transform(y_train), index=y_train.index)
                known_classes = set(le_fold.classes_)
                y_val_clean = y_val.map(lambda v: v if v in known_classes else le_fold.classes_[0])
                y_val = pd.Series(le_fold.transform(y_val_clean), index=y_val.index)

            pipeline.fit(X_train, y_train)
            score = pipeline.score(X_val, y_val)
            scores.append(float(score))

        # Final fit on full dataset
        if task_type == "classification":
            le_full = LabelEncoder()
            y = pd.Series(le_full.fit_transform(y), index=y.index)

        pipeline.fit(X, y)
        return scores, pipeline

