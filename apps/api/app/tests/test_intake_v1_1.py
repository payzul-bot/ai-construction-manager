import pytest

from app.contracts.intake_v1_1 import (
    AccessLogistics,
    ClientType,
    ProjectIntakeV1_1,
    WorkClass,
    WorkFor,
    WorkLocation,
    WorkType,
)
from app.domain.intake.location_profiles import get_location_profile, resolve_location_profile
from app.domain.intake.rules_engine import evaluate_intake_rules


def _base_access_logistics() -> AccessLogistics:
    return AccessLogistics(
        vehicle_access_allowed=True,
        unloading_distance_m=5,
        vehicle_max_height_m=3.0,
        vehicle_max_weight_t=5.0,
    )


def _base_intake() -> ProjectIntakeV1_1:
    return ProjectIntakeV1_1(
        location_profile_id="global_default_v1",
        work_type=WorkType.CONSTRUCTION,
        work_for=WorkFor.THIRD_PARTY,
        client_type=ClientType.COMPANY,
        work_class=WorkClass.ECONOMY,
        work_location=WorkLocation.OUTSIDE,
        access_logistics=_base_access_logistics(),
    )


def test_resolve_location_profile_defaults_to_global() -> None:
    assert resolve_location_profile(None) == "global_default_v1"


def test_rules_engine_visibility_for_third_party_outside() -> None:
    intake = _base_intake()
    profile = get_location_profile("global_default_v1")
    assert profile is not None
    output = evaluate_intake_rules(intake, profile)
    assert "client_type" in output.visible_fields
    assert "access_logistics.vehicle_max_height_m" in output.visible_fields
    assert "cost_responsibility.payer_materials" in output.visible_fields


def test_client_type_invalid_for_self() -> None:
    with pytest.raises(ValueError, match="client_type must not be set"):
        ProjectIntakeV1_1(
            location_profile_id="global_default_v1",
            work_type=WorkType.REPAIR,
            work_for=WorkFor.SELF,
            client_type=ClientType.PRIVATE_PERSON,
            work_class=WorkClass.COMFORT,
            work_location=WorkLocation.OUTSIDE,
            access_logistics=_base_access_logistics(),
        )
