import asyncio
import logging
from typing import Annotated

from app.ai.adk.agents_meetings import meeting_intelligence_adk
from app.ai.adk.availability import use_adk_agents
from app.ai.adk.env_setup import adk_runtime_env
from app.ai.base import AIService
from app.core.config import get_settings
from app.core.deps import get_activity_service, get_gemini_service, require_user
from app.core.exceptions import AIGenerationError
from app.schemas.enterprise import MeetingIntelligenceRequest, MeetingIntelligenceResponse
from app.services.analytics.bigquery_productivity import BigQueryProductivityService
from app.services.firebase.activity_service import ActivityService
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meetings", tags=["meetings"])

TIMEOUT = 90.0


@router.post("/intelligence", response_model=MeetingIntelligenceResponse)
async def meeting_intelligence(
    body: MeetingIntelligenceRequest,
    ai: Annotated[AIService, Depends(get_gemini_service)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> MeetingIntelligenceResponse:
    settings = get_settings()
    title = body.title or "Team meeting"

    try:
        if use_adk_agents(settings):
            with adk_runtime_env(settings):
                try:
                    analysis = await asyncio.wait_for(
                        meeting_intelligence_adk(settings, transcript=body.transcript),
                        timeout=TIMEOUT,
                    )
                except Exception:
                    logger.exception("ADK meeting intelligence failed; using legacy template.")
                    analysis = await asyncio.wait_for(
                        asyncio.to_thread(
                            ai.generate_from_template,
                            settings.ai_prompt_version,
                            "meeting_intelligence",
                            transcript=body.transcript,
                        ),
                        timeout=TIMEOUT,
                    )
        else:
            analysis = await asyncio.wait_for(
                asyncio.to_thread(
                    ai.generate_from_template,
                    settings.ai_prompt_version,
                    "meeting_intelligence",
                    transcript=body.transcript,
                ),
                timeout=TIMEOUT,
            )
    except TimeoutError as exc:
        raise AIGenerationError("Meeting analysis timed out.") from exc

    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_meeting_intelligence(user_id=uid, title=title)
    BigQueryProductivityService(settings).record_event(
        event_type="meeting_intelligence",
        user_id=uid,
        metadata={"title": title},
    )
    return MeetingIntelligenceResponse(title=title, analysis_markdown=analysis)
