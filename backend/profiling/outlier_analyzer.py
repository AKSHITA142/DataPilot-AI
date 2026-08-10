from typing import Dict, Any, List
import pandas as pd
import numpy as np


class OutlierAnalyzer:
    """Detects univariate outliers in numeric features using IQR and Z-scores."""

    @classmethod
    def analyze_outliers(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates IQR-based outlier counts for all numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        outlier_summary: Dict[str, Any] = {}

        total_rows = len(df)
        if total_rows == 0 or numeric_df.empty:
            return {"outlier_summary": {}, "columns_with_outliers": []}

        cols_with_outliers: List[str] = []

        for col in numeric_df.columns:
            clean_s = numeric_df[col].dropna()
            if len(clean_s) < 4:
                continue

            q1 = clean_s.quantile(0.25)
            q3 = clean_s.quantile(0.75)
            iqr = q3 - q1

            if iqr == 0:
                continue

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = clean_s[(clean_s < lower_bound) | (clean_s > upper_bound)]
            count = len(outliers)
            pct = round((count / total_rows) * 100.0, 2)

            if count > 0:
                outlier_summary[col] = {
                    "outlier_count": count,
                    "outlier_pct": pct,
                    "lower_bound": round(float(lower_bound), 4),
                    "upper_bound": round(float(upper_bound), 4),
                }
                if pct > 2.0:
                    cols_with_outliers.append(col)

        return {
            "outlier_summary": outlier_summary,
            "columns_with_outliers": cols_with_outliers,
        }
