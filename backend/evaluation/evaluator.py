from typing import List, Optional, Tuple
import logging

from backend.schemas.experiment import ExperimentResult
from backend.schemas.mission_brief import MissionBrief
from backend.schemas.enums import DecisionType
from backend.schemas.evaluation import (
    EvaluationReport,
    ResearchDirectorDecision,
)
from backend.evaluation.ranking_engine import RankingEngine
from backend.evaluation.improvement_detector import ImprovementDetector
from backend.evaluation.knowledge_generator import KnowledgeGenerator

logger = logging.getLogger("datapilot.evaluation.evaluator")


class EvaluationEngine:
    """Main entry point class for evaluating experiment batches and producing schema-valid EvaluationReports."""

    def evaluate_batch(
        self,
        results: List[ExperimentResult],
        job_id: str = "JOB_001",
        mission_brief: Optional[MissionBrief] = None,
        previous_reports: Optional[List[EvaluationReport]] = None,
    ) -> Tuple[EvaluationReport, ResearchDirectorDecision]:
        """Evaluates batch of experiment results and returns (EvaluationReport, ResearchDirectorDecision)."""
        logger.info(f"[EVALUATION] Starting evaluation of {len(results)} experiments for job '{job_id}'...")

        # 1. Rank Experiments via Multi-Dimensional Composite Scoring
        logger.info("[EVALUATION STEP 1/4] Ranking experiments via 5D composite score (Metric: 35%, Gen: 25%, Var: 20%, Eff: 10%)...")
        rankings = RankingEngine.rank_experiments(results, mission_brief)

        for rank_item in rankings:
            logger.info(f"  -> Rank #{rank_item.rank}: `{rank_item.experiment_id}` ({rank_item.model}) | Composite Score: {rank_item.score:.4f}")

        # Determine winner
        best_experiment_id: str = "none"
        best_score: float = 0.0

        if rankings and rankings[0].score > 0.0:
            winner_item = rankings[0]
            best_experiment_id = winner_item.experiment_id
            best_score = winner_item.score

        # 2. Check Improvement & Convergence
        logger.info(f"[EVALUATION STEP 2/4] Evaluating score gain vs previous iterations (Current Best Score: {best_score:.4f})...")
        gain, is_converged, convergence_reason = ImprovementDetector.evaluate_progress(
            current_best_score=best_score,
            previous_reports=previous_reports,
        )
        logger.info(f"[EVALUATION STEP 2/4] Score Gain: {gain:+.4f} | Converged: {is_converged} ({convergence_reason})")

        # 3. Generate Knowledge Base Findings
        logger.info("[EVALUATION STEP 3/4] Mining strategy knowledge base findings...")
        findings = KnowledgeGenerator.generate_findings(results)
        logger.info(f"[EVALUATION STEP 3/4] Mined {len(findings)} knowledge rules.")
        for f in findings:
            logger.info(f"  💡 Finding: {f.finding} (Confidence: {f.confidence:.2f})")

        # 4. Determine Continuation & Formulate Decision
        logger.info("[EVALUATION STEP 4/4] Formulating Research Director Decision...")
        if best_experiment_id == "none" or best_score == 0.0:
            should_continue = False
            decision_enum = DecisionType.STOP
            reasoning = "All experiments in batch failed execution or violated constraints."
        elif is_converged:
            should_continue = False
            decision_enum = DecisionType.STOP
            reasoning = f"Convergence reached: {convergence_reason} Winner: {best_experiment_id}."
        else:
            should_continue = True
            decision_enum = DecisionType.CONTINUE
            reasoning = f"Performance gain of {gain:.4f} achieved (> 0.005 threshold). Continuing optimization."

        report = EvaluationReport(
            winner=best_experiment_id,
            ranking=rankings,
            knowledge=findings,
            should_continue=should_continue,
            reason=reasoning,
        )

        decision = ResearchDirectorDecision(
            decision=decision_enum,
            confidence=0.90 if is_converged else 0.85,
            knowledge=[f.finding for f in findings],
            remaining_questions=[],
            next_experiments=[],
        )

        return report, decision
