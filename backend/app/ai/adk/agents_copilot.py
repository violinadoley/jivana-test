from __future__ import annotations

from typing import Any

from app.ai.adk.knowledge_tools import enterprise_search, retrieve_institutional_knowledge
from app.ai.adk.runner_helpers import function_tools, run_agent_text
from app.ai.adk.session_context import bind_settings
from app.core.config import Settings


def _copilot_agent(settings: Settings) -> Any:
    from google.adk.agents.llm_agent import Agent

    return Agent(
        name="jivana_copilot",
        model=settings.gemini_model,
        instruction=(
            "You are JIVANA, the healthcare enterprise copilot. "
            "Use retrieve_institutional_knowledge and enterprise_search when they help. "
            "Be concise, actionable, and cite which source you used. Never invent patient data."
        ),
        tools=function_tools(retrieve_institutional_knowledge, enterprise_search),
    )


async def copilot_turn_adk(
    settings: Settings,
    *,
    conversation_history: str,
    user_message: str,
) -> str:
    user_text = (
        f"Conversation so far:\n{conversation_history}\n\nLatest user message:\n{user_message}"
    )
    with bind_settings(settings):
        return await run_agent_text(_copilot_agent(settings), user_text)
