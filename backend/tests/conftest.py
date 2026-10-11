import os

os.environ.setdefault("AGENT_BACKEND", "legacy")

import pytest

from app.core.config import get_settings

get_settings.cache_clear()

from app.ai.base import AIService
from app.core.deps import get_gemini_service
from app.main import app
from fastapi.testclient import TestClient


class FakeAIService(AIService):
    def generate_text(self, prompt: str, *, institutional_context: str = "") -> str:
        del institutional_context
        return f"Echo: {prompt}"

    def generate_from_template(self, version: str, name: str, **replacements: str) -> str:
        del version, name, replacements
        return "Synthetic assistant response for tests."


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_gemini_service] = lambda: FakeAIService()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
