from typing import Dict, Any, List
import pandas as pd
from backend.schemas.enums import ColumnType
from backend.schemas.semantic_profile import ColumnProfile


class DistributionAnalyzer:
    """Analyzes distribution shapes of numeric features."""

    @classmethod
    def analyze_distributions(
        cls,
        df: pd.DataFrame,
        column_profiles: List[ColumnProfile]
    ) -> Dict[str, Any]:
        """Analyzes distribution shapes and identifies highly skewed or multi-modal columns."""
        distribution_info: Dict[str, Any] = {}

        for profile in column_profiles:
            if profile.type == ColumnType.NUMERIC and profile.skewness is not None:
                shape = "normal"
                if profile.skewness > 1.0:
                    shape = "right_skewed"
                elif profile.skewness < -1.0:
                    shape = "left_skewed"

                distribution_info[profile.name] = {
                    "skewness": profile.skewness,
                    "shape": shape,
                }

        return distribution_info
