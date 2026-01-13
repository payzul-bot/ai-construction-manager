from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.settings import settings

app = FastAPI(title="AI Construction Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "X-Tenant-Id",
        "X-API-Key",
        "Authorization",
        "Idempotency-Key",
    ],
)

app.include_router(v1_router)


@app.get("/health")
def health():
    return {"ok": True}
