from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.deps import get_db
from app.infra.db.base import Base
from app.infra.db.models.project import Project  # noqa: F401
from app.main import app


def _setup_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def _override_get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def test_projects_tenant_header_required():
    client = _setup_client()
    try:
        response = client.get("/v1/projects")
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "tenant_required"
    finally:
        app.dependency_overrides = {}


def test_projects_tenant_header_used_for_crud_visibility():
    client = _setup_client()
    try:
        headers = {"X-Tenant-Id": "demo"}
        create = client.post("/v1/projects", json={"title": "Demo"}, headers=headers)
        assert create.status_code == 200
        project_id = create.json()["id"]

        listing = client.get("/v1/projects", headers=headers)
        assert listing.status_code == 200
        ids = [item["id"] for item in listing.json()]
        assert project_id in ids
    finally:
        app.dependency_overrides = {}
