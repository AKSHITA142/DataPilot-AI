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


import logging
from backend.core.logging_config import log_phase_banner

logger = logging.getLogger("datapilot.profiling")


class ProfilingEngine:
    """
    Main orchestrator for dataset profiling.
    Observes raw dataset files and generates structured SemanticProfile and ExecutionHints.
    """

    @classmethod
    def profile_file(
        cls,
        file_path: str,
        target_column: Optional[str] = None
    ) -> Tuple[SemanticProfile, ExecutionHints]:
        """
        Profiles a dataset file (CSV/Parquet) and returns (SemanticProfile, ExecutionHints).
        """
        log_phase_banner("Phase 06: Profiling & Diagnostics", f"Profiling raw dataset file: {file_path}")
        logger.info(f"[PROFILING] Reading dataset file: {file_path}")
        df, file_meta = DataLoader.load_data(file_path)
        logger.info(f"[PROFILING] File loaded. Rows: {len(df)}, Columns: {len(df.columns)}, Format: {file_meta.get('format')}")
        return cls.profile_dataframe(df, file_meta, target_column=target_column)

    @classmethod
    def profile_dataframe(
        cls,
        df: pd.DataFrame,
        file_meta: Optional[Dict[str, Any]] = None,
        target_column: Optional[str] = None
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

        logger.info(f"[PROFILING STEP 1/8] Analyzing column schemas for {len(df.columns)} columns...")
        schema_result = SchemaAnalyzer.analyze_schema(df)
        column_types = schema_result["column_types"]
        logger.info(f"[PROFILING STEP 1/8] Inferred types: {column_types} | Candidate IDs: {schema_result['id_candidates']}")

        logger.info("[PROFILING STEP 2/8] Computing column statistical summaries (mean, std, min, max, nulls)...")
        col_profiles = StatisticsAnalyzer.compute_column_profiles(df, column_types)

        logger.info("[PROFILING STEP 3/8] Evaluating data quality issues (missingness, cardinality, duplicates)...")
        quality_issues = QualityAnalyzer.analyze_quality(df, col_profiles)
        logger.info(f"[PROFILING STEP 3/8] Identified {len(quality_issues)} quality issues.")

        logger.info("[PROFILING STEP 4/8] Analyzing numerical feature distributions & skewness...")
        dist_result = DistributionAnalyzer.analyze_distributions(df, col_profiles)

        logger.info("[PROFILING STEP 5/8] Computing feature correlations & relationships...")
        rel_result = RelationshipAnalyzer.analyze_relationships(df)

        logger.info("[PROFILING STEP 6/8] Detecting numeric outliers via IQR rule...")
        outlier_result = OutlierAnalyzer.analyze_outliers(df)

        logger.info(f"[PROFILING STEP 7/8] Analyzing target column: {target_column or 'Auto-detect'}...")
        target_result = TargetAnalyzer.analyze_target(df, target_column, column_types)
        logger.info(f"[PROFILING STEP 7/8] Target task type resolved: {target_result.get('task_type')}")

        logger.info("[PROFILING STEP 8/8] Assessing RAM footprint & generating execution hints...")
        resource_prof, exec_hints = ResourceAnalyzer.analyze_resources(
            df, file_meta.get("file_size_bytes", 0)
        )
        logger.info(f"[PROFILING STEP 8/8] RAM Footprint: {resource_prof.memory_mb:.2f} MB | Execution Mode: '{exec_hints.execution_mode}' | Workers: {exec_hints.parallel_workers}")

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

        recommendation_context = {
            "distributions": dist_result,
            "relationships": rel_result,
            "outliers": outlier_result,
        }

        semantic_profile = SemanticProfile(
            dataset_summary=dataset_summary,
            column_profiles=col_profiles,
            quality_issues=quality_issues,
            resource_profile=resource_prof,
            recommendation_context=recommendation_context,
        )

        logger.info(f"[PROFILING COMPLETE] Generated SemanticProfile for dataset '{file_meta.get('filename')}' successfully.")
        return semantic_profile, exec_hints
