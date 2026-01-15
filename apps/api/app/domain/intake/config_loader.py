from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.contracts.intake_v1_1 import LocationProfile


_CONFIG_DIR = Path(__file__).resolve().parent / "config"
_LOCATION_PROFILE_PATH = _CONFIG_DIR / "location_profiles.json"
_RULES_PATH = _CONFIG_DIR / "rules_v1_1.json"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid JSON config: {path.name}")
    return data


def load_location_profiles() -> list[LocationProfile]:
    data = _load_json(_LOCATION_PROFILE_PATH)
    profiles_data = data.get("profiles", [])
    if not isinstance(profiles_data, list):
        raise ValueError("location_profiles.json profiles must be a list")
    return [LocationProfile.model_validate(item) for item in profiles_data]


def load_rules_config() -> dict[str, Any]:
    return _load_json(_RULES_PATH)
