from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base Pydantic model with canonical configuration across all schemas."""
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        extra="ignore"
    )


class ConfidenceScoredModel(BaseSchema):
    """Base model for any schema that carries a confidence score."""
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
