from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.engine_v1.input import EngineInput, ProjectProfile


class WorkStatus(str, Enum):
    PLACEHOLDER = "PLACEHOLDER"


class WorkResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_id: str
    calculation_profile_id: str
    status: WorkStatus
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ResourceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: str
    quantity: Optional[float] = None
    unit: Optional[str] = None


class StageItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage_id: str
    name: Optional[str] = None
    order_index: Optional[int] = None


class QCItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qc_id: str
    stage_id: Optional[str] = None
    check: Optional[str] = None
    severity: Optional[str] = None


class RiskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None


class RangeValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: Optional[float] = None
    max: Optional[float] = None


class TotalsResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cost_range: Optional[RangeValue] = None
    time_range: Optional[RangeValue] = None


class EngineMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    engine_version: str
    rules_version: str
    created_at: datetime
    trace_id: str
    warnings: List[str] = Field(default_factory=list)


class EngineResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_profile: ProjectProfile
    inputs: EngineInput
    works: List[WorkResult] = Field(default_factory=list)
    materials: List[ResourceItem] = Field(default_factory=list)
    tools: List[ResourceItem] = Field(default_factory=list)
    equipment: List[ResourceItem] = Field(default_factory=list)
    stages: List[StageItem] = Field(default_factory=list)
    qc: List[QCItem] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    totals: TotalsResult
    meta: EngineMeta
