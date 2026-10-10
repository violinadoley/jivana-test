from typing import Annotated

from app.core.config import Settings, get_settings
from app.core.deps import get_activity_service, require_user
from app.schemas.enterprise import EnterpriseSearchResponse, SearchResultItem
from app.services.analytics.bigquery_productivity import BigQueryProductivityService
from app.services.firebase.activity_service import ActivityService
from app.services.search.enterprise_search_service import EnterpriseSearchService
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=EnterpriseSearchResponse)
async def enterprise_search(
    q: Annotated[str, Query(min_length=1, max_length=500)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
) -> EnterpriseSearchResponse:
    payload = EnterpriseSearchService(settings).search(q, limit=limit)
    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_enterprise_search(user_id=uid, query=q)
    BigQueryProductivityService(settings).record_event(
        event_type="enterprise_search",
        user_id=uid,
        metadata={"query_length": len(q)},
    )
    return EnterpriseSearchResponse(
        query=str(payload["query"]),
        engine=str(payload["engine"]),
        vertex_search_configured=bool(payload["vertex_search_configured"]),
        results=[SearchResultItem(**item) for item in payload["results"]],
    )
