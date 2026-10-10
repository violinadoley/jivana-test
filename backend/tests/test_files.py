from fastapi.testclient import TestClient


def test_file_upload_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "notes.txt"
    assert data["content_type"] == "text/plain"
    assert data["size_bytes"] == 11


def test_file_upload_invalid_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("bad.exe", b"data", "application/octet-stream")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "FILE_UPLOAD_ERROR"


def test_file_upload_oversized(client: TestClient) -> None:
    big = b"x" * (11 * 1024 * 1024)
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("big.txt", big, "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "FILE_UPLOAD_ERROR"
