import { buildHeaders, request } from "./client.js";

/**
 * @typedef {Object} Project
 * @property {string} id
 * @property {string} title
 * @property {Record<string, any>} meta
 */

/**
 * @param {{limit?: number, offset?: number}} [options]
 * @returns {Promise<Project[]>}
 */
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

/**
 * @param {{title: string, meta?: Record<string, any>}} payload
 * @returns {Promise<Project>}
 */
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

/**
 * @param {string} projectId
 * @param {{title?: string, meta?: Record<string, any>}} payload
 * @returns {Promise<Project>}
 */
export const patchProject = async (projectId, { title, meta }) => {
  return request(`/v1/projects/${projectId}`, {
    method: "PATCH",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title, meta })
  });
};

/**
 * @param {string} projectId
 * @returns {Promise<{ok: boolean}>}
 */
export const deleteProject = async (projectId) => {
  return request(`/v1/projects/${projectId}`, {
    method: "DELETE",
    headers: buildHeaders()
  });
};

/**
 * @param {string[]} projectIds
 * @returns {Promise<{deleted: number}>}
 */
export const deleteManyProjects = async (projectIds) => {
  return request("/v1/projects/delete-many", {
    method: "POST",
    headers: {
      ...buildHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ project_ids: projectIds })
  });
};
