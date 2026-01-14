"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { deleteManyProjects, deleteProject, getApiConfig, listProjects } from "../../src/lib/api";

const formatError = (error) => {
  if (!error) return "";
  const details = typeof error.body === "string" ? error.body : JSON.stringify(error.body);
  return [error.message, details].filter(Boolean).join(" | ");
};

export default function ProjectsPage() {
  const apiConfig = useMemo(() => getApiConfig(), []);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");
  const [selectedIds, setSelectedIds] = useState([]);

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
    <main>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>Projects</h1>
          <p style={{ marginTop: 0, color: "#4b5563" }}>
            API: {apiConfig.apiBase} | Tenant: {apiConfig.tenantId}
          </p>
        </div>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link href="/" style={{ color: "#2563eb", textDecoration: "none" }}>
            Home
          </Link>
          <Link href="/projects/new" style={{ color: "#2563eb", textDecoration: "none" }}>
            Create project
          </Link>
        </nav>
      </header>

      <section style={{ marginTop: 24 }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <button type="button" onClick={loadProjects} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </button>
          <button type="button" onClick={handleDeleteMany} disabled={deleting}>
            {deleting ? "Deleting..." : "Delete selected"}
          </button>
        </div>
        {error ? (
          <div style={{ marginTop: 12, color: "#b91c1c" }}>Error: {error}</div>
        ) : null}
      </section>

      <section style={{ marginTop: 16, background: "white", borderRadius: 16, padding: 16 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
              <th style={{ padding: "8px 4px" }}>Select</th>
              <th style={{ padding: "8px 4px" }}>ID</th>
              <th style={{ padding: "8px 4px" }}>Title</th>
              <th style={{ padding: "8px 4px" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} style={{ padding: 12, color: "#64748b" }}>
                  Loading projects...
                </td>
              </tr>
            ) : projects.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ padding: 12, color: "#64748b" }}>
                  No projects found.
                </td>
              </tr>
            ) : (
              projects.map((project) => (
                <tr key={project.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
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
                    <div style={{ display: "flex", gap: 8 }}>
                      <Link href={`/projects/${project.id}`} style={{ color: "#2563eb" }}>
                        Open
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleDelete(project.id)}
                        disabled={deleting}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </main>
  );
}
