from __future__ import annotations

import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.settings import settings
from app.common.context import request_id_var
from app.common.logging import setup_logging
from app.common.body_limit import BodySizeLimitMiddleware
from app.api.v1.router import router as v1_router

from app.infra.redis.client import get_redis
from app.common.rate_limit_redis import RateLimiter
from app.common.errors import AppError, raise_http


setup_logging(settings.log_level)
log = logging.getLogger("app")


app = FastAPI(
    title="AI Construction Platform API",
    version="0.1.0",
    default_response_class=ORJSONResponse,
)

# CORS
cors = settings.cors_list()
if cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# body limit
app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_body_bytes)


@app.middleware("http")
async def request_id_mw(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    token = request_id_var.set(rid)
    try:
        resp = await call_next(request)
        resp.headers["X-Request-Id"] = rid
        return resp
    finally:
        request_id_var.reset(token)


@app.middleware("http")
async def rate_limit_mw(request: Request, call_next):
    # rate limit only for /v1
    if request.url.path.startswith("/v1/"):
        tenant = request.headers.get("X-Tenant-Id") or "unknown"
        try:
            r = get_redis()
            limiter = RateLimiter(r, settings.rate_limit_prefix, settings.rate_limit_per_minute)
            limiter.check(tenant)
        except Exception:
            return ORJSONResponse({"detail": {"code": "rate_limited", "message": "Too many requests"}}, status_code=429)
    return await call_next(request)


@app.get("/health")
def health():
    return {"ok": True}


# API v1
app.include_router(v1_router)
