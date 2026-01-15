export const intakeSteps = [
  {
    id: "location",
    title: "Location Selection",
    fields: [
      "location_profile_id",
      "selected_place.location_id",
      "selected_place.country_iso2",
      "selected_place.admin_level_1",
      "selected_place.city",
      "selected_place.address_line",
      "selected_place.lat",
      "selected_place.lon",
      "selected_place.source"
    ]
  },
  {
    id: "work_type",
    title: "Work Type",
    fields: ["work_type"]
  },
  {
    id: "work_for",
    title: "Work For",
    fields: ["work_for", "client_type"]
  },
  {
    id: "work_class",
    title: "Work Class",
    fields: ["work_class"]
  },
  {
    id: "work_location",
    title: "Work Location",
    fields: ["work_location"]
  },
  {
    id: "object_taxonomy",
    title: "Object Taxonomy",
    fields: ["object_category", "commercial_object_type", "mall_areas"]
  },
  {
    id: "time_windows",
    title: "Time Windows",
    fields: [
      "time_windows.work_time_start",
      "time_windows.work_time_end",
      "time_windows.work_blackout_intervals",
      "time_windows.work_allowed_weekends",
      "time_windows.work_allowed_holidays"
    ]
  },
  {
    id: "access_logistics",
    title: "Access & Logistics",
    alwaysVisible: true,
    fields: [
      "access_logistics.vehicle_access_allowed",
      "access_logistics.unloading_distance_m",
      "access_logistics.freight_elevator_available",
      "access_logistics.freight_elevator_time_start",
      "access_logistics.freight_elevator_time_end",
      "access_logistics.freight_elevator_protection_required",
      "access_logistics.work_floor",
      "access_logistics.vehicle_max_height_m",
      "access_logistics.vehicle_max_weight_t",
      "access_logistics.machinery_access_allowed",
      "access_logistics.access_pass_required",
      "access_logistics.access_lead_time_days"
    ]
  },
  {
    id: "work_at_height",
    title: "Work at Height",
    fields: [
      "work_at_height.height_above_1_8m",
      "work_at_height.work_height_m",
      "work_at_height.height_above_5m",
      "work_at_height.height_above_10m",
      "work_at_height.height_work_conditions",
      "work_at_height.height_access_method",
      "work_at_height.height_safety_required"
    ]
  },
  {
    id: "noise_dust",
    title: "Noise & Dust",
    fields: [
      "noise_dust_protection.noise_restriction_enabled",
      "noise_dust_protection.noise_blackout_intervals",
      "noise_dust_protection.dust_control_required"
    ]
  },
  {
    id: "protection",
    title: "Protection",
    fields: ["noise_dust_protection.protection_required_for"]
  },
  {
    id: "cleanup_waste",
    title: "Cleanup & Waste",
    fields: [
      "cleanup_waste.cleanup_end_of_shift_required",
      "cleanup_waste.cleanup_common_areas_required",
      "cleanup_waste.trash_down_method",
      "cleanup_waste.trash_down_methods_additional",
      "cleanup_waste.trash_origin_floor",
      "cleanup_waste.trash_target_level",
      "cleanup_waste.trash_transfer_distance_m",
      "cleanup_waste.trash_container_required",
      "cleanup_waste.trash_container_volume_m3",
      "cleanup_waste.trash_container_count",
      "cleanup_waste.trash_container_distance_m",
      "cleanup_waste.trash_removal_mode"
    ]
  },
  {
    id: "payer_matrix",
    title: "Payer Matrix",
    fields: [
      "cost_responsibility.payer_materials",
      "cost_responsibility.payer_consumables",
      "cost_responsibility.payer_equipment_rental",
      "cost_responsibility.payer_height_access",
      "cost_responsibility.payer_logistics",
      "cost_responsibility.payer_cleanup",
      "cost_responsibility.payer_trash_down",
      "cost_responsibility.payer_container",
      "cost_responsibility.payer_trash_removal"
    ]
  },
  {
    id: "non_formalized_conditions",
    title: "Non-formalized Conditions",
    fields: ["non_formalized_conditions"]
  }
];
