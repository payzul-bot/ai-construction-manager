from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_projects_cors_preflight_allows_local_origin():
    client = TestClient(app)
    response = client.options(
        "/v1/projects",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "x-tenant-id" in response.headers["access-control-allow-headers"].lower()


def test_missing_api_key_returns_401():
    client = TestClient(app)
    response = client.post(
        "/v1/engine/calculate",
        json={
            "project_profile": {
                "region": "ru-moscow",
                "object_type": "apartment",
                "customer_type": "private",
                "quality_level": "comfort",
                "constraints": {},
            },
            "work_graph": [
                {
                    "work_id": "paint_walls_putty",
                    "parameters": {},
                    "dependencies": [],
                }
            ],
            "engine_context": {
                "rules_version": "rules_v1",
                "dictionaries_version": "dict_v1",
                "mode": "draft",
                "mode_flags": {},
                "request_metadata": {},
            },
        },
    )

    assert response.status_code == 401
