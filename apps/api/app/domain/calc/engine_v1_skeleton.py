from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from app.contracts.engine_v1.input import EngineInput, WorkUnit
from app.contracts.engine_v1.profile import CalculationProfile
from app.contracts.engine_v1.result import (
    EngineMeta,
    EngineResult,
    TotalsResult,
    WorkResult,
    WorkStatus,
)
from app.domain.calc.profile_registry import get_profile_by_id, get_profile_by_work_id


_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _stable_trace_id(payload: EngineInput) -> str:
    data = payload.model_dump(mode="json", by_alias=True, exclude_none=False)
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _resolve_created_at(payload: EngineInput) -> datetime:
    metadata = payload.engine_context.request_metadata
    created_at = metadata.get("created_at") if isinstance(metadata, dict) else None
    if isinstance(created_at, datetime):
        return created_at
    if isinstance(created_at, str):
        try:
            return datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            return _EPOCH
    return _EPOCH


def _expected_sections(profile: CalculationProfile) -> list[str]:
    return list(profile.outputs.model_dump().keys())


def _missing_required_params(profile: CalculationProfile, work_unit: WorkUnit) -> list[str]:
    required = [param.key for param in profile.params if param.required]
    return [key for key in required if key not in work_unit.parameters]


def _resolve_profile(work_unit: WorkUnit) -> CalculationProfile | None:
    if work_unit.calculation_profile_id:
        return get_profile_by_id(work_unit.calculation_profile_id)
    return get_profile_by_work_id(work_unit.work_id)


def _build_work_result(work_unit: WorkUnit, meta_warnings: list[str]) -> WorkResult:
    warnings: list[str] = []
    profile = _resolve_profile(work_unit)
    if profile is None:
        warning = f"PROFILE_NOT_FOUND:{work_unit.work_id}"
        warnings.append(warning)
        meta_warnings.append(warning)
        return WorkResult(
            work_id=work_unit.work_id,
            calculation_profile_id=work_unit.calculation_profile_id,
            status=WorkStatus.UNIMPLEMENTED,
            required_params=[],
            provided_params=list(work_unit.parameters.keys()),
            expected_sections=[],
            parameters=work_unit.parameters,
            dependencies=work_unit.dependencies,
            warnings=warnings,
        )

    missing = _missing_required_params(profile, work_unit)
    required_params = [param.key for param in profile.params if param.required]
    provided_params = list(work_unit.parameters.keys())
    status = WorkStatus.DRAFT
    if missing:
        warning = f"MISSING_REQUIRED_PARAMS:{','.join(missing)}"
        warnings.append(warning)
        meta_warnings.append(f"MISSING_REQUIRED_PARAMS:{work_unit.work_id}:{','.join(missing)}")
        status = WorkStatus.READY_FOR_INPUT

    return WorkResult(
        work_id=work_unit.work_id,
        calculation_profile_id=profile.profile_id,
        status=status,
        required_params=required_params,
        provided_params=provided_params,
        expected_sections=_expected_sections(profile),
        parameters=work_unit.parameters,
        dependencies=work_unit.dependencies,
        warnings=warnings,
    )


def calculate_v1(payload: EngineInput) -> EngineResult:
    meta_warnings: list[str] = []
    works = [
        _build_work_result(work_unit, meta_warnings) for work_unit in payload.work_graph
    ]
    trace_id = _stable_trace_id(payload)
    created_at = _resolve_created_at(payload)
    meta = EngineMeta(
        engine_version="engine_v1",
        rules_version=payload.engine_context.rules_version,
        created_at=created_at,
        trace_id=trace_id,
        warnings=meta_warnings,
    )
    totals = TotalsResult(cost_range=None, time_range=None)
    return EngineResult(
        project_profile=payload.project_profile,
        inputs=payload,
        works=works,
        materials=[],
        tools=[],
        equipment=[],
        stages=[],
        qc=[],
        risks=[],
        totals=totals,
        meta=meta,
    )
