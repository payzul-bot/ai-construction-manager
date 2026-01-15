from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.contracts.intake_v1_1 import (
    AppliedDefault,
    LocationProfile,
    MallArea,
    ProjectIntakeV1_1,
    RestrictiveDefault,
    RulesEngineOutput,
)
from app.domain.intake.config_loader import load_rules_config


class RuleCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    op: str
    value: Any = None


class RuleGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    all: List["RuleExpression"] = Field(default_factory=list)
    any: List["RuleExpression"] = Field(default_factory=list)

    @model_validator(mode="after")
    def _ensure_non_empty(self) -> "RuleGroup":
        if not self.all and not self.any:
            raise ValueError("RuleGroup must include all or any conditions")
        return self


RuleExpression = RuleCondition | RuleGroup


class RuleSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    fields: List[str]
    conditions: RuleGroup


class RulesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    always_visible: List[str] = Field(default_factory=list)
    always_required: List[str] = Field(default_factory=list)
    visibility_rules: List[RuleSpec] = Field(default_factory=list)
    required_rules: List[RuleSpec] = Field(default_factory=list)


@dataclass
class RuleContext:
    data: dict[str, Any]
    provided: dict[str, Any]


def _get_by_path(data: dict[str, Any], path: str) -> Any:
    if path.startswith("intake."):
        path = path.removeprefix("intake.")
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _field_exists(context: RuleContext, path: str) -> bool:
    return _get_by_path(context.provided, path) is not None


def _eval_condition(condition: RuleCondition, context: RuleContext) -> bool:
    op = condition.op
    value = condition.value
    field_value = _get_by_path(context.data, condition.field)
    if op == "exists":
        return _field_exists(context, condition.field)
    if op == "missing":
        return not _field_exists(context, condition.field)
    if op == "eq":
        return field_value == value
    if op == "in":
        return field_value in (value or [])
    if op == "contains":
        if isinstance(field_value, list):
            return value in field_value
        if isinstance(field_value, str):
            return value in field_value
        return False
    raise ValueError(f"Unsupported operation: {op}")


def _eval_expression(expression: RuleExpression, context: RuleContext) -> bool:
    if isinstance(expression, RuleCondition):
        return _eval_condition(expression, context)
    if expression.all:
        return all(_eval_expression(item, context) for item in expression.all)
    return any(_eval_expression(item, context) for item in expression.any)


def _load_rules() -> RulesConfig:
    config = load_rules_config()
    return RulesConfig.model_validate(config)


def _collect_mall_defaults(
    mall_areas: Iterable[MallArea],
    profile: LocationProfile,
) -> list[RestrictiveDefault]:
    defaults: list[RestrictiveDefault] = []
    for area in mall_areas:
        defaults.extend(profile.mall_area_defaults.get(area, []))
    if not defaults:
        return []
    by_field: dict[str, RestrictiveDefault] = {}
    for item in defaults:
        existing = by_field.get(item.field)
        if existing is None or item.restriction_rank > existing.restriction_rank:
            by_field[item.field] = item
    return list(by_field.values())


def _build_applied_defaults(
    intake: ProjectIntakeV1_1,
    profile: LocationProfile,
) -> list[AppliedDefault]:
    applied: list[AppliedDefault] = []
    intake_data = intake.model_dump()
    for field, value in profile.default_values.items():
        if _get_by_path(intake_data, field) is None:
            applied.append(AppliedDefault(field=field, value=value, source=profile.profile_id))
    mall_defaults = _collect_mall_defaults(intake.mall_areas, profile)
    for item in mall_defaults:
        if _get_by_path(intake_data, item.field) is None:
            applied.append(
                AppliedDefault(field=item.field, value=item.value, source=f"{profile.profile_id}:mall")
            )
    return applied


def _prune_context(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {key: _prune_context(val) for key, val in value.items()}
        return {key: val for key, val in cleaned.items() if val not in (None, {}, [])}
    if isinstance(value, list):
        cleaned_list = [_prune_context(item) for item in value]
        return [item for item in cleaned_list if item not in (None, {}, [])]
    return value


def _normalize_mall_areas(raw: Iterable[Any] | None) -> list[MallArea]:
    if not raw:
        return []
    parsed: list[MallArea] = []
    for item in raw:
        try:
            parsed.append(MallArea(item))
        except ValueError:
            continue
    return parsed


def _build_applied_defaults_for_payload(
    intake_data: dict[str, Any],
    profile: LocationProfile,
) -> list[AppliedDefault]:
    applied: list[AppliedDefault] = []
    for field, value in profile.default_values.items():
        if _get_by_path(intake_data, field) is None:
            applied.append(AppliedDefault(field=field, value=value, source=profile.profile_id))
    mall_defaults = _collect_mall_defaults(_normalize_mall_areas(intake_data.get("mall_areas")), profile)
    for item in mall_defaults:
        if _get_by_path(intake_data, item.field) is None:
            applied.append(
                AppliedDefault(field=item.field, value=item.value, source=f"{profile.profile_id}:mall")
            )
    return applied


def evaluate_intake_rules(
    intake: ProjectIntakeV1_1,
    location_profile: LocationProfile,
) -> RulesEngineOutput:
    rules = _load_rules()
    intake_data = intake.model_dump()
    context_data = {
        **intake_data,
        "location_profile": location_profile.model_dump(),
    }
    context_provided = intake.model_dump(exclude_defaults=True, exclude_none=True)
    provided_context = {
        **context_provided,
        "location_profile": location_profile.model_dump(exclude_defaults=True, exclude_none=True),
    }
    context = RuleContext(data=context_data, provided=provided_context)

    visible_fields = set(rules.always_visible)
    required_fields = set(rules.always_required)
    visible_fields.update(location_profile.visible_fields)
    required_fields.update(location_profile.required_fields)

    for rule in rules.visibility_rules:
        if _eval_expression(rule.conditions, context):
            visible_fields.update(rule.fields)

    for rule in rules.required_rules:
        if _eval_expression(rule.conditions, context):
            required_fields.update(rule.fields)

    applied_defaults = _build_applied_defaults(intake, location_profile)

    return RulesEngineOutput(
        visible_fields=sorted(visible_fields),
        required_fields=sorted(required_fields),
        applied_defaults=applied_defaults,
    )


def evaluate_intake_rules_payload(
    intake_data: dict[str, Any],
    location_profile: LocationProfile,
) -> RulesEngineOutput:
    rules = _load_rules()
    context_data = {
        **(intake_data or {}),
        "location_profile": location_profile.model_dump(),
    }
    provided_context = _prune_context(
        {
            **(intake_data or {}),
            "location_profile": location_profile.model_dump(exclude_defaults=True, exclude_none=True),
        }
    )
    context = RuleContext(data=context_data, provided=provided_context)

    visible_fields = set(rules.always_visible)
    required_fields = set(rules.always_required)
    visible_fields.update(location_profile.visible_fields)
    required_fields.update(location_profile.required_fields)

    for rule in rules.visibility_rules:
        if _eval_expression(rule.conditions, context):
            visible_fields.update(rule.fields)

    for rule in rules.required_rules:
        if _eval_expression(rule.conditions, context):
            required_fields.update(rule.fields)

    applied_defaults = _build_applied_defaults_for_payload(intake_data or {}, location_profile)

    return RulesEngineOutput(
        visible_fields=sorted(visible_fields),
        required_fields=sorted(required_fields),
        applied_defaults=applied_defaults,
    )
