import os
import tempfile
import pytest
import pandas as pd
from sklearn.linear_model import LogisticRegression

from backend.schemas.report import FinalRecommendation
from backend.schemas.experiment import PipelineDefinition, ExperimentOperation
from backend.schemas.evaluation import EvaluationReport, RankingItem
from backend.reports import (
    MarkdownReportGenerator,
    HTMLReportGenerator,
    ArtifactExporter,
    ReportService,
)


@pytest.fixture
def sample_recommendation():
    return FinalRecommendation(
        winning_experiment_id="EXP_WINNER_001",
        pipeline=PipelineDefinition(
            operations=[
                ExperimentOperation(type="imputation", method="median"),
                ExperimentOperation(type="encoding", method="onehot"),
            ],
            model_name="RandomForestClassifier",
        ),
        model="RandomForestClassifier",
        final_metrics={"accuracy": 0.94, "f1": 0.93},
        summary="RandomForestClassifier achieved top predictive accuracy with stable cross-validation scores.",
        key_findings=[
            "Median imputation prevented extreme outlier distortion.",
            "One-hot encoding improved categorical feature representation.",
        ],
        exported_artifacts={},
    )


@pytest.fixture
def sample_evaluation_report():
    return EvaluationReport(
        winner="EXP_WINNER_001",
        ranking=[
            RankingItem(rank=1, experiment_id="EXP_WINNER_001", score=0.94, model="RandomForestClassifier"),
            RankingItem(rank=2, experiment_id="EXP_002", score=0.82, model="LogisticRegression"),
        ],
        knowledge=[],
        should_continue=False,
        reason="Convergence reached",
    )


def test_markdown_generator(sample_recommendation, sample_evaluation_report):
    md = MarkdownReportGenerator.generate_markdown(
        recommendation=sample_recommendation,
        evaluation_report=sample_evaluation_report,
    )

    assert "# DataPilot-AI Research & Recommendation Report" in md
    assert "EXP_WINNER_001" in md
    assert "RandomForestClassifier" in md
    assert "| 1 | `EXP_WINNER_001` | `RandomForestClassifier` | `0.9400` |" in md


def test_html_generator(sample_recommendation, sample_evaluation_report):
    html = HTMLReportGenerator.generate_html(
        recommendation=sample_recommendation,
        evaluation_report=sample_evaluation_report,
    )

    assert "<!DOCTYPE html>" in html
    assert "EXP_WINNER_001" in html
    assert "RandomForestClassifier" in html
    assert "0.94" in html


def test_artifact_exporter(sample_recommendation):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. CSV export
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        csv_path = ArtifactExporter.export_cleaned_dataset(df, "JOB_TEST", storage_dir=tmp_dir)
        assert os.path.exists(csv_path)

        # 2. Model export
        model = LogisticRegression()
        model.fit([[1], [2]], [0, 1])
        model_path = ArtifactExporter.export_model_artifact(model, "JOB_TEST", storage_dir=tmp_dir)
        assert os.path.exists(model_path)

        # 3. Report files export
        reports = ArtifactExporter.export_report_files("<h1>Test</h1>", "# Test", "JOB_TEST", storage_dir=tmp_dir)
        assert os.path.exists(reports["html"])
        assert os.path.exists(reports["markdown"])


def test_report_service_end_to_end(sample_recommendation, sample_evaluation_report):
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = ReportService(db_session=None)
        res = service.generate_and_export_report(
            job_id="JOB_TEST_99",
            recommendation=sample_recommendation,
            evaluation_report=sample_evaluation_report,
            storage_dir=tmp_dir,
        )

        assert res["job_id"] == "JOB_TEST_99"
        assert "html" in res["artifacts"]
        assert os.path.exists(res["artifacts"]["html"])
