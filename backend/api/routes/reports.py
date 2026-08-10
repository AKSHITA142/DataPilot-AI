from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.services.report_service import ReportService
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/reports", tags=["Final Reports"])


@router.get("/{job_id}", response_model=SuccessResponse)
def get_final_report(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the final recommendation report for a completed research job.
    """
    service = ReportService(db)
    report_record = service.get_report_by_job(job_id)

    return SuccessResponse(
        data={
            "report_id": report_record.id,
            "job_id": report_record.job_id,
            "winning_experiment_id": report_record.winning_experiment_id,
            "report_file_path": report_record.report_file_path,
            "summary": report_record.summary,
            "created_at": report_record.created_at.isoformat() if report_record.created_at else None,
        },
        message="Final research report retrieved successfully.",
    )
