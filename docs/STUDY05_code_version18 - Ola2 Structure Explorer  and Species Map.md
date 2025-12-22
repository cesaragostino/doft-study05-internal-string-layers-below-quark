# DOFT – Ola2 Structure Explorer & Species Map  
**SPEC v1.1 (functional closure + implementation guide)**  
Date: 2025-12-21 (America/Argentina/Buenos_Aires)

> **Goal:** Generate and catalog *resonant species* in DOFT (structure + oscillators + memory), without guiding the search with the Standard Model (SM).  
> The SM appears only as an **observer** for later tagging.  
> **Nothing is discarded:** everything is classified (taxonomy) and reported.

---

## 1) Theoretical framework (what is “real” in DOFT)

### 1.1 DOFT ontology (axioms)

**A0. Nothing is discarded.**  
Every attempt is persisted. “viable / nonviable / …” is a **tag** (taxonomy), not an ontological filter.

**A1. SM does not guide the search.**  
`particle_name`, `d_total`, `allowed_particle_names`, or any SM data must **not** be used to propose structures/params.  
SM only lives in `labels_observer` (post).

**A2. Hard parameters = the only “real” objects.**  
What is real in DOFT = **structure (graph + weights)** + **engine parameters** + **memory** + **dynamics**.  
“Mass”, “gap”, “levels”, etc. are **emergent**: observer readout functions over DOFT invariants.

**A3. Wave1 is frozen.**  
Wave1 sweep and post-processing are not modified in this version. Wave2 fixes the “purism”.

---

### 1.2 What Wave1 vs Wave2 produce (to avoid confusion)

- **Wave1** produces *blocks* (DOFs) and their descriptors (peaks, omega_ref, etc.).  
  There is no structure (nodes/edges), therefore **no geometric Lock Signature** of a cluster exists in Wave1.

- **Wave2** produces *clusters* (structure + collective dynamics).  
  Here the following do exist:
  - `memory_score_k10` of the cluster
  - `Lock Signature LS(p/q)` as resonant geometry of the cluster
  - lock stability (width) measured via seeds/neighbors

> Consequence: the **MemoryScore vs LS(p/q)** map is **Wave2-only**. Not touching Wave1 does not reduce quality; it avoids inventing an LS that does not really exist there.

---

## 2) DOFT invariants and emergent observables

### 2.1 DOFT invariants (minimum set)

- **Structure**: template + graph + edge_weights + block assignment per node.
- **Hard parameters**: `engine_params` (couplings, dt, W, ticks, taus/memory, noise, etc.).
- **Dynamics**: phases/velocities (or whatever the engine uses internally).
- **Internal observables** (already present in your engine):  
  `R_final`, `R_mean_lastW`, `phase_var_lastW`, `edge_phase_diff_mean_lastW`, `edge_phase_diff_std_lastW`,  
  `QualityLock`, `entropy_quality`, `memory_score_k10`, energies (if applicable).

### 2.2 Lock Signature (LS) as resonant geometry

**Idea:** the identity of a DOFT “species” is not its mass; it is its **locking geometry**.  
LS captures *which rational relations* appear between effective frequencies of connected nodes.

- For each node `i`, estimate ω̄_i in the last window (lastW).
- For each edge (i,j), ratio: r_ij = ω̄_i / ω̄_j
- Approximate r_ij by a small fraction p/q if it quantizes (bounded denominators).
- Also store the *prime signature* (factorization of p and q).

This allows you to:
- catalog species (resonant DNA),
- measure lock stability/width via LS robustness,
- later define a “DOFT gap” as a critical threshold where LS breaks.

---

## 3) Functional specification (what the system must do)

### 3.1 Inputs

- `ola1_blocks.json` (pool of blocks)
- `compound_templates.json` (structure templates)
- `structure_explorer_config.json` (exploration config)
- (optional) `origin_tags` for human traceability (does not affect proposal)

### 3.2 Outputs (event sourcing)

**Single source of truth:**
- `attempts.jsonl` (1 record per attempt)

**Derived (views / exports):**
- `views/viable.jsonl`, `views/nonviable.jsonl`, `views/unstable.jsonl` (optional)
- `species_catalog.jsonl` (derived from attempts)
- `report.md` (derived)

> Rule: every export must be regenerable from `attempts.jsonl`.

---

### 3.3 Proposal (generation) – DOFT-blind

#### 3.3.1 Structure proposer
- samples template (dimer/triangle/…)
- samples blocks for nodes
- samples edge_weights if applicable
- produces canonical `structure_id`

**Forbidden:** using SM (`d_total`, names, etc.) in the proposal.

#### 3.3.2 Parameter proposer (engine_params)

##### 3.3.2.X Adaptive coupling (MarcoPolo): dimensionless α/β
**Motivation:** locking depends primarily on the frequency dispersion between nodes (Δω), more than on the absolute scale. To avoid per-wave *manual tuning*, coupling is parameterized in a **relative/dimensionless** way.

**Definitions per attempt (structure already instantiated):**
- `omega0_i`: base frequency per node (Wave3: `omega0_i = omega_eff` of the super-block).
- `delta_omega_raw = std_i(omega0_i)`  (**store this as-is** in the record)
- `delta_omega_eff = max(delta_omega_raw, omega_floor)`  (only for mapping α→K and to avoid division by zero)

**Dimensionless parameters:**
- `coupling_alpha = K_local / delta_omega_eff`
- `coupling_beta  = kappa_global / delta_omega_eff`

**Sampling (key):**
- `alpha ~ log_uniform(alpha_min, alpha_max)` with `alpha_range = [0.2, 20.0]`
- `beta  ~ log_uniform(beta_min,  beta_max)` with `beta_range  = [0.05, 5.0]`
- `K_local      = alpha * delta_omega_eff`
- `kappa_global = beta  * delta_omega_eff`

**Recommended persistence (clean contract):**
- `engine_params`: executed values (`K_local`, `kappa_global`, etc.)
- `derived`: `delta_omega_raw`, `delta_omega_eff`, `omega_floor`, `coupling_alpha`, `coupling_beta`
- `taxonomy`: tags/classes only (keep it clean)

**Note on eps/floor:**
- Default: `omega_floor = 1e-12` (equivalent to eps).
- If `omega_floor` is increased for numerical reasons, it must **not** replace `delta_omega_raw`; it only affects `delta_omega_eff`.

---

### 3.4 Simulation and metrics

#### 3.4.X ω_eff (effective frequency) – pure DOFT
**Goal:** enable emergent observables (e.g., mass via ħ) and reinforce LS(p/q) construction from **phase dynamics**, without using energies as the primary source.

**Source (engine):** per-node phase θ_i(t). Compute via *unwrap* and discrete derivative:
- ω_i(t) = (unwrap(θ_i(t)) − unwrap(θ_i(t−1))) / dt

**Summary in the last window `lastW`:**
- `node_omega_mean_lastW[i] = mean_{t∈lastW}(ω_i(t))`
- `node_omega_std_lastW[i]  = std_{t∈lastW}(ω_i(t))`

**Chosen definition (precise / tied to DOF):**
- `omega_eff = sqrt( mean_i( node_omega_mean_lastW[i]^2 ) )`  (RMS)
- `omega_eff_method = "rms"`

**Minimum per-attempt persistence:**
- `node_omega_mean_lastW` (list[float], length N)
- `node_omega_std_lastW`  (list[float], length N)
- `omega_eff` (float)
- `omega_eff_method` (string)

**Notes:**
- `node_omega_mean_lastW` can be negative; `omega_eff` (RMS) guarantees `omega_eff ≥ 0`.
- For Wave3 (species-as-blocks), the super-block’s `omega0` is taken as the species’ `omega_eff`.

`simulate_ola2(structure, engine_params, seed) -> metrics + (optional traces)`

**Minimum required metrics** (already exist or have equivalents):
- coherence: `R_final`, `R_mean_lastW`, `phase_var_lastW`
- lock/proxies: `edge_phase_diff_mean_lastW`, `edge_phase_diff_std_lastW`, `QualityLock`, `entropy_quality`
- memory: `memory_score_k10`
- energy: (if available) `PE_tick_norm`, `E_local_*`

---

### 3.5 Lock Signature LS(p/q) – (Wave2-only)

**Fixed quantization parameters** (defaults):
- `max_den = 31`
- `epsilon_rel = 1e-3`

**Operational definition:**
- unwrapped phase θ_i(t)
- ω_i(t) = (θ_i(t) - θ_i(t-1)) / dt
- ω̄_i = mean(ω_i(t)) for t in lastW
- r_ij = ω̄_i / ω̄_j
- rationalization: p/q with q<=max_den and relative error < epsilon_rel

**Per edge, store:**
- `ratio_raw`
- `ratio_pq` (string "p/q" or null if it does not quantize)
- `residual_rel`
- `p_factors` and `q_factors` (prime signature)

#### 3.5.1 LS canonicalization (no extra dependencies)
The explorer must produce:
- `canonical_node_order` (list of nodes in canonical order)

Then:
- re-express edges as indices in that order
- sort edges by (min(u), max(v))
- `LS_hash = sha256( canonical_edge_list_of_ratio_pq + primes + residual_bucket )`

> It is recommended to “bucket” the residual (e.g., 1e-4, 1e-3, 1e-2) to avoid numerical noise creating unintended distinct species.

---

### 3.6 Taxonomy (classification without filtering)

#### 3.6.X Sanity tag: ZOMBIE (negative memory)

**Simple rule (v1):**
- If `memory_score_k10 < 0` ⇒ add tag `ZOMBIE`.

**Axiom:** `ZOMBIE` neither deletes nor alters the existence of the attempt; it only tags it. It must not, by itself, change `viable_state` or `export_class`.

**Optional artifacts (human navigation, without bloating Mongo):**
- `zombies.tsv` (TSV): `attempt_id	species_id	memory_score_k10`
- `zombie_species.tsv` (TSV): `species_id	zombie_rate` where `zombie_rate = zombie_count / n_trials`

**Recommended use:** find “the bad within the good” and detect *tainted* species (with `zombie_rate > 0`) without filtering anything out.

---

### 3.7 Stability / lock width

**Configurable in the explorer config** (important):

- `N_seed` (for per-seed stability, recommended 15–20; safe default 12)
- `N_seed_probe` (for neighborhood probes, recommended 10–15; safe default 5)
- `param_neighbor_rel = 0.05` (±5% by default)
- `params_sensitive = [...]` (list of parameters to “move”)

#### 3.7.1 LS_stability_seed
For nominal (structure, engine_params):
- run `N_seed` seeds
- compute `LS_hash` per seed
- `LS_stability_seed = max_count(LS_hash) / N_seed` (mode/majority)

#### 3.7.2 LS_stability_param
Neighborhood: for each sensitive parameter p:
- test p*(1-δ), p, p*(1+δ) with δ = `param_neighbor_rel`
- total points: `N_param = 1 + 2*len(params_sensitive)` (no cross-combinatorics)

At each point:
- run `N_seed_probe` seeds
- obtain `LS_hash_mode(point)`
Then:
- `LS_stability_param = (#points with LS_hash_mode == LS_hash_mode(nominal)) / N_param`

#### 3.7.3 lock_width_index (exact formula)
- `lock_width_index = min(LS_stability_seed, LS_stability_param)`

---

### 3.8 Species catalog (DNA / DOFT mitosis)

#### 3.8.1 memory_bin (explicit bins)
Since `memory_score_k10` can be negative, default bins:

`[-inf, -0.5, 0.0, 0.5, 0.8, 0.9, 0.95, 0.98, +inf]`

Store:
- `memory_bin_id`
- `memory_bin_label`

#### 3.8.2 species_id
`species_id = sha256(template + structure_id + LS_hash + memory_bin_id)`

> Interpretation: “same species” = same resonant geometry + same memory context (binned).

#### 3.8.3 DOFT grade (explicit)
- **Grade A**:
  - `attractor_class == COHERENT_LOCKED`
  - `R_mean_lastW >= 0.95`
  - `lock_width_index >= 0.70`

- **Grade B**:
  - `attractor_class == COHERENT_LOCKED`
  - `R_mean_lastW >= 0.85`
  - `lock_width_index >= 0.40`

- **Grade C**:
  - `viability_state == BOUNDED` but does not satisfy A/B

- **Grade D**:
  - `INVALID` or `DIVERGENT`

---

### 3.9 Report and Species Map

#### 3.9.1 Minimal report (report.md)
1) Overview + provenance (hashes, code_version, run_id)
2) Table of **top species** (by grade and frequency)
3) Table of **top structures** (for debugging)
4) **MemoryScore vs LS(p/q) map**

#### 3.9.2 2D map (final definition)
- Y-axis: `memory_bin_label`
- X-axis:
  - **Dimers:** `p/q` (single edge) or "irr"
  - **Triangles+**: `LS_class` = top-K `LS_hash` by frequency + "other"

Values:
- recommended: **species count** per cell (real “islands”)
- alternative: attempt count

It is recommended to add extra columns in tables:
- `ls_complexity = mean(log(q_ij))` (informative only, does not replace LS)

---

### 3.10 DOFT gap (probe mode, post-sweep)

> *(Unchanged from previous spec; defined as a probe over noise/coupling where LS_stability_seed drops below a critical value. Implementation details remain as in v1.0.)*

### 3.11 Layered iteration (“onion”): species_as_blocks (Ola2 → Ola3/4)
**Idea:** a stable species (wide lock, high `seed_stability`) can be coarse-grained as a *super-oscillator* for the next level. You keep **a single explorer**; only the engine and templates change per wave.

**Minimum super-block contract (derived from `species_catalog.jsonl`):**
- `omega0 = best_metrics.omega_eff` (RMS)
- `omega_jitter = mean(best_metrics.node_omega_std_lastW)`
- `memory0 = best_metrics.memory_score_k10`
- `order0 = best_metrics.entropy_quality` (canonical)  
  (or `QualityLock`, but choose one and derive the other)

**Input mode (config):**
- `inputs.blocks_mode: "species_as_blocks"`
- `targets[].allowed_species: [...]` as a DOFT-ID restriction (not SM) for controlled / synthesis experiments.

**Risk to avoid:** double-counting memory. Explicitly define how `memory_local` (of the super-block) combines with `memory_global` (of the engine) in each wave.

**Practical goal:** use Ola2 to generate a catalog of “stable blocks” and then reuse the same pipeline (explorer + event sourcing + map) for Ola3/Ola4, changing only configuration and the engine backend.

---

## 4) Implementation specification (programming)

### 4.1 File structure

- `run_structure_explorer.py` (main)
- `propose_structure.py`
- `propose_params.py`
- `simulate_wrapper.py` (calls your simulate_ola2 and adds LS)
- `taxonomy.py`
- `species_catalog.py`
- `report_builder.py`

### 4.2 attempts.jsonl schema (minimum)


**Additional recommended fields (v1.1):**
- `best_metrics.node_omega_mean_lastW`: list[float]
- `best_metrics.node_omega_std_lastW`:  list[float]
- `best_metrics.omega_eff`: float
- `best_metrics.omega_eff_method`: "rms"
- `derived.delta_omega_raw`: float (if adaptive coupling is active)
- `derived.delta_omega_eff`: float
- `derived.omega_floor`: float
- `derived.coupling_alpha`: float
- `derived.coupling_beta`: float
- `tags`: may include `ZOMBIE`.


```json
{
  "schema_version": "ola2_attempt_v1",
  "run_id": "uuid",
  "attempt_id": "uuid",
  "timestamp_utc": "ISO8601",
  "provenance": {
    "config_hash": "sha256",
    "blocks_hash": "sha256",
    "templates_hash": "sha256",
    "code_version": "git_hash_or_file_hash",
    "machine": {"python": "...", "platform": "...", "hostname": "..."}
  },

  "structure": {
    "template_name": "meson_dimer|baryon_triangle|...",
    "structure_id": "sha256",
    "canonical_node_order": ["n0","n1","..."],
    "edges": [["n0","n1"], ["n1","n2"]],
    "edge_weights": {"n0-n1": 1.0},
    "assignment": {"n0": "block_key_001", "n1": "block_key_099"},
    "origin_tags": {"n0": "delta_1950"}  // optional, traceability only
  },

  "engine_params": { "...": "..." },
  "seed": 12345,

  "metrics": {
    "R_final": 0.0,
    "R_mean_lastW": 0.0,
    "phase_var_lastW": 0.0,
    "edge_phase_diff_mean_lastW": 0.0,
    "edge_phase_diff_std_lastW": 0.0,
    "QualityLock": 0.0,
    "entropy_quality": 0.0,
    "memory_score_k10": 0.0
  },

  "lock_signature": {
    "max_den": 31,
    "epsilon_rel": 1e-3,
    "edges": [
      {"u":"n0","v":"n1","ratio_raw":1.5,"ratio_pq":"3/2","residual_rel":2.1e-4,
       "p_factors":{"3":1},"q_factors":{"2":1}}
    ],
    "LS_hash": "sha256"
  },

  "stability": {
    "N_seed": 12,
    "LS_stability_seed": 0.75,
    "params_sensitive": ["kappa_global","sigma0"],
    "param_neighbor_rel": 0.05,
    "N_seed_probe": 5,
    "LS_stability_param": 0.66,
    "lock_width_index": 0.66
  },

  "taxonomy": {
    "viability_state": "BOUNDED",
    "attractor_class": "COHERENT_LOCKED",
    "grade": "A"
  },

  "labels_observer": {
    "sm_guess": null,
    "notes": ""
  }
}
```

**Rule:** `labels_observer` is not used in proposal.

---

### 4.3 Explorer config (includes N_seed/N_seed_probe)


**New knobs (v1.1):**
- `coupling_mode.mode = "adaptive_alpha"` with ranges `alpha_range`, `beta_range`, `omega_floor`.
- `inputs.blocks_mode = "species_as_blocks"` + `allowed_species`.
- `tagging.ZOMBIE_rule`: `memory_score_k10 < 0`.


```json
{
  "schema_version": "structure_explorer_config_v1",
  "proposal_policy": {
    "mode": "blind_uniform",
    "use_sm_guidance": false
  },

  "quantization": {
    "max_den": 31,
    "epsilon_rel": 1e-3,
    "residual_bucket_edges": [1e-4, 1e-3, 1e-2]
  },

  "stability": {
    "N_seed": 12,
    "N_seed_probe": 5,
    "param_neighbor_rel": 0.05,
    "params_sensitive": ["kappa_global", "sigma0", "tau_field", "K_local"]
  },

  "memory_bins": [-1e30, -0.5, 0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 1e30],

  "report": {
    "topK_ls_classes": 20,
    "map_value": "species_count"
  }
}
```

> **Note:** N_seed and N_seed_probe are tuned via config to experiment with (15–20 / 10–15) without touching code.

---

### 4.4 Pseudocode (main loop)

```python
for attempt in range(budget):
    structure = propose_structure(config, blocks, templates)  # DOFT-blind
    params = propose_params(config)
    seed = sample_seed()

    metrics, traces = simulate_ola2(structure, params, seed)

    ls = compute_lock_signature(traces, structure, config.quantization)
    taxonomy = classify(metrics, ls)

    # optional stability probes (phase2 or when taxonomy suggests locked)
    stability = maybe_compute_stability(structure, params, config.stability)

    record = build_attempt_record(...)
    append_jsonl("attempts.jsonl", record)
```

---

### 4.5 Performance / cost (practical notes)
- `N_seed` and `N_seed_probe` are the main multipliers.
- Operational recommendation:
  - start with `N_seed=12`, `N_seed_probe=5`
  - if it behaves well, bump to `15/10`, then `20/15`
- Stability can be computed only for:
  - attempts with `COHERENT_LOCKED`
  - or in phase2 (as you already do)

---

## 5) Closure: what this SPEC guarantees

- DOFT purity in the search (SM does not contaminate it).
- Full auditability (event sourcing).
- Species identity defined by resonant geometry (LS) + memory.
- A **real** “islands of stability” map = MemoryScore vs LS(p/q) (not a proxy).
- Ability to later scale to ħ_eff / gap / Rydberg as post-sweep probes, without touching the base engine.
