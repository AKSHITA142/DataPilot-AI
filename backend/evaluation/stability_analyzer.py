from typing import List, Dict, Any, Tuple
import numpy as np
from backend.schemas.experiment import ExperimentResult


class StabilityAnalyzer:
    """Evaluates cross-validation fold variance to determine pipeline stability."""

    @classmethod
    def calculate_stability(cls, result: ExperimentResult) -> Tuple[float, float, float]:
        """Calculates mean score, std dev, and normalized stability rating [0.0, 1.0]."""
        if not result.metrics or not result.metrics.cv_scores or len(result.metrics.cv_scores) < 2:
            return 0.0, 0.0, 0.5

        scores = np.array(result.metrics.cv_scores)
        mean_score = float(np.mean(scores))
        std_dev = float(np.std(scores))

        # Higher std_dev indicates lower stability. Scale std_dev into stability score:
        # std_dev of 0.0 -> stability 1.0, std_dev >= 0.2 -> stability 0.0
        stability_score = max(0.0, 1.0 - (std_dev / 0.2))
        return round(mean_score, 4), round(std_dev, 4), round(stability_score, 4)

    @classmethod
    def analyze_batch(cls, results: List[ExperimentResult]) -> Dict[str, float]:
        """Returns dictionary mapping experiment_id -> stability score."""
        stability_map: Dict[str, float] = {}
        for r in results:
            if r.status == "completed":
                _, _, score = cls.calculate_stability(r)
                stability_map[r.experiment_id] = score
            else:
                stability_map[r.experiment_id] = 0.0
        return stability_map
