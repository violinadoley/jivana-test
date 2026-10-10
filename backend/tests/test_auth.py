import pytest
from app.ai.base import AIService
from app.core.config import get_settings
from app.core.deps import get_gemini_service
from app.main import app
from fastapi.testclient import TestClient


class FakeAIService(AIService):
    def generate_text(self, prompt: str) -> str:
        return f"Echo: {prompt}"


@pytest.fixture
def auth_required_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    app.dependency_overrides[get_gemini_service] = lambda: FakeAIService()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    get_settings.cache_clear()
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)


def test_ai_generate_requires_auth_when_enabled(auth_required_client: TestClient) -> None:
    response = auth_required_client.post(
        "/api/v1/ai/generate",
        json={"message": "Hello"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_activity_requires_auth_when_enabled(auth_required_client: TestClient) -> None:
    response = auth_required_client.get("/api/v1/activity")
    assert response.status_code == 401


def test_activity_empty_for_anonymous_when_auth_optional(client: TestClient) -> None:
    response = client.get("/api/v1/activity")
    assert response.status_code == 200
    assert response.json()["items"] == []
