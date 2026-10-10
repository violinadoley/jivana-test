from fastapi.testclient import TestClient


def test_smart_configuration(client: TestClient) -> None:
    response = client.get("/api/v1/smart/configuration")
    assert response.status_code == 200
    body = response.json()
    assert "authorization_endpoint" in body
    assert body["smart_app_status"] == "demo_stub"
