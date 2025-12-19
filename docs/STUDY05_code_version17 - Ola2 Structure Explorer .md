# DOFT Wave2 (Ola2) – Structure Explorer (Revamp)

**Consolidated Specification (v2.0)**  
Language: English (repo-ready)  
Status: Ready for implementation

---

## 0. Executive summary

Structure Explorer is a structure-discovery stage for DOFT Wave2. It:

- Reads Wave1 promoted blocks (the existing Wave1 output file; same schema, same loader expectations).
- Generates candidate composite structures (template + node assignment + optional edge-weight pattern).
- Evaluates each candidate using Kuramoto + global memory + annealed noise and computes the same key metrics (including `memory_score_k10`).
- Tags everything (no silent dropping).
- Writes two JSONL streams (accepted and rejected), a Markdown report, progress-by-term logs, and a generated `structures_config.json` for the next stage (Wave1-extended frequency scan over composite structures).

---

## 1. Scope and non-goals

### 1.1 In scope

- Structure enumeration (templates + assignment + optional edge-weights).
- Simulation/evaluation with Kuramoto + memory.
- Tagging and logging of all candidates.
- Cross-run memory store (`ExplorerMemory`) and memory-guided search policy.
- Export of `structures_config.json` for the next pipeline stage.
- Progress output “by term” (to track long runs).

### 1.2 Non-goals

- No physics reinterpretation of Wave1. Explorer consumes Wave1 blocks as-is.
- No requirement to preserve legacy Wave2 CSV outputs (new folder + new artifacts).
- No requirement that Wave1 blocks contain per-block hashes/fingerprints. (Optional only.)

---

## 2. Inputs

### 2.1 Mandatory input: Wave1 promoted blocks file

The explorer **MUST** read the existing Wave1 promoted-blocks output file (commonly referred to as `simple_blocks.json` or equivalent) without requiring format conversion. This must be compatible with the current Wave1 output schema so the 4-day scan remains usable.

Required fields per block (minimum):

- `block_id` (preferred)
- `particle_name` (fallback identity if `block_id` missing)
- Any oscillator “genes” needed by the Kuramoto simulator (e.g., intrinsic frequency `omega_i` or derivable equivalent; plus any additional fields currently used by the simulator).

> Note: If the Wave1 file also contains any legacy “compounds” lists, the explorer ignores them by default. See optional warm-start in §6.5.

### 2.2 Templates input: `compound_templates.json`

Defines graph templates used to build composite structures.

Minimum per template:

- `name`
- `nodes` (N)
- `edges` (list of pairs, e.g., `[[0,1],[1,2]]`)

Optional:

- `type` (semantic label)
- Fixed weights per edge if `edge_weight_policy = "fixed_template"` (see §5).

### 2.3 Config input: `structure_explorer.json`

A single JSON config controls targets, search budget, parameter defaults, tagging thresholds, memory persistence, and outputs.

---

## 3. Identifiers and traceability

### 3.1 `run_id` vs `attempt_id` (exact definitions)

**`run_id`**

- Identifies one full execution (“job”) of Structure Explorer.
- Format: UUID (recommended) or timestamp+hash string.
- Constant across all outputs generated in that run.

**`attempt_id`**

- Identifies one candidate evaluation (one Kuramoto simulation on one candidate).
- Integer, monotonic within the run: `0..N-1`.
- Global within the run (does not reset per target).

Optional convenience fields:

- `target_index` (index in `targets[]`)
- `target_attempt_index` (counter local to target)

### 3.2 Input file hashing (mandatory traceability, no per-block hash required)

Because `simple_blocks` may not contain per-block hashes:

- On startup, compute `wave1_input_file_hash` = hash of the entire Wave1 blocks file content.
- Store it in:
  - `meta.json` (run-level metadata)
  - each JSONL record under `source.wave1_input_file_hash`

This guarantees run traceability to the exact Wave1 block universe.

### 3.3 Block identity (no per-block hash required)

Block identity key used for canonicalization and assignment identity:

- Primary: `block_id`
- Fallback: `particle_name`

If neither exists: candidate is invalid → log to `rejected.jsonl` with:

- `tag.viable = false`
- `tag.reason = "invalid_candidate_missing_identity"`

Each record **MUST** state:

- `canonicalization.block_key_used = "block_id" | "particle_name"`

Optional future-proofing: if a per-block hash/fingerprint appears later, it may be used preferentially, but must never be required.

---

## 4. Dynamics engine (Kuramoto + memory) and metrics

### 4.1 Required engine components

The evaluation engine must include:

- Local coupling on the template graph (degree-normalized weights).
- Global memory field `Z(t)` with relaxation `tau_field`.
- Annealed (tempered) noise `sigma(t)` with (`sigma0`, `sigma_tc`).

### 4.2 Engine parameters (defaults are configurable)

Parameters **MUST** be explicitly recorded per attempt:

- `dt`, `T_ticks`, `W`
- `K_local`, `kappa_global`, `tau_field`
- `sigma0`, `sigma_tc`
- `sigma_theta_init`

### 4.3 Mandatory metrics (recorded per attempt)

Each evaluation **MUST** compute and store:

- `R_final`
- `R_mean_lastW`
- `phase_var_lastW`
- `memory_score_k10` (required)
- `PE_tick_norm` (optional if already implemented; recommended)

No candidate record may omit metrics unless the engine fails; in that case set:

- `status.engine_status = "error"`
- store `status.error_message`

and still log the attempt (as rejected).

---

## 5. Edge weights policy (exact behavior)

Edge weights are controlled by `edge_weight_policy`:

### 5.1 `edge_weight_policy = "fixed_template"`

- Each template edge includes a fixed weight.
- The candidate uses template weights as-is.
- Weights are part of structure identity implicitly (because template definition includes them).

### 5.2 `edge_weight_policy = "sample_discrete"`

- Templates define only topology (edges).
- For each candidate, the explorer samples an `edge_weight_pattern`:
  - Each edge weight is selected from `edge_weight_levels` (e.g., `[0.5, 1.0, 2.0]`).

The sampled `edge_weight_pattern` **MUST**:

- be stored in the attempt record.
- be included in canonicalization/structure identity.

Each record **MUST** include:

- `template.edge_weights_mode = "fixed_template" | "sampled"`
- if sampled: `candidate.edge_weight_pattern` in a fixed canonical edge order.

---

## 6. Structure generation and search policy

### 6.1 Candidate structure definition

A candidate is:

- `template_id`
- `assignment`: block identity list in template node order
- optional: `edge_weight_pattern` (if sampled)
- `engine_params`
- `seed`

### 6.2 Canonicalization / symmetry reduction (required)

To avoid wasted compute on equivalent permutations:

- Precompute template automorphisms (for small N: brute-force permutations acceptable).
- Convert assignment to tokens using block identity key (see §3.3).
- Apply each automorphism to the assignment serialization and select the lexicographically minimal serialization as canonical.
- Include `edge_weight_pattern` in serialization when weights are sampled.
- Compute `structure_id = hash(canonical_serialization)`.

This makes structure identity independent of node labeling.

### 6.3 ExplorerMemory persistence (required)

ExplorerMemory is not only a log; it guides search.

Default store:

- JSONL append-only at: `explorer_memory/memory_store.jsonl`
- With a derived `memory_index.json` on load/build.

Modes:

- **Incremental (default):** load store on startup, update and append during run.
- **Rebuild mode (optional):** rebuild memory from prior outputs (accepted/rejected) if configured.

### 6.4 Search phases (required)

Structure Explorer runs two phases:

**Phase 1 — Broad discovery (coverage-first)**

- Prefer novel `structure_id`s.
- Enforce balanced coverage across templates/targets.
- Evaluate each structure with minimal seeds (usually 1).

**Phase 2 — Refinement (stability-first)**

- Select “promising” structures based on configurable rules.
- Run multiple seeds and optionally small parameter-neighborhood sweeps.
- Compute `seed_stability` per structure.

### 6.5 Optional warm-start (not required)

If desired, allow an optional `warm_start` list of previously known structures (e.g., from legacy compounds).  
Default: disabled; the explorer is fully self-contained from Wave1 blocks.

---

## 7. Tagging rules (no filtering)

### 7.1 Tagging is declarative and configurable

Default viability:

```text
viable = (R_mean_lastW > R_min) AND (phase_var_lastW < var_max)
```

Also compute:

- `memory_good = (memory_score_k10 >= mem_k10_min)` (configurable)

### 7.2 Logging rule (strict)

All evaluated candidates **MUST** be logged:

- If `viable = true` → `accepted.jsonl`
- If `viable = false` → `rejected.jsonl`

No attempt is silently dropped.

---

## 8. Export rules for `structures_config.json`

### 8.1 Default export content (exact)

By default, `structures_config.json` includes only structurally confirmed viable structures, defined by config thresholds on aggregated stability, e.g.:

- `seed_stability >= min_seed_stability_for_export` and/or
- `n_viable >= min_viable_hits_for_export`

### 8.2 Optional export of “promising non-viable”

Config flag:

- `export_promising_nonviable = true`

If enabled, include structures that fail viability but satisfy “promising” + memory-good conditions:

- `memory_good = true`
- `R_mean_lastW >= R_promising_min`
- `phase_var_lastW <= var_promising_max`

Each exported structure **MUST** include:

- `export_class = "CONFIRMED_VIABLE" | "PROMISING_MEMORY_GOOD"`

This avoids ambiguity downstream.

---

## 9. Outputs and folder layout

### 9.1 Output folder (new, does not overwrite legacy)

Default layout:

```text
<output_root>/
  explorer/
    accepted.jsonl
    rejected.jsonl
    structures_config.json
    report.md
    progress_terms.jsonl
    report_partial.md            (optional, if enabled)
  explorer_memory/
    memory_store.jsonl
    memory_index.json
  meta.json
```

### 9.2 JSONL schema (fixed; accepted and rejected share schema)

Each line is one JSON object:

```json
{
  "schema_version": "ola2_structure_explorer_v2",
  "run": {
    "run_id": "uuid",
    "attempt_id": 12345,
    "timestamp_utc": "2025-12-18T12:34:56Z",
    "seed": 9912,
    "target_index": 0,
    "target_attempt_index": 812
  },
  "source": {
    "wave1_input_file": "path/to/simple_blocks.json",
    "wave1_input_file_hash": "sha256:..."
  },
  "target": {
    "name": "baryon_explore"
  },
  "template": {
    "name": "baryon_triangle",
    "nodes": 3,
    "edges": [[0,1],[1,2],[2,0]],
    "edge_weights_mode": "sampled"
  },
  "candidate": {
    "edge_weight_pattern": [1.0, 2.0, 1.0]
  },
  "assignment": {
    "block_ids": ["blk_001","blk_812","blk_104"],
    "particle_names": ["rho_1700","meson_ds","lambda_c"]
  },
  "canonicalization": {
    "block_key_used": "block_id",
    "structure_id": "sha1:...",
    "canonical_serialization": "optional_debug_or_null"
  },
  "engine": {
    "dt": 1,
    "T_ticks": 120,
    "W": 20,
    "K_local": 0.15,
    "kappa_global": 0.25,
    "tau_field": 20,
    "sigma0": 0.30,
    "sigma_tc": 60,
    "sigma_theta_init": 0.5
  },
  "metrics": {
    "R_final": 0.93,
    "R_mean_lastW": 0.91,
    "phase_var_lastW": 0.011,
    "memory_score_k10": 0.12
  },
  "tag": {
    "viable": true,
    "memory_good": true,
    "reason": "locked",
    "thresholds_used": {
      "R_mean_lastW_min": 0.85,
      "phase_var_lastW_max": 0.02,
      "memory_score_k10_min": 0.0
    }
  },
  "status": {
    "engine_status": "ok",
    "error_message": null
  }
}
```

### 9.3 `progress_terms.jsonl` (term-based progress, mandatory)

Every term interval (by attempts and/or seconds) append one record:

- term index
- evals in term + cumulative
- viable in term + cumulative
- unique structures discovered
- template/target breakdown
- best structure so far (by configured score)

### 9.4 `report.md` (mandatory)

Must include:

- Overview counts and acceptance rate
- Coverage by target/template
- Distributions and top-k tables for key metrics
- Pareto-style summary (maximize `R_mean_lastW`, minimize `phase_var_lastW`, optionally include `memory_score_k10`)
- Memory effectiveness (unique structure count, repeat avoidance, phase1 vs phase2 summary)

### 9.5 `meta.json` (mandatory)

At minimum:

- `run_id`, timestamps
- full resolved config snapshot
- `wave1_input_file` and `wave1_input_file_hash`
- environment info (optional): git commit, hostname, python version

---

## 10. Parameter binning (optional, if engine variation enabled)

If the explorer samples parameter neighborhoods or bins:

- define bin edges arrays in config.
- bins are left-inclusive / right-exclusive, last bin closed.
- `parameter_bin_id` includes:

  - `K_local`, `kappa_global`, `tau_field`, `sigma0`, `sigma_tc`

- format:

  - `K{idx}_k{idx}_tau{idx}_s0{idx}_stc{idx}`

If engine variation is disabled, `parameter_bin_id = "fixed_defaults"`.

---

## 11. Implementation notes (for the programmer)

- Do not require any new Wave1 scan or data enrichment step.
- Always log rejected attempts (including errors) for traceability.
- Canonicalization must be deterministic and must match stored `structure_id` exactly across reruns with identical inputs + seeds.
- Prefer JSONL for high-volume logging; avoid CSV as the primary artifact in this revamp.

---

## Appendix A — Minimal config example

```json
{
  "schema_version": "ola2_structure_explorer_v2",
  "inputs": {
    "blocks_json": "data/processed/blocks/simple_blocks.json",
    "templates_json": "blocks/compound_templates.json"
  },
  "targets": [
    {
      "name": "baryon_explore",
      "templates": ["baryon_triangle", "baryon_chain"],
      "allowed_block_families": ["quark_like", "pion_like"],
      "allowed_particle_names": [],
      "budget_evals": 20000
    }
  ],
  "engine_defaults": {
    "dt": 1,
    "T_ticks": 120,
    "W": 20,
    "K_local": 0.15,
    "kappa_global": 0.25,
    "tau_field": 20,
    "sigma0": 0.30,
    "sigma_tc": 60,
    "sigma_theta_init": 0.5
  },
  "templates": {
    "edge_weight_policy": "sample_discrete",
    "edge_weight_levels": [0.5, 1.0, 2.0]
  },
  "tagging": {
    "R_mean_lastW_min": 0.85,
    "phase_var_lastW_max": 0.02,
    "memory_score_k10_min": 0.0
  },
  "export": {
    "min_seed_stability_for_export": 0.4,
    "min_viable_hits_for_export": 3,
    "export_promising_nonviable": false
  },
  "search_policy": {
    "phase1_fraction": 0.7,
    "phase2_fraction": 0.3,
    "phase2_seed_repeats_per_structure": 10
  },
  "canonicalization": {
    "enabled": true,
    "method": "template_automorphisms_lexmin",
    "block_key_preference": ["block_id", "particle_name"]
  },
  "memory_store": {
    "enabled": true,
    "format": "jsonl",
    "incremental": true
  },
  "progress": {
    "term_attempts": 500,
    "term_seconds": 10,
    "write_partial_report": true
  },
  "outputs": {
    "root": "data/ola2_structure_explorer_v2"
  }
}
```
