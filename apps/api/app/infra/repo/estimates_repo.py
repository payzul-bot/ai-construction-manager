# apps/api/app/infra/repo/estimates_repo.py
from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.estimate import Estimate, EstimateVersion


class EstimatesRepo:
    """
    Production-grade repository for Estimates + EstimateVersions.

    Notes:
    - Never use method name `list` to avoid shadowing built-in `list` in module scope,
      which breaks annotations like list[...].
    - All reads are tenant-scoped.
    - get_for_update() is used by use-cases that must serialize concurrent updates.
    """

    def __init__(self, db: Session):
        self.db = db

    # -------------------- Estimates --------------------

    def create(self, *, tenant_id: str, estimate_id: str, project_id: str) -> Estimate:
        """
        Create a new Estimate row.

        Does not commit. Caller controls transaction boundaries.
        """
        e = Estimate(
            id=estimate_id,  # if your Estimate PK is `id`
            tenant_id=tenant_id,
            project_id=project_id,
            current_version_no=0,
        )
        self.db.add(e)
        self.db.flush()  # to ensure PK is materialized
        return e

    def get(self, *, tenant_id: str, estimate_id: str) -> Estimate | None:
        """
        Load estimate by id (no lock).
        """
        stmt = select(Estimate).where(
            Estimate.tenant_id == tenant_id,
            Estimate.id == estimate_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_for_update(self, *, tenant_id: str, estimate_id: str) -> Estimate | None:
        """
        Load estimate by id and lock row FOR UPDATE.
        Use this in write use-cases to safely increment version_no etc.
        """
        stmt = (
            select(Estimate)
            .where(
                Estimate.tenant_id == tenant_id,
                Estimate.id == estimate_id,
            )
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(
        self,
        *,
        tenant_id: str,
        project_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Estimate]:
        """
        List estimates for tenant, optional filter by project_id.
        Ordered by created_at DESC when available, otherwise by id DESC.
        """
        stmt = select(Estimate).where(Estimate.tenant_id == tenant_id)

        if project_id is not None:
            stmt = stmt.where(Estimate.project_id == project_id)

        # Prefer created_at if exists; fallback to id
        order_col = getattr(Estimate, "created_at", None) or Estimate.id
        stmt = stmt.order_by(order_col.desc()).limit(limit).offset(offset)

        return self.db.execute(stmt).scalars().all()

    # -------------------- Versions --------------------

    def add_version(
        self,
        *,
        tenant_id: str,
        estimate_id: str,
        version_no: int,
        input: dict,
        result: dict,
    ) -> EstimateVersion:
        """
        Append a new version row for an estimate.

        Does not commit. Caller controls transaction boundaries.

        If your EstimateVersion PK differs, adjust constructor fields accordingly.
        """
        v = EstimateVersion(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
            version_no=version_no,
            input=input,
            result=result,
        )
        self.db.add(v)
        self.db.flush()
        return v

    def get_version(
        self,
        *,
        tenant_id: str,
        estimate_id: str,
        version_no: int,
    ) -> EstimateVersion | None:
        """
        Get a single specific version.
        """
        stmt = select(EstimateVersion).where(
            EstimateVersion.tenant_id == tenant_id,
            EstimateVersion.estimate_id == estimate_id,
            EstimateVersion.version_no == version_no,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_latest_version(
        self,
        *,
        tenant_id: str,
        estimate_id: str,
    ) -> EstimateVersion | None:
        """
        Get latest version by version_no DESC.
        """
        stmt = (
            select(EstimateVersion)
            .where(
                EstimateVersion.tenant_id == tenant_id,
                EstimateVersion.estimate_id == estimate_id,
            )
            .order_by(EstimateVersion.version_no.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_versions(
        self,
        *,
        tenant_id: str,
        estimate_id: str,
        limit: int = 50,
        offset: int = 0,
        newest_first: bool = True,
    ) -> Sequence[EstimateVersion]:
        """
        List versions for an estimate with pagination.
        """
        order = EstimateVersion.version_no.desc() if newest_first else EstimateVersion.version_no.asc()
        stmt = (
            select(EstimateVersion)
            .where(
                EstimateVersion.tenant_id == tenant_id,
                EstimateVersion.estimate_id == estimate_id,
            )
            .order_by(order)
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()