from typing import List, Dict, Any
import pandas as pd
import numpy as np
from scipy import stats

from backend.schemas.enums import ColumnType
from backend.schemas.semantic_profile import ColumnProfile


class StatisticsAnalyzer:
    """Computes summary statistics for each column and returns a list of ColumnProfile objects."""

    @classmethod
    def compute_column_profiles(
        cls,
        df: pd.DataFrame,
        column_types: Dict[str, ColumnType]
    ) -> List[ColumnProfile]:
        """Computes statistical profiles for all columns in DataFrame."""
        profiles: List[ColumnProfile] = []
        total_rows = len(df)

        for col in df.columns:
            col_type = column_types.get(col, ColumnType.UNKNOWN)
            series = df[col]

            missing_count = int(series.isna().sum())
            missing_pct = round((missing_count / total_rows) * 100.0, 2) if total_rows > 0 else 0.0
            distinct_count = int(series.nunique(dropna=True))

            sample_vals = series.dropna().head(5).tolist()
            # Clean sample values for JSON serialization
            sample_vals_cleaned = []
            for v in sample_vals:
                if isinstance(v, (np.integer, int)):
                    sample_vals_cleaned.append(int(v))
                elif isinstance(v, (np.floating, float)):
                    sample_vals_cleaned.append(float(v) if not np.isnan(v) else None)
                else:
                    sample_vals_cleaned.append(str(v))

            skewness = None
            mean_val = None
            std_val = None
            min_val = None
            max_val = None

            if col_type == ColumnType.NUMERIC:
                clean_num = series.dropna().astype(float)
                if len(clean_num) > 0:
                    mean_val = round(float(clean_num.mean()), 4)
                    std_val = round(float(clean_num.std()), 4) if len(clean_num) > 1 else 0.0
                    min_val = round(float(clean_num.min()), 4)
                    max_val = round(float(clean_num.max()), 4)

                    if len(clean_num) > 2 and std_val > 0:
                        skew_calc = stats.skew(clean_num)
                        if not np.isnan(skew_calc):
                            skewness = round(float(skew_calc), 4)

            profiles.append(
                ColumnProfile(
                    name=str(col),
                    type=col_type,
                    missing_count=missing_count,
                    missing_pct=missing_pct,
                    distinct_count=distinct_count,
                    skewness=skewness,
                    mean=mean_val,
                    std=std_val,
                    min=min_val,
                    max=max_val,
                    sample_values=sample_vals_cleaned,
                )
            )

        return profiles
