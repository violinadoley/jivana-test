from app.core.config import Settings, get_settings
from app.schemas.common import HealthResponse
from fastapi import APIRouter, Depends

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version=settings.app_version,
    )
