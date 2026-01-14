"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { createProject, getApiConfig } from "../../../src/lib/api";

const formatError = (error) => {
  if (!error) return "";
  const details = typeof error.body === "string" ? error.body : JSON.stringify(error.body);
  return [error.message, details].filter(Boolean).join(" | ");
};

const defaultConstraints = JSON.stringify({}, null, 2);

export default function NewProjectPage() {
  const apiConfig = useMemo(() => getApiConfig(), []);
  const [title, setTitle] = useState("");
  const [region, setRegion] = useState("");
  const [objectType, setObjectType] = useState("");
  const [customerType, setCustomerType] = useState("private");
  const [qualityLevel, setQualityLevel] = useState("economy");
  const [constraints, setConstraints] = useState(defaultConstraints);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [createdId, setCreatedId] = useState("");

  const handleCreate = async () => {
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    let constraintsPayload = {};
    try {
      constraintsPayload = constraints.trim() ? JSON.parse(constraints) : {};
    } catch (err) {
      setError("Constraints must be valid JSON.");
      return;
    }

    const meta = {
      project_profile: {
        region: region.trim(),
        object_type: objectType.trim(),
        customer_type: customerType,
        quality_level: qualityLevel,
        constraints: constraintsPayload
      }
    };

    setCreating(true);
    setError("");
    try {
      const created = await createProject({ title: title.trim(), meta });
      setCreatedId(created?.id || "");
    } catch (err) {
      setError(formatError(err));
    } finally {
      setCreating(false);
    }
  };

  return (
    <main>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>Create project</h1>
          <p style={{ marginTop: 0, color: "#4b5563" }}>
            API: {apiConfig.apiBase} | Tenant: {apiConfig.tenantId}
          </p>
        </div>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link href="/" style={{ color: "#2563eb", textDecoration: "none" }}>
            Home
          </Link>
          <Link href="/projects" style={{ color: "#2563eb", textDecoration: "none" }}>
            Projects
          </Link>
        </nav>
      </header>

      <section
        style={{
          marginTop: 24,
          background: "white",
          padding: 24,
          borderRadius: 16,
          border: "1px solid #e2e8f0"
        }}
      >
        <h2 style={{ marginTop: 0 }}>Project Passport (создание)</h2>
        <p style={{ color: "#4b5563" }}>
          Поля соответствуют Project Profile из Engine Spec. Данные сохраняются в meta проекта.
        </p>
        <div style={{ display: "grid", gap: 12 }}>
          <label style={{ display: "grid", gap: 6 }}>
            <span>Project title</span>
            <input
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Название проекта"
              style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
            />
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Region</span>
              <input
                type="text"
                value={region}
                onChange={(event) => setRegion(event.target.value)}
                placeholder="Москва, Россия"
                style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
              />
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Object type</span>
              <input
                type="text"
                value={objectType}
                onChange={(event) => setObjectType(event.target.value)}
                placeholder="Квартира, офис, склад"
                style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
              />
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Customer type</span>
              <select
                value={customerType}
                onChange={(event) => setCustomerType(event.target.value)}
                style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
              >
                <option value="private">private</option>
                <option value="company">company</option>
                <option value="government">government</option>
              </select>
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Quality level</span>
              <select
                value={qualityLevel}
                onChange={(event) => setQualityLevel(event.target.value)}
                style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
              >
                <option value="economy">economy</option>
                <option value="comfort">comfort</option>
                <option value="business">business</option>
                <option value="premium">premium</option>
              </select>
            </label>
          </div>
          <label style={{ display: "grid", gap: 6 }}>
            <span>Constraints (JSON)</span>
            <textarea
              value={constraints}
              onChange={(event) => setConstraints(event.target.value)}
              rows={6}
              style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0", fontFamily: "monospace" }}
            />
          </label>
        </div>
        <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
          <button type="button" onClick={handleCreate} disabled={creating}>
            {creating ? "Creating..." : "Create project"}
          </button>
          {createdId ? (
            <Link href={`/projects/${createdId}`} style={{ color: "#2563eb", alignSelf: "center" }}>
              Open created project
            </Link>
          ) : null}
        </div>
        {error ? <div style={{ marginTop: 12, color: "#b91c1c" }}>Error: {error}</div> : null}
      </section>
    </main>
  );
}
