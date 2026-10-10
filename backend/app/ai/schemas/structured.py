from pydantic import BaseModel, Field


class PlaceholderStructuredResponse(BaseModel):
    """TODO: Replace with domain-specific structured outputs."""

    summary: str = Field(..., description="Short summary of the response.")
