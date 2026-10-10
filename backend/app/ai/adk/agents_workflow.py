from __future__ import annotations

from typing import Any

from app.ai.adk.knowledge_tools import build_workflow_context
from app.ai.adk.runner_helpers import run_agent_text
from app.ai.prompts.loader import render_named_prompt
from app.core.config import Settings
from app.schemas.enterprise import WorkflowStep


def _planner_agent(settings: Settings) -> Any:
    from google.adk.agents.llm_agent import Agent

    return Agent(
        name="jivana_workflow_planner",
        model=settings.gemini_model,
        instruction=(
            "You are JIVANA, a healthcare operations workflow planner. "
            "Write clear markdown plans with numbered steps and explicit human sign-off "
            "gates for clinical work. Never invent patient identifiers."
        ),
    )


async def run_workflow_agent_adk(
    settings: Settings,
    goal: str,
) -> tuple[list[WorkflowStep], str, list[str]]:
    """ADK plan synthesis after deterministic knowledge + search steps."""
    steps, knowledge_text, search_text, tools_used = build_workflow_context(settings, goal)

    prompt = render_named_prompt(
        settings.ai_prompt_version,
        "workflow_agent",
        goal=goal,
        knowledge=knowledge_text or "None.",
        search=search_text,
    )

    plan = await run_agent_text(_planner_agent(settings), prompt)
    if not plan:
        plan = "No plan generated."

    tools_used.append("vertex_gemini")
    tools_used.append("google_adk")
    steps.append(
        WorkflowStep(
            step=3,
            tool="vertex_gemini",
            status="completed",
            output_preview=plan[:220] + ("…" if len(plan) > 220 else ""),
        )
    )
    return steps, plan, tools_used
