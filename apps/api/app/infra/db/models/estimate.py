from __future__ import annotations

from sqlalchemy import String, Integer, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Estimate(Base):
    __tablename__ = "estimates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)

    current_version_no: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EstimateVersion(Base):
    __tablename__ = "estimate_versions"

    estimate_id: Mapped[str] = mapped_column(String(36), ForeignKey("estimates.id", ondelete="CASCADE"), primary_key=True)
    version_no: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[str] = mapped_column(String(36), index=True)

    input: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


Index("ix_estimate_versions_tenant_estimate", EstimateVersion.tenant_id, EstimateVersion.estimate_id)
