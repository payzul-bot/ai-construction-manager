from __future__ import annotations

from typing import Any

from app.common.errors import AppError
from app.common.ids import new_uuid
from app.contracts.input_v1 import EstimateInputV1
from app.contracts.result_v1 import EstimateResultV1
from app.domain.calc import get_calc_engine_v1
from app.domain.calc.errors import CalcError
from app.infra.repo.estimates_repo import EstimatesRepo
from app.infra.repo.projects_repo import ProjectsRepo


class EstimatesUC:
    def __init__(self, projects_repo: ProjectsRepo, estimates_repo: EstimatesRepo):
        self.projects_repo = projects_repo
        self.estimates_repo = estimates_repo

    def create(self, *, tenant_id: str, project_id: str) -> dict[str, Any]:
        p = self.projects_repo.get(tenant_id=tenant_id, project_id=project_id)
        if p is None:
            raise AppError(code="project_not_found", message="Project not found", status_code=404)

        estimate_id = new_uuid()
        e = self.estimates_repo.create(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
            project_id=project_id,
        )

        return {
            "id": e.id,
            "project_id": e.project_id,
            "current_version_no": e.current_version_no,
        }

    def recalc(self, *, tenant_id: str, estimate_id: str, input: dict[str, Any]) -> dict[str, Any]:
        e = self.estimates_repo.get_for_update(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
        )
        if e is None:
            raise AppError(code="estimate_not_found", message="Estimate not found", status_code=404)

        new_version_no = e.current_version_no + 1

        try:
            parsed_input = EstimateInputV1.model_validate(input)
        except Exception as exc:
            raise AppError(code="invalid_input", message=str(exc), status_code=400)

        engine = get_calc_engine_v1()
        try:
            raw_result = engine.calculate(parsed_input.model_dump())
        except CalcError as ce:
            raise AppError(code=ce.code, message=ce.message, status_code=400)

        try:
            parsed_result = EstimateResultV1.model_validate(raw_result)
        except Exception as exc:
            raise AppError(code="invalid_result", message=str(exc), status_code=500)

        self.estimates_repo.add_version(
            tenant_id=tenant_id,
            estimate_id=e.id,
            version_no=new_version_no,
            input=parsed_input.model_dump(),
            result=parsed_result.model_dump(),
        )

        e.current_version_no = new_version_no

        return {
            "estimate_id": e.id,
            "version_no": new_version_no,
            "result": parsed_result.model_dump(),
        }

    def get_version(self, *, tenant_id: str, estimate_id: str, version_no: int) -> dict[str, Any]:
        v = self.estimates_repo.get_version(
            tenant_id=tenant_id,
            estimate_id=estimate_id,
            version_no=version_no,
        )
        if v is None:
            raise AppError(code="version_not_found", message="Version not found", status_code=404)

        return {
            "estimate_id": v.estimate_id,
            "version_no": v.version_no,
            "input": v.input,
            "result": v.result,
            "created_at": v.created_at,
        }
