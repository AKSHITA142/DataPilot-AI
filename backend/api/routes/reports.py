from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{job_id}", response_model=SuccessResponse)
def get_report_for_job(job_id: str, db: Session = Depends(get_db)):
    """Get final report metadata for a specific research job (skeleton route)."""
    return SuccessResponse(data={"job_id": job_id, "report": None})
