"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createProject,
  deleteManyProjects,
  deleteProject,
  getApiConfig,
  listProjects
} from "../src/lib/api";

const formatError = (error) => {
  if (!error) return "";
  const details = typeof error.body === "string" ? error.body : JSON.stringify(error.body);
  return [error.message, details].filter(Boolean).join(" | ");
};

export default function HomePage() {
  const [projects, setProjects] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");
  const [selectedIds, setSelectedIds] = useState([]);

  const apiConfig = useMemo(() => getApiConfig(), []);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listProjects();
      setProjects(Array.isArray(data) ? data : []);
      setSelectedIds([]);
    } catch (err) {
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleCreate = async () => {
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    setCreating(true);
    setError("");
    try {
      await createProject({ title: title.trim(), meta: {} });
      setTitle("");
      await loadProjects();
    } catch (err) {
      setError(formatError(err));
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (projectId) => {
    setDeleting(true);
    setError("");
    try {
      await deleteProject(projectId);
      await loadProjects();
    } catch (err) {
      setError(formatError(err));
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteMany = async () => {
    if (selectedIds.length === 0) {
      setError("Select at least one project to delete.");
      return;
    }
    setDeleting(true);
    setError("");
    try {
      await deleteManyProjects(selectedIds);
      await loadProjects();
    } catch (err) {
      setError(formatError(err));
    } finally {
      setDeleting(false);
    }
  };

  const toggleSelection = (projectId) => {
    setSelectedIds((prev) =>
      prev.includes(projectId) ? prev.filter((id) => id !== projectId) : [...prev, projectId]
    );
  };

  return (
    <main style={{ maxWidth: 960, margin: "0 auto" }}>
      <h1 style={{ marginBottom: 8 }}>Project CRUD</h1>
      <p style={{ marginTop: 0, color: "#555" }}>
        API: {apiConfig.apiBase} | Tenant: {apiConfig.tenantId}
      </p>

      <section style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 8 }}>Create Project</h2>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <input
            type="text"
            value={title}
            placeholder="Project title"
            onChange={(event) => setTitle(event.target.value)}
            style={{ padding: 8, minWidth: 240 }}
          />
          <button type="button" onClick={handleCreate} disabled={creating}>
            {creating ? "Creating..." : "Create"}
          </button>
          <button type="button" onClick={loadProjects} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </section>

      <section>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ marginBottom: 8 }}>Projects</h2>
          <button type="button" onClick={handleDeleteMany} disabled={deleting}>
            {deleting ? "Deleting..." : "Delete Selected"}
          </button>
        </div>
        {error ? (
          <div style={{ color: "#b00020", marginBottom: 12 }}>Error: {error}</div>
        ) : null}
        {loading ? (
          <div>Loading projects...</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
                <th style={{ padding: "8px 4px" }}>Select</th>
                <th style={{ padding: "8px 4px" }}>ID</th>
                <th style={{ padding: "8px 4px" }}>Title</th>
                <th style={{ padding: "8px 4px" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ padding: 12, color: "#666" }}>
                    No projects found.
                  </td>
                </tr>
              ) : (
                projects.map((project) => (
                  <tr key={project.id} style={{ borderBottom: "1px solid #f0f0f0" }}>
                    <td style={{ padding: "8px 4px" }}>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(project.id)}
                        onChange={() => toggleSelection(project.id)}
                      />
                    </td>
                    <td style={{ padding: "8px 4px" }}>{project.id}</td>
                    <td style={{ padding: "8px 4px" }}>{project.title}</td>
                    <td style={{ padding: "8px 4px" }}>
                      <button
                        type="button"
                        onClick={() => handleDelete(project.id)}
                        disabled={deleting}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
