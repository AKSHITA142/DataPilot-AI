from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from backend.schemas.enums import TaskType, ColumnType


class TargetAnalyzer:
    """Analyzes target column to infer task type and class balance."""

    @classmethod
    def analyze_target(
        cls,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
        column_types: Optional[Dict[str, ColumnType]] = None
    ) -> Dict[str, Any]:
        """Infers target column, task type, and class distribution."""
        # Auto-detect target column if not supplied
        if not target_column or target_column not in df.columns:
            # Check last column or common target names
            common_targets = ["target", "label", "class", "churn", "price", "is_churn"]
            for name in common_targets:
                matches = [c for c in df.columns if c.lower() == name]
                if matches:
                    target_column = matches[0]
                    break

            if not target_column and len(df.columns) > 0:
                target_column = df.columns[-1]  # Default to last column

        if not target_column or target_column not in df.columns:
            return {"target_column": None, "task_type": TaskType.CLASSIFICATION.value}

        series = df[target_column].dropna()
        unique_count = series.nunique()
        total = len(series)

        # Task type inference
        col_type = column_types.get(target_column, ColumnType.UNKNOWN) if column_types else ColumnType.UNKNOWN

        if col_type == ColumnType.NUMERIC and unique_count > 20 and (unique_count / total) > 0.05:
            task_type = TaskType.REGRESSION
            is_imbalanced = False
            class_distribution = {}
        else:
            task_type = TaskType.CLASSIFICATION
            counts = series.value_counts(normalize=True).round(4).to_dict()
            class_distribution = {str(k): float(v) for k, v in counts.items()}
            
            # Check class imbalance (e.g. min class < 20%)
            min_prop = min(class_distribution.values()) if class_distribution else 0.5
            is_imbalanced = min_prop < 0.20

        return {
            "target_column": target_column,
            "task_type": task_type.value if hasattr(task_type, "value") else str(task_type),
            "is_imbalanced": is_imbalanced,
            "class_distribution": class_distribution,
            "distinct_targets": unique_count,
        }
