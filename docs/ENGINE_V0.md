# Engine V0 (Legacy/Prototype) Contract

## Scope

Engine V0 is the current legacy/prototype calculation engine implementation exposed by the API. It is implemented as a registry-driven calculator lookup with a single concrete work calculator today (`wall_painting_v1`). The engine accepts a minimal dictionary input (work identifier plus parameters) and routes the request to the matching calculator without any additional schema enforcement. The calculator logic is recipe-backed and returns a compact result payload containing summary fields, material quantities, labor hours, and cost totals. This document freezes the observed behavior as the internal `engine_v0` contract without introducing any new logic or structure changes.

## Limitations

- **Single work scope**: The registry currently resolves only the `wall_painting_v1` work. Any other `work_id` results in an unknown work error. This means Engine V0 is not a general multi-work engine. 
- **Minimal input contract**: Input is a free-form dictionary with `work_id` (or legacy aliases `work`/`code`), `params`, and optional `prices`. There is no EngineInput schema, project profile, or engine context enforcement. 
- **Recipe-coupled logic**: The calculator pulls norms/defaults from a YAML recipe file at runtime and applies them directly; there is no CalculationProfile data layer separate from code. 
- **Ad-hoc output shape**: The result includes `summary`, `materials`, `labor`, and `cost` fields with totals, rather than the fixed EngineResult structure defined in ENGINE_SPEC. 
- **Pricing embedded in core**: Pricing is computed inside the calculator when `prices` are present, which couples the core calculation path to procurement/pricing inputs.

## Known Violations vs. ENGINE_SPEC

The following deviations from ENGINE_SPEC are explicitly acknowledged for `engine_v0` and must remain unchanged until a versioned migration step addresses them:

- **Input schema mismatch**: ENGINE_SPEC requires structured EngineInput (project profile, work graph, engine context). Engine V0 accepts a minimal dict and optional pricing without schema validation. 
- **Output structure mismatch**: ENGINE_SPEC requires a deterministic EngineResult structure (works, materials, tools, equipment, stages, qc, risks, totals, meta). Engine V0 returns a compact, work-specific payload without these fixed placeholders. 
- **Pricing/procurement coupling**: ENGINE_SPEC requires a region-agnostic core without pricing/procurement. Engine V0 computes `material_cost`, `labor_cost`, and `total_cost` inside the core calculator. 
- **CalculationProfile as data**: ENGINE_SPEC requires CalculationProfile to be data-driven and versioned. Engine V0 hardcodes calculation logic in Python and reads norms from a recipe YAML without a formal profile contract.
