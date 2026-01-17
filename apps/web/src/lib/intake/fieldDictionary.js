export const intakeFieldDictionary = {
  intake_version: { label: "Intake version", type: "string" },
  location_profile_id: { label: "Location profile ID", type: "string" },
  "selected_place.location_id": { label: "Location ID", type: "string" },
  "selected_place.country_iso2": { label: "Country (ISO2)", type: "string" },
  "selected_place.admin_level_1": { label: "Region / Admin level 1", type: "string" },
  "selected_place.city": { label: "City", type: "string" },
  "selected_place.address_line": { label: "Address line", type: "string" },
  "selected_place.lat": { label: "Latitude", type: "number" },
  "selected_place.lon": { label: "Longitude", type: "number" },
  "selected_place.source": {
    label: "Location source",
    type: "enum",
    options: [
      { value: "manual", label: "Manual" },
      { value: "map_provider", label: "Map provider" }
    ]
  },
  work_type: {
    label: "Work type",
    type: "enum",
    options: [
      { value: "construction", label: "Construction" },
      { value: "repair", label: "Repair" }
    ]
  },
  work_for: {
    label: "Work for",
    type: "enum",
    options: [
      { value: "self", label: "Self" },
      { value: "third_party", label: "Third party" }
    ]
  },
  client_type: {
    label: "Client type",
    type: "enum",
    options: [
      { value: "private_person", label: "Private person" },
      { value: "company", label: "Company" },
      { value: "government", label: "Government" }
    ]
  },
  work_class: {
    label: "Work class",
    type: "enum",
    options: [
      { value: "economy", label: "Economy" },
      { value: "comfort", label: "Comfort" },
      { value: "business", label: "Business" },
      { value: "premium", label: "Premium" }
    ]
  },
  work_location: {
    label: "Work location",
    type: "enum",
    options: [
      { value: "inside", label: "Inside" },
      { value: "outside", label: "Outside" }
    ]
  },
  object_category: {
    label: "Object category",
    type: "enum",
    options: [
      { value: "residential", label: "Residential" },
      { value: "commercial", label: "Commercial" },
      { value: "industrial", label: "Industrial" },
      { value: "other", label: "Other" }
    ]
  },
  commercial_object_type: {
    label: "Commercial object type",
    type: "enum",
    options: [
      { value: "mall", label: "Mall" },
      { value: "standalone_commercial", label: "Standalone commercial" },
      { value: "residential_building_commercial", label: "Residential building commercial" }
    ]
  },
  mall_areas: {
    label: "Mall areas",
    type: "array_enum",
    options: [
      { value: "tenant_unit", label: "Tenant unit" },
      { value: "common_areas", label: "Common areas" }
    ]
  },
  "time_windows.work_time_start": { label: "Work time start", type: "time" },
  "time_windows.work_time_end": { label: "Work time end", type: "time" },
  "time_windows.work_blackout_intervals": { label: "Work blackout intervals", type: "array_intervals" },
  "time_windows.work_allowed_weekends": { label: "Work allowed on weekends", type: "boolean" },
  "time_windows.work_allowed_holidays": { label: "Work allowed on holidays", type: "boolean" },
  "access_logistics.vehicle_access_allowed": { label: "Vehicle access allowed", type: "boolean" },
  "access_logistics.unloading_distance_m": { label: "Unloading distance (m)", type: "number" },
  "access_logistics.freight_elevator_available": { label: "Freight elevator available", type: "boolean" },
  "access_logistics.freight_elevator_time_start": { label: "Freight elevator time start", type: "time" },
  "access_logistics.freight_elevator_time_end": { label: "Freight elevator time end", type: "time" },
  "access_logistics.freight_elevator_protection_required": {
    label: "Freight elevator protection required",
    type: "boolean"
  },
  "access_logistics.work_floor": { label: "Work floor", type: "number", numberFormat: "int" },
  "access_logistics.vehicle_max_height_m": { label: "Vehicle max height (m)", type: "number" },
  "access_logistics.vehicle_max_weight_t": { label: "Vehicle max weight (t)", type: "number" },
  "access_logistics.machinery_access_allowed": { label: "Machinery access allowed", type: "boolean" },
  "access_logistics.access_pass_required": { label: "Access pass required", type: "boolean" },
  "access_logistics.access_lead_time_days": {
    label: "Access lead time (days)",
    type: "number",
    numberFormat: "int"
  },
  "work_at_height.height_above_1_8m": { label: "Work above 1.8m", type: "boolean" },
  "work_at_height.work_height_m": { label: "Work height (m)", type: "number" },
  "work_at_height.height_above_5m": { label: "Work above 5m", type: "boolean" },
  "work_at_height.height_above_10m": { label: "Work above 10m", type: "boolean" },
  "work_at_height.height_work_conditions": {
    label: "Height work conditions",
    type: "array_enum",
    options: [
      { value: "on_facade", label: "On facade" },
      { value: "above_openings", label: "Above openings" },
      { value: "above_active_zones", label: "Above active zones" }
    ]
  },
  "work_at_height.height_access_method": {
    label: "Height access method",
    type: "enum",
    options: [
      { value: "ladder", label: "Ladder" },
      { value: "scaffold", label: "Scaffold" },
      { value: "tower", label: "Tower" },
      { value: "lift", label: "Lift" },
      { value: "crane", label: "Crane" },
      { value: "rope", label: "Rope" }
    ]
  },
  "work_at_height.height_safety_required": { label: "Height safety required", type: "boolean" },
  "noise_dust_protection.noise_restriction_enabled": {
    label: "Noise restriction enabled",
    type: "boolean"
  },
  "noise_dust_protection.noise_blackout_intervals": {
    label: "Noise blackout intervals",
    type: "array_intervals"
  },
  "noise_dust_protection.dust_control_required": { label: "Dust control required", type: "boolean" },
  "noise_dust_protection.protection_required_for": {
    label: "Protection required for",
    type: "array_enum",
    options: [
      { value: "floor", label: "Floor" },
      { value: "walls", label: "Walls" },
      { value: "windows", label: "Windows" },
      { value: "common_areas", label: "Common areas" }
    ]
  },
  "cleanup_waste.cleanup_end_of_shift_required": { label: "Cleanup end of shift required", type: "boolean" },
  "cleanup_waste.cleanup_common_areas_required": { label: "Cleanup common areas required", type: "boolean" },
  "cleanup_waste.trash_down_method": { label: "Trash down method", type: "string" },
  "cleanup_waste.trash_down_methods_additional": {
    label: "Additional trash down methods",
    type: "array_string"
  },
  "cleanup_waste.trash_origin_floor": { label: "Trash origin floor", type: "number", numberFormat: "int" },
  "cleanup_waste.trash_target_level": { label: "Trash target level", type: "number", numberFormat: "int" },
  "cleanup_waste.trash_transfer_distance_m": {
    label: "Trash transfer distance (m)",
    type: "number"
  },
  "cleanup_waste.trash_container_required": { label: "Trash container required", type: "boolean" },
  "cleanup_waste.trash_container_volume_m3": { label: "Trash container volume (m³)", type: "number" },
  "cleanup_waste.trash_container_count": { label: "Trash container count", type: "number", numberFormat: "int" },
  "cleanup_waste.trash_container_distance_m": {
    label: "Trash container distance (m)",
    type: "number"
  },
  "cleanup_waste.trash_removal_mode": { label: "Trash removal mode", type: "string" },
  "cost_responsibility.payer_materials": {
    label: "Payer (materials)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_consumables": {
    label: "Payer (consumables)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_equipment_rental": {
    label: "Payer (equipment rental)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_height_access": {
    label: "Payer (height access)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_logistics": {
    label: "Payer (logistics)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_cleanup": {
    label: "Payer (cleanup)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_trash_down": {
    label: "Payer (trash down)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_container": {
    label: "Payer (container)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  "cost_responsibility.payer_trash_removal": {
    label: "Payer (trash removal)",
    type: "enum",
    options: [
      { value: "customer", label: "Customer" },
      { value: "contractor", label: "Contractor" },
      { value: "included", label: "Included" },
      { value: "separate", label: "Separate" }
    ]
  },
  non_formalized_conditions: {
    label: "Non-formalized conditions",
    type: "text"
  }
};
