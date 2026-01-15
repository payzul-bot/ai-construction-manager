from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.common.errors import AppError
from app.common.ids import new_uuid
from app.contracts.intake_v1_1 import ProjectIntakeV1_1, SelectedPlace
from app.domain.intake.location_profiles import get_location_profile, resolve_location_profile
from app.domain.intake.rules_engine import evaluate_intake_rules_payload
from app.infra.repo.projects_repo import ProjectsRepo


class IntakeUC:
    def __init__(self, repo: ProjectsRepo):
        self.repo = repo

    def _normalize_selected_place(self, payload: Optional[Dict[str, Any]]) -> Optional[SelectedPlace]:
        if not payload:
            return None
        required = {"location_id", "country_iso2", "city", "source"}
        if not required.issubset(payload.keys()):
            return None
        return SelectedPlace.model_validate(payload)

    def _normalize_intake_payload(self, intake_payload: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(intake_payload or {})
        selected_place = self._normalize_selected_place(data.get("selected_place"))
        if selected_place is not None:
            data["selected_place"] = selected_place.model_dump()
        data.setdefault("intake_version", "v1.1")
        if not data.get("location_profile_id"):
            data["location_profile_id"] = resolve_location_profile(selected_place)
        return data

    def evaluate_rules(self, intake_payload: Dict[str, Any]) -> tuple[Dict[str, Any], Any, Any]:
        normalized = self._normalize_intake_payload(intake_payload)
        profile = get_location_profile(normalized["location_profile_id"])
        if profile is None:
            raise AppError(code="not_found", message="Location profile not found", status_code=404)
        rules = evaluate_intake_rules_payload(normalized, profile)
        return normalized, profile, rules

    def list_snapshots(self, *, tenant_id: str, project_id: str) -> list[dict]:
        project = self.repo.get(tenant_id=tenant_id, project_id=project_id)
        if project is None:
            raise AppError(code="not_found", message="Project not found", status_code=404)
        meta = project.meta or {}
        snapshots = meta.get("intake_snapshots")
        if isinstance(snapshots, list):
            return snapshots
        return []

    def create_snapshot(
        self,
        *,
        tenant_id: str,
        project_id: str,
        intake_payload: Dict[str, Any],
        status: str,
    ) -> dict:
        project = self.repo.get(tenant_id=tenant_id, project_id=project_id)
        if project is None:
            raise AppError(code="not_found", message="Project not found", status_code=404)
        normalized = self._normalize_intake_payload(intake_payload)
        intake = ProjectIntakeV1_1.model_validate(normalized)
        created_at = datetime.now(timezone.utc).isoformat()
        status_value = status.value if hasattr(status, "value") else status
        snapshot = {
            "snapshot_id": new_uuid(),
            "status": status_value,
            "created_at": created_at,
            "intake": intake.model_dump(),
        }
        meta = project.meta or {}
        snapshots = meta.get("intake_snapshots")
        existing: list[dict]
        if isinstance(snapshots, list):
            existing = list(snapshots)
        else:
            existing = []
        next_meta = {**meta, "intake_snapshots": [*existing, snapshot]}
        self.repo.update(tenant_id=tenant_id, project_id=project_id, meta=next_meta)
        return snapshot
