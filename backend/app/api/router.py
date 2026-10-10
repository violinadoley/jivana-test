from app.api.routes import (
    activity,
    ai,
    analytics,
    copilot,
    enterprise_search,
    files,
    health,
    knowledge,
    meddocs,
    meetings,
    platform,
    research,
    workflows,
)
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ai.router)
api_router.include_router(files.router)
api_router.include_router(activity.router)
api_router.include_router(meddocs.router)
api_router.include_router(knowledge.router)
api_router.include_router(copilot.router)
api_router.include_router(enterprise_search.router)
api_router.include_router(meetings.router)
api_router.include_router(research.router)
api_router.include_router(workflows.router)
api_router.include_router(analytics.router)
api_router.include_router(platform.router)
