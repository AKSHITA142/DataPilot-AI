from typing import Any, Dict, Optional
from pydantic import Field
from backend.schemas.base import BaseSchema


class ValidationErrorDetail(BaseSchema):
    """Validation issue detail nested inside ErrorResponse details."""
    field: str
    issue: str


class SuccessResponse(BaseSchema):
    """Canonical envelope for every successful API response."""
    data: Any
    meta: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseSchema):
    """Canonical envelope for every failed API response."""
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
