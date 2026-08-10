from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np


class RelationshipAnalyzer:
    """Computes feature relationships, correlation matrices, and collinearity."""

    @classmethod
    def analyze_relationships(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Computes correlation matrix and identifies high collinearity pairs."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return {"correlation_matrix": {}, "high_correlation_pairs": []}

        # Drop constant columns before correlation
        numeric_df = numeric_df.loc[:, numeric_df.std() > 0]
        if len(numeric_df.columns) < 2:
            return {"correlation_matrix": {}, "high_correlation_pairs": []}

        corr_matrix = numeric_df.corr(method="pearson").round(4)
        
        # Identify high correlation pairs (> 0.85)
        high_corr_pairs: List[Dict[str, Any]] = []
        cols = corr_matrix.columns

        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                col1, col2 = cols[i], cols[j]
                val = float(corr_matrix.loc[col1, col2])
                if not np.isnan(val) and abs(val) >= 0.85:
                    high_corr_pairs.append({
                        "feature_1": col1,
                        "feature_2": col2,
                        "correlation": val,
                    })

        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "high_correlation_pairs": high_corr_pairs,
        }
