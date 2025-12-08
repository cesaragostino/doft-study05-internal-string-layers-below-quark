# 0. Do we have to tear everything down?

No.  
What you already have in Study05 is enough as the engine for Ola1:

- DOFT with 3 internal layers (Q, S1, S2, optional S3).
- Parameter sweeps.
- Spectra + proxies + per-layer weights.

What’s missing is:

- Add a few more fields to the per-run output (`lock_quality`, `structure_tier`, role of S2).
- A new layer of scripts for:
  - **Ola1:** extract “promoted simple blocks” from the sweeps.
  - **Ola2:** combine those blocks into composite structures and see whether complex SM-like hadrons appear.

I would separate this as a logical “Study06”, but reusing the `study05.simulation` engine.

---

# 1. Ola1 – Discover and promote simple blocks

## 1.1. Sweep engine (almost the same as now)

Script (you already have something like this):  
`study05.run_sweep`

We leave it as-is at the CLI level, or clone it to `study06.run_ola1_sweep` if you want to separate:

```bash
PYTHONPATH=src python3 -m study05.run_sweep   --case HadronCore_3layers   --runs 2000   --seed 123   --band-min 0.1   --band-max 3.0   --output-root data/ola1
```

New requirements in the per-run output (in addition to what’s already there):

In the results JSON (and the proxies CSV), add columns:

- `lock_quality_Q`, `lock_quality_S1`, `lock_quality_S2 ∈ [0,1]`
- `structure_tier ∈ {none, level1, level2, level3}`
- `s2_band_fraction` (you already have it or it’s easy to derive)
- `s2_state ∈ {none, latent, structural}`

Initial simple rules (tunable):

```text
structure_tier:
  none    : lock_quality_Q < T_Q
  level1  : Q ok,    S1 not ok
  level2  : Q+S1 ok, S2 not ok
  level3  : Q+S1+S2 ok

s2_state:
  none        : s2_band_fraction < 1e-3
  latent      : s2_band_fraction ∈ [1e-3, S2_LATENT_MAX]  (e.g. 0.1)
  structural  : s2_band_fraction > S2_LATENT_MAX & lock_quality_S2 > T_S2
```

All of this is stored in:

```text
data/ola1/raw/study05_sweep_results.json
data/ola1/processed/ola1_all_runs_proxies.csv   # 1 row per run
```

---

## 1.2. SM catalog (particle zoo)

Directory: `data/raw/sm_catalog/particles.json`

Format:

```json
[
  {
    "name": "pion",
    "family": "pion_like",
    "type": "meson",
    "JPC": "0-",
    "masses_gev": [0.139, 1.30],
    "widths_gev": [0.0, 0.4],
    "energy_window": [0.1, 3.0],
    "tolerances": {
      "spacing_rel": 0.1,
      "mass_abs": 0.02,
      "width_abs": 0.05
    }
  },
  {
    "name": "rho",
    "family": "rho_like",
    "type": "meson",
    "JPC": "1-",
    "masses_gev": [0.775, 1.45, 1.72],
    "widths_gev": [0.15, 0.35, 0.30],
    "energy_window": [0.1, 3.0],
    "tolerances": { "...": "..." }
  },
  {
    "name": "proton",
    "family": "nucleon_like",
    "type": "baryon",
    "JPC": "1/2+",
    "masses_gev": [0.939, 1.44, 1.71, 1.88],
    "widths_gev": [0.0, 0.35, 0.15, 0.25],
    "energy_window": [0.2, 3.0],
    "tolerances": { "...": "..." }
  }
]
```

(You can extend this list with the rest of the hadronic zoo you want.)

This replaces / unifies the `pion_like.json`, `rho_like.json`, etc. JSONs into a single format.

---

## 1.3. SM evaluator per run (match against the whole zoo)

Script: `study06.match_sm_ola1`

CLI:

```bash
PYTHONPATH=src python3 -m study06.match_sm_ola1   --proxies-csv data/ola1/processed/ola1_all_runs_proxies.csv   --sm-catalog data/raw/sm_catalog/particles.json   --output reports/ola1_matches
```

Logic:

For each run:

1. Extract the list of simulated levels inside `band-min/band-max` (centers + widths).
2. For each particle in `particles.json`:
   - cut levels to those falling in `energy_window`,
   - compute metrics:
     - `d_spacing`, `d_total`, `enough_levels` (as you already do).

Save CSV:

```text
reports/ola1_matches/zoo_matches.csv
```

with columns:

```text
run_id,target_name,family,type,d_total,d_spacing,enough_levels
```

and another summary CSV:

```text
reports/ola1_matches/best_match_per_run.csv
```

with:

```text
run_id,best_target,best_family,best_d_total
```

---

## 1.4. Promotion of simple blocks (Ola1 → block catalog)

Script: `study06.promote_simple_blocks`

CLI:

```bash
PYTHONPATH=src python3 -m study06.promote_simple_blocks   --proxies-csv data/ola1/processed/ola1_all_runs_proxies.csv   --structure-csv reports/ola1_structure_scores.csv   --zoo-matches-csv reports/ola1_matches/zoo_matches.csv   --sm-catalog data/raw/sm_catalog/particles.json   --output blocks/simple_blocks.json
```

Minimum inputs:

- `ola1_all_runs_proxies.csv` (with `lock_quality`, `s2_band_fraction`, etc.).
- `zoo_matches.csv` (all distances to SM).

Promotion rules (tunable but clear):

For each run and each “simple” target (pion, rho, etc.):

**Structure:**

- `structure_tier >= level2` (Q+S1 finalized).
- `s2_state ∈ {none, latent}` (S2 not structural).

**SM match:**

- `target.type == "meson"` (for Ola1; baryons are left to Ola2).
- `enough_levels = True`.
- `d_total < d_yes` (threshold for a “good match”, e.g. 0.3).

**Diversity:**

- you can cap to N blocks per particle (e.g. top 10 by `d_total`).

Output: `blocks/simple_blocks.json`

Format:

```json
[
  {
    "block_id": "pion_block_0001",
    "origin_run_id": "CaseB_debug_seed123_idx42",
    "particle_name": "pion",
    "family": "pion_like",
    "theta_internal": { "...": "..." },     // full parameter set used in the run
    "structure_tier": "level2",
    "lock_quality": {
      "Q": 0.93,
      "S1": 0.87,
      "S2": 0.12
    },
    "s2_state": "latent",
    "s2_band_fraction": 0.03,
    "match_score": {
      "d_total": 0.18,
      "d_spacing": 0.09
    }
  }
]
```

(And similarly for other blocks like `rho_block_0001`, etc.)

That’s Ola1 solved:
you have a list of promoted simple blocks that “exist on their own” and match real mesons.

---

# 2. Ola2 – Block structures (composites)

Ola2 does NOT change the internal engine; it adds:

- combinations of simple blocks,
- discrete topologies,
- new couplings,
- matching against complex hadrons (baryons, etc.).

## 2.1. Defining structures (graph templates)

File: `blocks/compound_templates.json`

Example:

```json
[
  {
    "name": "baryon_triangle",
    "type": "baryon",
    "nodes": 3,
    "edges": [[0,1],[1,2],[2,0]],
    "allowed_block_families": ["pion_like", "rho_like", "quark_like"]
  },
  {
    "name": "baryon_chain",
    "type": "baryon",
    "nodes": 3,
    "edges": [[0,1],[1,2]],
    "allowed_block_families": ["pion_like","rho_like","quark_like"]
  },
  {
    "name": "meson_dimer",
    "type": "meson_complex",
    "nodes": 2,
    "edges": [[0,1]],
    "allowed_block_families": ["pion_like","rho_like"]
  }
]
```

Later you can add more templates, but at the beginning 2–3 are enough.

---

## 2.2. Composite engine (Ola2)

Script: `study06.run_ola2_compounds`

CLI:

```bash
PYTHONPATH=src python3 -m study06.run_ola2_compounds   --blocks-json blocks/simple_blocks.json   --templates-json blocks/compound_templates.json   --sm-catalog data/raw/sm_catalog/particles.json   --targets proton neutron delta   --runs-per-target 1000   --seed 123   --band-min 0.1   --band-max 3.0   --output-root data/ola2
```

Logic per target (e.g. proton):

For each attempt (up to `runs-per-target`):

1. Choose a template compatible with the type (`baryon`).
2. Choose `nodes` blocks from `simple_blocks.json` with compatible `particle_name` / `family`.
3. Sample coupling parameters per edge:
   - `k_edge[i,j]`, `g_edge[i,j]`, `tau_edge[i,j]` in defined ranges.  
     (this is the “environment” that can switch S2 strongly on).
4. Build an effective system:
   - each block contributes its internal DOFs (Q, S1, latent S2),
   - add coupling terms between blocks according to the template.
5. Run the simulator (reuse the integrator from `study05.simulation`, now with more DOFs).
6. Extract from the composite run:
   - global spectrum (`energies`, `widths`),
   - `lock_quality_{Q,S1,S2}` at composite level,
   - `s2_band_fraction_compound`,
   - proxies like `spacing_mean_compound`, etc.
7. Evaluate:
   - structure: `structure_tier_compound` (here we want `level3` for baryons),
   - SM match vs the target (proton):
     - `d_total_target`, `enough_levels`.

Save one row per run in CSV:

```text
data/ola2/raw/compounds_runs.csv
```

with:

```text
target,template_name,run_id,block_ids,k_edge_params,g_edge_params,...
structure_tier_compound,lock_Q,lock_S1,lock_S2,s2_band_fraction,d_total_target,enough_levels
```

---

## 2.3. Viability labels (YES / POSSIBLE / NO)

Script: `study06.label_ola2_viability`

CLI:

```bash
PYTHONPATH=src python3 -m study06.label_ola2_viability   --compounds-csv data/ola2/raw/compounds_runs.csv   --sm-catalog data/raw/sm_catalog/particles.json   --output reports/ola2_viability
```

Typical rules for baryons:

For each row (run, target):

**Layer hierarchy:**

- if `structure_tier_compound < level3` → `label = NO`  
  (a baryon needs Q+S1+S2 finalized as a composite).

**Spectral match:**

- if `enough_levels = false` → `label = NO`.
- if `d_total_target < d_yes_baryon` → `label = YES`.
- if `d_yes_baryon ≤ d_total_target < d_possible_baryon` → `label = POSSIBLE`.
- if `d_total_target ≥ d_possible_baryon` → `label = NO`.

Save:

```text
reports/ola2_viability/viability_labels.csv
```

with:

```text
target,template_name,run_id,block_ids,structure_tier_compound,d_total_target,label
```

---

## 2.4. Simple reports (without going overboard)

I would just do:

- One XLS (or CSV openable in Excel) with:
  - Ola1: `best_match_per_run.csv`, and `simple_blocks.json` converted to a table.
  - Ola2: `viability_labels.csv` + `compounds_runs.csv` filtered to the YES/POSSIBLE rows.

- 2–3 plots per script (optional), each as PNG:

  **Ola1:**
  - scatter of `first_energy` vs `spacing_mean`, colored by `best_target` (pion/rho/etc.).

  **Ola2:**
  - histogram of `d_total_target` for each target,
  - bar plot of how many YES/POSSIBLE/NO per target.

Nothing beyond that, to avoid filling everything with images.

---

# 3. Operational summary

You don’t need to rewrite the engine, just:

- add `lock_quality`, `structure_tier`, `s2_state` to the sweep outputs.

**Ola1:**

- run sweeps as you already do,
- match against the full SM zoo,
- promote simple blocks (mainly pion-like and some rho-like) to `blocks/simple_blocks.json`.

**Ola2:**

- use those blocks + structural templates,
- sample couplings (environment),
- see whether S2 switches on strongly and whether the composite matches real baryons,
- label YES/POSSIBLE/NO.

All of this respects:

- sweeping without prejudice,
- logging EVERYTHING,
- filtering only between waves to decide what survives as a viable block / structure.
