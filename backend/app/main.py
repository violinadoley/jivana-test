import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    ReadyResponse,
)
from app.services.firebase.admin import init_firebase

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    init_firebase(settings)
    logger.info("Application startup complete", extra={"environment": settings.environment})
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Backend API",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                details=exc.details or None,
            )
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid request.",
                details={"errors": exc.errors()},
            )
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        message = "An unexpected error occurred." if settings.is_production else str(exc)
        body = ErrorResponse(error=ErrorDetail(code="INTERNAL_ERROR", message=message))
        return JSONResponse(status_code=500, content=body.model_dump())

    def _health_payload() -> dict[str, str]:
        return {
            "status": "ok",
            "environment": settings.environment,
            "version": settings.app_version,
        }

    @app.get("/", tags=["health"], response_model=None)
    def root(request: Request) -> HTMLResponse | dict[str, str]:
        """Browsers get a single named link; API clients get JSON."""
        if "text/html" in request.headers.get("accept", ""):
            return HTMLResponse(
                """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Backend API</title>
</head>
<body style="font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5;">
  <p><a href="/docs">Backend API (Swagger UI)</a></p>
</body>
</html>"""
            )
        return {
            "service": "Backend API",
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "api": "/api/v1",
        }

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    def root_health() -> HealthResponse:
        return HealthResponse(**_health_payload())

    @app.get("/ready", response_model=ReadyResponse, tags=["health"])
    def readiness() -> ReadyResponse:
        return ReadyResponse(
            status="ready",
            environment=settings.environment,
            version=settings.app_version,
        )

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
