from __future__ import annotations

from datetime import time
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IntakeVersion(str, Enum):
    V1_0 = "v1.0"
    V1_1 = "v1.1"


class SelectedPlaceSource(str, Enum):
    MANUAL = "manual"
    MAP_PROVIDER = "map_provider"


class SelectedPlace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: UUID
    country_iso2: str = Field(..., min_length=2, max_length=2)
    admin_level_1: Optional[str] = None
    city: str = Field(..., min_length=1)
    address_line: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    source: SelectedPlaceSource
    confidence_object_type: Optional[float] = Field(default=None, ge=0, le=1)


class WorkType(str, Enum):
    CONSTRUCTION = "construction"
    REPAIR = "repair"


class WorkFor(str, Enum):
    SELF = "self"
    THIRD_PARTY = "third_party"


class ClientType(str, Enum):
    PRIVATE_PERSON = "private_person"
    COMPANY = "company"
    GOVERNMENT = "government"


class WorkClass(str, Enum):
    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    PREMIUM = "premium"


class WorkLocation(str, Enum):
    INSIDE = "inside"
    OUTSIDE = "outside"


class ObjectCategory(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    OTHER = "other"


class CommercialObjectType(str, Enum):
    MALL = "mall"
    STANDALONE_COMMERCIAL = "standalone_commercial"
    RESIDENTIAL_BUILDING_COMMERCIAL = "residential_building_commercial"


class MallArea(str, Enum):
    TENANT_UNIT = "tenant_unit"
    COMMON_AREAS = "common_areas"


class TimeInterval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: time
    end: time

    @model_validator(mode="after")
    def _validate_interval(self) -> "TimeInterval":
        if self.end <= self.start:
            raise ValueError("Time interval end must be after start")
        return self


class TimeWindows(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_time_start: Optional[time] = None
    work_time_end: Optional[time] = None
    work_blackout_intervals: List[TimeInterval] = Field(default_factory=list)
    work_allowed_weekends: Optional[bool] = None
    work_allowed_holidays: Optional[bool] = None

    @model_validator(mode="after")
    def _validate_window(self) -> "TimeWindows":
        if self.work_time_start is not None and self.work_time_end is not None:
            if self.work_time_end <= self.work_time_start:
                raise ValueError("work_time_end must be after work_time_start")
        return self


class AccessLogistics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_access_allowed: bool
    unloading_distance_m: float = Field(..., ge=0)
    freight_elevator_available: Optional[bool] = None
    freight_elevator_time_start: Optional[time] = None
    freight_elevator_time_end: Optional[time] = None
    freight_elevator_protection_required: Optional[bool] = None
    work_floor: Optional[int] = None
    vehicle_max_height_m: Optional[float] = Field(default=None, gt=0)
    vehicle_max_weight_t: Optional[float] = Field(default=None, gt=0)
    machinery_access_allowed: Optional[bool] = None
    access_pass_required: Optional[bool] = None
    access_lead_time_days: Optional[int] = Field(default=None, ge=0)


class HeightWorkCondition(str, Enum):
    ON_FACADE = "on_facade"
    ABOVE_OPENINGS = "above_openings"
    ABOVE_ACTIVE_ZONES = "above_active_zones"


class HeightAccessMethod(str, Enum):
    LADDER = "ladder"
    SCAFFOLD = "scaffold"
    TOWER = "tower"
    LIFT = "lift"
    CRANE = "crane"
    ROPE = "rope"


class WorkAtHeight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    height_above_1_8m: Optional[bool] = None
    work_height_m: Optional[float] = Field(default=None, gt=0)
    height_above_5m: Optional[bool] = None
    height_above_10m: Optional[bool] = None
    height_work_conditions: List[HeightWorkCondition] = Field(default_factory=list)
    height_access_method: Optional[HeightAccessMethod] = None
    height_safety_required: Optional[bool] = None


class ProtectionTarget(str, Enum):
    FLOOR = "floor"
    WALLS = "walls"
    WINDOWS = "windows"
    COMMON_AREAS = "common_areas"


class NoiseDustProtection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    noise_restriction_enabled: Optional[bool] = None
    noise_blackout_intervals: List[TimeInterval] = Field(default_factory=list)
    dust_control_required: Optional[bool] = None
    protection_required_for: List[ProtectionTarget] = Field(default_factory=list)


class CleanupWaste(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cleanup_end_of_shift_required: Optional[bool] = None
    cleanup_common_areas_required: Optional[bool] = None
    trash_down_method: Optional[str] = None
    trash_down_methods_additional: List[str] = Field(default_factory=list)
    trash_origin_floor: Optional[int] = None
    trash_target_level: Optional[int] = None
    trash_transfer_distance_m: Optional[float] = Field(default=None, ge=0)
    trash_container_required: Optional[bool] = None
    trash_container_volume_m3: Optional[float] = Field(default=None, gt=0)
    trash_container_count: Optional[int] = Field(default=None, ge=0)
    trash_container_distance_m: Optional[float] = Field(default=None, ge=0)
    trash_removal_mode: Optional[str] = None


class Payer(str, Enum):
    CUSTOMER = "customer"
    CONTRACTOR = "contractor"
    INCLUDED = "included"
    SEPARATE = "separate"


class CostResponsibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payer_materials: Optional[Payer] = None
    payer_consumables: Optional[Payer] = None
    payer_equipment_rental: Optional[Payer] = None
    payer_height_access: Optional[Payer] = None
    payer_logistics: Optional[Payer] = None
    payer_cleanup: Optional[Payer] = None
    payer_trash_down: Optional[Payer] = None
    payer_container: Optional[Payer] = None
    payer_trash_removal: Optional[Payer] = None


class VisibilityFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time_windows: bool = False
    noise_dust: bool = False
    protection: bool = False


class LocationProfileMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country_iso2: Optional[str] = None
    admin_level_1: Optional[str] = None
    city: Optional[str] = None


class RestrictiveDefault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    value: Any
    restriction_rank: int = 0


class LocationProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(..., min_length=1)
    match_rules: List[LocationProfileMatch] = Field(default_factory=list)
    default_values: Dict[str, Any] = Field(default_factory=dict)
    mall_area_defaults: Dict[MallArea, List[RestrictiveDefault]] = Field(default_factory=dict)
    visibility_flags: VisibilityFlags = Field(default_factory=VisibilityFlags)
    visible_fields: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)


class AppliedDefault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    value: Any
    source: str


class RulesEngineOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visible_fields: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)
    applied_defaults: List[AppliedDefault] = Field(default_factory=list)


class ProjectIntakeV1_1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    intake_version: IntakeVersion = IntakeVersion.V1_1
    selected_place: Optional[SelectedPlace] = None
    location_profile_id: str = Field(..., min_length=1)
    work_type: WorkType
    work_for: WorkFor
    client_type: Optional[ClientType] = None
    work_class: WorkClass
    work_location: WorkLocation
    object_category: Optional[ObjectCategory] = None
    commercial_object_type: Optional[CommercialObjectType] = None
    mall_areas: List[MallArea] = Field(default_factory=list)
    time_windows: TimeWindows = Field(default_factory=TimeWindows)
    access_logistics: AccessLogistics
    work_at_height: WorkAtHeight = Field(default_factory=WorkAtHeight)
    noise_dust_protection: NoiseDustProtection = Field(default_factory=NoiseDustProtection)
    cleanup_waste: CleanupWaste = Field(default_factory=CleanupWaste)
    cost_responsibility: Optional[CostResponsibility] = None
    non_formalized_conditions: Optional[str] = None

    @model_validator(mode="after")
    def _validate_core_fields(self) -> "ProjectIntakeV1_1":
        if self.work_for == WorkFor.SELF and self.client_type is not None:
            raise ValueError("client_type must not be set when work_for=self")
        if self.work_for == WorkFor.THIRD_PARTY and self.client_type is None:
            raise ValueError("client_type must be set when work_for=third_party")
        if self.object_category != ObjectCategory.COMMERCIAL:
            if self.commercial_object_type is not None:
                raise ValueError("commercial_object_type requires object_category=commercial")
            if self.mall_areas:
                raise ValueError("mall_areas requires object_category=commercial")
        return self

    @model_validator(mode="after")
    def _validate_access_logistics(self) -> "ProjectIntakeV1_1":
        if self.work_location == WorkLocation.INSIDE:
            required = [
                self.access_logistics.freight_elevator_available,
                self.access_logistics.freight_elevator_time_start,
                self.access_logistics.freight_elevator_time_end,
                self.access_logistics.freight_elevator_protection_required,
                self.access_logistics.work_floor,
            ]
            if any(item is None for item in required):
                raise ValueError("inside work requires freight elevator and work floor fields")
        if self.work_location == WorkLocation.OUTSIDE:
            if self.access_logistics.vehicle_max_height_m is None:
                raise ValueError("outside work requires vehicle_max_height_m")
            if self.access_logistics.vehicle_max_weight_t is None:
                raise ValueError("outside work requires vehicle_max_weight_t")
        if self.object_category in {ObjectCategory.COMMERCIAL, ObjectCategory.INDUSTRIAL}:
            if self.access_logistics.access_pass_required is None:
                raise ValueError("access_pass_required is required for commercial/industrial")
            if self.access_logistics.access_lead_time_days is None:
                raise ValueError("access_lead_time_days is required for commercial/industrial")
        return self

    @model_validator(mode="after")
    def _validate_height(self) -> "ProjectIntakeV1_1":
        if self.work_at_height.height_above_1_8m:
            required = [
                self.work_at_height.work_height_m,
                self.work_at_height.height_above_5m,
                self.work_at_height.height_above_10m,
                self.work_at_height.height_access_method,
                self.work_at_height.height_safety_required,
            ]
            if any(item is None for item in required):
                raise ValueError("height details required when height_above_1_8m is true")
        else:
            if any(
                value is not None
                for value in [
                    self.work_at_height.work_height_m,
                    self.work_at_height.height_above_5m,
                    self.work_at_height.height_above_10m,
                    self.work_at_height.height_access_method,
                    self.work_at_height.height_safety_required,
                ]
            ):
                raise ValueError("height details require height_above_1_8m to be true")
        return self

    @model_validator(mode="after")
    def _validate_cost_responsibility(self) -> "ProjectIntakeV1_1":
        if self.work_for == WorkFor.SELF and self.cost_responsibility is not None:
            raise ValueError("cost_responsibility is only valid for third_party work")
        return self


class LegacyProjectIntake(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    intake_version: Optional[IntakeVersion] = None

    @model_validator(mode="after")
    def _validate_version(self) -> "LegacyProjectIntake":
        if self.intake_version not in {None, IntakeVersion.V1_0}:
            raise ValueError("legacy intakes may omit intake_version or set v1.0")
        return self

    def effective_version(self) -> IntakeVersion:
        return self.intake_version or IntakeVersion.V1_0
