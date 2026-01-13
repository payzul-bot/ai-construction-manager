# Migration Plan: Engine V0 to Engine Spec

## Purpose

This document defines a staged migration from the current V0 implementation to the target Engine Spec, while preserving immutability, explicit contracts, and auditability. It is documentation-first and does **not** implement code changes. It respects Development Mode constraints and avoids inventing construction norms, formulas, or regulatory data. The plan is deterministic, data-driven, and aligned with long-term maintainability requirements. See ENGINE_SPEC and DEVELOPMENT_MODE for definitions and constraints.

## Gap Analysis: V0 vs. Target Engine Spec

The current V0 implementation delivers a working, but informal, engine workflow. The Engine Spec defines explicit input/output schemas, deterministic output structure, and separation of concerns. Key gaps to close:

- **Contract clarity**: V0 behavior exists but is not fully captured as a versioned, internal contract. Engine Spec requires explicit, immutable contracts for inputs, outputs, and versions.
- **Schema completeness**: Engine Spec calls for structured EngineInput and EngineResult schemas with predictable fields, while V0 outputs may be incomplete or ad-hoc. The migration must add schemas without inventing missing domain data.
- **Deterministic structure**: Engine outputs must include placeholders for QC, stages, and rules in a fixed deterministic structure; V0 does not guarantee this. The migration must add deterministic placeholders without changing logic.
- **Profile data separation**: Engine Spec expects calculation profiles as data templates, not hard-coded logic. V0 lacks a formal profile data layer and leaf_id mapping as a data contract.
- **Pricing/procurement separation**: Engine Spec expects the core engine to be region-agnostic and not tied to procurement/pricing. V0 may blend these concerns. The migration must separate layers without changing core architectural decisions.

## Migration Milestones

### M0 — Freeze V0 Behavior as `engine_v0` Contract (Internal Only)

**Acceptance Criteria**
- The current V0 behavior is explicitly documented as an internal `engine_v0` contract.
- The contract is immutable and versioned (internal reference only).
- Documentation clarifies that `engine_v0` is the authoritative description of current behavior, without changes to logic.
- The contract document includes scope, limitations, and known violations vs. ENGINE_SPEC.

See `ENGINE_V0.md` for the frozen contract description.

**Required Code Changes (High-Level, Not Implemented)**
- Add a versioned contract document for `engine_v0` (internal-only) aligned with existing behavior.
- Add references in documentation and code comments to the frozen contract version.
- Ensure tests (if any) reference the contract version and output shape.

---

### M1 — Introduce EngineInput/EngineResult Schemas per Engine Spec

**Acceptance Criteria**
- EngineInput and EngineResult schemas exist and are versioned, even if many fields are empty/TBD.
- The schema structure matches Engine Spec requirements and is deterministic.
- The schemas are documented and referenced as the canonical interfaces.

**Required Code Changes (High-Level, Not Implemented)**
- Define schema types (e.g., JSON Schema, TypeScript types, or equivalent) for EngineInput and EngineResult.
- Add validation scaffolding that tolerates empty/TBD fields while preserving structure.
- Update engine entry points to accept/return the schema structure without altering core logic.

---

### M2 — Add CalculationProfile Data Layer and Map One Canonical `leaf_id`

**Acceptance Criteria**
- A CalculationProfile template exists as data (not logic), with a loader.
- One canonical `leaf_id` is mapped to a CalculationProfile using a data-driven mapping.
- The mapping is deterministic and documented; no new domain rules are invented.

**Required Code Changes (High-Level, Not Implemented)**
- Create CalculationProfile data template(s) and a loader interface.
- Implement a registry or mapping table from `leaf_id` to CalculationProfile.
- Ensure engine logic references the data layer without changing formulas or norms.

---

### M3 — Add QC/Stages/Rules Placeholders in Output (Deterministic Structure)

**Acceptance Criteria**
- EngineResult includes fixed, deterministic placeholders for QC, stages, and rules.
- The structure is stable and versioned; contents can be empty but must be present.
- Output format conforms to Engine Spec and remains backward compatible with `engine_v0` where applicable.

**Required Code Changes (High-Level, Not Implemented)**
- Extend EngineResult schema with QC, stages, and rules fields.
- Update output builders to populate empty or default placeholders consistently.
- Add tests asserting deterministic output shape (not values).

---

### M4 — Separate Pricing/Procurement Layer from Core; Core Becomes Region-Agnostic

**Acceptance Criteria**
- Core engine operates without pricing/procurement logic and is region-agnostic.
- Pricing/procurement is encapsulated in a separate layer/service or adapter.
- Contract boundaries are explicit, versioned, and documented.

**Required Code Changes (High-Level, Not Implemented)**
- Refactor interfaces to isolate pricing/procurement from core calculation flow.
- Introduce a dedicated pricing/procurement adapter with explicit inputs/outputs.
- Ensure core engine consumes only region-agnostic data inputs and emits region-agnostic results.

## Notes on Constraints and Governance

- **No invented norms or formulas**: The migration does not introduce construction norms, formulas, or regulatory data. It only defines structures and placeholders. Development Mode constraints apply throughout.
- **Immutability and auditability**: Each milestone freezes contracts and schemas with explicit versioning to preserve audit trails and backward compatibility.
- **Deterministic, data-driven design**: Structures and mappings are data-driven; logic changes are deferred until they can be aligned with explicit contracts and documented rules.
