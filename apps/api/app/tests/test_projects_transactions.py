from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1 import deps
from app.infra.db.base import Base
from app.infra.db.models.project import Project  # noqa: F401
from app.main import app


def _setup_client(monkeypatch) -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(deps, "SessionLocal", session_local)
    return TestClient(app)


def test_projects_crud_commits_transactions(monkeypatch):
    client = _setup_client(monkeypatch)
    headers = {"X-Tenant-Id": "demo"}

    create = client.post("/v1/projects", json={"title": "Demo"}, headers=headers)
    assert create.status_code == 200
    project_id = create.json()["id"]

    listing = client.get("/v1/projects", headers=headers)
    assert listing.status_code == 200
    ids = [item["id"] for item in listing.json()]
    assert project_id in ids

    delete = client.delete(f"/v1/projects/{project_id}", headers=headers)
    assert delete.status_code == 200

    listing_after = client.get("/v1/projects", headers=headers)
    assert listing_after.status_code == 200
    ids_after = [item["id"] for item in listing_after.json()]
    assert project_id not in ids_after
