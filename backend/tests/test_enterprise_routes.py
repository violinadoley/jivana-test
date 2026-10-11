from fastapi.testclient import TestClient


def test_enterprise_search_returns_results(client: TestClient) -> None:
    response = client.get("/api/v1/search", params={"q": "medication reconciliation"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["results"]) >= 1


def test_research_synthesize(client: TestClient) -> None:
    response = client.post(
        "/api/v1/research/synthesize",
        json={"question": "What is the human-in-the-loop policy?"},
    )
    assert response.status_code == 200
    assert "answer_markdown" in response.json()


def test_workflow_agent_run(client: TestClient) -> None:
    response = client.post(
        "/api/v1/workflows/agent-run",
        json={"goal": "Create a discharge medication checklist for nurses."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "plan_markdown" in data
    assert "vertex_gemini" in data["tools_used"]
    assert len(data.get("steps", [])) == 3


def test_platform_capabilities(client: TestClient) -> None:
    response = client.get("/api/v1/platform/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert len(body["capabilities"]) >= 5


def test_copilot_chat(client: TestClient) -> None:
    response = client.post(
        "/api/v1/copilot/chat",
        json={"message": "What is our med rec policy?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"]
    assert data["response"]


def test_meeting_intelligence(client: TestClient) -> None:
    response = client.post(
        "/api/v1/meetings/intelligence",
        json={
            "title": "Morning huddle",
            "transcript": "Pharmacy will cover warfarin counseling. Dr. Lee owns follow-up.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Morning huddle"
    assert data["analysis_markdown"]


def test_platform_demo_readiness(client: TestClient) -> None:
    response = client.get("/api/v1/platform/demo-readiness")
    assert response.status_code == 200
    body = response.json()
    assert body["core_demo_ready"] is True
    assert body["agent_backend"] == "legacy"
    assert any(i["id"] == "gemini" for i in body["required"])
    assert any(i["id"] == "vertex_search" for i in body["optional"])


def test_platform_demo_readiness_probe(client: TestClient) -> None:
    response = client.get("/api/v1/platform/demo-readiness", params={"probe": "true"})
    assert response.status_code == 200
    body = response.json()
    corpus = next(i for i in body["required"] if i["id"] == "institutional_corpus")
    assert corpus.get("live_probe_ok") is True
