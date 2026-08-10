from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.services.dataset_service import DatasetService
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/upload", tags=["Dataset Upload"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)

async def upload_dataset(
    file: UploadFile = File(...),
    target_column: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Uploads a raw CSV/Parquet dataset file, runs automated profiling, and registers dataset.
    """
    service = DatasetService(db)
    dataset_record = service.upload_dataset(file=file, target_column=target_column)

    return SuccessResponse(
        data={
            "dataset_id": dataset_record.id,
            "filename": dataset_record.filename,
            "file_path": dataset_record.file_path,
            "checksum": dataset_record.checksum,
            "semantic_profile": dataset_record.semantic_profile,
        },
        message="Dataset uploaded and profiled successfully.",
    )


@router.get("/{dataset_id}", response_model=SuccessResponse)
def get_dataset_details(dataset_id: str, db: Session = Depends(get_db)):
    """
    Retrieves metadata and semantic profile for an uploaded dataset.
    """
    service = DatasetService(db)
    dataset_record = service.get_dataset(dataset_id)

    return SuccessResponse(
        data={
            "dataset_id": dataset_record.id,
            "filename": dataset_record.filename,
            "checksum": dataset_record.checksum,
            "semantic_profile": dataset_record.semantic_profile,
            "created_at": dataset_record.created_at.isoformat() if dataset_record.created_at else None,
        },
        message="Dataset details retrieved successfully.",
    )
