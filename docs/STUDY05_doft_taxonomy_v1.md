# DOFT Taxonomy V1

**DOFT Classification of Individuals (Wave1 → WaveN)**  
**Status:** V1 integrated (no backward compatibility).  
**Goal:** Label and group DOFT individuals using *only internal dynamics* (coherence / locking / memory / topology / robustness), in a recursive, traceable, and hashable way.

---

## 0) Principles (DOFT-only, no SM)

- **DOFT-only:** No rule uses the Standard Model (SM), SM names, distances to SM, or SM-derived features.
- **Recursive by waves:** Each wave adds its own genes and refines classification without rewriting previous waves.
- **Separation of roles:**
  - *Explorer / Sweep* generate raw metrics (observations).
  - *DOFT Classifier* generates labels, IDs, grades, and “families” using only those genes.
- **Traceability:** Every individual has an `entity_id`, a reproducible `build_plan`, and hashes of config / code / data.
- **Versioned operational criteria:** Thresholds and bins are *classification criteria* (operational), not “physical parameters of the universe.” Changing thresholds/bins changes the taxonomy, not engine dynamics. Controlled via `taxonomy_version`.

---

## 1) Identities and Records

### 1.1 `entity_id` (cross-wave individual ID)

`entity_id` identifies the individual as a “construction plan / tree” (DAG).

- **Wave1:** `entity_id = block_id` (or `dof_id` if present).
- **Wave2+:** `entity_id = hash(build_plan_canonical)`.

`build_plan_canonical` (Wave2+) includes:

- `template_name`
- `edges` or `template_signature` (if template-fixed)
- `assignment.block_ids` in canonical order
- `engine_params_base` (base set only, not results)
- minimum `schema_version` (for parsing)
- minimum `code_hash` (to avoid mixing engines)

**V1 recommendation:** “The individual *is* the plan”; therefore `entity_id == candidate_id`. State (genes / grade / family) is computed from evaluations.

### 1.2 `eval_id` (observation ID)

Each run produces an identifiable observation:

```
eval_id = hash(entity_id || seed || neighbor_id || sweep_config_hash || code_hash)
```

### 1.3 Canonical serialization (stable hash without quantizing “physics”)

To ensure hash stability:

- Floats: exact serialization (`float.hex()` or equivalent).
- Canonical JSON: sorted keys, no whitespace, fixed-order arrays.
- `taxonomy_version` and `schema_version` are always recorded with each output.

---

## 2) Provisional vs Confirmed (general rule)

To avoid single-seed “accidents”:

- **Provisional:** Label computed from a single evaluation (typical of Explorer).
- **Confirmed:** Label validated with minimum robustness in a sweep (multiple seeds and/or parameter neighborhood).

Applies to:

- Kingdom (`LOCKED_provisional` vs `LOCKED_confirmed`)
- Family (provisional vs confirmed families)

**Minimum robustness V1:**

- `S_MIN = 2` seeds (absolute minimum)
- *(optional)* neighborhood minimum: `NBR_MIN = 1` valid neighbor

---

## 3) DOFT Tree: Taxonomic Levels

The taxonomy assigns **four levels**:

```
Kingdom → Phylum → Class → Family
```

Each level produces:

- `*_name` (logical name)
- `*_id` (stable hash)
- `*_friendly` (human-readable name)

---

## 4) Kingdom (Dynamic Class)

**Definition:** Grouping by global behavior (zombie / coherence / attractor / boundedness).

### 4.1 Rules (priority order)

Evaluated in this order:

**ZOMBIE**  
If `zombie == true` (tag) or robust negative memory (see §7)  
→ `KINGDOM = ZOMBIE`

**LOCKED (real coherence)**  
If coherence holds in the final window:

- `R_mean_lastW >= R_LOCK_MIN`
- `phase_var_lastW <= PV_LOCK_MAX`

Then:

- Single evaluation → `LOCKED_PROVISIONAL`
- `seed_survival_count_locked >= S_MIN` → `LOCKED_CONFIRMED`

**BOUNDED**  
If `viability_state == BOUNDED` (or equivalent dynamic indicator)

**DRIFT**  
If `attractor_class` indicates drift (`DRIFT_*`)

**UNSTABLE**  
If none of the above

### 4.2 Versioned operational defaults (V1)

- `R_LOCK_MIN = 0.80`
- `PV_LOCK_MAX = 0.05`

These are operational criteria. Changing them bumps `taxonomy_version`; physics does not change.

### 4.3 Output

- `kingdom_name ∈ {ZOMBIE, LOCKED_PROVISIONAL, LOCKED_CONFIRMED, BOUNDED, DRIFT, UNSTABLE}`
- `kingdom_id = sha1("KINGDOM|" + kingdom_name + "|" + taxonomy_version)`
- `kingdom_friendly = kingdom_name`

---

## 5) Phylum (Memory Signature)

**Definition:** Identity by memory (sign + robustness).

### 5.1 Base genes (per evaluation)

- `memory_score_k10`
- `memory_sign ∈ {POS, NEG, ZERO}` (derivable)
- `entropy_quality` (if available)
- `memory_good = (memory_score_k10 > 0)` (V1)

### 5.2 Robust genes (requires sweep)

- `mem_survival_rate = (# seeds memory_good) / N`
- `mem_sign_flip_rate = (# sign changes) / N`
- `mem_param_stability = (% neighbors where memory_good holds)`

### 5.3 V1 Rules

- **MEMORY_POS_STABLE:** `mem_survival_rate >= MS_POS_MIN` and `mem_sign_flip_rate <= MS_FLIP_MAX`
- **MEMORY_MIXED:** intermediate or high flip rate
- **MEMORY_ZERO:** optional dead band around zero
- **MEMORY_NEG_STABLE:** robust negative memory

### 5.4 Versioned defaults (V1)

- `MS_POS_MIN = 0.80`
- `MS_FLIP_MAX = 0.10`

### 5.5 Output

- `phylum_id = sha1("PHYLUM|" + phylum_name + "|" + taxonomy_version)`
- `phylum_friendly = phylum_name`

---

## 6) Class (Topological Morphology)

**Definition:** Structural class via graph invariants (not SM-based).

### 6.1 Topological features

- Number of nodes `N`, edges `E`
- Degree histogram (or bins)
- Flags: `is_chain`, `is_ring`, `is_bipartite`
- `template_name` if template-derived

### 6.2 V1 Rules

- If `template_name` exists → `CLASS = TEMPLATE::<template_name>`
- Else → `CLASS = GRAPH::<topology_signature>`

### 6.3 Output

- `class_id = sha1("CLASS|" + class_name + "|" + topology_signature + "|" + taxonomy_version)`
- `class_friendly = class_name`

---

## 7) Family (Resonant Fingerprint)

**Definition:** Fine grouping by resonant response + robustness. This is the *real DOFT family*.

### 7.1 Golden rule (bins vs raw)

- Raw metrics are always stored as genes.
- Bins are used *only* for:
  - stable grouping
  - stable hash IDs (`family_id`)

Changing bins / thresholds:

- bumps `taxonomy_version`
- does **not** imply a change in dynamics (“physics does not change”)

### 7.2 V1 Fingerprint (minimum)

Recommended bins:

- `omega_eff_bin`
- `R_bin` (from `R_mean_lastW`)
- `PV_bin` (from `phase_var_lastW`)
- `mem_bin` (from `memory_score_k10`)
- `seed_robust_bin` (from survival rate)
- `param_robust_bin` (from neighborhood stability)

Prefixes (not binned): `kingdom_name`, `phylum_name`, `class_name`

### 7.3 Provisional vs Confirmed families

- **Provisional family:** computed from a single evaluation (Explorer). Useful for exploration, not closure.
- **Confirmed family:** requires verification sweep with minimum robustness:
  - `seed_survival_count_locked >= S_MIN`
  - *(optional)* `param_survival_count_locked >= NBR_MIN`

### 7.4 `family_id`

```
family_id = sha1(
  kingdom_name | phylum_name | class_name | fingerprint_bins | taxonomy_version
)
```

### 7.5 `family_friendly` (V1)

Format:

```
<KINGDOM>.<PHYLUM>.<CLASS>.ωbX.RbY.PVbZ.MbK.SRbA.PRbB
```

Example:

```
LOCKED_CONFIRMED.MEMORY_POS_STABLE.TEMPLATE::icosahedron.ωb07.Rb09.PVb01.Mb05.SRb09.PRb06
```

---

## 8) DOFT-only Grades A/B/C (operational selection)

**Definition:** Operational quality for pipeline filtering. Not SM, not “truth”.

### 8.1 Grade per wave

Emit `grade_wave1`, `grade_wave2`, … (no single absolute grade).

### 8.2 Suggested V1 rules for `grade_wave2` (sweep-aware)

- **A** if:
  - `KINGDOM == LOCKED_CONFIRMED`
  - `seed_survival_rate_locked >= 0.80`
  - `mem_survival_rate >= 0.80`

- **B** if:
  - `KINGDOM == LOCKED_PROVISIONAL` with good signals, or
  - `KINGDOM == BOUNDED` with robust positive memory (optional)

- **C** if:
  - `KINGDOM ∈ {ZOMBIE, DRIFT, UNSTABLE}`, or
  - very low robustness

Grade thresholds are versioned operational criteria. Changing them bumps `taxonomy_version`.

### 8.3 Global projection (optional)

```
global_grade = min(grade_wave1, grade_wave2, …)
```

("fail below → fail above")

---

## 9) Data Artifacts (recommended formats)

### 9.1 `entities` (cross-wave)

Per individual / plan:

- `entity_id`, `wave_birth`, `parents[]`
- `build_plan` (template, edge signature, assignment, base params)
- `provenance` (`config_hash`, `code_hash`, `blocks_hash`, `templates_hash`)

### 9.2 `genome_layers` (genes per wave)

Per `(entity, wave)`:

- `entity_id`, `wave`
- raw `genes_*`
- `kingdom / phylum / class / family` (+ friendly)
- `grade_wave`
- timestamps

### 9.3 `evaluations` (sweep output)

Per run:

- `eval_id`, `entity_id`, `seed`, `neighbor_id`
- full raw metrics
- hashes (config / code)

---

## 10) Versioning and Reproducibility

Every relevant record must include:

- `taxonomy_version`
- `schema_version`
- `code_hash`
- `config_hash`

---

## 11) Presentation in Paper / Report (to avoid confusion)

Reports explicitly show **two layers**:

- **Provisional families (Explorer):** exploratory grouping (single evaluation).
- **Confirmed families (Sweep verification):** robustness-validated grouping (≥2 seeds, optional neighborhood).

This makes it clear that the Explorer *proposes* and the Sweep *confirms*, without SM and without bureaucratic rechecking: it is a methodological distinction.

