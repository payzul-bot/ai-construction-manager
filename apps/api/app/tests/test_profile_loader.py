from __future__ import annotations

from app.domain.calc.profile_registry import get_profile_by_work_id


def test_profile_loader_paint_walls_putty():
    profile = get_profile_by_work_id("paint_walls_putty")
    assert profile is not None
    assert profile.profile_id == "paint_walls_putty@v1"
    assert profile.work_id == "paint_walls_putty"
