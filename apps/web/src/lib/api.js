const DEFAULT_API_BASE = "http://localhost:8000";
const DEFAULT_TENANT_ID = "demo";

const getEnv = () => ({
  apiBase: process.env.NEXT_PUBLIC_API_BASE || DEFAULT_API_BASE,
  tenantId: process.env.NEXT_PUBLIC_TENANT_ID || DEFAULT_TENANT_ID,
  apiKey: process.env.NEXT_PUBLIC_API_KEY || ""
});

const buildHeaders = () => {
  const { tenantId, apiKey } = getEnv();
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

const request = async (path, options = {}) => {
  const { apiBase } = getEnv();
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

export const listProjects = async ({ limit = 50, offset = 0 } = {}) => {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  });
  return request(`/v1/projects?${query.toString()}`, {
    method: "GET",
    headers: buildHeaders()
  });
};

export const createProject = async ({ title, meta = {} }) => {
  return request("/v1/projects", {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title, meta })
  });
};

export const deleteProject = async (projectId) => {
  return request(`/v1/projects/${projectId}`, {
    method: "DELETE",
    headers: buildHeaders()
  });
};

export const deleteManyProjects = async (ids) => {
  return request("/v1/projects/delete-many", {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ ids })
  });
};

export const getApiConfig = () => getEnv();
