from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/upload", tags=["Dataset Upload"])


@router.get("", response_model=SuccessResponse)
def list_datasets(db: Session = Depends(get_db)):
    """List uploaded datasets (skeleton route)."""
    return SuccessResponse(data={"datasets": []})


@router.get("/{dataset_id}", response_model=SuccessResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get metadata for a specific uploaded dataset (skeleton route)."""
    return SuccessResponse(data={"dataset_id": dataset_id, "status": "available"})
