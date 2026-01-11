from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_tenant_id
from app.common.errors import AppError, raise_http
from app.contracts.result_v1 import (
    CreateProjectBody,
    PatchProjectBody,
    DeleteManyProjectsBody,
    ProjectOut,
    OkOut,
    DeleteManyOut,
)
from app.infra.repo.projects_repo import ProjectsRepo
from app.usecases.projects import ProjectsUC

router = APIRouter()


@router.post("/projects", response_model=ProjectOut)
def create_project(
    body: CreateProjectBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = ProjectsUC(ProjectsRepo(db))
        return uc.create(tenant_id=tenant_id, title=body.title, meta=body.meta)
    except AppError as e:
        raise_http(e)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        uc = ProjectsUC(ProjectsRepo(db))
        return uc.list(tenant_id=tenant_id, limit=limit, offset=offset)
    except AppError as e:
        raise_http(e)


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def patch_project(
    project_id: str,
    body: PatchProjectBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = ProjectsUC(ProjectsRepo(db))
        return uc.patch(tenant_id=tenant_id, project_id=project_id, title=body.title, meta=body.meta)
    except AppError as e:
        raise_http(e)


@router.delete("/projects/{project_id}", response_model=OkOut)
def delete_project(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = ProjectsUC(ProjectsRepo(db))
        uc.delete(tenant_id=tenant_id, project_id=project_id)
        return {"ok": True}
    except AppError as e:
        raise_http(e)


@router.post("/projects/delete-many", response_model=DeleteManyOut)
def delete_many_projects(
    body: DeleteManyProjectsBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = ProjectsUC(ProjectsRepo(db))
        deleted = uc.delete_many(tenant_id=tenant_id, project_ids=body.project_ids)
        return {"deleted": deleted}
    except AppError as e:
        raise_http(e)
