from typing import List, Dict, Any, Optional
from backend.schemas.experiment import ExperimentResult


class MetricAnalyzer:
    """Analyzes and normalizes raw metric results across experiment runs."""

    @classmethod
    def extract_primary_metric_score(cls, result: ExperimentResult) -> float:
        """Extracts primary metric score from an experiment result."""
        if not result.metrics or result.status != "completed":
            return 0.0
        return float(result.metrics.primary_metric)

    @classmethod
    def normalize_scores(cls, results: List[ExperimentResult]) -> Dict[str, float]:
        """Normalizes primary metric scores into [0.0, 1.0] relative scale."""
        scores = {r.experiment_id: cls.extract_primary_metric_score(r) for r in results if r.status == "completed"}
        if not scores:
            return {}

        min_val = min(scores.values())
        max_val = max(scores.values())

        if min_val == max_val:
            return {exp_id: 1.0 for exp_id in scores}

        range_val = max_val - min_val
        return {exp_id: round((val - min_val) / range_val, 4) for exp_id, val in scores.items()}
