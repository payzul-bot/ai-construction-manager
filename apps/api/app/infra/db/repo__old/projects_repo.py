from __future__ import annotations

from sqlalchemy.orm import Session

from app.infra.db.models.project import Project


class ProjectsRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, tenant_id: str, project_id: str, title: str, meta: dict) -> Project:
        p = Project(id=project_id, tenant_id=tenant_id, title=title, meta=meta or {})
        self.db.add(p)
        self.db.flush()
        return p

    def get(self, *, tenant_id: str, project_id: str) -> Project | None:
        return (
            self.db.query(Project)
            .filter(Project.tenant_id == tenant_id, Project.id == project_id)
            .one_or_none()
        )
