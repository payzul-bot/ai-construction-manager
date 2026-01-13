from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import ValidationError

from app.contracts.engine_v1.profile import CalculationProfile
from app.domain.calc.errors import CalcFailed
from app.domain.calc.recipes_loader import load_yaml_recipe

_PROFILE_DIR = Path(__file__).resolve().parent / "profiles"


def load_profiles() -> List[CalculationProfile]:
    profiles: List[CalculationProfile] = []
    if not _PROFILE_DIR.exists():
        return profiles

    for path in sorted(_PROFILE_DIR.glob("*.yaml")):
        data = load_yaml_recipe(path)
        try:
            profile = CalculationProfile.model_validate(data)
        except ValidationError as exc:
            raise CalcFailed(f"Invalid calculation profile: {path.name}") from exc
        profiles.append(profile)
    return profiles
