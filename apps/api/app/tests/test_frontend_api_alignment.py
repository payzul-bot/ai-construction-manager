from __future__ import annotations

import re
from pathlib import Path

from app.main import app


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _normalize_path(path: str) -> str:
    path = path.split("?", 1)[0]
    path = re.sub(r"\$\{[^}]+\}", "{}", path)
    path = re.sub(r"\{[^}]+\}", "{}", path)
    return path


def _extract_frontend_paths() -> set[str]:
    api_dir = _repo_root() / "apps" / "web" / "src" / "lib" / "api"
    paths: set[str] = set()
    for js_file in api_dir.glob("*.js"):
        text = js_file.read_text(encoding="utf-8")
        for match in re.findall(r"[\"'`](/v1[^\"'`]+)[\"'`]", text):
            paths.add(_normalize_path(match))
    return paths


def test_frontend_api_paths_exist_in_openapi() -> None:
    frontend_paths = _extract_frontend_paths()
    openapi_paths = {_normalize_path(path) for path in app.openapi()["paths"].keys()}

    missing = sorted(frontend_paths - openapi_paths)
    assert not missing, f"Missing OpenAPI paths for frontend calls: {missing}"
