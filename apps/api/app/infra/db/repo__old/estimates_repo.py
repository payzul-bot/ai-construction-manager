from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.estimate import Estimate, EstimateVersion


class EstimatesRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, tenant_id: str, estimate_id: str, project_id: str) -> Estimate:
        e = Estimate(id=estimate_id, tenant_id=tenant_id, project_id=project_id, current_version_no=0)
        self.db.add(e)
        self.db.flush()
        return e

    def get_for_update(self, *, tenant_id: str, estimate_id: str) -> Estimate | None:
        stmt = (
            select(Estimate)
            .where(Estimate.tenant_id == tenant_id, Estimate.id == estimate_id)
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def add_version(self, *, tenant_id: str, estimate_id: str, version_no: int, input: dict, result: dict) -> EstimateVersion:
        v = EstimateVersion(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
            version_no=version_no,
            input=input or {},
            result=result or {},
        )
        self.db.add(v)
        self.db.flush()
        return v

    def get_version(self, *, tenant_id: str, estimate_id: str, version_no: int) -> EstimateVersion | None:
        return (
            self.db.query(EstimateVersion)
            .filter(
                EstimateVersion.tenant_id == tenant_id,
                EstimateVersion.estimate_id == estimate_id,
                EstimateVersion.version_no == version_no,
            )
            .one_or_none()
        )
