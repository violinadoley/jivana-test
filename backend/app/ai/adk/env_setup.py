from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from app.core.config import Settings


@contextmanager
def adk_runtime_env(settings: Settings) -> Iterator[None]:
    """Ensure google-genai / ADK can authenticate like GeminiService."""
    prior: dict[str, str | None] = {}
    updates: dict[str, str] = {}

    if settings.gemini_api_key and settings.gemini_api_key.strip():
        updates["GEMINI_API_KEY"] = settings.gemini_api_key.strip()
        updates["GOOGLE_API_KEY"] = settings.gemini_api_key.strip()

    project = settings.effective_gcp_project_id
    if project:
        updates["GOOGLE_CLOUD_PROJECT"] = project
        updates["GCP_PROJECT"] = project

    for key, value in updates.items():
        prior[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        yield
    finally:
        for key, old in prior.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
