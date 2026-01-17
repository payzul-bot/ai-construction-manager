from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.intake_v1_1 import LocationProfile, RulesEngineOutput


class IntakeRulesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intake: Dict[str, Any] = Field(default_factory=dict)


class IntakeRulesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intake: Dict[str, Any]
    rules: RulesEngineOutput
    location_profile: LocationProfile


class IntakeSnapshotStatus(str, Enum):
    DRAFT = "draft"
    FINAL = "final"


class IntakeSnapshotCreateBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intake: Dict[str, Any]
    status: IntakeSnapshotStatus = IntakeSnapshotStatus.DRAFT


class IntakeSnapshotOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str
    status: IntakeSnapshotStatus
    created_at: datetime
    intake: Dict[str, Any]


class IntakeSnapshotsOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: List[IntakeSnapshotOut] = Field(default_factory=list)
