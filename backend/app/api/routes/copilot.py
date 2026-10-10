import asyncio
import logging
from typing import Annotated, Any

from app.ai.adk.agents_copilot import copilot_turn_adk
from app.ai.adk.availability import use_adk_agents
from app.ai.adk.env_setup import adk_runtime_env
from app.ai.base import AIService
from app.core.config import get_settings
from app.core.deps import get_activity_service, get_copilot_store, get_gemini_service, require_user
from app.core.exceptions import AIGenerationError, AppException
from app.schemas.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotMessage,
    CopilotSessionCreateRequest,
    CopilotSessionResponse,
)
from app.services.analytics.bigquery_productivity import BigQueryProductivityService
from app.services.copilot.session_store import CopilotSessionStore
from app.services.firebase.activity_service import ActivityService
from app.services.knowledge.institutional_knowledge import InstitutionalKnowledgeService
from app.services.search.enterprise_search_service import EnterpriseSearchService
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copilot", tags=["copilot"])

AI_TIMEOUT = 90.0


def _history_text(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for msg in messages[-12:]:
        role = msg.get("role", "user")
        content = str(msg.get("content", "")).strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(none)"


@router.post("/sessions", response_model=CopilotSessionResponse)
async def create_session(
    body: CopilotSessionCreateRequest,
    store: Annotated[CopilotSessionStore, Depends(get_copilot_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> CopilotSessionResponse:
    uid = str(user["uid"]) if user and user.get("uid") else None
    session = store.create(user_id=uid, title=body.title)
    return CopilotSessionResponse(
        session_id=str(session["session_id"]),
        title=str(session["title"]),
        messages=[],
    )


@router.post("/chat", response_model=CopilotChatResponse)
async def copilot_chat(
    body: CopilotChatRequest,
    store: Annotated[CopilotSessionStore, Depends(get_copilot_store)],
    ai: Annotated[AIService, Depends(get_gemini_service)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> CopilotChatResponse:
    uid = str(user["uid"]) if user and user.get("uid") else None
    settings = get_settings()

    if body.session_id:
        session = store.get(body.session_id)
        if not session:
            raise AppException("NOT_FOUND", "Copilot session not found.", status_code=404)
    else:
        session = store.create(user_id=uid, title=body.message[:80])

    session_id = str(session["session_id"])
    store.append_message(session_id, role="user", content=body.message)

    updated = store.get(session_id) or session
    history = _history_text(list(updated.get("messages") or []))

    try:
        if use_adk_agents(settings):
            with adk_runtime_env(settings):
                try:
                    response_text = await asyncio.wait_for(
                        copilot_turn_adk(
                            settings,
                            conversation_history=history,
                            user_message=body.message,
                        ),
                        timeout=AI_TIMEOUT,
                    )
                except Exception:
                    logger.exception("ADK copilot failed; using legacy template path.")
                    knowledge = InstitutionalKnowledgeService().format_context(body.message)
                    search_payload = EnterpriseSearchService(settings).search(body.message, limit=5)
                    search_context = (
                        "\n".join(
                            f"- {r['title']}: {r['snippet']}"
                            for r in search_payload.get("results", [])[:5]
                        )
                        or "No enterprise search hits."
                    )
                    response_text = await asyncio.wait_for(
                        asyncio.to_thread(
                            ai.generate_from_template,
                            settings.ai_prompt_version,
                            "copilot",
                            institutional_context=knowledge or "None.",
                            search_context=search_context,
                            conversation_history=history,
                            user_message=body.message,
                        ),
                        timeout=AI_TIMEOUT,
                    )
        else:
            knowledge = InstitutionalKnowledgeService().format_context(body.message)
            search_payload = EnterpriseSearchService(settings).search(body.message, limit=5)
            search_context = (
                "\n".join(
                    f"- {r['title']}: {r['snippet']}" for r in search_payload.get("results", [])[:5]
                )
                or "No enterprise search hits."
            )
            response_text = await asyncio.wait_for(
                asyncio.to_thread(
                    ai.generate_from_template,
                    settings.ai_prompt_version,
                    "copilot",
                    institutional_context=knowledge or "None.",
                    search_context=search_context,
                    conversation_history=history,
                    user_message=body.message,
                ),
                timeout=AI_TIMEOUT,
            )
    except TimeoutError as exc:
        raise AIGenerationError("Copilot request timed out.") from exc

    store.append_message(session_id, role="model", content=response_text)
    final = store.get(session_id) or updated
    messages = [
        CopilotMessage(role=str(m["role"]), content=str(m["content"]))
        for m in final.get("messages") or []
    ]

    activity.log_copilot_turn(user_id=uid, session_id=session_id)
    BigQueryProductivityService(settings).record_event(
        event_type="copilot_chat",
        user_id=uid,
        metadata={"session_id": session_id},
    )

    return CopilotChatResponse(session_id=session_id, response=response_text, messages=messages)
