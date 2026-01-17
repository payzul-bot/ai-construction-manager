import { buildHeaders, request } from "./client.js";

export const evaluateIntakeRules = async (intake) =>
  request("/v1/intake/rules/evaluate", {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ intake })
  });

export const listIntakeSnapshots = async ({ projectId }) =>
  request(`/v1/projects/${projectId}/intake/snapshots`, {
    headers: buildHeaders()
  });

export const createIntakeSnapshot = async ({ projectId, intake, status }) =>
  request(`/v1/projects/${projectId}/intake/snapshots`, {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ intake, status })
  });
