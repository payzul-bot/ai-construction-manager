from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.project import Project


class ProjectsRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, tenant_id: str, project_id: str, title: str, meta: dict) -> Project:
        p = Project(id=project_id, tenant_id=tenant_id, title=title, meta=meta)
        self.db.add(p)
        self.db.flush()
        return p

    def get(self, *, tenant_id: str, project_id: str) -> Project | None:
        stmt = select(Project).where(Project.tenant_id == tenant_id, Project.id == project_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self, *, tenant_id: str, limit: int = 200, offset: int = 0) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.tenant_id == tenant_id)
            .order_by(Project.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(stmt).scalars().all())

    def update(
        self,
        *,
        tenant_id: str,
        project_id: str,
        title: str | None = None,
        meta: dict | None = None,
    ) -> Project | None:
        p = self.get(tenant_id=tenant_id, project_id=project_id)
        if p is None:
            return None
        if title is not None:
            p.title = title
        if meta is not None:
            p.meta = meta
        self.db.flush()
        return p

    def delete(self, *, tenant_id: str, project_id: str) -> bool:
        p = self.get(tenant_id=tenant_id, project_id=project_id)
        if p is None:
            return False
        self.db.delete(p)
        self.db.flush()
        return True

    def delete_many(self, *, tenant_id: str, project_ids: list[str]) -> int:
        deleted = 0
        for pid in project_ids:
            if self.delete(tenant_id=tenant_id, project_id=pid):
                deleted += 1
        return deleted
