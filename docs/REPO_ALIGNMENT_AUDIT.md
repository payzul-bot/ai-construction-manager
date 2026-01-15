# Repository Alignment Audit (Docs-First)

## What docs say (source of truth)

- **Architecture & boundaries**: Core engine is deterministic; UI/API/LLM only collect input and render results. Calculation logic stays in core; inputs/outputs are structured and versioned. Any change to inputs/rules creates a new version. 【F:docs/ARCHITECTURE.md†L14-L167】【F:docs/ENGINE_SPEC.md†L1-L137】
- **Domain model**: `Project` is immutable; changes produce new calculation versions. `Estimate`/`EstimateVersion` are versioned snapshots with structured inputs/results. Entities are tenant-scoped and immutable by version. 【F:docs/DOMAIN_MODEL.md†L44-L134】
- **Security & auth**: API keys are header-based; tenant isolation is mandatory; all data access occurs in tenant context. 【F:docs/SECURITY.md†L18-L90】
- **Development mode**: phase focuses on skeleton visualization; no hardcoded domain logic in UI; calculation is gated. Development instructions are expected to match actual repo layout and commands. 【F:docs/DEVELOPMENT_MODE.md†L1-L53】

## What code does (observed repo state)

### Backend (apps/api)
- FastAPI app mounted at `/` with health check `GET /health`, and v1 router under `/v1`. 【F:apps/api/app/main.py†L1-L28】
- v1 routes:
  - Projects CRUD (`/v1/projects`, `/v1/projects/{project_id}`, `/v1/projects/delete-many`). 【F:apps/api/app/api/v1/routes/projects.py†L1-L78】
  - Estimates (`/v1/estimates`, `/v1/estimates/{estimate_id}/recalculate`, `/v1/estimates/{estimate_id}/versions/{version_no}`). 【F:apps/api/app/api/v1/routes/estimates.py†L1-L118】
  - Engine V0 calculate (`/v1/calculations/calculate`). 【F:apps/api/app/api/v1/routes/calculations.py†L1-L18】
  - Engine V1 skeleton (`/v1/engine/calculate`). 【F:apps/api/app/api/v1/routes/engine_v1.py†L1-L23】
- Tenant header is required (`X-Tenant-Id`) for project/estimate routes. API key is required for calculation endpoints. 【F:apps/api/app/api/v1/deps.py†L28-L87】
- Default API key exists in settings (dev key) but API key checks are always enforced. 【F:apps/api/app/settings.py†L10-L33】【F:apps/api/app/api/v1/deps.py†L48-L87】
- `docker-compose.yml` references `./apps/api/.env` for API keys, but no `.env` file exists in repo. 【F:docker-compose.yml†L23-L60】

### Frontend (apps/web)
- API client uses `NEXT_PUBLIC_API_BASE`, `NEXT_PUBLIC_TENANT_ID`, `NEXT_PUBLIC_API_KEY` env values with defaults for base/tenant; API key defaults empty. 【F:apps/web/src/lib/api/client.js†L1-L58】
- Frontend API calls target:
  - `/v1/projects` CRUD and `/v1/projects/delete-many`. 【F:apps/web/src/lib/api/projects.js†L1-L79】
  - `/v1/estimates` list/create, `/v1/estimates/{estimateId}/recalculate`, `/v1/estimates/{estimateId}/versions/{versionNo}`. 【F:apps/web/src/lib/api/estimates.js†L1-L76】
  - `/v1/engine/calculate`. 【F:apps/web/src/lib/api/engine.js†L1-L16】
- Web README implies API key may be optional, depending on backend enforcement. 【F:apps/web/README.md†L11-L16】

## Mismatches (exact paths/symbols)

1. **API key enforcement mismatch**
   - Backend always requires `X-API-Key` for `/v1/calculations/calculate` and `/v1/engine/calculate`. 【F:apps/api/app/api/v1/deps.py†L48-L87】【F:apps/api/app/api/v1/routes/engine_v1.py†L1-L23】
   - Frontend defaults to an empty API key and the Web README describes the API key as optional. 【F:apps/web/src/lib/api/client.js†L1-L26】【F:apps/web/README.md†L11-L16】

2. **Local dev determinism gap for API env**
   - Docker compose expects `./apps/api/.env`, but the file is absent; this breaks deterministic `docker compose up` on clean checkout. 【F:docker-compose.yml†L23-L60】
   - Docs do not provide exact commands/steps for backend/ frontend startup within the documented repo layout. 【F:docs/DEVELOPMENT_MODE.md†L1-L53】

3. **Unused backend endpoint**
   - Backend exposes `/v1/calculations/calculate` (Engine V0) but the frontend does not call it. This is acceptable but should be documented to avoid confusion. 【F:apps/api/app/api/v1/routes/calculations.py†L1-L18】【F:apps/web/src/lib/api/engine.js†L1-L16】

## Remediation plan (minimal, deterministic, docs-first)

1. **Align API key expectations end-to-end**
   - Update frontend documentation to state that API key is required when calling engine endpoints.
   - Provide a canonical dev key in an example env file and reference it in docs.

2. **Make dev run deterministic**
   - Add `apps/api/.env.example` (non-secret dev defaults) and update docs to copy to `.env` for docker compose.
   - Update `docs/DEVELOPMENT_MODE.md` with exact commands and working directories for API and web.
   - Ensure `NEXT_PUBLIC_API_BASE`, `NEXT_PUBLIC_TENANT_ID`, `NEXT_PUBLIC_API_KEY` are documented with concrete dev defaults.

3. **Lock in frontend/backend alignment**
   - Add a deterministic test that extracts frontend API paths and asserts they exist in backend OpenAPI.

## Backward compatibility considerations

- Do not change existing endpoint paths or payloads; only document and configure access consistently.
- Introduce example env files without secrets; no behavior change in runtime contracts.
- Add tests without altering API behavior.
