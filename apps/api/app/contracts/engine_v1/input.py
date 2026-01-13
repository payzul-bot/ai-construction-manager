from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class CustomerType(str, Enum):
    PRIVATE = "private"
    COMPANY = "company"
    GOVERNMENT = "government"


class QualityLevel(str, Enum):
    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    PREMIUM = "premium"


class ProjectProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region: str = Field(..., min_length=1)
    object_type: str = Field(..., min_length=1)
    customer_type: CustomerType
    quality_level: QualityLevel
    constraints: Dict[str, Any] = Field(default_factory=dict)


class WorkUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_id: str = Field(..., min_length=1)
    calculation_profile_id: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)


class EngineContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules_version: str = Field(..., min_length=1)
    dictionaries_version: str = Field(..., min_length=1)
    mode: Literal["draft", "final"]
    mode_flags: Dict[str, bool] = Field(default_factory=dict)
    request_metadata: Dict[str, Any] = Field(default_factory=dict)


class EngineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_profile: ProjectProfile
    work_graph: List[WorkUnit] = Field(default_factory=list)
    engine_context: EngineContext
