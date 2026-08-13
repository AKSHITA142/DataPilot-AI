from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.repositories.dataset_repository import DatasetRepository
from backend.services.dataset_service import DatasetService
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/datasets", tags=["Datasets"])


def _dataset_to_frontend(ds) -> dict:
    """Converts a DatasetModel row into the dictionary shape the frontend Dataset type expects."""
    return {
        "dataset_id": ds.id,
        "filename": ds.filename,
        "file_size_bytes": ds.file_size_bytes or 0,
        "row_count": ds.row_count or 0,
        "column_count": ds.column_count or 0,
        "upload_timestamp": ds.created_at.isoformat() if ds.created_at else None,
        "status": "profiled" if ds.semantic_profile else "uploaded",
        "mission_brief": getattr(ds, "mission_brief", None),
        "profile": ds.semantic_profile,
        "file_path": ds.file_path,
        "checksum": ds.checksum,
    }


@router.get("", response_model=SuccessResponse)
def list_datasets(db: Session = Depends(get_db)):
    """
    Lists all uploaded datasets.
    Frontend calls GET /api/v1/datasets.
    """
    repo = DatasetRepository(db)
    datasets = repo.list(skip=0, limit=200)
    return SuccessResponse(
        data=[_dataset_to_frontend(ds) for ds in datasets],
        message=f"Retrieved {len(datasets)} datasets.",
    )


@router.get("/{dataset_id}", response_model=SuccessResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """
    Retrieves metadata and semantic profile for an uploaded dataset.
    Frontend calls GET /api/v1/datasets/{dataset_id}.
    """
    service = DatasetService(db)
    dataset_record = service.get_dataset(dataset_id)
    return SuccessResponse(
        data=_dataset_to_frontend(dataset_record),
        message="Dataset details retrieved successfully.",
    )
