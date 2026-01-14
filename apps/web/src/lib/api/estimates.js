import { buildHeaders, request } from "./client.js";

/**
 * @typedef {Object} Estimate
 * @property {string} id
 * @property {string} project_id
 * @property {number} current_version_no
 */

/**
 * @param {{projectId?: string, limit?: number, offset?: number}} [options]
 * @returns {Promise<Estimate[]>}
 */
export const listEstimates = async ({ projectId, limit = 50, offset = 0 } = {}) => {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  });
  if (projectId) {
    query.set("project_id", projectId);
  }
  return request(`/v1/estimates?${query.toString()}`, {
    method: "GET",
    headers: buildHeaders()
  });
};

/**
 * @param {{projectId: string}} payload
 * @returns {Promise<Estimate>}
 */
export const createEstimate = async ({ projectId }) => {
  return request("/v1/estimates", {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ project_id: projectId })
  });
};

/**
 * @param {string} estimateId
 * @param {Record<string, any>} input
 * @param {{idempotencyKey?: string}} [options]
 * @returns {Promise<{estimate_id: string, version_no: number, result: Record<string, any>}>}
 */
export const recalculateEstimate = async (estimateId, input, options = {}) => {
  const headers = {
    ...buildHeaders(),
    "Content-Type": "application/json"
  };
  if (options.idempotencyKey) {
    headers["Idempotency-Key"] = options.idempotencyKey;
  }
  return request(`/v1/estimates/${estimateId}/recalculate`, {
    method: "POST",
    headers,
    body: JSON.stringify({ input })
  });
};

/**
 * @param {string} estimateId
 * @param {number} versionNo
 * @returns {Promise<Record<string, any>>}
 */
export const getEstimateVersion = async (estimateId, versionNo) => {
  return request(`/v1/estimates/${estimateId}/versions/${versionNo}`, {
    method: "GET",
    headers: buildHeaders()
  });
};
