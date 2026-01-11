from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class WallPaintingParamsV1(BaseModel):
    area_m2: float = Field(..., gt=0)
    coats: int = Field(default=2, ge=1, le=6)
    base: Literal[
        "concrete",
        "plaster",
        "drywall",
        "painted_wall",
        "wallpaper_paintable",
    ]
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
