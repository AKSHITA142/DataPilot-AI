from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("/{job_id}", response_model=SuccessResponse)
def list_experiments_for_job(job_id: str, db: Session = Depends(get_db)):
    """List experiments executed for a specific research job (skeleton route)."""
    return SuccessResponse(data={"job_id": job_id, "experiments": []})
