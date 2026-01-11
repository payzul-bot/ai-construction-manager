from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_tenant_id
from app.common.errors import AppError, raise_http
from app.infra.repo.estimates_repo import EstimatesRepo
from app.infra.repo.projects_repo import ProjectsRepo
from app.usecases.estimates import EstimatesUC
from app.contracts.result_v1 import CreateEstimateBody, EstimateOut, RecalcOut
from app.contracts.input_v1 import RecalcBody

from app.infra.redis.client import get_redis
from app.infra.redis.idempotency import IdempotencyStore
from app.settings import settings

router = APIRouter()


# -------------------- Create estimate --------------------

@router.post("/estimates", response_model=EstimateOut)
def create_estimate(
    body: CreateEstimateBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = EstimatesUC(ProjectsRepo(db), EstimatesRepo(db))
        return uc.create(tenant_id=tenant_id, project_id=body.project_id)
    except AppError as e:
        raise_http(e)


# -------------------- List estimates --------------------

@router.get("/estimates", response_model=list[EstimateOut])
def list_estimates(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    project_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        repo = EstimatesRepo(db)
        items = repo.list_all(
            tenant_id=tenant_id,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
        return [
            {
                "id": e.id,
                "project_id": e.project_id,
                "current_version_no": e.current_version_no,
            }
            for e in items
        ]
    except AppError as e:
        raise_http(e)


# -------------------- Recalculate --------------------

@router.post("/estimates/{estimate_id}/recalculate", response_model=RecalcOut)
def recalculate(
    estimate_id: str,
    body: RecalcBody,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    try:
        if settings.require_idempotency and not idempotency_key:
            raise AppError(
                code="idempotency_required",
                message="Idempotency-Key header required",
                status_code=400,
            )

        if idempotency_key:
            r = get_redis()
            store = IdempotencyStore(
                r,
                settings.idempotency_prefix,
                settings.idempotency_ttl_sec,
            )

            cached = store.get_response(tenant_id, idempotency_key)
            if cached:
                _, payload = cached
                return payload

            if not store.lock(tenant_id, idempotency_key):
                raise AppError(
                    code="idempotency_in_progress",
                    message="Request in progress, retry",
                    status_code=409,
                )

        uc = EstimatesUC(ProjectsRepo(db), EstimatesRepo(db))
        out = uc.recalc(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
            input=body.input.model_dump(),
        )

        if idempotency_key:
            store.set_response(tenant_id, idempotency_key, 200, out)

        return out
    except AppError as e:
        raise_http(e)


# -------------------- Get version --------------------

@router.get("/estimates/{estimate_id}/versions/{version_no}")
def get_version(
    estimate_id: str,
    version_no: int,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        uc = EstimatesUC(ProjectsRepo(db), EstimatesRepo(db))
        return uc.get_version(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
            version_no=version_no,
        )
    except AppError as e:
        raise_http(e)
