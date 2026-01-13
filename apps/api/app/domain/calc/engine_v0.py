from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .errors import CalcFailed, CalcInvalidInput, CalcUnknownWork
from .registry_v0 import build_registry_v0

CalculatorFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class CalcEngineV0:
    registry: dict[str, CalculatorFn]

    def calculate(self, input: dict[str, Any]) -> dict[str, Any]:
        """
        Минимальный формат input:
          {
            "work_id": "wall_painting_v1",
            "params": {...},
            "prices": {...}  # optional
          }

        Для совместимости:
          work_id можно передать как work / code.
        """
        work_id = input.get("work_id") or input.get("work") or input.get("code")
        if not work_id or not isinstance(work_id, str):
            raise CalcInvalidInput("Missing work_id/work/code in input")

        calc = self.registry.get(work_id)
        if calc is None:
            raise CalcUnknownWork(f"Unknown work_id: {work_id}")

        try:
            return calc(input)
        except CalcInvalidInput:
            raise
        except CalcUnknownWork:
            raise
        except Exception as e:
            # наружу не отдаём сырую ошибку
            raise CalcFailed(f"Calculation failed: {e.__class__.__name__}") from e


_engine_singleton: CalcEngineV0 | None = None


def get_calc_engine_v0() -> CalcEngineV0:
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = CalcEngineV0(registry=build_registry_v0())
    return _engine_singleton
