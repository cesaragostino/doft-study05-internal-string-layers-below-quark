# SPEC — Paper Metrics Pack (Ola2+ / DOFT-only)

# PREREQUISTE

Ensure that the pipeline exports the following **claim-bearing outputs** (for papers and for system control) in a **deterministic and auditable** way:

- **technical_viable_rate (S4.4)** = “passed sweep” (simple, non-taxonomic definition)
- **taxonomy rates (S4.5)** = attractor_class rates, promoted_rate, etc.
- **R_network / PE_lock / H_part** (already present)
- **Robustness by seeds (v1)**
- **Robustness by bins (v2)**
- **time_per_eval** and **nan_rate**
- **N = node_count** materialized explicitly

---

## Minimal Changes and Where They Belong

### A) `evaluations.jsonl` (Sweep) — Per-evaluation Instrumentation

No changes to the engine itself; only add scalar fields per evaluation.

#### A1. Persist Seeds per Evaluation

Add to each record in `evaluations.jsonl`:

- `seed_index: int` — index within the planned evaluations for that entity (0..planned_evals−1)
- `seed_u32: int` — actual seed value used in the simulation

This enables **true robustness v1** (per-seed std + success rate).

#### A2. Persist Parameter Bin

Ensure each evaluation stores:

- `engine_params_bin_id: str`

(If already present, no change needed.)

#### A3. Runtime per Evaluation

Add:

- `runtime_sec: float` — wall-clock time for this evaluation (measured via `perf_counter()`)

#### A4. Finite / NaN Flags (Paper-safe)

Add:

- `is_finite_primary: bool`
- `nan_primary_count: int`

**Primary metrics** (example set):
- `R_network_S1_mean`
- `PE_lockS1_norm_mean`
- `H_part_norm_mean`

Rules:
```
is_finite_primary = all(isfinite(m) for m in primaries)
nan_primary_count = count(not isfinite(m) for m in primaries)
```

#### A5. `sweep_passed` (Technical) per Evaluation

Add:

- `sweep_passed: bool`

Rule (S4.4, non-taxonomic):

```
sweep_passed = (status == "ok") AND is_finite_primary
```

This avoids circularity with S4.5. Taxonomy classifies later; S4.4 only counts “passed”.

#### A6. Strict JSON

No arrays. Short lists of strings for `tags_raw` / `reasons_raw` are acceptable.

---

### B) `genome_layers_olaN.csv` (Catalog Builder)

The builder performs a LEFT JOIN: candidates ← evaluations. Add derived columns here.

#### B1. Explicit `node_count` (N)

Add column:

- `node_count: int`

Derivation order (deterministic):
1. `len(entity.build_plan.assignment.block_ids)`
2. fallback: `len(entity.build_plan.canonical_node_order)`
3. final fallback: `len(entity.assignment.block_ids)` if present

#### B2. Sweep Counters

Add per-entity columns:

- `sweep_evals_planned: int`
- `sweep_evals_total: int`
- `sweep_passed_total: int`
- `sweep_passed_any: bool` (= `sweep_passed_total > 0`)
- `nan_primary_total: int`
- `nan_primary_rate: float`

```
nan_primary_rate = nan_primary_total / (sweep_evals_total * num_primary)  if total > 0
```

From this:
```
technical_viable_rate = mean(sweep_passed_any)
```

#### B3. Robustness v1 (by Seeds)

Requires A1 + A5.

Add:

- `seed_success_rate = sweep_passed_total / sweep_evals_planned` (if planned > 0)
- Means and stds over evaluations with `sweep_passed=True`:
  - `R_network_S1_mean_mean`, `R_network_S1_mean_std`
  - `PE_lockS1_norm_mean_mean`, `PE_lockS1_norm_mean_std`
  - `H_part_norm_mean_mean`, `H_part_norm_mean_std` (optional)

#### B4. Robustness v2 (by Bins)

Requires A2 and bin exploration in sweep.

Add per entity:

- `bins_used_count: int`
- `R_network_over_bins_std: float`
- `PE_lock_over_bins_std: float`

Computation (no arrays):
1. Group `sweep_passed` evals by `engine_params_bin_id`
2. Compute mean(R), mean(PE) per bin
3. Take std across bin means

Optional: min/max bin success rates.

#### B5. Timing

Add per entity:

- `runtime_sec_mean`
- `runtime_sec_p95` (optional)
- `time_per_eval_sec_mean` (alias of mean)

---

### C) `genome_layers_olaN_taxonomy.csv` (Taxonomy)

This already contains `attractor_class` and grades. Close definitions here.

#### C1. Propagate Technical Fields

Propagate (or recompute via join):

- `node_count`
- `sweep_passed_any`
- robustness fields (if needed for plots)

#### C2. `promoted` Flag

Add:

- `promoted: bool`

Rule:
```
promoted = (dof_grade in allowed_grades)
```

Also store in rollup metadata:
- `allowed_grades_used: "A,B"`

---

### D) Rollups (`rollups.json`, `taxonomy_rollups.json`)

#### D1. `rollups.json` (Technical)

Include:

- `candidates_total`
- `evaluated_total`
- `technical_viable_rate`
- `nan_primary_rate_global`
- `time_per_eval_sec_mean_global`

Optional breakdowns by `node_count` and `template_name`.

#### D2. `taxonomy_rollups.json` (Taxonomic)

Include:

- `attractor_class_rate`
- `promoted_rate` (define denominator explicitly)
- Breakdowns by `node_count` and template family

---

## On `dof_grade` in `genome_layers_olaN.csv`

Current behavior (correct): `dof_grade` is guaranteed in `_taxonomy.csv`.

Clean separation:

- `genome_layers_olaN.csv`: technical + robustness + N
- `genome_layers_olaN_taxonomy.csv`: adds taxonomy (`attractor_class`, `dof_grade`, `promoted`)

If convenience is needed, produce an additional:
- `genome_layers_olaN_enriched.csv` after taxonomy (no taxonomy logic inside the builder).

---

## Implementation Checklist (Priority Order)

1. **Sweep**: add `seed_index`, `seed_u32`, `engine_params_bin_id`, `runtime_sec`,
   `is_finite_primary`, `nan_primary_count`, `sweep_passed`
2. **Catalog builder**: `node_count`, counters, robustness v1/v2, timing
3. **Taxonomy**: propagate fields + `promoted`
4. **Rollups**: global rates + breakdowns

## Canonical Definitions (Non‑Negotiable)

### 1) `sweep_passed` / `viable`

**Goal:** ensure that `viable_rate` does not depend on post‑hoc inference.

#### `sweep_passed` (technical)

Boolean.

`True` if the entity has **≥ 1 valid evaluation** in `evaluations.jsonl`
(i.e. `sweep_evals_total > 0`) **and** the run produced **finite metrics**
(no NaN / None) for the minimum required primaries.

**Minimum finite primaries (example):**
- `R_network_S1_mean`
- `PE_lockS1_norm_mean`
- `H_part_norm_mean`
(or whatever set is currently defined as the primary base)

If **any** of these is NaN / None ⇒ `sweep_passed = False`.

#### `viable` (taxonomic, optional but recommended)

Boolean.

`True` if `attractor_class != INCOHERENT`.

(Optional stricter version):  
`viable := attractor_class ∈ {FUNCTIONAL_LOCK, HYPER_SYNC}`

#### Reporting levels

- **passed_rate (technical)** = mean(`sweep_passed`)
- **viable_rate (taxonomic)** = mean(`viable`)

---

### 2) `promoted`

**Definition:**

`promoted := dof_grade ∈ allowed_grades` (e.g. `{A, B}`)

This must be explicitly documented in `taxonomy_rollups.json`.

---

## Checklist — What to Add and Where

### P0 — Always Materialize `N` (node count)

**Where:** catalog builder (S4/S5) or wherever `genome_layers_olaN.csv` is built.

**New field:**
- `node_count: int` (alias `N`)

**Deterministic derivation:**
- From `entities.jsonl`:  
  `len(build_plan.assignment.block_ids)`  
  (or `len(canonical_node_order)` if that is the only consistent source)

**Hard‑fail** if it cannot be derived.

**Acceptance:**
- `genome_layers_olaN.csv` and `genome_layers_olaN_taxonomy.csv`
  both include `node_count`.

---

### P1 — Persist `sweep_passed` (technical) in genome / taxonomy

**Where:** catalog builder (technical rollups, S4.4), via LEFT JOIN
candidates ← evals.

**New per‑entity fields (in `genome_layers_olaN.csv`):**
- `sweep_evals_total: int`
- `sweep_passed: bool`
- `nan_primary_count: int`
- `nan_primary_rate: float` (`nan_primary_count / num_primaries`)

**Rule:**
```
sweep_passed = (sweep_evals_total > 0) and (nan_primary_count == 0)
```

**Acceptance:**
- Orphan entities (no evals) have:
  `sweep_evals_total = 0`, `sweep_passed = False`, metrics = null.

---

### P2 — Robustness v1 (seeds) + `seed_success_rate`

**Problem:** current pipeline does not expose dispersion by seed.

#### P2.1 Minimal persistence per evaluation

**Where:** `evaluations.jsonl` (Sweep output)

Ensure each record contains:
- `entity_id`
- `seed_index` (or `seed_u32`, but must identify the seed per entity)
- `engine_params_bin_id`
- primary metrics (`R_network_S1_mean`, `PE_lockS1_norm_mean`, etc.)
- `is_finite_primary: bool` (new)

`is_finite_primary = True` if all minimum primaries are finite.

**Important:** no arrays — only scalars + tags/reasons.

#### P2.2 Per‑entity aggregation (builder)

**Where:** catalog builder, grouping evals by `entity_id`.

Compute:
- `seed_evals_total`
- `seed_success_count = sum(is_finite_primary)`
- `seed_success_rate = seed_success_count / seed_evals_total` (if total > 0)
- `R_seed_mean`, `R_seed_std`
- `PE_seed_mean`, `PE_seed_std`

**Robustness score v1 (simple):**
```
robust_R  = 1 - std(R)  / max(eps, abs(mean(R)))
robust_PE = 1 - std(PE) / max(eps, abs(mean(PE)))
robust_score_v1 = clamp(min(robust_R, robust_PE), 0, 1)
```

**Acceptance:**
- These fields appear in `genome_layers_olaN.csv`
  and/or `_taxonomy.csv`.

---

### P3 — Robustness v2 (bins / neighborhood)

**Only include if used in the paper.**

**Requirement:** each eval has `engine_params_bin_id` and `entity_id`.

**Where:** catalog builder (additional aggregation).

Per entity:
- group evals by `bin_id`
- compute variation:
  - `R_bin_std`
  - `PE_bin_std`

**Score:**
```
robust_score_v2 = 1 - std_over_bins(metric) / max(eps, mean(metric))
```

If the sweep already enforces “base bin + neighbors”, this falls out naturally.

---

### P4 — `time_per_eval` (performance), no global timestamps

**Where:** Sweep, during each differential engine run.

Add per evaluation:
- `runtime_sec: float` (wall‑clock time)

(Optional: `ticks_simulated`, `dt`, `T_ticks`, `W`
if not already in config/provenance.)

**Builder aggregation (per entity):**
- `runtime_sec_mean`
- `runtime_sec_p50`
- `runtime_sec_p95` (optional)

**Acceptance:**
- Enables cost vs `N` / template analysis.

---

### P5 — Explicit `promoted_rate` in rollups

**Where:** `taxonomy_rollups.json` and/or `rollups.json`

Add:
- `allowed_grades` (copied from config)
- `promoted_count`
- `promoted_rate`

**Definition (textual):**
```
promoted := dof_grade ∈ allowed_grades
```

---

## Exact Deliverables to Produce

### In `genome_layers_olaN.csv` (minimum for paper)

- `entity_id`
- `template_name`
- `node_count`
- `sweep_evals_total`
- `sweep_passed`
- `attractor_class` (if present; otherwise in `_taxonomy.csv`)
- `dof_grade`
- `R_network_S1_mean`
- `PE_lockS1_norm_mean`
- `H_part_norm_mean`
- `seed_success_rate`
- `robust_score_v1`
- *(optional)* `robust_score_v2`
- `runtime_sec_mean`
- `nan_primary_rate`

### In `rollups.json`

- **totals:** `candidates`, `orphans`, `sweep_passed_count`,
  `viable_count`, `promoted_count`
- **rates:** `passed_rate`, `viable_rate`, `promoted_rate`
- breakdowns by `template_name` and by `node_count`

---

## Acceptance Tests (to close the chapter)

- **LEFT JOIN preserves orphans:**  
  `entities_candidates_count == genome_layers_rows_count`

- **Determinism:**  
  run builder twice ⇒ identical outputs (ordering, hashes, counts)

- **No arrays in JSONL:**  
  `evaluations.jsonl` contains only scalars + string lists (tags/reasons)

- **Semantic checks:**
  - `sweep_passed = False` if `sweep_evals_total = 0`
  - `seed_success_rate ≤ 1`
  - `robust_score_v1 ∈ [0, 1]`
