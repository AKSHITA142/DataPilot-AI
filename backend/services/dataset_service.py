import os
import hashlib
import uuid
from typing import Optional, Dict, Any, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.core.exceptions import ValidationException, NotFoundException
from backend.repositories.dataset_repository import DatasetRepository
from backend.models.dataset import DatasetModel
from backend.profiling import ProfilingEngine
from backend.schemas.semantic_profile import SemanticProfile


class DatasetService:
    """Service layer managing dataset uploads, storage, profiling, and repository registration."""

    def __init__(self, db: Session, storage_dir: str = "storage/data"):
        self.db = db
        self.repository = DatasetRepository(db)
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def upload_dataset(
        self,
        file: UploadFile,
        owner_id: str = "user_default",
        target_column: Optional[str] = None
    ) -> DatasetModel:
        """
        Validates, saves binary file to disk, computes checksum, runs ProfilingEngine,
        and registers dataset in database.
        """
        filename = file.filename or "uploaded_dataset.csv"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".csv", ".parquet", ".pq", ".txt"]:
            raise ValidationException(f"Unsupported file extension '{ext}'. Only CSV and Parquet are supported.")

        dataset_id = f"ds_{uuid.uuid4().hex[:8]}"
        dest_dir = os.path.join(self.storage_dir, dataset_id)
        os.makedirs(dest_dir, exist_ok=True)

        file_path = os.path.join(dest_dir, filename)

        # Read file contents and calculate SHA-256 checksum
        hasher = hashlib.sha256()
        file_bytes = file.file.read()
        file_size = len(file_bytes)
        hasher.update(file_bytes)
        checksum = hasher.hexdigest()

        # Save to disk
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Check if checksum already exists (deduplication check)
        existing = self.repository.get_by_checksum(checksum)
        if existing:
            return existing

        # Execute ProfilingEngine to generate SemanticProfile
        rows, cols = 0, 0
        try:
            profile, _ = ProfilingEngine.profile_file(file_path, target_column=target_column)
            profile_dict = profile.model_dump()
            summary = profile_dict.get("dataset_summary", {})
            rows = summary.get("rows", 0)
            cols = summary.get("columns", 0)
        except Exception as e:
            profile_dict = {"error": f"Profiling failed: {str(e)}"}

        # Create Database Record
        dataset_record = self.repository.create(
            DatasetModel(
                id=dataset_id,
                owner_id=owner_id,
                filename=filename,
                file_path=file_path,
                file_size_bytes=file_size,
                row_count=rows,
                column_count=cols,
                checksum=checksum,
                semantic_profile=profile_dict,
            )
        )
        return dataset_record

    def get_dataset(self, dataset_id: str) -> DatasetModel:
        """Retrieves dataset record by ID."""
        dataset = self.repository.get_by_id(dataset_id)
        if not dataset:
            raise NotFoundException(f"Dataset with ID '{dataset_id}' not found.")
        return dataset
