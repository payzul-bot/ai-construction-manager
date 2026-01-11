from __future__ import annotations

from typing import Generator, Optional

from fastapi import Header, Request
from sqlalchemy.orm import Session

from app.common.context import tenant_id_var
from app.common.errors import AppError
from app.common.jwt_auth import JwtVerifier
from app.infra.db.session import SessionLocal
from app.settings import settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_tenant_id(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    # 1) JWT preferred
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        verifier = JwtVerifier(settings.jwt_secret, settings.jwt_issuer, settings.jwt_audience)
        try:
            claims = verifier.verify(token)
        except Exception:
            raise AppError(code="unauthorized", message="Invalid JWT", status_code=401)
        tid = claims.get("tenant_id")
        if not tid:
            raise AppError(code="unauthorized", message="tenant_id missing in JWT", status_code=401)
        tenant_id_var.set(tid)
        return tid

    # 2) API key fallback
    if x_api_key:
        m = settings.api_key_map()
        tid = m.get(x_api_key)
        if not tid:
            raise AppError(code="unauthorized", message="Invalid API key", status_code=401)
        tenant_id_var.set(tid)
        return tid

    # 3) header fallback (only if enabled)
    if settings.allow_tenant_header_fallback and x_tenant_id:
        tenant_id_var.set(x_tenant_id)
        return x_tenant_id

    raise AppError(code="unauthorized", message="Missing auth", status_code=401)
