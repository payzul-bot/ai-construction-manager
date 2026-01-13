from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes.projects import router as projects_router
from app.api.v1.routes.estimates import router as estimates_router
from app.api.v1.routes.calculations import router as calculations_router
from app.api.v1.routes.engine_v1 import router as engine_v1_router

router = APIRouter(prefix="/v1")

router.include_router(projects_router, tags=["projects"])
router.include_router(estimates_router, tags=["estimates"])
router.include_router(calculations_router, tags=["calculations"])
router.include_router(engine_v1_router, tags=["engine_v1"])
