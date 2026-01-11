from __future__ import annotations

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)

    title: Mapped[str] = mapped_column(String(255))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
