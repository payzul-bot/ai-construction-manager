from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_tenant_id
from app.common.errors import AppError, raise_http
from app.contracts.intake_api import (
    IntakeRulesRequest,
    IntakeRulesResponse,
    IntakeSnapshotCreateBody,
    IntakeSnapshotOut,
    IntakeSnapshotsOut,
)
from app.infra.repo.projects_repo import ProjectsRepo
from app.usecases.intake import IntakeUC

router = APIRouter()


@router.post("/intake/rules/evaluate", response_model=IntakeRulesResponse)
def evaluate_intake_rules(
    body: IntakeRulesRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = IntakeUC(ProjectsRepo(db))
        normalized, profile, rules = uc.evaluate_rules(body.intake)
        return {"intake": normalized, "rules": rules, "location_profile": profile}
    except AppError as e:
        raise_http(e)


@router.get("/projects/{project_id}/intake/snapshots", response_model=IntakeSnapshotsOut)
def list_intake_snapshots(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = IntakeUC(ProjectsRepo(db))
        items = uc.list_snapshots(tenant_id=tenant_id, project_id=project_id)
        return {"items": items}
    except AppError as e:
        raise_http(e)


@router.post("/projects/{project_id}/intake/snapshots", response_model=IntakeSnapshotOut)
def create_intake_snapshot(
    project_id: str,
    body: IntakeSnapshotCreateBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = IntakeUC(ProjectsRepo(db))
        snapshot = uc.create_snapshot(
            tenant_id=tenant_id,
            project_id=project_id,
            intake_payload=body.intake,
            status=body.status,
        )
        return snapshot
    except AppError as e:
        raise_http(e)
