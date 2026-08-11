import os
import hashlib
import uuid
import logging
from typing import Optional, Dict, Any, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.exceptions import ValidationException, NotFoundException
from backend.repositories.dataset_repository import DatasetRepository
from backend.models.dataset import DatasetModel
from backend.profiling import ProfilingEngine
from backend.schemas.semantic_profile import SemanticProfile

logger = logging.getLogger("datapilot.services.dataset_service")

# Chunk size for reading uploaded files (64 KB) — prevents OOM on large uploads
_READ_CHUNK_SIZE = 64 * 1024


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
        settings = get_settings()
        max_bytes = settings.max_upload_size_mb * 1024 * 1024

        filename = file.filename or "uploaded_dataset.csv"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".csv", ".parquet", ".pq", ".txt"]:
            raise ValidationException(f"Unsupported file extension '{ext}'. Only CSV and Parquet are supported.")

        dataset_id = f"ds_{uuid.uuid4().hex[:8]}"
        dest_dir = os.path.join(self.storage_dir, dataset_id)
        os.makedirs(dest_dir, exist_ok=True)

        file_path = os.path.join(dest_dir, filename)

        # Stream file to disk in chunks and compute SHA-256 checksum simultaneously
        # This avoids loading 100MB+ files into memory all at once
        hasher = hashlib.sha256()
        file_size = 0

        with open(file_path, "wb") as f:
            while True:
                chunk = file.file.read(_READ_CHUNK_SIZE)
                if not chunk:
                    break
                file_size += len(chunk)

                # Enforce upload size limit during streaming
                if file_size > max_bytes:
                    f.close()
                    os.remove(file_path)
                    raise ValidationException(
                        f"File exceeds maximum upload size of {settings.max_upload_size_mb} MB."
                    )

                hasher.update(chunk)
                f.write(chunk)

        checksum = hasher.hexdigest()
        logger.info(f"Dataset '{filename}' saved ({file_size} bytes, SHA256={checksum[:12]}...)")

        # Check if checksum already exists (deduplication check)
        existing = self.repository.get_by_checksum(checksum)
        if existing:
            # Clean up duplicate file
            os.remove(file_path)
            os.rmdir(dest_dir)
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
            logger.warning(f"Profiling failed for {filename}: {e}")
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

