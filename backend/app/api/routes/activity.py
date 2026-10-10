import logging
from typing import Annotated, Any

from app.core.deps import get_activity_service, get_current_user_optional
from app.schemas.activity import ActivityItem, ActivityListResponse
from app.services.firebase.activity_service import ActivityService
from fastapi import APIRouter, Depends, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/activity", tags=["activity"])


def _user_id(user: dict[str, Any] | None) -> str | None:
    if not user:
        return None
    uid = user.get("uid")
    return str(uid) if uid else None


@router.get("", response_model=ActivityListResponse)
async def list_activity(
    activity: Annotated[ActivityService, Depends(get_activity_service)],
    user: Annotated[dict[str, Any] | None, Depends(get_current_user_optional)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ActivityListResponse:
    uid = _user_id(user)
    items: list[ActivityItem] = []
    for row in activity.list_recent(user_id=uid, limit=limit):
        created = ActivityService.parse_timestamp(row.get("created_at"))
        item_type = row.get("type")
        if item_type not in ("ai_generate", "file_upload"):
            continue
        items.append(
            ActivityItem(
                id=str(row["id"]),
                type=item_type,
                title=str(row.get("title") or "Activity"),
                summary=row.get("summary"),
                user_id=row.get("user_id"),
                created_at=created,
            )
        )
    return ActivityListResponse(items=items)
