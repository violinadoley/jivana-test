from __future__ import annotations

import asyncio
import logging

from app.ai.adk.agents_workflow import run_workflow_agent_adk
from app.ai.adk.availability import use_adk_agents
from app.ai.adk.env_setup import adk_runtime_env
from app.ai.base import AIService
from app.core.config import Settings
from app.schemas.enterprise import WorkflowStep
from app.services.workflows.agent_orchestrator import run_workflow_agent

logger = logging.getLogger(__name__)


async def run_workflow_agent_dispatch(
    settings: Settings,
    ai: AIService,
    goal: str,
) -> tuple[list[WorkflowStep], str, list[str]]:
    if not use_adk_agents(settings):
        return await asyncio.to_thread(run_workflow_agent, settings, ai, goal)

    with adk_runtime_env(settings):
        try:
            return await run_workflow_agent_adk(settings, goal)
        except Exception:
            logger.exception("ADK workflow agent failed; falling back to legacy orchestration.")
            return await asyncio.to_thread(run_workflow_agent, settings, ai, goal)
