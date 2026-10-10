from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


async def _fake_meeting_adk(_settings, *, transcript: str) -> str:
    del transcript
    return "## Summary\nADK path used in test."


@pytest.fixture
def adk_meeting_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr("app.api.routes.meetings.use_adk_agents", lambda _s: True)
    monkeypatch.setattr(
        "app.api.routes.meetings.meeting_intelligence_adk",
        AsyncMock(side_effect=_fake_meeting_adk),
    )
    return client


def test_meeting_intelligence_prefers_adk_when_enabled(adk_meeting_client: TestClient) -> None:
    response = adk_meeting_client.post(
        "/api/v1/meetings/intelligence",
        json={"transcript": "Team agreed to pause new admissions until census drops."},
    )
    assert response.status_code == 200
    assert "ADK path used" in response.json()["analysis_markdown"]
