from typing import Dict, Any, List
import pandas as pd
import numpy as np
from backend.schemas.enums import ColumnType


class SchemaAnalyzer:
    """Analyzes DataFrame columns to infer data types, nullability, and candidates."""

    @staticmethod
    def infer_column_type(series: pd.Series) -> ColumnType:
        """Infers ColumnType enum for a given pandas Series."""
        # Drop missing values for type analysis
        clean_s = series.dropna()
        if len(clean_s) == 0:
            return ColumnType.UNKNOWN

        dtype = series.dtype

        # Boolean
        if pd.api.types.is_bool_dtype(dtype) or (clean_s.isin([True, False, 0, 1]).all() and len(clean_s.unique()) <= 2):
            return ColumnType.BOOLEAN

        # Datetime
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return ColumnType.DATETIME

        # Try parsing strings as datetimes if small sample looks like dates
        if pd.api.types.is_string_dtype(dtype) or dtype == object:
            sample_str = clean_s.astype(str).iloc[:20]
            try:
                # Check if strings look like date strings
                if sample_str.str.contains(r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}").any():
                    pd.to_datetime(sample_str, errors="raise")
                    return ColumnType.DATETIME
            except Exception:
                pass

        # Numeric
        if pd.api.types.is_numeric_dtype(dtype):
            return ColumnType.NUMERIC

        # Text vs Categorical
        if pd.api.types.is_string_dtype(dtype) or dtype == object:
            unique_ratio = len(clean_s.unique()) / len(clean_s)
            avg_length = clean_s.astype(str).str.len().mean()
            if avg_length > 50 or unique_ratio > 0.8:
                return ColumnType.TEXT
            return ColumnType.CATEGORICAL

        return ColumnType.UNKNOWN

    @classmethod
    def analyze_schema(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes schema and returns column type mapping and candidate columns."""
        column_types: Dict[str, ColumnType] = {}
        id_candidates: List[str] = []
        timestamp_candidates: List[str] = []

        total_rows = len(df)

        for col in df.columns:
            col_type = cls.infer_column_type(df[col])
            column_types[col] = col_type

            # Check ID candidates (unique values = total rows, or name contains id)
            if ("id" in col.lower() or "uuid" in col.lower()) and df[col].nunique() == total_rows:
                id_candidates.append(col)

            # Check timestamp candidates
            if col_type == ColumnType.DATETIME or "time" in col.lower() or "date" in col.lower():
                timestamp_candidates.append(col)

        return {
            "column_types": column_types,
            "id_candidates": id_candidates,
            "timestamp_candidates": timestamp_candidates,
        }
