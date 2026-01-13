from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

_FORBIDDEN_KEY_TOKENS = {
    "price",
    "cost",
    "rate",
    "rub",
    "labor_rate",
    "consumption",
}


def _find_forbidden_keys(data: Any, found: set[str] | None = None) -> set[str]:
    if found is None:
        found = set()
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(key, str):
                lowered = key.lower()
                if any(token in lowered for token in _FORBIDDEN_KEY_TOKENS):
                    found.add(key)
            _find_forbidden_keys(value, found)
    elif isinstance(data, list):
        for item in data:
            _find_forbidden_keys(item, found)
    return found


class ParamType(str, Enum):
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    ENUM = "enum"


class ProfileParam(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., min_length=1)
    type: ParamType
    required: bool
    validation: Dict[str, Any] = Field(default_factory=dict)
    ui_hint: str | None = None
    options: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_enum_options(self) -> "ProfileParam":
        if self.type == ParamType.ENUM and not self.options:
            raise ValueError("Enum params must define options")
        if self.type != ParamType.ENUM and self.options:
            raise ValueError("Options are only allowed for enum params")
        return self


class FormulaSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    formula_id: str = Field(..., min_length=1)
    expression: str = Field(..., min_length=1)
    unit: str | None = None


class BomItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: str = Field(..., min_length=1)
    resource_type: str = Field(..., min_length=1)
    unit: str | None = None
    quantity: str | None = None


class RuleSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_type: str = Field(..., min_length=1)
    condition: str = Field(..., min_length=1)
    message: str | None = None


class OutputSections(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materials: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    qc: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class CalculationProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(..., min_length=1)
    work_id: str = Field(..., min_length=1)
    params: List[ProfileParam] = Field(default_factory=list)
    formulas: List[FormulaSpec] = Field(default_factory=list)
    bom: List[BomItem] = Field(default_factory=list)
    rules: List[RuleSpec] = Field(default_factory=list)
    qc: List[str] = Field(default_factory=list)
    outputs: OutputSections

    @model_validator(mode="before")
    @classmethod
    def _reject_forbidden_keys(cls, data: Any) -> Any:
        forbidden = sorted(_find_forbidden_keys(data))
        if forbidden:
            raise ValueError(f"Forbidden keys in profile: {', '.join(forbidden)}")
        return data

    @model_validator(mode="after")
    def _ensure_unique_params(self) -> "CalculationProfile":
        keys = [param.key for param in self.params]
        if len(keys) != len(set(keys)):
            raise ValueError("Param keys must be unique within a profile")
        return self
