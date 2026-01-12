from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# -------------------- Common --------------------

class OkOut(BaseModel):
    ok: bool = True


# -------------------- Projects --------------------

class ProjectOut(BaseModel):
    id: str
    title: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class ProjectsListOut(BaseModel):
    items: List[ProjectOut] = Field(default_factory=list)


class CreateProjectBody(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    meta: Dict[str, Any] = Field(default_factory=dict)


class PatchProjectBody(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    meta: Optional[Dict[str, Any]] = None


class DeleteManyProjectsBody(BaseModel):
    ids: List[str] = Field(min_length=1)


class DeleteManyOut(BaseModel):
    deleted: int = 0


# -------------------- Estimates: result models --------------------

class EstimateOut(BaseModel):
    id: str
    project_id: str
    current_version_no: int = 0
    created_at: Optional[Any] = None


class CreateEstimateBody(BaseModel):
    project_id: str


# -------------------- Calculator result (V1) --------------------

class EstimateResultSummaryV1(BaseModel):
    area_m2: float
    coats: int
    base: str
    quality: str
    waste_pct: float


class EstimateResultMaterialsV1(BaseModel):
    paint_l: float
    primer_l: float
    masking_tape_rolls: int
    film_rolls: int


class EstimateResultLaborV1(BaseModel):
    hours: float


class EstimateResultCostV1(BaseModel):
    material_cost: float
    labor_cost: float
    total_cost: float
    currency: str = "RUB"


class EstimateResultV1(BaseModel):
    work_id: str
    version: int
    summary: EstimateResultSummaryV1
    materials: EstimateResultMaterialsV1
    labor: EstimateResultLaborV1
    cost: EstimateResultCostV1


class RecalcOut(BaseModel):
    estimate_id: str
    version_no: int
    result: Dict[str, Any] = Field(default_factory=dict)


class EstimateVersionOut(BaseModel):
    estimate_id: str
    version_no: int
    input: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[Any] = None
