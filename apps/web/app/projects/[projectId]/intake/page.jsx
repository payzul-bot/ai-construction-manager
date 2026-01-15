"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createIntakeSnapshot,
  evaluateIntakeRules,
  getApiConfig,
  listIntakeSnapshots,
  listProjects
} from "../../../../src/lib/api";
import { intakeFieldDictionary } from "../../../../src/lib/intake/fieldDictionary";
import { intakeSteps } from "../../../../src/lib/intake/steps";
import {
  buildDefaultIntake,
  getValueByPath,
  mergeAppliedDefaults,
  setValueByPath
} from "../../../../src/lib/intake/utils";

const inputStyle = { padding: 10, borderRadius: 10, border: "1px solid #e2e8f0" };

const formatError = (error) => {
  if (!error) return "";
  const details = typeof error.body === "string" ? error.body : JSON.stringify(error.body);
  return [error.message, details].filter(Boolean).join(" | ");
};

const normalizePayload = (value) => {
  if (Array.isArray(value)) {
    return value
      .map(normalizePayload)
      .filter(
        (item) =>
          item !== null &&
          item !== "" &&
          !(Array.isArray(item) && item.length === 0) &&
          !(typeof item === "object" && item && !Array.isArray(item) && Object.keys(item).length === 0)
      );
  }
  if (value && typeof value === "object") {
    return Object.entries(value).reduce((acc, [key, val]) => {
      const normalized = normalizePayload(val);
      if (
        normalized !== null &&
        normalized !== "" &&
        !(Array.isArray(normalized) && normalized.length === 0) &&
        !(typeof normalized === "object" && !Array.isArray(normalized) && Object.keys(normalized).length === 0)
      ) {
        acc[key] = normalized;
      }
      return acc;
    }, {});
  }
  if (value === "") {
    return null;
  }
  return value;
};

const buildAppliedDefaultsMap = (appliedDefaults) =>
  new Map((appliedDefaults || []).map((item) => [item.field, item.value]));

const extractFieldErrors = (error) => {
  const detail = error?.body?.detail;
  if (!Array.isArray(detail)) {
    return {};
  }
  return detail.reduce((acc, item) => {
    const path = Array.isArray(item.loc)
      ? item.loc
          .filter((segment) => typeof segment === "string" && segment !== "body")
          .join(".")
      : "";
    if (path) {
      acc[path.replace("intake.", "")] = item.msg || "Invalid value";
    }
    return acc;
  }, {});
};

const ensureArray = (value) => (Array.isArray(value) ? value : []);

const getDisplayValue = (data, defaultsMap, path) => {
  const current = getValueByPath(data, path);
  if (Array.isArray(current)) {
    if (current.length > 0) return current;
    return defaultsMap.get(path) || [];
  }
  if (current !== undefined && current !== null && current !== "") {
    return current;
  }
  return defaultsMap.has(path) ? defaultsMap.get(path) : current ?? "";
};

const buildVisibleSteps = (visibleFields, steps) => {
  const visibleSet = new Set(visibleFields || []);
  return steps.filter((step) => step.alwaysVisible || step.fields.some((field) => visibleSet.has(field)));
};

const validateSelectedPlace = (selectedPlace) => {
  if (!selectedPlace || typeof selectedPlace !== "object") return null;
  const hasAny = Object.values(selectedPlace).some((value) => value !== "" && value !== null);
  if (!hasAny) return null;
  const required = ["location_id", "country_iso2", "city", "source"];
  const missing = required.filter((key) => !selectedPlace[key]);
  if (missing.length > 0) {
    return "Location details require location_id, country_iso2, city, and source.";
  }
  return null;
};

export default function ProjectIntakePage() {
  const params = useParams();
  const projectId = params.projectId;
  const apiConfig = useMemo(() => getApiConfig(), []);
  const [project, setProject] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [selectedSnapshotId, setSelectedSnapshotId] = useState("");
  const [intakeData, setIntakeData] = useState(buildDefaultIntake());
  const [rulesOutput, setRulesOutput] = useState({ visible_fields: [], required_fields: [], applied_defaults: [] });
  const [loading, setLoading] = useState(false);
  const [rulesLoading, setRulesLoading] = useState(false);
  const [error, setError] = useState("");
  const [rulesError, setRulesError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const defaultsMap = useMemo(
    () => buildAppliedDefaultsMap(rulesOutput?.applied_defaults),
    [rulesOutput?.applied_defaults]
  );
  const visibleSteps = useMemo(
    () => buildVisibleSteps(rulesOutput?.visible_fields, intakeSteps),
    [rulesOutput?.visible_fields]
  );
  const currentStep = visibleSteps[currentStepIndex] || visibleSteps[0];
  const requiredSet = useMemo(() => new Set(rulesOutput?.required_fields || []), [rulesOutput?.required_fields]);

  const latestSnapshot = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;
  const selectedSnapshot = snapshots.find((item) => item.snapshot_id === selectedSnapshotId) || null;
  const activeSnapshot = selectedSnapshot || latestSnapshot;
  const intakeVersion = activeSnapshot?.intake?.intake_version;
  const isLegacy = Boolean(activeSnapshot) && intakeVersion !== "v1.1";
  const isFinal = activeSnapshot?.status === "final";
  const isReadOnly =
    Boolean(activeSnapshot) &&
    (isLegacy ||
      isFinal ||
      (latestSnapshot && activeSnapshot?.snapshot_id !== latestSnapshot.snapshot_id));

  const loadProject = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listProjects();
      const found = Array.isArray(data) ? data.find((item) => item.id === projectId) : null;
      setProject(found || null);
      if (!found) {
        setError("Project not found in list response.");
      }
    } catch (err) {
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  const loadSnapshots = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listIntakeSnapshots({ projectId });
      const items = Array.isArray(data?.items) ? data.items : [];
      setSnapshots(items);
      if (items.length > 0) {
        const latest = items[items.length - 1];
        setSelectedSnapshotId(latest.snapshot_id);
        setIntakeData(latest.intake);
      } else {
        setSelectedSnapshotId("");
        setIntakeData(buildDefaultIntake());
      }
    } catch (err) {
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadProject();
    loadSnapshots();
  }, [loadProject, loadSnapshots]);

  useEffect(() => {
    if (visibleSteps.length === 0) return;
    if (currentStepIndex >= visibleSteps.length) {
      setCurrentStepIndex(0);
    }
  }, [visibleSteps, currentStepIndex]);

  useEffect(() => {
    if (isLegacy) {
      return;
    }
    let active = true;
    const timer = setTimeout(async () => {
      setRulesLoading(true);
      setRulesError("");
      try {
        const payload = normalizePayload(intakeData);
        const response = await evaluateIntakeRules(payload);
        if (!active) return;
        setRulesOutput(response?.rules || { visible_fields: [], required_fields: [], applied_defaults: [] });
        if (response?.intake?.location_profile_id && !intakeData.location_profile_id) {
          setIntakeData((prev) => ({ ...prev, location_profile_id: response.intake.location_profile_id }));
        }
      } catch (err) {
        if (!active) return;
        setRulesError(formatError(err));
      } finally {
        if (active) setRulesLoading(false);
      }
    }, 300);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [intakeData, isReadOnly]);

  const updateField = (path, value) => {
    setIntakeData((prev) => setValueByPath(prev, path, value));
    setFieldErrors((prev) => {
      const next = { ...prev };
      delete next[path];
      return next;
    });
  };

  const updateArrayItem = (path, index, key, value) => {
    const current = ensureArray(getValueByPath(intakeData, path));
    const next = current.map((item, idx) => (idx === index ? { ...item, [key]: value } : item));
    updateField(path, next);
  };

  const addInterval = (path) => {
    const current = ensureArray(getValueByPath(intakeData, path));
    updateField(path, [...current, { start: "", end: "" }]);
  };

  const removeInterval = (path, index) => {
    const current = ensureArray(getValueByPath(intakeData, path));
    updateField(
      path,
      current.filter((_, idx) => idx !== index)
    );
  };

  const addStringItem = (path, value) => {
    const current = ensureArray(getValueByPath(intakeData, path));
    if (!value.trim()) return;
    updateField(path, [...current, value.trim()]);
  };

  const removeStringItem = (path, index) => {
    const current = ensureArray(getValueByPath(intakeData, path));
    updateField(
      path,
      current.filter((_, idx) => idx !== index)
    );
  };

  const handleSnapshotSelect = (snapshotId) => {
    setSelectedSnapshotId(snapshotId);
    const next = snapshots.find((item) => item.snapshot_id === snapshotId);
    if (next) {
      setIntakeData(next.intake);
    }
  };

  const validateStep = () => {
    if (!currentStep) return true;
    const nextErrors = {};
    const selectedPlaceError = validateSelectedPlace(intakeData?.selected_place);
    if (selectedPlaceError) {
      nextErrors["selected_place.location_id"] = selectedPlaceError;
    }
    currentStep.fields.forEach((path) => {
      if (!requiredSet.has(path)) return;
      if (!rulesOutput.visible_fields.includes(path)) return;
      const value = getDisplayValue(intakeData, defaultsMap, path);
      if (Array.isArray(value) && value.length === 0) {
        nextErrors[path] = "Required field.";
      } else if (value === null || value === undefined || value === "") {
        nextErrors[path] = "Required field.";
      }
    });
    setFieldErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const buildSnapshotPayload = () => {
    const merged = mergeAppliedDefaults(intakeData, rulesOutput?.applied_defaults);
    const normalized = normalizePayload(merged);
    if (normalized?.selected_place && Object.keys(normalized.selected_place).length === 0) {
      normalized.selected_place = null;
    }
    return normalized;
  };

  const handleSaveSnapshot = async (status) => {
    if (isReadOnly) return;
    const valid = validateStep();
    if (!valid) {
      return false;
    }
    setSaving(true);
    setSaveMessage("");
    setError("");
    try {
      const payload = buildSnapshotPayload();
      const created = await createIntakeSnapshot({ projectId, intake: payload, status });
      setSnapshots((prev) => [...prev, created]);
      setSelectedSnapshotId(created.snapshot_id);
      setSaveMessage(status === "final" ? "Final snapshot saved." : "Draft snapshot saved.");
      return true;
    } catch (err) {
      setError(formatError(err));
      setFieldErrors(extractFieldErrors(err));
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleNext = async () => {
    if (!currentStep) return;
    const saved = await handleSaveSnapshot("draft");
    if (saved && currentStepIndex < visibleSteps.length - 1) {
      setCurrentStepIndex((prev) => Math.min(prev + 1, visibleSteps.length - 1));
    }
  };

  const handleBack = () => {
    setCurrentStepIndex((prev) => Math.max(prev - 1, 0));
  };

  const renderField = (path) => {
    const def = intakeFieldDictionary[path];
    if (!def) return null;
    const value = getDisplayValue(intakeData, defaultsMap, path);
    const required = requiredSet.has(path);
    const errorMessage = fieldErrors[path];

    const handleChange = (event) => {
      let nextValue = event.target.value;
      if (def.type === "number") {
        if (nextValue === "") {
          nextValue = "";
        } else {
          nextValue = def.numberFormat === "int" ? parseInt(nextValue, 10) : parseFloat(nextValue);
          if (Number.isNaN(nextValue)) {
            nextValue = "";
          }
        }
      }
      if (def.type === "boolean") {
        if (nextValue === "") {
          nextValue = null;
        } else {
          nextValue = nextValue === "true";
        }
      }
      updateField(path, nextValue);
    };

    if (def.type === "array_enum") {
      const options = def.options || [];
      const current = ensureArray(value);
      return (
        <div key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <div style={{ display: "grid", gap: 8 }}>
            {options.map((option) => {
              const checked = current.includes(option.value);
              return (
                <label key={option.value} style={{ display: "flex", gap: 8 }}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(event) => {
                      const next = event.target.checked
                        ? [...current, option.value]
                        : current.filter((item) => item !== option.value);
                      updateField(path, next);
                    }}
                    disabled={isReadOnly}
                  />
                  <span>{option.label}</span>
                </label>
              );
            })}
          </div>
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </div>
      );
    }

    if (def.type === "array_intervals") {
      const intervals = ensureArray(value);
      return (
        <div key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <div style={{ display: "grid", gap: 12 }}>
            {intervals.map((interval, index) => (
              <div key={`${path}-${index}`} style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <input
                  type="time"
                  value={interval.start || ""}
                  onChange={(event) => updateArrayItem(path, index, "start", event.target.value)}
                  style={inputStyle}
                  disabled={isReadOnly}
                />
                <span>→</span>
                <input
                  type="time"
                  value={interval.end || ""}
                  onChange={(event) => updateArrayItem(path, index, "end", event.target.value)}
                  style={inputStyle}
                  disabled={isReadOnly}
                />
                <button type="button" onClick={() => removeInterval(path, index)} disabled={isReadOnly}>
                  Remove
                </button>
              </div>
            ))}
            <button type="button" onClick={() => addInterval(path)} disabled={isReadOnly}>
              Add interval
            </button>
          </div>
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </div>
      );
    }

    if (def.type === "array_string") {
      const current = ensureArray(value);
      return (
        <div key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <div style={{ display: "grid", gap: 8 }}>
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="text"
                placeholder="Add value"
                style={{ ...inputStyle, flex: 1 }}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addStringItem(path, event.currentTarget.value);
                    event.currentTarget.value = "";
                  }
                }}
                disabled={isReadOnly}
              />
              <button
                type="button"
                onClick={(event) => {
                  const input = event.currentTarget.parentElement?.querySelector("input");
                  if (!input) return;
                  addStringItem(path, input.value);
                  input.value = "";
                }}
                disabled={isReadOnly}
              >
                Add
              </button>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {current.map((item, index) => (
                <span
                  key={`${path}-${item}-${index}`}
                  style={{
                    background: "#f1f5f9",
                    padding: "4px 8px",
                    borderRadius: 999,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6
                  }}
                >
                  {item}
                  <button type="button" onClick={() => removeStringItem(path, index)} disabled={isReadOnly}>
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </div>
      );
    }

    if (def.type === "boolean") {
      return (
        <label key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <select
            value={value === null || value === undefined ? "" : String(value)}
            onChange={handleChange}
            style={inputStyle}
            disabled={isReadOnly}
          >
            <option value="">Select</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </label>
      );
    }

    if (def.type === "number") {
      return (
        <label key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <input
            type="number"
            value={value === null || value === undefined ? "" : value}
            onChange={handleChange}
            style={inputStyle}
            disabled={isReadOnly}
          />
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </label>
      );
    }

    if (def.type === "enum") {
      return (
        <label key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <select value={value || ""} onChange={handleChange} style={inputStyle} disabled={isReadOnly}>
            <option value="">Select</option>
            {(def.options || []).map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </label>
      );
    }

    if (def.type === "time") {
      return (
        <label key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <input type="time" value={value || ""} onChange={handleChange} style={inputStyle} disabled={isReadOnly} />
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </label>
      );
    }

    if (def.type === "text") {
      return (
        <label key={path} style={{ display: "grid", gap: 6 }}>
          <span>
            {def.label} {required ? "*" : ""}
          </span>
          <textarea value={value || ""} onChange={handleChange} rows={4} style={inputStyle} disabled={isReadOnly} />
          {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
        </label>
      );
    }

    return (
      <label key={path} style={{ display: "grid", gap: 6 }}>
        <span>
          {def.label} {required ? "*" : ""}
        </span>
        <input type="text" value={value || ""} onChange={handleChange} style={inputStyle} disabled={isReadOnly} />
        {errorMessage ? <div style={{ color: "#b91c1c" }}>{errorMessage}</div> : null}
      </label>
    );
  };

  return (
    <main>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>Project Intake V1.1</h1>
          <p style={{ marginTop: 0, color: "#4b5563" }}>
            API: {apiConfig.apiBase} | Tenant: {apiConfig.tenantId}
          </p>
          {project ? (
            <p style={{ marginTop: 4, color: "#4b5563" }}>
              Project: {project.title} ({project.id})
            </p>
          ) : null}
        </div>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link href="/" style={{ color: "#2563eb", textDecoration: "none" }}>
            Home
          </Link>
          <Link href="/projects" style={{ color: "#2563eb", textDecoration: "none" }}>
            Projects
          </Link>
          <Link href={`/projects/${projectId}`} style={{ color: "#2563eb", textDecoration: "none" }}>
            Project detail
          </Link>
        </nav>
      </header>

      {error ? <div style={{ marginTop: 12, color: "#b91c1c" }}>Error: {error}</div> : null}
      {rulesError ? (
        <div style={{ marginTop: 12, color: "#b45309" }}>
          Rules evaluation error: {rulesError}{" "}
          <button type="button" onClick={() => setIntakeData((prev) => ({ ...prev }))} disabled={rulesLoading}>
            Retry
          </button>
        </div>
      ) : null}
      {rulesLoading ? <div style={{ marginTop: 12, color: "#64748b" }}>Evaluating rules...</div> : null}
      {saveMessage ? <div style={{ marginTop: 12, color: "#15803d" }}>{saveMessage}</div> : null}

      <section style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 24, marginTop: 24 }}>
        <aside style={{ background: "white", padding: 16, borderRadius: 16, border: "1px solid #e2e8f0" }}>
          <h2 style={{ marginTop: 0 }}>Snapshots</h2>
          {loading ? <p style={{ color: "#64748b" }}>Loading...</p> : null}
          {snapshots.length === 0 ? <p style={{ color: "#64748b" }}>No snapshots yet.</p> : null}
          <div style={{ display: "grid", gap: 8 }}>
            {snapshots.map((snapshot) => (
              <button
                key={snapshot.snapshot_id}
                type="button"
                onClick={() => handleSnapshotSelect(snapshot.snapshot_id)}
                style={{
                  textAlign: "left",
                  padding: 10,
                  borderRadius: 12,
                  border:
                    snapshot.snapshot_id === selectedSnapshotId ? "1px solid #2563eb" : "1px solid #e2e8f0",
                  background: snapshot.snapshot_id === selectedSnapshotId ? "#eff6ff" : "white"
                }}
              >
                <div style={{ fontWeight: 600 }}>
                  {snapshot.status === "final" ? "Final" : "Draft"} snapshot
                </div>
                <div style={{ fontSize: 12, color: "#64748b" }}>{snapshot.created_at}</div>
              </button>
            ))}
          </div>
          {isReadOnly ? (
            <div style={{ marginTop: 12, fontSize: 12, color: "#64748b" }}>
              Viewing read-only snapshot for audit.
            </div>
          ) : null}
        </aside>

        <section style={{ background: "white", padding: 24, borderRadius: 16, border: "1px solid #e2e8f0" }}>
          <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h2 style={{ marginTop: 0 }}>{currentStep ? currentStep.title : "Loading step..."}</h2>
              <p style={{ color: "#64748b", marginTop: 4 }}>
                Step {currentStepIndex + 1} of {visibleSteps.length}
              </p>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={handleBack} disabled={currentStepIndex === 0 || isReadOnly}>
                Back
              </button>
              {currentStepIndex < visibleSteps.length - 1 ? (
                <button type="button" onClick={handleNext} disabled={saving || isReadOnly}>
                  {saving ? "Saving..." : "Next"}
                </button>
              ) : (
                <button type="button" onClick={() => handleSaveSnapshot("final")} disabled={saving || isReadOnly}>
                  {saving ? "Saving..." : "Submit / Calculate"}
                </button>
              )}
            </div>
          </header>

          {currentStep ? (
            <div style={{ display: "grid", gap: 16, marginTop: 16 }}>
              {currentStep.fields
                .filter((field) => rulesOutput.visible_fields.includes(field))
                .map((field) => renderField(field))}
            </div>
          ) : null}

          {isLegacy ? (
            <div style={{ marginTop: 20, background: "#f8fafc", padding: 12, borderRadius: 12 }}>
              <strong>Legacy intake detected.</strong>
              <pre style={{ marginTop: 8, whiteSpace: "pre-wrap" }}>
                {JSON.stringify(activeSnapshot?.intake || {}, null, 2)}
              </pre>
            </div>
          ) : null}
        </section>
      </section>
    </main>
  );
}
