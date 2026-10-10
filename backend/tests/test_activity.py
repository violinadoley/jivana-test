from fastapi.testclient import TestClient


def test_list_activity_empty_without_firebase(client: TestClient) -> None:
    response = client.get("/api/v1/activity")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["items"] == []
