from typing import Dict, Any, Tuple
import pandas as pd

from backend.schemas.semantic_profile import ResourceProfile
from backend.profiling.execution_hints import ExecutionHints


class ResourceAnalyzer:
    """Computes resource usage metrics and operational execution hints."""

    @classmethod
    def analyze_resources(cls, df: pd.DataFrame, file_size_bytes: int) -> Tuple[ResourceProfile, ExecutionHints]:
        """Calculates dataset size in memory and returns ResourceProfile & ExecutionHints."""
        memory_bytes = df.memory_usage(deep=True).sum()
        memory_mb = round(memory_bytes / (1024 * 1024), 2)
        total_rows = len(df)

        if memory_mb > 500 or total_rows > 1_000_000:
            execution_mode = "large_dataset"
            use_lazy = True
            rec_sampling = "10%" if total_rows > 2_000_000 else None
            workers = 8
        elif memory_mb > 100 or total_rows > 100_000:
            execution_mode = "standard"
            use_lazy = False
            rec_sampling = None
            workers = 4
        else:
            execution_mode = "lightweight"
            use_lazy = False
            rec_sampling = None
            workers = 2

        res_profile = ResourceProfile(
            execution_mode=execution_mode,
            use_lazy_loading=use_lazy,
            recommended_workers=workers,
            memory_mb=memory_mb,
        )

        exec_hints = ExecutionHints(
            execution_mode=execution_mode,
            use_lazy_loading=use_lazy,
            recommended_sampling=rec_sampling,
            parallel_workers=workers,
        )

        return res_profile, exec_hints
