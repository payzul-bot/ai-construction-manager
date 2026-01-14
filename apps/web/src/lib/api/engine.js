import { buildHeaders, request } from "./client.js";

/**
 * @param {Record<string, any>} input
 * @returns {Promise<Record<string, any>>}
 */
export const calculateEngineV1 = async (input) => {
  return request("/v1/engine/calculate", {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });
};
