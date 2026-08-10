import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.database.connection import init_db
from backend.models import (
    UserModel,
    DatasetModel,
    JobModel,
    ExperimentModel,
    KnowledgeEntryModel,
    ReportModel,
)
from backend.repositories import (
    DatasetRepository,
    JobRepository,
    ExperimentRepository,
    KnowledgeRepository,
    ReportRepository,
)
from backend.schemas import (
    SemanticProfile,
    ColumnProfile,
    ColumnType,
    QualityIssue,
    MissionBrief,
    JobStatus,
)


@pytest.fixture
def db_session():
    """Fixture providing an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_init_db_and_tables(db_session):
    """Verify all 6 core ORM tables are created correctly."""
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()
    expected_tables = {"users", "datasets", "jobs", "experiments", "knowledge_entries", "reports"}
    assert expected_tables.issubset(set(tables))


def test_dataset_repository_crud(db_session):
    """Test DatasetRepository CRUD operations."""
    user = UserModel(email="researcher@example.com", full_name="Dr. Data")
    db_session.add(user)
    db_session.commit()

    repo = DatasetRepository(db_session)
    dataset = DatasetModel(
        owner_id=user.id,
        filename="housing.csv",
        file_path="/storage/datasets/housing.csv",
        file_size_bytes=1048576,
        row_count=500,
        column_count=14,
        checksum="sha256_checksum_hash_123"
    )
    created = repo.create(dataset)
    assert created.id is not None
    assert created.filename == "housing.csv"

    # Lookup by checksum
    found = repo.get_by_checksum("sha256_checksum_hash_123")
    assert found is not None
    assert found.id == created.id

    # List by owner
    by_owner = repo.list_by_owner(user.id)
    assert len(by_owner) == 1
    assert by_owner[0].filename == "housing.csv"


def test_job_repository_crud(db_session):
    """Test JobRepository status updates and mission brief storage."""
    dataset = DatasetModel(
        filename="test.csv",
        file_path="/path/test.csv",
        file_size_bytes=100
    )
    db_session.add(dataset)
    db_session.commit()

    repo = JobRepository(db_session)
    job = JobModel(
        dataset_id=dataset.id,
        status=JobStatus.QUEUED.value,
        objective="Optimize accuracy"
    )
    created = repo.create(job)
    assert created.status == "queued"

    # Update status
    updated = repo.update_status(created.id, status=JobStatus.EXECUTING.value, progress_pct=50.0)
    assert updated.status == "executing"
    assert updated.progress_pct == 50.0

    # Set mission brief
    mb = MissionBrief(objective="Optimize accuracy")
    with_mb = repo.set_mission_brief(created.id, mb.model_dump())
    assert with_mb.mission_brief["objective"] == "Optimize accuracy"

    # Query by status
    executing_jobs = repo.list_by_status("executing")
    assert len(executing_jobs) == 1


def test_experiment_repository_crud(db_session):
    """Test ExperimentRepository batch insertion and query methods."""
    dataset = DatasetModel(filename="data.csv", file_path="/data.csv", file_size_bytes=50)
    db_session.add(dataset)
    db_session.commit()

    job = JobModel(dataset_id=dataset.id, status="executing")
    db_session.add(job)
    db_session.commit()

    repo = ExperimentRepository(db_session)
    e1 = ExperimentModel(
        job_id=job.id,
        experiment_id_code="EXP_001",
        model_name="RandomForest",
        metrics={"accuracy": 0.88, "f1": 0.87},
        runtime_seconds=4.5
    )
    e2 = ExperimentModel(
        job_id=job.id,
        experiment_id_code="EXP_002",
        model_name="XGBoost",
        metrics={"accuracy": 0.93, "f1": 0.92},
        runtime_seconds=6.1
    )

    batch_created = repo.create_batch([e1, e2])
    assert len(batch_created) == 2

    # Query by job
    by_job = repo.list_by_job(job.id)
    assert len(by_job) == 2

    # Query by code
    exp_by_code = repo.get_by_code(job.id, "EXP_002")
    assert exp_by_code is not None
    assert exp_by_code.model_name == "XGBoost"


def test_knowledge_and_report_repository(db_session):
    """Test KnowledgeRepository and ReportRepository CRUD operations."""
    dataset = DatasetModel(filename="data.csv", file_path="/data.csv", file_size_bytes=50)
    db_session.add(dataset)
    db_session.commit()

    job = JobModel(dataset_id=dataset.id, status="completed")
    db_session.add(job)
    db_session.commit()

    # Knowledge Repository
    k_repo = KnowledgeRepository(db_session)
    k_entry = KnowledgeEntryModel(
        job_id=job.id,
        finding="Log transformation reduced skewness",
        confidence=0.95,
        source_experiment_ids=["EXP_001", "EXP_002"]
    )
    k_repo.create(k_entry)

    findings = k_repo.list_by_job(job.id)
    assert len(findings) == 1
    assert findings[0].confidence == 0.95

    # Report Repository
    r_repo = ReportRepository(db_session)
    report = ReportModel(
        job_id=job.id,
        winning_experiment_id="EXP_002",
        report_file_path="/reports/job_123.md",
        summary={"winning_model": "XGBoost", "winning_score": 0.93}
    )
    r_repo.create(report)

    fetched_report = r_repo.get_by_job(job.id)
    assert fetched_report is not None
    assert fetched_report.winning_experiment_id == "EXP_002"


def test_pydantic_to_orm_integration(db_session):
    """Verify integration between Phase 1 Pydantic models and Phase 2 ORM JSON columns."""
    col = ColumnProfile(name="income", type=ColumnType.NUMERIC, missing_pct=2.1)
    issue = QualityIssue(problem="high_skewness", confidence=0.88, affected_columns=["income"])
    profile = SemanticProfile(
        dataset_summary={"rows": 10000, "cols": 12},
        column_profiles=[col],
        quality_issues=[issue]
    )

    dataset = DatasetModel(
        filename="income.csv",
        file_path="/data/income.csv",
        file_size_bytes=2048576,
        semantic_profile=profile.model_dump()
    )
    db_session.add(dataset)
    db_session.commit()

    fetched = db_session.query(DatasetModel).filter(DatasetModel.id == dataset.id).first()
    assert fetched.semantic_profile["dataset_summary"]["rows"] == 10000

    # Reconstruct Pydantic model from fetched JSON column
    restored_profile = SemanticProfile.model_validate(fetched.semantic_profile)
    assert restored_profile.column_profiles[0].name == "income"
    assert restored_profile.quality_issues[0].confidence == 0.88
