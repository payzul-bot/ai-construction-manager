const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "demo";

const headers = {
  "Content-Type": "application/json",
  "X-Tenant-Id": TENANT_ID
};

const request = async (path, payload) => {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload)
  });
  const bodyText = await response.text();
  const body = bodyText ? JSON.parse(bodyText) : null;
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${bodyText}`);
  }
  return body;
};

const baseIntake = {
  intake_version: "v1.1",
  location_profile_id: "global_default_v1",
  work_type: "repair",
  work_for: "self",
  work_class: "economy",
  work_location: "inside",
  access_logistics: {
    vehicle_access_allowed: true,
    unloading_distance_m: 5,
    freight_elevator_available: true,
    freight_elevator_time_start: "08:00",
    freight_elevator_time_end: "18:00",
    freight_elevator_protection_required: false,
    work_floor: 3,
    vehicle_max_height_m: 3,
    vehicle_max_weight_t: 5
  }
};

const scenarios = [
  {
    name: "Residential repair, self, inside",
    intake: {
      ...baseIntake,
      work_for: "self",
      work_location: "inside",
      object_category: "residential"
    },
    expectedVisible: ["object_category", "access_logistics.freight_elevator_available"],
    expectedHidden: ["client_type", "work_at_height.height_above_1_8m"]
  },
  {
    name: "Commercial in residential building, third_party",
    intake: {
      ...baseIntake,
      work_for: "third_party",
      client_type: "company",
      object_category: "commercial",
      commercial_object_type: "residential_building_commercial"
    },
    expectedVisible: ["client_type", "commercial_object_type", "access_logistics.access_pass_required"]
  },
  {
    name: "Mall tenant + common areas",
    intake: {
      ...baseIntake,
      work_for: "third_party",
      client_type: "company",
      object_category: "commercial",
      commercial_object_type: "mall",
      mall_areas: ["tenant_unit", "common_areas"]
    },
    expectedVisible: ["mall_areas"]
  },
  {
    name: "Outside works with logistics fields",
    intake: {
      ...baseIntake,
      work_location: "outside",
      access_logistics: {
        vehicle_access_allowed: true,
        unloading_distance_m: 10,
        vehicle_max_height_m: 4,
        vehicle_max_weight_t: 8
      }
    },
    expectedVisible: ["access_logistics.vehicle_max_height_m", "access_logistics.vehicle_max_weight_t"]
  },
  {
    name: "Industrial inside with height trigger",
    intake: {
      ...baseIntake,
      object_category: "industrial",
      work_location: "inside"
    },
    expectedVisible: ["work_at_height.height_above_1_8m"]
  }
];

const run = async () => {
  console.log(`Running intake rules QA against ${API_BASE}`);
  for (const scenario of scenarios) {
    const result = await request("/v1/intake/rules/evaluate", { intake: scenario.intake });
    const visibleFields = new Set(result.rules.visible_fields || []);
    const missing = (scenario.expectedVisible || []).filter((field) => !visibleFields.has(field));
    const shouldBeHidden = (scenario.expectedHidden || []).filter((field) => visibleFields.has(field));
    if (missing.length || shouldBeHidden.length) {
      console.error(`Scenario failed: ${scenario.name}`);
      if (missing.length) {
        console.error(`  Missing visible fields: ${missing.join(", ")}`);
      }
      if (shouldBeHidden.length) {
        console.error(`  Unexpected visible fields: ${shouldBeHidden.join(", ")}`);
      }
      process.exit(1);
    } else {
      console.log(`✓ ${scenario.name}`);
    }
  }
};

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
