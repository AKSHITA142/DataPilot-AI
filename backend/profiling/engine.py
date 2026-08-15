from typing import Optional, Tuple, Dict, Any
import pandas as pd

from backend.schemas.semantic_profile import SemanticProfile
from backend.profiling.loader import DataLoader
from backend.profiling.schema_analyzer import SchemaAnalyzer
from backend.profiling.statistics_analyzer import StatisticsAnalyzer
from backend.profiling.quality_analyzer import QualityAnalyzer
from backend.profiling.distribution_analyzer import DistributionAnalyzer
from backend.profiling.relationship_analyzer import RelationshipAnalyzer
from backend.profiling.outlier_analyzer import OutlierAnalyzer
from backend.profiling.target_analyzer import TargetAnalyzer
from backend.profiling.resource_analyzer import ResourceAnalyzer
from backend.profiling.execution_hints import ExecutionHints


class ProfilingEngine:
    """
    Main orchestrator for dataset profiling.
    Observes raw dataset files and generates structured SemanticProfile and ExecutionHints.
    """

    @classmethod
    def profile_file(
        cls,
        file_path: str,
        target_column: Optional[str] = None,
        user_mission: str = "",
        user_task_type: str = "general",
    ) -> Tuple[SemanticProfile, ExecutionHints]:
        """
        Profiles a dataset file (CSV/Parquet) and returns (SemanticProfile, ExecutionHints).
        Uses lazy sampling on large datasets to keep profiling fast and RAM-safe.
        """
        df, file_meta, is_sampled = DataLoader.load_lazy_sample(file_path)
        return cls.profile_dataframe(
            df, file_meta,
            target_column=target_column,
            user_mission=user_mission,
            user_task_type=user_task_type,
        )

    @classmethod
    def profile_bytes(
        cls,
        file_bytes: bytes,
        filename: str = "dataset.csv",
        target_column: Optional[str] = None,
        user_mission: str = "",
        user_task_type: str = "general",
    ) -> Tuple[SemanticProfile, ExecutionHints]:
        """
        Profiles in-memory dataset bytes (CSV/Parquet) directly without disk writes.
        """
        df, file_meta, is_sampled = DataLoader.load_lazy_sample_from_bytes(file_bytes, filename=filename)
        return cls.profile_dataframe(
            df, file_meta,
            target_column=target_column,
            user_mission=user_mission,
            user_task_type=user_task_type,
        )

    @classmethod
    def profile_dataframe(
        cls,
        df: pd.DataFrame,
        file_meta: Optional[Dict[str, Any]] = None,
        target_column: Optional[str] = None,
        user_mission: str = "",
        user_task_type: str = "general",
    ) -> Tuple[SemanticProfile, ExecutionHints]:
        """
        Profiles an in-memory DataFrame and returns (SemanticProfile, ExecutionHints).
        """
        file_meta = file_meta or {
            "filename": "in_memory_dataset",
            "file_size_bytes": int(df.memory_usage(deep=True).sum()),
            "row_count": len(df),
            "column_count": len(df.columns),
            "format": "dataframe",
        }

        # 1. Schema Analysis
        schema_result = SchemaAnalyzer.analyze_schema(df)
        column_types = schema_result["column_types"]

        # 2. Statistics Analysis
        col_profiles = StatisticsAnalyzer.compute_column_profiles(df, column_types)

        # 3. Quality Analysis
        quality_issues = QualityAnalyzer.analyze_quality(df, col_profiles)

        # 4. Distribution Analysis
        dist_result = DistributionAnalyzer.analyze_distributions(df, col_profiles)

        # 5. Relationship / Correlation Analysis
        rel_result = RelationshipAnalyzer.analyze_relationships(df)

        # 6. Outlier Analysis
        outlier_result = OutlierAnalyzer.analyze_outliers(df)

        # 7. Target Analysis
        target_result = TargetAnalyzer.analyze_target(
            df, target_column, column_types,
            user_mission=user_mission,
            user_task_type=user_task_type,
        )

        # 8. Resource Analysis & Execution Hints
        resource_prof, exec_hints = ResourceAnalyzer.analyze_resources(
            df, file_meta.get("file_size_bytes", 0)
        )

        # Construct Dataset Summary
        dataset_summary = {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": resource_prof.memory_mb,
            "filename": file_meta.get("filename"),
            "file_size_bytes": file_meta.get("file_size_bytes"),
            "target": target_result,
            "id_candidates": schema_result["id_candidates"],
            "timestamp_candidates": schema_result["timestamp_candidates"],
        }

        # Construct Recommendation Context
        recommendation_context = {
            "distributions": dist_result,
            "relationships": rel_result,
            "outliers": outlier_result,
        }

        # Build SemanticProfile Pydantic object
        semantic_profile = SemanticProfile(
            dataset_summary=dataset_summary,
            column_profiles=col_profiles,
            quality_issues=quality_issues,
            resource_profile=resource_prof,
            recommendation_context=recommendation_context,
        )

        return semantic_profile, exec_hints
