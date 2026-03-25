from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_response_envelope() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["status"] == "ok"
    assert payload["request_id"]
    assert payload["timestamp"]


def test_analyze_rejects_empty_text() -> None:
    response = client.post(
        "/api/analyze",
        data={
            "mode": "text",
            "source_platform": "官网",
            "source_url": "",
            "raw_text": "",
        },
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_INPUT"
    assert "文本模式下请提供 JD 文本" in payload["error"]["message"]
    assert payload["error"]["suggestions"]


def test_write_rejects_empty_excel_path() -> None:
    response = client.post(
        "/api/write",
        json={
            "record": {"company": "测试公司", "job_title": "测试岗位"},
            "excel_path": "",
            "sheet_name": "",
        },
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_INPUT"
    assert "Excel 路径" in payload["error"]["message"]
