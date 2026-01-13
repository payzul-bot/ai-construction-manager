from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.v1.deps import require_api_key
from app.contracts.input_v1 import EstimateInputV1
from app.domain.calc import get_calc_engine_v0

router = APIRouter(prefix="/calculations")


@router.post("/calculate")
def calculate(
    body: EstimateInputV1,
    _=Depends(require_api_key),
) -> dict[str, Any]:
    engine = get_calc_engine_v0()
    return engine.calculate(body.model_dump())
