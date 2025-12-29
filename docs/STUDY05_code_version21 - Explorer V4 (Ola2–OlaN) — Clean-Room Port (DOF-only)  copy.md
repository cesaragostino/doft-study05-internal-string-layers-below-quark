# Explorer V4 (Ola2–OlaN) — Clean-Room Port (DOF-only)

## 1. Purpose

Build a **DOF-only Explorer V1** that searches candidate structures using predefined templates, evaluates them with a *cheap engine*, and writes results as **append-only JSONL streams** so that a downstream **Sweep** can consume promising candidates in parallel.

Explorer V4 **must be SM-agnostic by default**: no SM data may influence sampling, gating, or scoring.

---

## 2. Scope

### Included

Explorer V4 includes:

- DOF block pool loading from Ola1 outputs  
- DOF-only sampling  
- Template-based structure construction, canonicalization, and stable IDs  
- Cheap engine evaluation and metric computation  
- DOF-only gating into candidates  
- Append-only writers with safe resume capability  

### Explicitly Excluded

Explorer V4 explicitly excludes:

- SM matching or SM-based weighting  
- Backward compatibility layers beyond reading the Ola1 DOF DNA table  
- “Scientific cross-validation” between Explorer and Sweep  
  *(Sweep refines; it does not validate Explorer decisions)*

---

## 3. Inputs (DOF-only)

Explorer reads:

- `simple_blocks.json` — Ola1 blocks/entities  
- `dof_dna_catalog.csv` — Ola1 DOF DNA (**required**)  
- `ola2_templates.json` — templates / topologies  
- `ola2_explorer.json` — Explorer configuration  
- `doft_run_inputs_v4.json` — run wiring and path routing  

Optional (audit channel only):

- SM artifacts **may exist** but must not influence sampling, gating, or ranking.

---

## 4. Outputs (Append-only)

Explorer **must always write**:

- `attempts.jsonl` (append-only)  
  - One record per evaluated attempt  
  - Full metrics and provenance  

- `entities_candidates.jsonl` (append-only)  
  - Subset of attempts passing DOF gating  
  - Minimal payload for Sweep streaming  

Both files must be **append-safe and resumable**.

---

## 5. Clean-Room Port Rule

Legacy Explorer code may be reused **only mechanically**, by copying individual functions (not files).

### Allowed Re-use (copy/adapt only)

- Structure construction, canonicalization, and stable `structure_id`  
- Cheap engine runner and metric computation  
- Attempt record schema and provenance formatting  

### Forbidden Re-use (must be rewritten DOF-only)

- Any SM-based sampling or filters  
- Any “fallback if DNA missing” logic  
- Any dependency on SM universe data  

---

## 6. Architecture (Module Boundaries)

Explorer V4 is implemented with strict separation of concerns.

### 6.1 CLI Layer

**`src/olar/explorer_cli.py`**

Responsibilities:

- Parse CLI arguments  
- Load configs  
- Resolve input/output paths  
- Initialize append-only writers  
- Drive the main loop  

---

### 6.2 Pool / Sampling Layer (Critical DOF-only)

**`src/olar/explorer_pool.py`**

Responsibilities:

- Load blocks from `simple_blocks.json`  
- Load `dof_dna_catalog.csv`  
- Join blocks with DOF genes (`dof_grade`, `dof_family_id`, …)  
- Apply DOF-only filters:
  - Allowed grades  
  - Allow/deny family IDs  
  - Optional quality constraints  

Sampling modes:

- `uniform` (default)  
- `dof_grade_boost` (optional)  

**Hard rule:** no SM fields may be read here.

---

### 6.3 Search / Plan Layer

**`src/olar/explorer_search.py`**

Responsibilities:

- Select target and template per config  
- Assign blocks to nodes  
- Canonicalize node order  
- Generate stable plan identifiers (`plan_id`, `structure_id`)  
- Choose parameter bins and engine parameters  

---

### 6.4 Engine / Evaluation Layer

**`src/olar/explorer_engine.py`**

Responsibilities:

- Run cheap engine simulation  
- Compute metrics:
  - `R_mean_lastW`
  - `phase_var_lastW`
  - `QualityLock`
  - `memory_score_k10`
  - `omega_eff`
  - …  

- Compute DOF-only tags and reasons  
- Emit full attempt record to `attempts.jsonl`  
- If candidate passes gating → emit minimal record to `entities_candidates.jsonl`  

---

## 7. Candidate Gating (DOF-only)

Candidate gating is **operational**, not physical law.  
Thresholds live in `ola2_explorer.json` and are versioned.

Recommended minimum gating:

- `R_mean_lastW >= R_min`  
- `phase_var_lastW <= phase_var_max`  
- `QualityLock >= qlock_min`  
- `memory_score_k10 >= mem_min`  
  *(soft vs hard controlled by `viability_mode`)*  

Candidate gating **must never consult SM**.

---

## 8. Identifiers and Provenance

Explorer records must include **stable IDs** and **full provenance**.

### 8.1 Provenance

Each record must include hashes:

- `config_hash`
- `blocks_hash`
- `templates_hash`
- `code_hash`

Plus machine metadata (Python version, platform).

---

### 8.2 IDs

Two-level hashing:

**`plan_id`** (a.k.a. `entity_id`)  
Stable hash of the construction blueprint **only**:
- `template_name`
- canonical edges
- `canonical_node_order`
- assignment (`block_ids` aligned to `canonical_node_order`)

Goal: identical structure + assignment → identical `plan_id`.

**`eval_id`**  
Hash of:
- `entity_id`
- `seed`
- `engine_params_bin_id` (a.k.a. `param_bin_id`)
- `role` (e.g. `"explorer"`)
- `schema_version`

Goal: different seeds or bins → different evaluations.

Notes:
- Do **not** include engine params (floats) in `eval_id`.
- Do **not** include provenance hashes in `eval_id`; keep them in `provenance`.

`attempt_id` may be sequential, but **`eval_id` is the dedupe key**.

---

## 9. Append-only + Resume Semantics

Implement in **`src/core/io/jsonl.py`**:

- Atomic line-delimited JSON writes  
- Resume by scanning existing files  
- Build set of existing `eval_id`s  

On resume:

- If `eval_id` exists → skip  
- Else → append  

This guarantees safe stop/restart without corruption.

---

## 10. Acceptance Criteria (No-Leak + Correctness)

Explorer V4 is acceptable if it:

- Runs with **no SM files present**  
- Uses **only DOF data** for sampling and gating  
- Always produces:
  - `attempts.jsonl`
  - `entities_candidates.jsonl`  
- Resumes without duplicating `eval_id`s  
- Emits records with complete provenance and stable IDs  
