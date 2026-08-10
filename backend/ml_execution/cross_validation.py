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
        if task_type == "classification" and len(np.unique(y)) > 1:
            cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        else:
            cv = KFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        scores: List[float] = []

        for train_idx, val_idx in cv.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            pipeline.fit(X_train, y_train)
            score = pipeline.score(X_val, y_val)
            scores.append(float(score))

        # Final fit on full dataset
        pipeline.fit(X, y)
        return scores, pipeline
