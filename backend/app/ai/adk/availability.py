from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings


@lru_cache
def adk_importable() -> bool:
    try:
        import google.adk  # noqa: F401

        return True
    except ImportError:
        return False


def resolve_agent_backend(settings: Settings) -> str:
    """Return ``legacy`` or ``adk``."""
    mode = (settings.agent_backend or "auto").strip().lower()
    if mode == "legacy":
        return "legacy"
    if mode == "adk":
        return "adk" if adk_importable() else "legacy"
    # auto: prefer ADK when installed
    return "adk" if adk_importable() else "legacy"


def use_adk_agents(settings: Settings) -> bool:
    return resolve_agent_backend(settings) == "adk"
