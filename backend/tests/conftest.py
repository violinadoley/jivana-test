import pytest
from app.ai.base import AIService
from app.core.deps import get_gemini_service
from app.main import app
from fastapi.testclient import TestClient


class FakeAIService(AIService):
    def generate_text(self, prompt: str) -> str:
        return f"Echo: {prompt}"


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_gemini_service] = lambda: FakeAIService()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
