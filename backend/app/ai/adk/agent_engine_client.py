"""Vertex AI Agent Engine bridge (Phase 2).

When ``VERTEX_AGENT_ENGINE_ID`` is set, routes can delegate to a hosted runtime.
Until Agent Engine is provisioned in GCP, callers fall back to in-process ADK.
"""

from __future__ import annotations

import logging

from app.core.config import Settings

logger = logging.getLogger(__name__)


def agent_engine_available(settings: Settings) -> bool:
    return settings.vertex_agent_engine_configured


async def invoke_agent_engine_text(
    settings: Settings, *, agent_name: str, prompt: str
) -> str | None:
    """Return model text from Agent Engine, or ``None`` to use in-process ADK."""
    if not agent_engine_available(settings):
        return None
    engine_id = (settings.vertex_agent_engine_id or "").strip()
    logger.info(
        "Agent Engine id=%s configured but remote invoke not wired; using in-process ADK.",
        engine_id,
    )
    return None
