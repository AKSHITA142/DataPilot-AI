from typing import List, Dict, Any
from collections import defaultdict
from backend.schemas.experiment import ExperimentResult
from backend.schemas.evaluation import KnowledgeFinding


class KnowledgeGenerator:
    """Extracts cross-experiment strategy insights into reusable KnowledgeFinding objects."""

    @classmethod
    def generate_findings(cls, results: List[ExperimentResult]) -> List[KnowledgeFinding]:
        """Extracts generalizable strategy patterns across experiment results."""
        findings: List[KnowledgeFinding] = []
        completed = [r for r in results if r.status == "completed" and r.metrics]

        if len(completed) < 2:
            return findings

        # Group metrics by model family
        model_scores = defaultdict(list)
        operation_scores = defaultdict(list)

        for r in completed:
            score = float(r.metrics.primary_metric)
            model_scores[r.model].append(score)

            if r.pipeline:
                for op in r.pipeline.operations:
                    key = f"{op.type}:{op.method}"
                    operation_scores[key].append(score)

        # 1. Evaluate top performing model family
        best_model = max(model_scores.keys(), key=lambda m: sum(model_scores[m]) / len(model_scores[m]))
        avg_score = round(sum(model_scores[best_model]) / len(model_scores[best_model]), 4)

        findings.append(
            KnowledgeFinding(
                finding=f"Model family '{best_model}' consistently achieved high primary metric performance (avg: {avg_score}).",
                confidence=0.88,
                supporting_experiments=[r.experiment_id for r in completed if r.model == best_model],
            )
        )

        # 2. Evaluate top performing preprocessing operation
        if operation_scores:
            best_op = max(operation_scores.keys(), key=lambda op: sum(operation_scores[op]) / len(operation_scores[op]))
            op_avg = round(sum(operation_scores[best_op]) / len(operation_scores[best_op]), 4)
            op_type, op_method = best_op.split(":")

            findings.append(
                KnowledgeFinding(
                    finding=f"Preprocessing strategy '{op_method}' ({op_type}) demonstrated positive impact across experiments (avg: {op_avg}).",
                    confidence=0.85,
                    supporting_experiments=[
                        r.experiment_id for r in completed
                        if r.pipeline and any(op.method == op_method for op in r.pipeline.operations)
                    ],
                )
            )

        return findings
