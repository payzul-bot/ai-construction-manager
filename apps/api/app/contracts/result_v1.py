from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class SummaryV1(BaseModel):
    area_m2: float
    coats: int
    base: str
    quality: str
    waste_pct: float


class MaterialsV1(BaseModel):
    paint_l: float
    primer_l: float
    masking_tape_rolls: int
    film_rolls: int


class LaborV1(BaseModel):
    hours: float


class CostV1(BaseModel):
    material_cost: float
    labor_cost: float
    total_cost: float
    currency: str


class EstimateResultV1(BaseModel):
    work_id: Literal["wall_painting_v1"]
    version: int
    summary: SummaryV1
    materials: MaterialsV1
    labor: LaborV1
    cost: CostV1
