from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.domain.calc.errors import CalcFailed, CalcInvalidInput
from app.domain.calc.recipes_loader import load_yaml_recipe

_RECIPE_PATH = Path(__file__).resolve().parents[1] / "recipes" / "wall_painting_v1.yaml"
_RECIPE_CACHE: dict[str, Any] | None = None


def _recipe() -> dict[str, Any]:
    global _RECIPE_CACHE
    if _RECIPE_CACHE is None:
        _RECIPE_CACHE = load_yaml_recipe(_RECIPE_PATH)
    return _RECIPE_CACHE


def _num(x: Any, *, name: str) -> float:
    try:
        v = float(x)
    except Exception:
        raise CalcInvalidInput(f"{name} must be a number")
    if v <= 0:
        raise CalcInvalidInput(f"{name} must be > 0")
    return v


def _int(x: Any, *, name: str) -> int:
    try:
        v = int(x)
    except Exception:
        raise CalcInvalidInput(f"{name} must be integer")
    return v


def _round_up_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return math.ceil(value / step) * step


def calc_wall_painting_v1(input: dict[str, Any]) -> dict[str, Any]:
    r = _recipe()

    params = input.get("params") if isinstance(input.get("params"), dict) else input
    defaults = r.get("defaults", {}) if isinstance(r.get("defaults"), dict) else {}
    norms = r.get("norms", {}) if isinstance(r.get("norms"), dict) else {}
    bundles = r.get("bundles", {}) if isinstance(r.get("bundles"), dict) else {}
    rounding = r.get("rounding", {}) if isinstance(r.get("rounding"), dict) else {}

    area_m2 = _num(params.get("area_m2"), name="area_m2")

    coats = _int(params.get("coats", defaults.get("coats", 2)), name="coats")
    if coats < 1 or coats > 6:
        raise CalcInvalidInput("coats must be between 1 and 6")

    base = params.get("base")
    quality = params.get("quality")
    if not isinstance(base, str):
        raise CalcInvalidInput("base must be a string")
    if not isinstance(quality, str):
        raise CalcInvalidInput("quality must be a string")

    allowed_base = set((r.get("enums", {}) or {}).get("base", []))
    allowed_quality = set((r.get("enums", {}) or {}).get("quality", []))
    if allowed_base and base not in allowed_base:
        raise CalcInvalidInput(f"base must be one of {sorted(allowed_base)}")
    if allowed_quality and quality not in allowed_quality:
        raise CalcInvalidInput(f"quality must be one of {sorted(allowed_quality)}")

    waste_pct_raw = params.get("waste_pct", defaults.get("waste_pct", 10))
    try:
        waste_pct = float(waste_pct_raw)
    except Exception:
        raise CalcInvalidInput("waste_pct must be a number")
    if waste_pct < 0 or waste_pct > 30:
        raise CalcInvalidInput("waste_pct must be between 0 and 30")

    paint_cov_map = norms.get("paint_coverage_m2_per_l_by_base", {})
    primer_cov_map = norms.get("primer_coverage_m2_per_l_by_base", {})
    labor_map = norms.get("labor_hours_per_m2_by_quality", {})

    try:
        paint_cov = float(paint_cov_map[base])
        primer_cov = float(primer_cov_map[base])
        labor_h_m2 = float(labor_map[quality])
    except Exception as e:
        raise CalcFailed("Recipe is missing required norms for given base/quality") from e

    waste_k = 1.0 + (waste_pct / 100.0)

    paint_l = (area_m2 * coats / paint_cov) * waste_k
    primer_l = (area_m2 / primer_cov) * waste_k if primer_cov > 0 else 0.0
    labor_hours = area_m2 * labor_h_m2

    liters_step = float(rounding.get("liters_step", 0.1) or 0.1)
    hours_step = float(rounding.get("hours_step", 0.1) or 0.1)

    paint_l_ceil = _round_up_step(paint_l, liters_step)
    primer_l_ceil = _round_up_step(primer_l, liters_step)
    labor_hours_ceil = _round_up_step(labor_hours, hours_step)

    tape_per_50 = int(bundles.get("masking_tape_rolls_per_50m2", 1) or 1)
    film_per_40 = int(bundles.get("film_rolls_per_40m2", 1) or 1)
    masking_tape_rolls = max(1, math.ceil(area_m2 / 50.0) * tape_per_50)
    film_rolls = max(1, math.ceil(area_m2 / 40.0) * film_per_40)

    prices = input.get("prices") if isinstance(input.get("prices"), dict) else {}
    paint_price_per_l = float(prices.get("paint_price_per_l", 0) or 0)
    primer_price_per_l = float(prices.get("primer_price_per_l", 0) or 0)
    tape_price_per_roll = float(prices.get("masking_tape_price_per_roll", 0) or 0)
    film_price_per_roll = float(prices.get("film_price_per_roll", 0) or 0)
    labor_price_per_hour = float(prices.get("labor_price_per_hour", 0) or 0)

    material_cost = (
        paint_l_ceil * paint_price_per_l
        + primer_l_ceil * primer_price_per_l
        + masking_tape_rolls * tape_price_per_roll
        + film_rolls * film_price_per_roll
    )
    labor_cost = labor_hours_ceil * labor_price_per_hour
    total_cost = material_cost + labor_cost

    return {
        "work_id": "wall_painting_v1",
        "version": int(r.get("version", 1) or 1),
        "summary": {
            "area_m2": float(area_m2),
            "coats": int(coats),
            "base": base,
            "quality": quality,
            "waste_pct": float(waste_pct),
        },
        "materials": {
            "paint_l": float(paint_l_ceil),
            "primer_l": float(primer_l_ceil),
            "masking_tape_rolls": int(masking_tape_rolls),
            "film_rolls": int(film_rolls),
        },
        "labor": {"hours": float(labor_hours_ceil)},
        "cost": {
            "material_cost": round(float(material_cost), 2),
            "labor_cost": round(float(labor_cost), 2),
            "total_cost": round(float(total_cost), 2),
            "currency": str(prices.get("currency", "RUB")),
        },
    }
