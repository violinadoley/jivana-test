from app.api.routes import activity, ai, files, health, meddocs
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ai.router)
api_router.include_router(files.router)
api_router.include_router(activity.router)
api_router.include_router(meddocs.router)
