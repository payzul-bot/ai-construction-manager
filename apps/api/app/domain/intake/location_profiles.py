from __future__ import annotations

from typing import Optional

from app.contracts.intake_v1_1 import LocationProfile, LocationProfileMatch, SelectedPlace
from app.domain.intake.config_loader import load_location_profiles


_GLOBAL_DEFAULT_PROFILE_ID = "global_default_v1"


def _matches_rule(rule: LocationProfileMatch, selected_place: SelectedPlace) -> bool:
    if rule.country_iso2 is not None and rule.country_iso2 != selected_place.country_iso2:
        return False
    if rule.admin_level_1 is not None and rule.admin_level_1 != selected_place.admin_level_1:
        return False
    if rule.city is not None and rule.city != selected_place.city:
        return False
    return True


def resolve_location_profile(selected_place: Optional[SelectedPlace]) -> str:
    profiles = load_location_profiles()
    if selected_place is None:
        return _GLOBAL_DEFAULT_PROFILE_ID
    for profile in profiles:
        if profile.profile_id == _GLOBAL_DEFAULT_PROFILE_ID:
            continue
        for rule in profile.match_rules:
            if _matches_rule(rule, selected_place):
                return profile.profile_id
    return _GLOBAL_DEFAULT_PROFILE_ID


def get_location_profile(profile_id: str) -> LocationProfile | None:
    profiles = load_location_profiles()
    for profile in profiles:
        if profile.profile_id == profile_id:
            return profile
    return None
