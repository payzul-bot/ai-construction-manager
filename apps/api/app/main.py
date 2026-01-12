from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.router import router as v1_router

app = FastAPI(title="AI Construction Platform API")

app.include_router(v1_router)


@app.get("/health")
def health():
    return {"ok": True}
