import pytest

from backend.schemas.experiment import (
    ExperimentOperation,
    ExperimentResult,
    PipelineDefinition,
    MetricsResult,
)
from backend.schemas.mission_brief import MissionBrief, MissionConstraints
from backend.schemas.enums import DecisionType
from backend.evaluation.metric_analyzer import MetricAnalyzer
from backend.evaluation.stability_analyzer import StabilityAnalyzer
from backend.evaluation.constraint_validator import ConstraintValidator
from backend.evaluation.ranking_engine import RankingEngine
from backend.evaluation.improvement_detector import ImprovementDetector
from backend.evaluation.knowledge_generator import KnowledgeGenerator
from backend.evaluation.evaluator import EvaluationEngine


@pytest.fixture
def sample_experiment_results():
    """Generates sample experiment results with varying metrics and stability."""
    return [
        ExperimentResult(
            experiment_id="EXP_001",
            pipeline=PipelineDefinition(
                operations=[
                    ExperimentOperation(type="imputation", method="median"),
                    ExperimentOperation(type="scaling", method="standard"),
                ],
                model_name="RandomForestClassifier",
            ),
            model="RandomForestClassifier",
            metrics=MetricsResult(
                primary_metric=0.88,
                metrics={"accuracy": 0.88, "f1": 0.87},
                cv_scores=[0.88, 0.87, 0.89, 0.88, 0.88],  # Stable fold scores
            ),
            runtime=1.5,
            status="completed",
        ),
        ExperimentResult(
            experiment_id="EXP_002",
            pipeline=PipelineDefinition(
                operations=[
                    ExperimentOperation(type="imputation", method="mean"),
                    ExperimentOperation(type="scaling", method="minmax"),
                ],
                model_name="LogisticRegression",
            ),
            model="LogisticRegression",
            metrics=MetricsResult(
                primary_metric=0.92,
                metrics={"accuracy": 0.92, "f1": 0.91},
                cv_scores=[0.99, 0.65, 0.98, 0.70, 0.99],  # Unstable fold scores
            ),
            runtime=12.0,
            status="completed",
        ),
        ExperimentResult(
            experiment_id="EXP_003",
            pipeline=PipelineDefinition(
                operations=[
                    ExperimentOperation(type="imputation", method="constant"),
                ],
                model_name="SVC",
            ),
            model="SVC",
            metrics=MetricsResult(
                primary_metric=0.50,
                metrics={"accuracy": 0.50},
                cv_scores=[0.50, 0.50, 0.50],
            ),
            runtime=0.5,
            status="completed",
        ),
    ]


def test_metric_analyzer(sample_experiment_results):
    norm = MetricAnalyzer.normalize_scores(sample_experiment_results)
    assert len(norm) == 3
    assert norm["EXP_002"] == 1.0  # Highest metric normalized to 1.0
    assert norm["EXP_003"] == 0.0  # Lowest metric normalized to 0.0


def test_stability_analyzer(sample_experiment_results):
    mean_s, std_s, score_s = StabilityAnalyzer.calculate_stability(sample_experiment_results[0])
    mean_u, std_u, score_u = StabilityAnalyzer.calculate_stability(sample_experiment_results[1])

    assert score_s > score_u  # Stable pipeline has higher stability score than unstable pipeline


def test_constraint_validator(sample_experiment_results):
    # Mission constraint: prefer interpretable models via custom_constraints
    mission = MissionBrief(
        objective="Test",
        constraints=MissionConstraints(custom_constraints={"prefer_interpretable_models": True})
    )

    valid_001 = ConstraintValidator.validate_constraints(sample_experiment_results[0], mission)
    valid_002 = ConstraintValidator.validate_constraints(sample_experiment_results[1], mission)

    assert valid_001 is False  # RandomForest is not interpretable
    assert valid_002 is True   # LogisticRegression is interpretable


def test_ranking_engine(sample_experiment_results):
    rankings = RankingEngine.rank_experiments(sample_experiment_results)
    assert len(rankings) == 3
    assert rankings[0].rank == 1
    assert rankings[1].rank == 2
    assert rankings[2].rank == 3
    assert rankings[0].model == "RandomForestClassifier"


def test_improvement_detector():
    gain, converged, msg = ImprovementDetector.evaluate_progress(0.92, previous_reports=[])
    assert converged is False

    # Minimal gain <= threshold
    report_fake, _ = EvaluationEngine().evaluate_batch([], job_id="J1")
    gain2, converged2, msg2 = ImprovementDetector.evaluate_progress(
        0.921,
        previous_reports=[report_fake]
    )


def test_knowledge_generator(sample_experiment_results):
    findings = KnowledgeGenerator.generate_findings(sample_experiment_results)
    assert len(findings) > 0
    assert findings[0].confidence > 0.0


def test_evaluation_engine_end_to_end(sample_experiment_results):
    engine = EvaluationEngine()
    report, decision = engine.evaluate_batch(
        results=sample_experiment_results,
        job_id="JOB_TEST_100",
    )

    assert report.winner != "none"
    assert len(report.ranking) == 3
    assert len(report.knowledge) > 0
    assert report.should_continue is True
    assert decision.decision in (DecisionType.CONTINUE, DecisionType.STOP)
