from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings


def _minimal_payload() -> dict:
    return {
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
                "calculation_profile_id": "profile_placeholder",
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
    }


def test_engine_v1_response_structure():
    client = TestClient(app)
    response = client.post(
        "/v1/engine/calculate",
        json=_minimal_payload(),
        headers={"X-API-Key": settings.api_keys.split("=", 1)[1]},
    )
    assert response.status_code == 200
    payload = response.json()

    for key in [
        "project_profile",
        "inputs",
        "works",
        "materials",
        "tools",
        "equipment",
        "stages",
        "qc",
        "risks",
        "totals",
        "meta",
    ]:
        assert key in payload

    for key in ["works", "materials", "tools", "equipment", "stages", "qc", "risks"]:
        assert isinstance(payload[key], list)

    assert payload["meta"]["engine_version"] == "engine_v1"


def test_engine_v1_deterministic_response():
    client = TestClient(app)
    headers = {"X-API-Key": settings.api_keys.split("=", 1)[1]}
    first = client.post("/v1/engine/calculate", json=_minimal_payload(), headers=headers)
    second = client.post("/v1/engine/calculate", json=_minimal_payload(), headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
