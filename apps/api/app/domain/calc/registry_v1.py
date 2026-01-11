from __future__ import annotations

from typing import Any, Callable

from .calculators.wall_painting_v1 import calc_wall_painting_v1

CalculatorFn = Callable[[dict[str, Any]], dict[str, Any]]


def build_registry_v1() -> dict[str, CalculatorFn]:
    return {
        "wall_painting_v1": calc_wall_painting_v1,
    }
