from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from app.contracts.engine_v1.input import EngineInput, WorkUnit
from app.contracts.engine_v1.result import (
    EngineMeta,
    EngineResult,
    TotalsResult,
    WorkResult,
    WorkStatus,
)


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


def _build_work_result(work_unit: WorkUnit) -> WorkResult:
    warnings: list[str] = []
    if not work_unit.parameters:
        warnings.append("parameters_missing")
    return WorkResult(
        work_id=work_unit.work_id,
        calculation_profile_id=work_unit.calculation_profile_id,
        status=WorkStatus.PLACEHOLDER,
        parameters=work_unit.parameters,
        dependencies=work_unit.dependencies,
        warnings=warnings,
    )


def calculate_v1(payload: EngineInput) -> EngineResult:
    works = [_build_work_result(work_unit) for work_unit in payload.work_graph]
    trace_id = _stable_trace_id(payload)
    created_at = _resolve_created_at(payload)
    meta = EngineMeta(
        engine_version="engine_v1",
        rules_version=payload.engine_context.rules_version,
        created_at=created_at,
        trace_id=trace_id,
        warnings=[],
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
