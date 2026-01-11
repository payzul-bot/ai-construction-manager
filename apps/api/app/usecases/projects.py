from __future__ import annotations

from app.common.errors import AppError
from app.common.ids import new_uuid
from app.infra.repo.projects_repo import ProjectsRepo


class ProjectsUC:
    def __init__(self, repo: ProjectsRepo):
        self.repo = repo

    def create(self, *, tenant_id: str, title: str, meta: dict) -> dict:
        pid = new_uuid()
        p = self.repo.create(tenant_id=tenant_id, project_id=pid, title=title, meta=meta or {})
        return {"id": p.id, "title": p.title, "meta": p.meta}

    def list(self, *, tenant_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
        items = self.repo.list_all(tenant_id=tenant_id, limit=limit, offset=offset)
        return [{"id": p.id, "title": p.title, "meta": p.meta} for p in items]

    def patch(self, *, tenant_id: str, project_id: str, title: str | None = None, meta: dict | None = None) -> dict:
        p = self.repo.update(tenant_id=tenant_id, project_id=project_id, title=title, meta=meta)
        if p is None:
            raise AppError(code="not_found", message="Project not found", status_code=404)
        return {"id": p.id, "title": p.title, "meta": p.meta}

    def delete(self, *, tenant_id: str, project_id: str) -> None:
        ok = self.repo.delete(tenant_id=tenant_id, project_id=project_id)
        if not ok:
            raise AppError(code="not_found", message="Project not found", status_code=404)

    def delete_many(self, *, tenant_id: str, project_ids: list[str]) -> int:
        # Идемпотентно: удаляем всё что есть, считаем реально удалённые
        return self.repo.delete_many(tenant_id=tenant_id, project_ids=project_ids)