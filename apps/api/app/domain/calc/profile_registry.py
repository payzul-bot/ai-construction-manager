from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.contracts.engine_v1.profile import CalculationProfile
from app.domain.calc.errors import CalcFailed
from app.domain.calc.profile_loader import load_profiles


@dataclass(frozen=True)
class ProfileRegistry:
    profiles_by_id: Dict[str, CalculationProfile]
    profiles_by_work_id: Dict[str, CalculationProfile]

    def get_profile_by_id(self, profile_id: str) -> Optional[CalculationProfile]:
        return self.profiles_by_id.get(profile_id)

    def get_profile_by_work_id(self, work_id: str) -> Optional[CalculationProfile]:
        return self.profiles_by_work_id.get(work_id)

    def list_profiles(self) -> List[CalculationProfile]:
        return list(self.profiles_by_id.values())


def _build_registry(profiles: List[CalculationProfile]) -> ProfileRegistry:
    profiles_by_id: Dict[str, CalculationProfile] = {}
    profiles_by_work_id: Dict[str, CalculationProfile] = {}
    for profile in profiles:
        if profile.profile_id in profiles_by_id:
            raise CalcFailed(f"Duplicate profile_id: {profile.profile_id}")
        if profile.work_id in profiles_by_work_id:
            raise CalcFailed(f"Duplicate work_id: {profile.work_id}")
        profiles_by_id[profile.profile_id] = profile
        profiles_by_work_id[profile.work_id] = profile
    return ProfileRegistry(
        profiles_by_id=profiles_by_id,
        profiles_by_work_id=profiles_by_work_id,
    )


_REGISTRY_CACHE: ProfileRegistry | None = None


def _get_registry() -> ProfileRegistry:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        profiles = load_profiles()
        _REGISTRY_CACHE = _build_registry(profiles)
    return _REGISTRY_CACHE


def get_profile_by_work_id(work_id: str) -> Optional[CalculationProfile]:
    return _get_registry().get_profile_by_work_id(work_id)


def get_profile_by_id(profile_id: str) -> Optional[CalculationProfile]:
    return _get_registry().get_profile_by_id(profile_id)


def list_profiles() -> List[CalculationProfile]:
    return _get_registry().list_profiles()
