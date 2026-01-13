from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.deps import require_api_key
from app.contracts.engine_v1.input import EngineInput
from app.contracts.engine_v1.result import EngineResult
from app.domain.calc.engine_v1_skeleton import calculate_v1

router = APIRouter(prefix="/engine")


@router.post(
    "/calculate",
    summary="Run Engine V1 calculation",
    response_model=EngineResult,
)
def calculate_engine_v1(
    body: EngineInput,
    _=Depends(require_api_key),
) -> EngineResult:
    return calculate_v1(body)
