from pydantic import BaseModel, Field


class PlaceholderStructuredResponse(BaseModel):
    """Generic structured output placeholder; med rec uses schemas in app/schemas/meddocs.py."""

    summary: str = Field(..., description="Short summary of the response.")
