from __future__ import annotations

from typing import Any

from app.ai.adk.knowledge_tools import enterprise_search
from app.ai.adk.runner_helpers import function_tools, run_agent_text
from app.ai.adk.session_context import bind_settings
from app.core.config import Settings
from app.schemas.enterprise import SearchResultItem
from app.services.search.enterprise_search_service import EnterpriseSearchService


def _research_agent(settings: Settings) -> Any:
    from google.adk.agents.llm_agent import Agent

    return Agent(
        name="jivana_research",
        model=settings.gemini_model,
        instruction=(
            "You are JIVANA research assistant for healthcare operations. "
            "Call enterprise_search to gather sources, then answer in markdown with "
            "inline citations to titles you retrieved. If sources are thin, say so."
        ),
        tools=function_tools(enterprise_search),
    )


async def research_synthesize_adk(
    settings: Settings,
    question: str,
) -> tuple[str, list[SearchResultItem]]:
    search_payload = EnterpriseSearchService(settings).search(question, limit=8)
    sources = [SearchResultItem(**item) for item in search_payload["results"]]

    with bind_settings(settings):
        answer = await run_agent_text(
            _research_agent(settings),
            f"Research question:\n{question}",
        )

    return answer or "No answer generated.", sources
