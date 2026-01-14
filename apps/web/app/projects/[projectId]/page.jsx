"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  calculateEngineV1,
  createEstimate,
  getApiConfig,
  listEstimates,
  listProjects,
  patchProject,
  recalculateEstimate
} from "../../../src/lib/api";

const formatError = (error) => {
  if (!error) return "";
  const details = typeof error.body === "string" ? error.body : JSON.stringify(error.body);
  return [error.message, details].filter(Boolean).join(" | ");
};

const emptyProfile = {
  region: "",
  object_type: "",
  customer_type: "private",
  quality_level: "economy",
  constraints: {}
};

const safeJsonParse = (value, fallback) => {
  try {
    return value.trim() ? JSON.parse(value) : fallback;
  } catch (error) {
    return null;
  }
};

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params.projectId;
  const apiConfig = useMemo(() => getApiConfig(), []);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [project, setProject] = useState(null);
  const [title, setTitle] = useState("");
  const [profile, setProfile] = useState(emptyProfile);
  const [constraintsText, setConstraintsText] = useState(JSON.stringify({}, null, 2));
  const [workGraph, setWorkGraph] = useState([]);
  const [metaBase, setMetaBase] = useState({});

  const [workId, setWorkId] = useState("");
  const [calculationProfileId, setCalculationProfileId] = useState("");
  const [workParameters, setWorkParameters] = useState(JSON.stringify({}, null, 2));
  const [workDependencies, setWorkDependencies] = useState("");

  const [estimates, setEstimates] = useState([]);
  const [selectedEstimateId, setSelectedEstimateId] = useState("");
  const [estimateInput, setEstimateInput] = useState(
    JSON.stringify({ work_id: "", params: {}, prices: null }, null, 2)
  );
  const [estimateResult, setEstimateResult] = useState(null);
  const [estimateError, setEstimateError] = useState("");
  const [estimateBusy, setEstimateBusy] = useState(false);

  const [engineRulesVersion, setEngineRulesVersion] = useState("");
  const [engineDictionariesVersion, setEngineDictionariesVersion] = useState("");
  const [engineMode, setEngineMode] = useState("draft");
  const [engineRequestMetadata, setEngineRequestMetadata] = useState(JSON.stringify({}, null, 2));
  const [engineResult, setEngineResult] = useState(null);
  const [engineError, setEngineError] = useState("");
  const [engineBusy, setEngineBusy] = useState(false);

  const hydrateFromProject = useCallback((found) => {
    const meta = found?.meta || {};
    const profileData = meta.project_profile || emptyProfile;
    const constraintsValue = JSON.stringify(profileData.constraints || {}, null, 2);
    const nextMetaBase = { ...meta };
    delete nextMetaBase.project_profile;
    delete nextMetaBase.work_graph;

    setProject(found);
    setTitle(found?.title || "");
    setProfile({
      region: profileData.region || "",
      object_type: profileData.object_type || "",
      customer_type: profileData.customer_type || "private",
      quality_level: profileData.quality_level || "economy",
      constraints: profileData.constraints || {}
    });
    setConstraintsText(constraintsValue);
    setWorkGraph(Array.isArray(meta.work_graph) ? meta.work_graph : []);
    setMetaBase(nextMetaBase);
  }, []);

  const loadProject = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listProjects();
      const found = Array.isArray(data) ? data.find((item) => item.id === projectId) : null;
      if (!found) {
        setError("Project not found in list response.");
      } else {
        hydrateFromProject(found);
      }
    } catch (err) {
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  }, [projectId, hydrateFromProject]);

  const loadEstimates = useCallback(async () => {
    try {
      const data = await listEstimates({ projectId });
      const items = Array.isArray(data) ? data : [];
      setEstimates(items);
      if (items.length > 0) {
        setSelectedEstimateId((prev) => prev || items[0].id);
      }
    } catch (err) {
      setEstimateError(formatError(err));
    }
  }, [projectId]);

  useEffect(() => {
    loadProject();
    loadEstimates();
  }, [loadProject, loadEstimates]);

  const buildMetaPayload = (constraintsPayload, graphPayload) => ({
    ...metaBase,
    project_profile: {
      region: profile.region,
      object_type: profile.object_type,
      customer_type: profile.customer_type,
      quality_level: profile.quality_level,
      constraints: constraintsPayload
    },
    work_graph: graphPayload
  });

  const handleSavePassport = async () => {
    const parsed = safeJsonParse(constraintsText, {});
    if (parsed === null) {
      setError("Constraints must be valid JSON.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const meta = buildMetaPayload(parsed, workGraph);
      const updated = await patchProject(projectId, { title: title.trim(), meta });
      hydrateFromProject(updated);
    } catch (err) {
      setError(formatError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleAddWorkUnit = () => {
    if (!workId.trim()) {
      setError("work_id is required to add a work unit.");
      return;
    }
    const parametersPayload = safeJsonParse(workParameters, {});
    if (parametersPayload === null) {
      setError("Work parameters must be valid JSON.");
      return;
    }
    const dependencies = workDependencies
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);

    const nextWorkGraph = [
      ...workGraph,
      {
        work_id: workId.trim(),
        calculation_profile_id: calculationProfileId.trim() || null,
        parameters: parametersPayload,
        dependencies
      }
    ];
    setWorkGraph(nextWorkGraph);
    setWorkId("");
    setCalculationProfileId("");
    setWorkParameters(JSON.stringify({}, null, 2));
    setWorkDependencies("");
  };

  const handleRemoveWorkUnit = (index) => {
    const next = workGraph.filter((_, idx) => idx !== index);
    setWorkGraph(next);
  };

  const handleSaveWorkGraph = async () => {
    const parsed = safeJsonParse(constraintsText, {});
    if (parsed === null) {
      setError("Constraints must be valid JSON.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const meta = buildMetaPayload(parsed, workGraph);
      const updated = await patchProject(projectId, { title: title.trim(), meta });
      hydrateFromProject(updated);
    } catch (err) {
      setError(formatError(err));
    } finally {
      setSaving(false);
    }
  };

  const handleCreateEstimate = async () => {
    setEstimateBusy(true);
    setEstimateError("");
    try {
      const created = await createEstimate({ projectId });
      await loadEstimates();
      setSelectedEstimateId(created?.id || created?.estimate_id || "");
    } catch (err) {
      setEstimateError(formatError(err));
    } finally {
      setEstimateBusy(false);
    }
  };

  const handleRecalculate = async () => {
    if (!selectedEstimateId) {
      setEstimateError("Select or create an estimate first.");
      return;
    }
    const parsed = safeJsonParse(estimateInput, {});
    if (parsed === null) {
      setEstimateError("Estimate input must be valid JSON.");
      return;
    }
    setEstimateBusy(true);
    setEstimateError("");
    try {
      const result = await recalculateEstimate(selectedEstimateId, parsed);
      setEstimateResult(result);
    } catch (err) {
      setEstimateError(formatError(err));
    } finally {
      setEstimateBusy(false);
    }
  };

  const handleEngineCalculate = async () => {
    const constraintsPayload = safeJsonParse(constraintsText, {});
    const metadataPayload = safeJsonParse(engineRequestMetadata, {});
    if (constraintsPayload === null) {
      setEngineError("Constraints must be valid JSON.");
      return;
    }
    if (metadataPayload === null) {
      setEngineError("Engine request metadata must be valid JSON.");
      return;
    }
    if (!engineRulesVersion.trim() || !engineDictionariesVersion.trim()) {
      setEngineError("Rules version and dictionaries version are required.");
      return;
    }

    const engineInput = {
      project_profile: {
        region: profile.region,
        object_type: profile.object_type,
        customer_type: profile.customer_type,
        quality_level: profile.quality_level,
        constraints: constraintsPayload
      },
      work_graph: workGraph,
      engine_context: {
        rules_version: engineRulesVersion.trim(),
        dictionaries_version: engineDictionariesVersion.trim(),
        mode: engineMode,
        mode_flags: {},
        request_metadata: metadataPayload
      }
    };

    setEngineBusy(true);
    setEngineError("");
    try {
      const result = await calculateEngineV1(engineInput);
      setEngineResult(result);
    } catch (err) {
      setEngineError(formatError(err));
    } finally {
      setEngineBusy(false);
    }
  };

  const renderResourceList = (items, emptyLabel) => {
    if (!items || items.length === 0) {
      return <p style={{ color: "#64748b" }}>{emptyLabel}</p>;
    }
    return (
      <ul style={{ margin: 0, paddingLeft: 20 }}>
        {items.map((item, index) => (
          <li key={`${item.resource_id || item.stage_id || item.qc_id || index}`}>
            <code>{JSON.stringify(item)}</code>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <main>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>Project Passport & Engine</h1>
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

      {loading ? <p>Loading project...</p> : null}
      {error ? <div style={{ marginTop: 12, color: "#b91c1c" }}>Error: {error}</div> : null}

      {project ? (
        <>
          <section
            style={{
              marginTop: 24,
              background: "white",
              padding: 24,
              borderRadius: 16,
              border: "1px solid #e2e8f0"
            }}
          >
            <h2 style={{ marginTop: 0 }}>Project Passport</h2>
            <p style={{ color: "#4b5563" }}>
              Поля соответствуют Project Profile из Engine Spec и сохраняются в meta проекта.
            </p>
            <div style={{ display: "grid", gap: 12 }}>
              <label style={{ display: "grid", gap: 6 }}>
                <span>Project title</span>
                <input
                  type="text"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                />
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                <label style={{ display: "grid", gap: 6 }}>
                  <span>Region</span>
                  <input
                    type="text"
                    value={profile.region}
                    onChange={(event) => setProfile({ ...profile, region: event.target.value })}
                    style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                  />
                </label>
                <label style={{ display: "grid", gap: 6 }}>
                  <span>Object type</span>
                  <input
                    type="text"
                    value={profile.object_type}
                    onChange={(event) => setProfile({ ...profile, object_type: event.target.value })}
                    style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                  />
                </label>
                <label style={{ display: "grid", gap: 6 }}>
                  <span>Customer type</span>
                  <select
                    value={profile.customer_type}
                    onChange={(event) => setProfile({ ...profile, customer_type: event.target.value })}
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
                    value={profile.quality_level}
                    onChange={(event) => setProfile({ ...profile, quality_level: event.target.value })}
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
                  value={constraintsText}
                  onChange={(event) => setConstraintsText(event.target.value)}
                  rows={6}
                  style={{
                    padding: 10,
                    borderRadius: 10,
                    border: "1px solid #e2e8f0",
                    fontFamily: "monospace"
                  }}
                />
              </label>
            </div>
            <div style={{ marginTop: 16 }}>
              <button type="button" onClick={handleSavePassport} disabled={saving}>
                {saving ? "Saving..." : "Save passport"}
              </button>
            </div>
          </section>

          <section
            style={{
              marginTop: 24,
              background: "white",
              padding: 24,
              borderRadius: 16,
              border: "1px solid #e2e8f0"
            }}
          >
            <h2 style={{ marginTop: 0 }}>Work Graph</h2>
            <p style={{ color: "#4b5563" }}>
              Граф работ описан в Engine Spec. Пока нет канонического справочника,
              поэтому ввод осуществляется вручную и сохраняется в meta проекта.
            </p>
            <div style={{ display: "grid", gap: 12, marginBottom: 16 }}>
              <label style={{ display: "grid", gap: 6 }}>
                <span>work_id</span>
                <input
                  type="text"
                  value={workId}
                  onChange={(event) => setWorkId(event.target.value)}
                  placeholder="canonical_work_id"
                  style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                />
              </label>
              <label style={{ display: "grid", gap: 6 }}>
                <span>calculation_profile_id (optional)</span>
                <input
                  type="text"
                  value={calculationProfileId}
                  onChange={(event) => setCalculationProfileId(event.target.value)}
                  placeholder="profile_id"
                  style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                />
              </label>
              <label style={{ display: "grid", gap: 6 }}>
                <span>parameters (JSON)</span>
                <textarea
                  value={workParameters}
                  onChange={(event) => setWorkParameters(event.target.value)}
                  rows={4}
                  style={{
                    padding: 10,
                    borderRadius: 10,
                    border: "1px solid #e2e8f0",
                    fontFamily: "monospace"
                  }}
                />
              </label>
              <label style={{ display: "grid", gap: 6 }}>
                <span>dependencies (comma-separated)</span>
                <input
                  type="text"
                  value={workDependencies}
                  onChange={(event) => setWorkDependencies(event.target.value)}
                  placeholder="work_a, work_b"
                  style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                />
              </label>
              <button type="button" onClick={handleAddWorkUnit}>
                Add work unit
              </button>
            </div>
            {workGraph.length === 0 ? (
              <p style={{ color: "#64748b" }}>Work graph is empty.</p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {workGraph.map((unit, index) => (
                  <li key={`${unit.work_id}-${index}`} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                      <code>{JSON.stringify(unit)}</code>
                      <button type="button" onClick={() => handleRemoveWorkUnit(index)}>
                        Remove
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            <div style={{ marginTop: 16 }}>
              <button type="button" onClick={handleSaveWorkGraph} disabled={saving}>
                {saving ? "Saving..." : "Save work graph"}
              </button>
            </div>
          </section>

          <section
            style={{
              marginTop: 24,
              background: "white",
              padding: 24,
              borderRadius: 16,
              border: "1px solid #e2e8f0"
            }}
          >
            <h2 style={{ marginTop: 0 }}>Estimate & Recalculate (V0)</h2>
            <p style={{ color: "#4b5563" }}>
              Текущий backend использует Calc Engine V0. Введите JSON входа
              согласно контракту (work_id, params, prices).
            </p>
            <div style={{ display: "grid", gap: 12 }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center" }}>
                <select
                  value={selectedEstimateId}
                  onChange={(event) => setSelectedEstimateId(event.target.value)}
                  style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                >
                  <option value="">Select estimate</option>
                  {estimates.map((estimate) => (
                    <option key={estimate.id} value={estimate.id}>
                      {estimate.id} (v{estimate.current_version_no})
                    </option>
                  ))}
                </select>
                <button type="button" onClick={handleCreateEstimate} disabled={estimateBusy}>
                  {estimateBusy ? "Creating..." : "Create estimate"}
                </button>
              </div>
              <label style={{ display: "grid", gap: 6 }}>
                <span>Recalc input (JSON)</span>
                <textarea
                  value={estimateInput}
                  onChange={(event) => setEstimateInput(event.target.value)}
                  rows={8}
                  style={{
                    padding: 10,
                    borderRadius: 10,
                    border: "1px solid #e2e8f0",
                    fontFamily: "monospace"
                  }}
                />
              </label>
              <button type="button" onClick={handleRecalculate} disabled={estimateBusy}>
                {estimateBusy ? "Recalculating..." : "Recalculate"}
              </button>
              {estimateError ? <div style={{ color: "#b91c1c" }}>Error: {estimateError}</div> : null}
              {estimateResult ? (
                <pre style={{ background: "#0f172a", color: "#e2e8f0", padding: 16, borderRadius: 12 }}>
                  {JSON.stringify(estimateResult, null, 2)}
                </pre>
              ) : null}
            </div>
          </section>

          <section
            style={{
              marginTop: 24,
              background: "white",
              padding: 24,
              borderRadius: 16,
              border: "1px solid #e2e8f0"
            }}
          >
            <h2 style={{ marginTop: 0 }}>Engine V1 Result</h2>
            <p style={{ color: "#4b5563" }}>
              Расчёт по Engine Spec V1 (строго структурированный вход). Требует API key,
              если настроена проверка в backend.
            </p>
            <div style={{ display: "grid", gap: 12 }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                <label style={{ display: "grid", gap: 6 }}>
                  <span>Rules version</span>
                  <input
                    type="text"
                    value={engineRulesVersion}
                    onChange={(event) => setEngineRulesVersion(event.target.value)}
                    placeholder="rules_version"
                    style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                  />
                </label>
                <label style={{ display: "grid", gap: 6 }}>
                  <span>Dictionaries version</span>
                  <input
                    type="text"
                    value={engineDictionariesVersion}
                    onChange={(event) => setEngineDictionariesVersion(event.target.value)}
                    placeholder="dictionaries_version"
                    style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                  />
                </label>
                <label style={{ display: "grid", gap: 6 }}>
                  <span>Mode</span>
                  <select
                    value={engineMode}
                    onChange={(event) => setEngineMode(event.target.value)}
                    style={{ padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" }}
                  >
                    <option value="draft">draft</option>
                    <option value="final">final</option>
                  </select>
                </label>
              </div>
              <label style={{ display: "grid", gap: 6 }}>
                <span>Request metadata (JSON)</span>
                <textarea
                  value={engineRequestMetadata}
                  onChange={(event) => setEngineRequestMetadata(event.target.value)}
                  rows={6}
                  style={{
                    padding: 10,
                    borderRadius: 10,
                    border: "1px solid #e2e8f0",
                    fontFamily: "monospace"
                  }}
                />
              </label>
              <button type="button" onClick={handleEngineCalculate} disabled={engineBusy}>
                {engineBusy ? "Calculating..." : "Run Engine V1"}
              </button>
              {engineError ? <div style={{ color: "#b91c1c" }}>Error: {engineError}</div> : null}
            </div>
            {engineResult ? (
              <div style={{ marginTop: 16 }}>
                <h3>EngineResult</h3>
                <div style={{ display: "grid", gap: 16 }}>
                  <div>
                    <h4>Project Profile</h4>
                    <pre style={{ background: "#0f172a", color: "#e2e8f0", padding: 12, borderRadius: 12 }}>
                      {JSON.stringify(engineResult.project_profile, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <h4>Works</h4>
                    {renderResourceList(engineResult.works, "No works returned.")}
                  </div>
                  <div>
                    <h4>Materials</h4>
                    {renderResourceList(engineResult.materials, "No materials returned.")}
                  </div>
                  <div>
                    <h4>Tools</h4>
                    {renderResourceList(engineResult.tools, "No tools returned.")}
                  </div>
                  <div>
                    <h4>Equipment</h4>
                    {renderResourceList(engineResult.equipment, "No equipment returned.")}
                  </div>
                  <div>
                    <h4>Stages</h4>
                    {renderResourceList(engineResult.stages, "No stages returned.")}
                  </div>
                  <div>
                    <h4>QC</h4>
                    {renderResourceList(engineResult.qc, "No QC items returned.")}
                  </div>
                  <div>
                    <h4>Risks</h4>
                    {renderResourceList(engineResult.risks, "No risks returned.")}
                  </div>
                  <div>
                    <h4>Totals</h4>
                    <pre style={{ background: "#0f172a", color: "#e2e8f0", padding: 12, borderRadius: 12 }}>
                      {JSON.stringify(engineResult.totals, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <h4>Meta</h4>
                    <pre style={{ background: "#0f172a", color: "#e2e8f0", padding: 12, borderRadius: 12 }}>
                      {JSON.stringify(engineResult.meta, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ) : null}
          </section>
        </>
      ) : null}
    </main>
  );
}
