from fastapi.testclient import TestClient


def test_create_case_rejects_invalid_transition(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/meddocs/cases",
        json={"case_label": "Test", "transition_type": "emergency"},
    )
    assert resp.status_code == 422


def test_create_admission_case(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/meddocs/cases",
        json={"case_label": "Admission — SYN-2", "transition_type": "admission"},
    )
    assert resp.status_code == 200
    assert resp.json()["transition_type"] == "admission"


def test_create_discharge_case(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/meddocs/cases",
        json={"case_label": "Discharge — SYN-1", "synthetic_mrn": "SYN-1"},
    )
    assert resp.status_code == 200
    assert resp.json()["transition_type"] == "discharge"
    assert resp.json()["case_status"] == "draft"
