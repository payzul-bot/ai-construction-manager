from __future__ import annotations

from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.common.errors import AppError, raise_http
from app.common.jwt_auth import JwtVerifier
from app.infra.db.session import SessionLocal
from app.settings import settings


# -------------------- DB --------------------

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- Tenant --------------------

def get_tenant_id(x_tenant_id: str = Header(default="")) -> str:
    tenant_id = (x_tenant_id or "").strip()
    if not tenant_id:
        raise_http(
            AppError(
                code="tenant_required",
                message="X-Tenant-Id header is required",
                status_code=400,
            )
        )
    return tenant_id


# -------------------- API KEY --------------------

def require_api_key(x_api_key: str = Header(default="")) -> str:
    """
    settings.api_keys format:
    "name=key,name2=key2"
    example:
    API_KEYS=devkey=11111111-1111-1111-1111-111111111111
    """
    allowed: dict[str, str] = {}

    raw = (settings.api_keys or "").strip()
    if raw:
        for part in raw.split(","):
            part = part.strip()
            if not part or "=" not in part:
                continue
            name, key = part.split("=", 1)
            allowed[name.strip()] = key.strip()

    if not x_api_key or x_api_key not in allowed.values():
        raise AppError(
            code="unauthorized",
            message="Invalid API key",
            status_code=401,
        )

    return x_api_key


# -------------------- JWT (optional) --------------------

def get_current_user(
    authorization: str | None = Header(default=None),
) -> dict:
    """
    Optional JWT auth.
    If Authorization header is not provided → returns empty dict.
    """
    if not authorization:
        return {}

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise AppError(
            code="invalid_authorization",
            message="Invalid Authorization header",
            status_code=401,
        )

    verifier = JwtVerifier(settings.jwt_secret)
    payload = verifier.verify(token)
    return payload
