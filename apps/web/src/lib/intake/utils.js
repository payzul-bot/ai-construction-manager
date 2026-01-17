export const getValueByPath = (data, path) => {
  if (!path) return undefined;
  return path.split(".").reduce((acc, key) => (acc ? acc[key] : undefined), data);
};

export const setValueByPath = (data, path, value) => {
  const parts = path.split(".");
  const next = { ...data };
  let current = next;
  parts.forEach((part, index) => {
    if (index === parts.length - 1) {
      current[part] = value;
    } else {
      current[part] = typeof current[part] === "object" && current[part] !== null ? { ...current[part] } : {};
      current = current[part];
    }
  });
  return next;
};

export const removeValueByPath = (data, path) => {
  const parts = path.split(".");
  const next = { ...data };
  let current = next;
  parts.forEach((part, index) => {
    if (index === parts.length - 1) {
      delete current[part];
    } else if (current[part] && typeof current[part] === "object") {
      current[part] = { ...current[part] };
      current = current[part];
    }
  });
  return next;
};

export const buildDefaultIntake = () => ({
  intake_version: "v1.1",
  location_profile_id: "",
  selected_place: null,
  work_type: "",
  work_for: "",
  client_type: null,
  work_class: "",
  work_location: "",
  object_category: null,
  commercial_object_type: null,
  mall_areas: [],
  time_windows: {
    work_time_start: "",
    work_time_end: "",
    work_blackout_intervals: [],
    work_allowed_weekends: null,
    work_allowed_holidays: null
  },
  access_logistics: {
    vehicle_access_allowed: null,
    unloading_distance_m: "",
    freight_elevator_available: null,
    freight_elevator_time_start: "",
    freight_elevator_time_end: "",
    freight_elevator_protection_required: null,
    work_floor: "",
    vehicle_max_height_m: "",
    vehicle_max_weight_t: "",
    machinery_access_allowed: null,
    access_pass_required: null,
    access_lead_time_days: ""
  },
  work_at_height: {
    height_above_1_8m: null,
    work_height_m: "",
    height_above_5m: null,
    height_above_10m: null,
    height_work_conditions: [],
    height_access_method: "",
    height_safety_required: null
  },
  noise_dust_protection: {
    noise_restriction_enabled: null,
    noise_blackout_intervals: [],
    dust_control_required: null,
    protection_required_for: []
  },
  cleanup_waste: {
    cleanup_end_of_shift_required: null,
    cleanup_common_areas_required: null,
    trash_down_method: "",
    trash_down_methods_additional: [],
    trash_origin_floor: "",
    trash_target_level: "",
    trash_transfer_distance_m: "",
    trash_container_required: null,
    trash_container_volume_m3: "",
    trash_container_count: "",
    trash_container_distance_m: "",
    trash_removal_mode: ""
  },
  cost_responsibility: {
    payer_materials: "",
    payer_consumables: "",
    payer_equipment_rental: "",
    payer_height_access: "",
    payer_logistics: "",
    payer_cleanup: "",
    payer_trash_down: "",
    payer_container: "",
    payer_trash_removal: ""
  },
  non_formalized_conditions: ""
});

export const mergeAppliedDefaults = (intake, appliedDefaults = []) => {
  let merged = { ...intake };
  appliedDefaults.forEach((item) => {
    const current = getValueByPath(merged, item.field);
    const isEmptyArray = Array.isArray(current) && current.length === 0;
    if (current === undefined || current === null || current === "" || isEmptyArray) {
      merged = setValueByPath(merged, item.field, item.value);
    }
  });
  return merged;
};

export const sanitizeSelectedPlace = (intake) => {
  const selectedPlace = intake?.selected_place;
  if (!selectedPlace || typeof selectedPlace !== "object") {
    return { ...intake, selected_place: null };
  }
  const requiredKeys = ["location_id", "country_iso2", "city", "source"];
  const hasAnyValue = Object.values(selectedPlace).some((value) => value !== "" && value !== null);
  if (!hasAnyValue) {
    return { ...intake, selected_place: null };
  }
  const missingRequired = requiredKeys.some((key) => !selectedPlace[key]);
  if (missingRequired) {
    return intake;
  }
  return intake;
};
