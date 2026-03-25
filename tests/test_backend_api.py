from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as backend_main
from src.auth_store import AuthStore
from src.history_store import HistoryStore
from src.schemas import JobRecord


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    auth_store = AuthStore(tmp_path / "auth.db")
    history_store = HistoryStore(tmp_path / "history.db")
    test_service = backend_main.JobIntakeService(history=history_store, auth=auth_store)
    monkeypatch.setattr(backend_main, "service", test_service)
    return TestClient(backend_main.app)


def auth_headers(client: TestClient, username: str = "alice", password: str = "secret12") -> dict[str, str]:
    response = client.post("/api/auth/register", json={"username": username, "password": password})
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_response_envelope(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["status"] == "ok"
    assert payload["request_id"]
    assert payload["timestamp"]


def test_register_and_bootstrap_requires_auth(client: TestClient) -> None:
    response = client.post("/api/auth/register", json={"username": "demo", "password": "secret12"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["user"]["username"] == "demo"
    assert payload["data"]["token"]

    unauthenticated = client.get("/api/bootstrap")
    assert unauthenticated.status_code == 401

    authenticated = client.get("/api/bootstrap", headers={"Authorization": f"Bearer {payload['data']['token']}"})
    assert authenticated.status_code == 200
    assert authenticated.json()["data"]["history_count"] == 0


def test_analyze_rejects_empty_text_after_auth(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        data={
            "mode": "text",
            "source_platform": "官网",
            "source_url": "",
            "raw_text": "",
        },
        headers=auth_headers(client),
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_INPUT"
    assert "文本模式下请提供 JD 文本" in payload["error"]["message"]


def test_write_rejects_empty_excel_path_after_auth(client: TestClient) -> None:
    response = client.post(
        "/api/write",
        json={
            "record": {"company": "测试公司", "job_title": "测试岗位"},
            "excel_path": "",
            "sheet_name": "",
        },
        headers=auth_headers(client),
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_INPUT"
    assert "Excel 路径" in payload["error"]["message"]


def test_history_is_isolated_by_user(client: TestClient) -> None:
    headers_a = auth_headers(client, username="alice", password="secret12")
    headers_b = auth_headers(client, username="bob", password="secret34")

    user_a = backend_main.service.current_user(headers_a["Authorization"].split(" ", 1)[1])
    user_b = backend_main.service.current_user(headers_b["Authorization"].split(" ", 1)[1])

    backend_main.service.history.insert(
        JobRecord(company="甲公司", job_title="Agent Intern"),
        user_id=user_a["id"],
    )
    backend_main.service.history.insert(
        JobRecord(company="乙公司", job_title="Product Intern"),
        user_id=user_b["id"],
    )

    response_a = client.get("/api/history", headers=headers_a)
    response_b = client.get("/api/history", headers=headers_b)

    rows_a = response_a.json()["data"]["rows"]
    rows_b = response_b.json()["data"]["rows"]

    assert len(rows_a) == 1
    assert rows_a[0]["company"] == "甲公司"
    assert len(rows_b) == 1
    assert rows_b[0]["company"] == "乙公司"
