from __future__ import annotations

from typing import Any

from app.ai.adk.runner_helpers import run_agent_text
from app.ai.prompts.loader import render_named_prompt
from app.core.config import Settings


def _meeting_agent(settings: Settings) -> Any:
    from google.adk.agents.llm_agent import Agent

    return Agent(
        name="jivana_meeting_intelligence",
        model=settings.gemini_model,
        instruction=(
            "You summarize healthcare team meetings and handoffs. "
            "Output markdown with Summary, Decisions, and Action items (owner + task). "
            "Never invent patient identifiers."
        ),
    )


async def meeting_intelligence_adk(settings: Settings, *, transcript: str) -> str:
    prompt = render_named_prompt(
        settings.ai_prompt_version,
        "meeting_intelligence",
        transcript=transcript,
    )
    return await run_agent_text(_meeting_agent(settings), prompt)
