from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)


class GenerateResponse(BaseModel):
    success: bool = True
    response: str
