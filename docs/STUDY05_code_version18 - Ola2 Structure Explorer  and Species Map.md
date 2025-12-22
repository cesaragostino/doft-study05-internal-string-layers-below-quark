# DOFT – Wave2 Structure Explorer & Species Map  
**SPEC v1.0 (functional closure + implementation guide)**  
Date: 2025-12-21 (America/Argentina/Buenos_Aires)

> **Objective:** generate and catalog *resonant species* in DOFT (structure + oscillators + memory), without guiding the search using the SM.  
> The SM appears only as an **observer** for later tagging.  
> **Nothing is discarded:** everything is classified (taxonomy) and reported.

---

## 1) Theoretical framework (what is “real” in DOFT)

### 1.1 DOFT ontology (axioms)

**A0. Nothing is discarded.**  
Every attempt is persisted. “viable / nonviable / …” is a **tag** (taxonomy), not an ontological filter.

**A1. The SM does not guide the search.**  
Do not use `particle_name`, `d_total`, `allowed_particle_names`, or anything SM-related to propose structures/params.  
The SM only lives in `labels_observer` (post).

**A2. Hard parameters = the only real things.**  
Real in DOFT = **structure (graph + weights)** + **engine parameters** + **memory** + **dynamics**.  
“Mass”, “gap”, “levels”, etc. are **emergent**: observer readout functions over DOFT invariants.

**A3. Wave1 is frozen.**  
Wave1 sweep and post-processing are not modified in this version. Wave2 fixes the purism.

---

### 1.2 What Wave1 vs Wave2 produce (to avoid confusion)

- **Wave1** produces *blocks* (DOFs) and their descriptors (peaks, omega_ref, etc.).  
  There is no structure (nodes/edges), therefore there is **no geometric Lock Signature** of a cluster in Wave1.

- **Wave2** produces *clusters* (structure + collective dynamics).  
  Here we do have:
  - `memory_score_k10` of the cluster
  - `Lock Signature LS(p/q)` as the resonant geometry of the cluster
  - lock stability (width) measured via seeds/neighbors

> Consequence: the **MemoryScore vs LS(p/q)** map is **Wave2-only**. Not touching Wave1 does not reduce quality; it avoids inventing an LS that does not exist there.

---

## 2) DOFT invariants and emergent observables

### 2.1 DOFT invariants (minimum)

- **Structure**: template + graph + edge_weights + block assignment per node.
- **Hard parameters**: `engine_params` (couplings, dt, W, ticks, taus/memory, noise, etc.).
- **Dynamics**: phases/velocities (or whatever the engine uses internally).
- **Internal observables** (already existing in your engine):  
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

- `ola1_blocks.json` (block pool)
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

**Forbidden:** using SM (`d_total`, names, etc.) in proposal.

#### 3.3.2 Parameter proposer (`engine_params`)
- samples parameters according to ranges + sweep strategy (phase1/phase2 if you want)
- produces `engine_params`

---

### 3.4 Simulation and metrics
`simulate_ola2(structure, engine_params, seed) -> metrics + (optional traces)`

**Minimum required metrics** (already exist or equivalents):
- coherence: `R_final`, `R_mean_lastW`, `phase_var_lastW`
- lock/proxy: `edge_phase_diff_mean_lastW`, `edge_phase_diff_std_lastW`, `QualityLock`, `entropy_quality`
- memory: `memory_score_k10`
- energy: (if present) `PE_tick_norm`, `E_local_*`

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

**Per edge store:**
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

> It is recommended to “bucket” the residual (e.g. 1e-4, 1e-3, 1e-2) to avoid numerical noise creating distinct species unintentionally.

---

### 3.6 Taxonomy (classification without filtering)

Each attempt receives:
- `viability_state`: `INVALID` | `DIVERGENT` | `BOUNDED`
- `attractor_class` (minimum):
  - `COHERENT_LOCKED`
  - `COHERENT_QUASI`
  - `DRIFT_BOUNDED`
  - optional: `CHAOTIC_BOUNDED` (if you add a temporal metric)

**Rule:** never delete; only tag.

---

### 3.7 Stability / lock width

**Configurable in the explorer config** (important):

- `N_seed` (for seed-based stability, recommended 15–20; safe default 12)
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
- total points: `N_param = 1 + 2*len(params_sensitive)` (no cross combinations)

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
Because `memory_score_k10` can be negative, default bins:

`[-inf, -0.5, 0.0, 0.5, 0.8, 0.9, 0.95, 0.98, +inf]`

Store:
- `memory_bin_id`
- `memory_bin_label`

#### 3.8.2 species_id
`species_id = sha256(template + structure_id + LS_hash + memory_bin_id)`

> Interpretation: “same species” = same resonant geometry + same memory context (binned).

#### 3.8.3 DOFT Grade (explicit)
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

#### 3.9.1 Minimum report (`report.md`)
1) Overview + provenance (hashes, code_version, run_id)  
2) **Top species** table (by grade and frequency)  
3) **Top structures** table (for debugging)  
4) **MemoryScore vs LS(p/q) map**

#### 3.9.2 2D map (final definition)
- Y axis: `memory_bin_label`
- X axis:
  - **Dimers:** `p/q` (single edge) or "irr"
  - **Triangles+**: `LS_class` = top-K `LS_hash` by frequency + "other"

Values:
- recommended: **species count** per cell (real islands)
- alternative: attempt count

It is recommended to add extra columns in tables:
- `ls_complexity = mean(log(q_ij))` (informative only, does not replace LS)

---

### 3.10 DOFT gap (probe mode, post-sweep)
Not run during massive exploration.

For a candidate species (A/B):
- fix base structure+params
- sweep σ (noise) or K (coupling) on a log grid
- at each point: run `N_seed_gap` (e.g. 12) and measure `LS_stability_seed`
- define:
  - σ_crit: first σ where `LS_stability_seed < 0.5`
  - K_crit: analogous

This is later used in Wave3/Wave4 (superconductivity) as the “DOFT gap”.

---

## 4) Implementation specification (programming)

### 4.1 File structure

- `run_structure_explorer.py` (main)
- `propose_structure.py`
- `propose_params.py`
- `simulate_wrapper.py` (calls your `simulate_ola2` and adds LS)
- `taxonomy.py`
- `species_catalog.py`
- `report_builder.py`

### 4.2 `attempts.jsonl` schema (minimum)

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

> **Note:** N_seed and N_seed_probe are adjusted via config (15–20 / 10–15) without changing code.

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

### 4.5 Performance / cost (practical)
- `N_seed` and `N_seed_probe` are the main multipliers.
- Operational recommendation:
  - start with `N_seed=12`, `N_seed_probe=5`
  - if it’s stable, raise to `15/10`, then `20/15`
- Stability can be run only on:
  - attempts with `COHERENT_LOCKED`
  - or in phase2 (as you already do)

---

## 5) Closing: what this SPEC guarantees

- DOFT purity in the search (SM does not contaminate it).
- Full auditability (event sourcing).
- Species identity defined by resonant geometry (LS) + memory.
- A **real** “stability islands” map = MemoryScore vs LS(p/q) (not a proxy).
- Ability to later scale to ħ_eff / gap / rydberg as post-sweep probes, without touching the base engine.


## ADDENDUM ASI NOMAS... Masa emergente
Agregar ω̄ por nodo (lastW)

La simulación debe exponer por nodo la fase θ_i(t) (o directamente ω_i(t) si ya la tiene).

Calcular unwrap de θ_i(t) (evita wrap a ±π).

Calcular ω_i(t) = (θ_i(t) - θ_i(t-1)) / dt.

En la ventana final lastW guardar:

node_omega_mean_lastW[i] = mean(ω_i(t))

node_omega_std_lastW[i] = std(ω_i(t))

Definir ω_eff del cluster (método elegido: RMS)

Con los promedios por nodo:

𝜔
eff
=
1
𝑁
∑
𝑖
(
𝜔
ˉ
𝑖
)
2
ω
eff
	​

=
N
1
	​

i
∑
	​

(
ω
ˉ
i
	​

)
2
	​


Guardar en el attempt:

omega_eff

omega_eff_method = "rms"

No usar energías/PE para ω_eff (por ahora)

ω_eff sale solo de dinámica de fase (Kuramoto + memoria).

Energías/PE quedan como métricas auxiliares.

Persistencia mínima en attempts.jsonl (sin traces gigantes)
En cada record guardar:

node_omega_mean_lastW (lista floats, largo N)

node_omega_std_lastW (lista floats, largo N)

omega_eff (float)

omega_eff_method (string)

Compatibilidad con Lock Signature (LS)

LS(p/q) se calcula después con ratios por arista:
r_ij = node_omega_mean_lastW[i] / node_omega_mean_lastW[j]

Esto conecta directo con el resto del pipeline (species_id, mapa, etc.).

Masa emergente (solo observador, opcional en esta etapa)

Si se quiere preview: mass_emergent_gev = hbar_ola1 * omega_eff

Guardarlo en labels_observer o emergents, nunca afecta proposal.

Chequeo rápido anti-bug

Verificar que omega_eff no sea ~0 por wraps (si pasa, faltó unwrap).

Verificar que node_omega_std_lastW sea razonable (no NaN/inf) y que omega_eff sea estable para seeds cuando el lock es estable.