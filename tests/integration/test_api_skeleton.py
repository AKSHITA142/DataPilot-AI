import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.response import ErrorResponse

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint responds with Welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs_url"] == "/docs"


def test_health_check_endpoint():
    """Verify GET /health returns 200 OK with app and DB status."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    health_data = json_data["data"]
    assert health_data["app"] == "DataPilot-AI"
    assert health_data["status"] in ["healthy", "degraded"]
    assert "timestamp" in health_data


def test_registered_route_skeletons():
    """Verify all registered API routes (/upload, /jobs, /experiments, /reports) respond with 200 OK."""
    # Upload
    r_upload = client.get("/upload")
    assert r_upload.status_code == 200
    assert "data" in r_upload.json()

    # Jobs
    r_jobs = client.get("/jobs")
    assert r_jobs.status_code == 200
    assert "data" in r_jobs.json()

    # Experiments
    r_exp = client.get("/experiments/job_123")
    assert r_exp.status_code == 200
    assert r_exp.json()["data"]["job_id"] == "job_123"

    # Reports
    r_rep = client.get("/reports/job_123")
    assert r_rep.status_code == 200
    assert r_rep.json()["data"]["job_id"] == "job_123"


def test_correlation_id_header():
    """Verify X-Correlation-ID header is generated and returned."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-correlation-id" in response.headers


def test_phase_3_error_response_gate():
    """
    PHASE 3 GATE VERIFICATION:
    Verify that a deliberately-thrown AppException returns a 404 with exact ErrorResponse shape.
    """
    response = client.get("/health/error-test")
    assert response.status_code == 404
    json_data = response.json()

    # Validate against ErrorResponse Pydantic schema
    error_obj = ErrorResponse.model_validate(json_data)
    assert error_obj.error_code == "NOT_FOUND"
    assert "Phase 3 gate verification" in error_obj.message
    assert error_obj.details == {"test_key": "gate_passed"}
