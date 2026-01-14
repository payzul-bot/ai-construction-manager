const DEFAULT_API_BASE = "http://localhost:8000";
const DEFAULT_TENANT_ID = "demo";

/**
 * @typedef {Object} ApiConfig
 * @property {string} apiBase
 * @property {string} tenantId
 * @property {string} apiKey
 */

/**
 * @returns {ApiConfig}
 */
export const getApiConfig = () => ({
  apiBase: process.env.NEXT_PUBLIC_API_BASE || DEFAULT_API_BASE,
  tenantId: process.env.NEXT_PUBLIC_TENANT_ID || DEFAULT_TENANT_ID,
  apiKey: process.env.NEXT_PUBLIC_API_KEY || ""
});

export const buildHeaders = () => {
  const { tenantId, apiKey } = getApiConfig();
  const headers = {
    "X-Tenant-Id": tenantId
  };

  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  return headers;
};

const parseBody = async (response) => {
  const text = await response.text();
  if (!text) {
    return { text: "", json: null };
  }

  try {
    return { text, json: JSON.parse(text) };
  } catch (error) {
    return { text, json: null };
  }
};

export const request = async (path, options = {}) => {
  const { apiBase } = getApiConfig();
  const response = await fetch(`${apiBase}${path}`, options);
  const body = await parseBody(response);

  if (!response.ok) {
    const message = body.text || response.statusText;
    const error = new Error(`Request failed (${response.status}): ${message}`);
    error.status = response.status;
    error.body = body.json ?? body.text;
    throw error;
  }

  return body.json ?? body.text;
};
