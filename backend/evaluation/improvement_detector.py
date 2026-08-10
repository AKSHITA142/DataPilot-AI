from typing import List, Optional, Tuple
from backend.schemas.evaluation import EvaluationReport


class ImprovementDetector:
    """Detects metric gains and convergence across research iterations."""

    CONVERGENCE_THRESHOLD = 0.005  # 0.5% gain threshold

    @classmethod
    def evaluate_progress(
        cls,
        current_best_score: float,
        previous_reports: Optional[List[EvaluationReport]] = None,
    ) -> Tuple[float, bool, str]:
        """Calculates metric gain, checks convergence, and generates recommendation reasoning."""
        if not previous_reports:
            return 0.0, False, "Initial iteration baseline established."

        prev_scores = []
        for r in previous_reports:
            if r.ranking and len(r.ranking) > 0 and r.ranking[0].score > 0.0:
                prev_scores.append(r.ranking[0].score)

        if not prev_scores:
            return 0.0, False, "Initial iteration baseline established."

        last_best = max(prev_scores)
        gain = round(current_best_score - last_best, 4)

        if gain <= cls.CONVERGENCE_THRESHOLD:
            return gain, True, f"Diminishing returns detected (gain: +{gain} <= threshold {cls.CONVERGENCE_THRESHOLD})."
        else:
            return gain, False, f"Significant improvement achieved (+{gain}). Continuing iteration."
