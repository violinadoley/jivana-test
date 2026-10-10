from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ActivityType = Literal["ai_generate", "file_upload"]


class ActivityItem(BaseModel):
    id: str
    type: ActivityType
    title: str
    summary: str | None = None
    user_id: str | None = None
    created_at: datetime | None = None


class ActivityListResponse(BaseModel):
    success: bool = True
    items: list[ActivityItem] = Field(default_factory=list)
