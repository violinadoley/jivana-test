import asyncio
import logging
from typing import Annotated

from app.ai.adk.agents_research import research_synthesize_adk
from app.ai.adk.availability import use_adk_agents
from app.ai.adk.env_setup import adk_runtime_env
from app.ai.base import AIService
from app.core.config import get_settings
from app.core.deps import get_activity_service, get_gemini_service, require_user
from app.core.exceptions import AIGenerationError
from app.schemas.enterprise import ResearchRequest, ResearchResponse, SearchResultItem
from app.services.analytics.bigquery_productivity import BigQueryProductivityService
from app.services.firebase.activity_service import ActivityService
from app.services.search.enterprise_search_service import EnterpriseSearchService
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])

TIMEOUT = 90.0


@router.post("/synthesize", response_model=ResearchResponse)
async def research_synthesize(
    body: ResearchRequest,
    ai: Annotated[AIService, Depends(get_gemini_service)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> ResearchResponse:
    settings = get_settings()

    try:
        if use_adk_agents(settings):
            with adk_runtime_env(settings):
                try:
                    answer, sources = await asyncio.wait_for(
                        research_synthesize_adk(settings, body.question),
                        timeout=TIMEOUT,
                    )
                except Exception:
                    logger.exception("ADK research failed; using legacy template path.")
                    search_payload = EnterpriseSearchService(settings).search(
                        body.question, limit=8
                    )
                    sources = [SearchResultItem(**item) for item in search_payload["results"]]
                    sources_text = (
                        "\n\n".join(
                            f"Title: {s.title}\nSource: {s.source}\n{s.snippet}" for s in sources
                        )
                        or "No sources retrieved."
                    )
                    answer = await asyncio.wait_for(
                        asyncio.to_thread(
                            ai.generate_from_template,
                            settings.ai_prompt_version,
                            "research",
                            question=body.question,
                            sources=sources_text,
                        ),
                        timeout=TIMEOUT,
                    )
        else:
            search_payload = EnterpriseSearchService(settings).search(body.question, limit=8)
            sources = [SearchResultItem(**item) for item in search_payload["results"]]
            sources_text = (
                "\n\n".join(f"Title: {s.title}\nSource: {s.source}\n{s.snippet}" for s in sources)
                or "No sources retrieved."
            )
            answer = await asyncio.wait_for(
                asyncio.to_thread(
                    ai.generate_from_template,
                    settings.ai_prompt_version,
                    "research",
                    question=body.question,
                    sources=sources_text,
                ),
                timeout=TIMEOUT,
            )
    except TimeoutError as exc:
        raise AIGenerationError("Research synthesis timed out.") from exc

    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_research(user_id=uid, question=body.question)
    BigQueryProductivityService(settings).record_event(
        event_type="research_synthesize",
        user_id=uid,
        metadata={"question_length": len(body.question)},
    )
    return ResearchResponse(question=body.question, answer_markdown=answer, sources=sources)
