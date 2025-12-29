# DOFT Recursive Stack V1 Checklist (Status)

This checklist maps to `docs/STUDY05_code_version20 - Recursive Stack V1 Spec (Ola2–OlaN).md`.

## 0. Scope
- Goal: I/O-first, config-driven recursive stack: DONE (scaffolding + I/O).
- Non-goals enforced (no changes to ola1 engine): DONE.

## 1. Repository Layout
- `src/core/*`: DONE (created).
- `src/olar/*`: DONE (created).
- `src/sm/*`: DONE (created).
- `src/ola1/*` frozen: DONE (untouched).
- Naming rule (no “wave” in new artifacts): DONE (new paths use “ola”).

## 2. Config Organization
- `data/config/run_sequence.json`: DONE.
- `data/config/ola2/*` minimal configs: DONE.
- Additional olaX dirs created: DONE.

## 3. Data Contracts (Recursion Interfaces)
- Block contract fields: PARTIAL (schema helper exists; enforcement not yet strict).
- Entity contract fields: DONE (hard required fields enforced).
- Evaluation contract fields: DONE (hard required fields enforced).
- Genome layer contract fields: DONE (placeholders written for required fields).

## 4. ID and Provenance
- config/code/inputs hash: DONE.
- entity_id from build plan: DONE.
- eval_id policy: DONE (hash of entity_id, seed, engine_params_bin_id, role, schema_version; no floats/config/code).
- machine metadata: DONE.

## 5. Explorer (src/olar/explorer.py)
- Purpose: cheap search only: SCAFFOLD (I/O only).
- Inputs: blocks, DNA, templates, selection rules: DONE.
- Outputs: attempts.jsonl + entities_candidates.jsonl (append-only): DONE.
- Resume index: DONE (scan + dedupe).

## 6. Sweep (src/olar/sweep.py)
- Inputs: attempts/entities: DONE.
- Deterministic seed policy: DONE.
- Outputs: evaluations.jsonl (append-only): DONE.
- Neighborhood rules / budgets: TODO (not implemented beyond I/O).

## 7. Catalog Builder
- Deterministic rebuild from raw logs: PARTIAL (entities/genome/rollups minimal).
- Deleting catalog safe: DONE (rebuilds from logs).

## 8. DOFT Taxonomy
- DOFT-only: DONE.
- Versioned bins/thresholds: PARTIAL (applied if present).
- Provisional vs confirmed families: TODO (Explorer writes provisional_family_id; Sweep writes confirmed_family_id; Catalog publishes).

## 9. Recursion Rule
- Entity -> Block promotion (block_id = entity_id): TODO (not implemented).
- Lineage preserved: TODO.

## 10. Resume / Safety
- Append-only JSONL: DONE.
- Resume index: DONE (scan + dedupe).

## 11. Seed Policy
- Explorer deterministic seeds: DONE.
- Sweep deterministic seeds: DONE.

## Deliverables Checklist (Spec)
- core + olar structure: DONE.
- schemas: PARTIAL (helpers only).
- explorer: SCAFFOLD (I/O only).
- sweep: DONE (I/O only).
- catalog builder: PARTIAL (minimal).
- taxonomy: PARTIAL (minimal).
- recursion support: TODO.
- run_sequence orchestrator: DONE.

## Notes
- This is an I/O-first scaffold; simulation/metrics are intentionally not implemented yet.
