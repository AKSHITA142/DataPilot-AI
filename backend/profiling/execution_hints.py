from typing import Optional
from pydantic import Field
from backend.schemas.base import BaseSchema


class ExecutionHints(BaseSchema):
    """Operational guidance passed to the Execution Engine for efficient dataset processing."""
    execution_mode: str = Field(default="standard", description="standard, large_dataset, or memory_constrained")
    use_lazy_loading: bool = Field(default=False, description="Whether lazy loading/scanning should be enabled")
    recommended_sampling: Optional[str] = Field(default=None, description="Recommended sampling ratio (e.g. '10%') if dataset is very large")
    parallel_workers: int = Field(default=4, description="Recommended parallel worker count")
