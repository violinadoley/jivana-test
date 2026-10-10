from fastapi.testclient import TestClient


def test_ai_generate_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ai/generate",
        json={"message": "Hello"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["response"] == "Echo: Hello"


def test_ai_generate_validation_error(client: TestClient) -> None:
    response = client.post("/api/v1/ai/generate", json={"message": ""})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
