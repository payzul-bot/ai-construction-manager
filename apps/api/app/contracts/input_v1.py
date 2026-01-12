from __future__ import annotations

from typing import Any, Dict, Literal, Optional, Type

from pydantic import BaseModel, Field, create_model


# =========================
# Explicit contracts (what we know)
# =========================

class CreateProjectBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    meta: Dict[str, Any] = Field(default_factory=dict)


class CreateEstimateBody(BaseModel):
    project_id: str


class RecalcEstimateBody(BaseModel):
    work_id: str
    params: Dict[str, Any] = Field(default_factory=dict)
    prices: Optional[Dict[str, Any]] = None


# ===== Calc Input V1 (strict) =====

class WallPaintingParamsV1(BaseModel):
    area_m2: float = Field(..., gt=0)
    coats: int = Field(default=2, ge=1, le=6)
    base: Literal["concrete", "plaster", "drywall", "painted_wall", "wallpaper_paintable"]
    quality: Literal["econom", "comfort", "premium"]
    waste_pct: float = Field(default=10, ge=0, le=30)


class PricesV1(BaseModel):
    currency: str = "RUB"
    paint_price_per_l: float = 0
    primer_price_per_l: float = 0
    masking_tape_price_per_roll: float = 0
    film_price_per_roll: float = 0
    labor_price_per_hour: float = 0


class EstimateInputV1(BaseModel):
    work_id: Literal["wall_painting_v1"]
    params: WallPaintingParamsV1
    prices: Optional[PricesV1] = None


# =========================
# Compatibility shim for missing names
# =========================

__dynamic_cache: Dict[str, Type[BaseModel]] = {}


def __getattr__(name: str):
    if name in globals():
        return globals()[name]
    if name in __dynamic_cache:
        return __dynamic_cache[name]
    M = create_model(name, __base__=BaseModel, __module__=__name__)
    __dynamic_cache[name] = M
    return M
