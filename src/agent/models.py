from pydantic import BaseModel, Field


class ImageQueryClassification(BaseModel):
    is_image_request: bool = Field(
        description="Whether the query is requesting image generation"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for the classification"
    )
    image_description: str | None = Field(
        default=None,
        description="Extracted image description if it's an image request"
    )
    rejection_reason: str | None = Field(
        default=None,
        description="Reason for rejection if not an image request"
    )