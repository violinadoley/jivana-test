from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str | None = None
    version: str | None = None


class ReadyResponse(BaseModel):
    status: str = "ready"
    environment: str | None = None
    version: str | None = None
