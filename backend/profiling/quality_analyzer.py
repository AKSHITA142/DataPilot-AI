from typing import List
import pandas as pd

from backend.schemas.enums import SeverityLevel
from backend.schemas.semantic_profile import ColumnProfile, QualityIssue


class QualityAnalyzer:
    """Analyzes dataset quality issues such as missing values, constant columns, duplicate rows, etc."""

    @classmethod
    def analyze_quality(
        cls,
        df: pd.DataFrame,
        column_profiles: List[ColumnProfile]
    ) -> List[QualityIssue]:
        """Detects quality issues across columns and dataset structure."""
        issues: List[QualityIssue] = []
        total_rows = len(df)

        if total_rows == 0:
            return issues

        # 1. Check Missing Values
        high_missing_cols = [p.name for p in column_profiles if p.missing_pct > 20.0]
        critical_missing_cols = [p.name for p in column_profiles if p.missing_pct > 50.0]

        if critical_missing_cols:
            issues.append(
                QualityIssue(
                    problem="critical_missing_values",
                    severity=SeverityLevel.CRITICAL,
                    description=f"Columns with >50% missing values detected: {', '.join(critical_missing_cols)}",
                    affected_columns=critical_missing_cols,
                    confidence=0.98,
                )
            )
        elif high_missing_cols:
            issues.append(
                QualityIssue(
                    problem="high_missing_values",
                    severity=SeverityLevel.HIGH,
                    description=f"Columns with >20% missing values detected: {', '.join(high_missing_cols)}",
                    affected_columns=high_missing_cols,
                    confidence=0.90,
                )
            )

        # 2. Check Constant Columns (single unique value)
        constant_cols = [p.name for p in column_profiles if p.distinct_count <= 1 and p.missing_count < total_rows]
        if constant_cols:
            issues.append(
                QualityIssue(
                    problem="constant_columns",
                    severity=SeverityLevel.MEDIUM,
                    description=f"Constant columns containing only a single unique value: {', '.join(constant_cols)}",
                    affected_columns=constant_cols,
                    confidence=0.95,
                )
            )

        # 3. Check High Skewness
        highly_skewed_cols = [p.name for p in column_profiles if p.skewness is not None and abs(p.skewness) > 1.5]
        if highly_skewed_cols:
            issues.append(
                QualityIssue(
                    problem="high_skewness",
                    severity=SeverityLevel.MEDIUM,
                    description=f"Highly skewed numeric features (|skew| > 1.5): {', '.join(highly_skewed_cols)}",
                    affected_columns=highly_skewed_cols,
                    confidence=0.88,
                )
            )

        # 4. Check Duplicate Rows
        duplicate_count = int(df.duplicated().sum())
        if duplicate_count > 0:
            dup_pct = round((duplicate_count / total_rows) * 100.0, 2)
            sev = SeverityLevel.HIGH if dup_pct > 5.0 else SeverityLevel.LOW
            issues.append(
                QualityIssue(
                    problem="duplicate_rows",
                    severity=sev,
                    description=f"Dataset contains {duplicate_count} duplicate rows ({dup_pct}% of total).",
                    affected_columns=[],
                    confidence=0.99,
                )
            )

        return issues
