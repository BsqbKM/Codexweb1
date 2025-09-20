from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint(db_session_local) -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
