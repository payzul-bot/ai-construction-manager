from __future__ import annotations

from pathlib import Path
from typing import Any

from app.domain.calc.errors import CalcFailed


def load_yaml_recipe(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise CalcFailed("Missing dependency: pyyaml") from e

    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise CalcFailed("Invalid recipe format: root must be a mapping")
        return data
    except CalcFailed:
        raise
    except Exception as e:
        raise CalcFailed(f"Failed to load recipe: {path.name}") from e
