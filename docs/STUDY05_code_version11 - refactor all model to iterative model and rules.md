# 0. Refactor objectives

- Fix the base physical model:
  - 3 internal layers (Q, S1, S2) always active.
  - No more “CaseA 2 layers / CaseB_debug 3 layers” → a single coherent engine.
- Clearly separate:
  - DOFT computation core (oscillators + delays),
  - between-wave evaluator (“natural selector”),
  - pipeline that chains waves.
- Move selection / promotion logic out of the code and into:
  - per-wave JSON rule files that can be read as “physical conditions + thresholds”.
- Clean up “test trash”:
  - keep modes and scripts with stable names,
  - move experimental stuff to `legacy/` or similar.

---

## 1. Final architecture (target picture)

### 1.1. Software layers

**Layer 1 – DOFT engine**  
Modules: `study05.simulation`, `study05.run_sweep`  
Always does the same thing: integrates oscillator systems with 3 layers, applies delays, extracts spectra and proxies.

**Layer 2 – Per-wave evaluators**  
New (or unified) modules in `study06`:

- `study06.match_sm_ola1` (already exists, keep as is).
- `study06.apply_wave_rules` (new generic rules engine).
- `study06.run_ola2_compounds` (compound engine).
- `study06.label_ola2_viability` (YES/POSSIBLE/NO classifier).

**Layer 3 – Pipeline**  
Module: `study06.run_pipeline`  
Reads a JSON sequence of steps and calls:

- sweeps,
- analyses,
- rule evaluators.

### 1.2. Standard directories

- `data/raw/config/core/engine_core3.json` → physical configuration of the engine.
- `data/raw/config/layer_states.yaml` → lock / S2 state thresholds.
- `data/raw/config/rules/wave1_blocks.json` → Wave 1 rules.
- `data/raw/config/rules/wave2_compounds.json` → Wave 2 rules.
- `data/raw/config/pipeline/sequence.json` → wave sequence.

- `data/raw/sm_catalog/particles.json` → SM catalog.

- `data/processed/ola1/*` → raw Ola1 outputs.
- `data/processed/ola2/*` → raw Ola2 outputs.
- `data/processed/blocks/simple_blocks.json` → promoted blocks.
- `data/processed/digest/*` → summary CSV/XLS.

---

## 2. Core refactor: 3 layers, a single “case”

### 2.1. Unify the simulation “case”

Today you have things like `CaseA_2layers`, `CaseB_3layers`, `CaseB_debug`.  
Refactor:

- Explicitly delete / deprecate:
  - `CaseA_2layers`, `CaseB_3layers`, `CaseB_debug`.
- Define a single stable case, for example:
  - `Core3L_Hadron`.

In `study05.run_sweep`:

- Use `--case Core3L_Hadron` or, even better, allow:

```bash
--engine-config data/raw/config/core/engine_core3.json
```

### 2.2. `engine_core3.json` (fixed 3 layers)

Example content:

```json
{
  "name": "Core3L_Hadron",
  "layers": [
    { "name": "Q",  "index": 0, "n_modes": 1, "freq_range": [0.1, 1.0] },
    { "name": "S1", "index": 1, "n_modes": 1, "freq_range": [0.5, 2.0] },
    { "name": "S2", "index": 2, "n_modes": 1, "freq_range": [1.0, 5.0] }
  ],
  "integration": {
    "t_max": 200.0,
    "dt": 0.01
  },
  "spectrum": {
    "band_min": 0.1,
    "band_max": 3.0,
    "window_type": "lorentz"
  },
  "noise": {
    "type": "white",
    "amplitude_range": [0.0, 0.1]
  },
  "delays": {
    "enabled": true,
    "tau_range": [0.1, 10.0]
  }
}
```

In code:

- `run_sweep` receives `--engine-config` and always builds 3 layers Q/S1/S2.
- Any reference to S3 in the engine is disabled or removed for this study.

### 2.3. Standard `run_sweep` outputs

Each run writes (as it already does, but now fixed):

- energy bands (centers + widths),
- `lock_quality_Q`, `lock_quality_S1`, `lock_quality_S2`,
- `structure_tier` (using relative logic `q_rel`, `s1_rel`, `s2_rel`),
- `s2_band_fraction`, `s2_state`,
- global proxies (`first_energy`, `spacing_mean`, etc.).

In the global JSON:

```json
{
  "case": "Core3L_Hadron",
  "runs_requested": 2000,
  "runs_valid": 2000,
  "band_window_gev": [0.1, 3.0],
  "summary": { "...": "..." },
  "runs": [ "... per-run data ..." ]
}
```

And then `analyze_proxies` always generates:

```text
data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv
```

with correct quotes for lists (already fixed).

---

## 3. Unified SM catalog and cleanup

### 3.1. `data/raw/sm_catalog/particles.json`

Keep a single JSON with all relevant hadrons (for now: pion, rho, proton):

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
      "mass_abs": 0.02
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
    "tolerances": {
      "spacing_rel": 0.1,
      "mass_abs": 0.03
    }
  },
  {
    "name": "proton",
    "family": "nucleon_like",
    "type": "baryon",
    "JPC": "1/2+",
    "masses_gev": [0.939, 1.44, 1.71, 1.88],
    "widths_gev": [0.0, 0.35, 0.15, 0.25],
    "energy_window": [0.2, 3.0],
    "tolerances": {
      "spacing_rel": 0.1,
      "mass_abs": 0.03
    }
  }
]
```

### 3.2. Trash to clean up or move

Files like `pion_like.json`, `rho_like.json`, `nucleon_like.json`:

- move to `data/raw/legacy/sm_families/` or delete them if they’re no longer used.

Super-specific analysis scripts:

- `analyze_s2_friendly_families.py`,
- `analyze_s3_on_s2_zone.py`,
- `catalog_families_s2.py`,
- etc.

→ move to `legacy/analysis/` and make sure they’re not called from the pipeline.

---

## 4. Ola1: block promotion, now 100% declarative

### 4.1. Ola1 rules in JSON

File: `config/rules/wave1_blocks.json` (production version, not debug):

```json
{
  "wave": "ola1",

  "inputs": {
    "proxies_csv": "data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv",
    "zoo_matches_csv": "data/processed/Core3L_Hadron/ola1_matches/zoo_matches.csv"
  },

  "selections": [
    {
      "name": "pion_simple_blocks",
      "target_name": "pion",
      "type": "meson",

      "filters": [
        { "field": "best_target", "op": "==", "value": "pion" },
        { "field": "structure_tier", "op": "in", "value": ["level1", "level2"] },
        { "field": "s2_state", "op": "in", "value": ["none", "latent"] },
        { "field": "best_d_total", "op": "<=", "value": 0.3 },
        { "field": "Pion_like_has_enough_levels", "op": "==", "value": 1 }
      ],

      "pick": {
        "mode": "top_n",
        "n": 20,
        "order_by": "best_d_total",
        "ascending": true
      },

      "output": {
        "blocks_path": "data/processed/blocks/simple_blocks.json",
        "append": false,
        "block_type": "simple",
        "particle_name": "pion",
        "family": "pion_like",
        "include_fields": [
          "run_id",
          "structure_tier",
          "lock_quality_Q",
          "lock_quality_S1",
          "lock_quality_S2",
          "s2_state",
          "s2_band_fraction",
          "best_d_total",
          "R_S1_Q",
          "R_S2_S1",
          "R_S3_S2"
        ]
      }
    }
  ]
}
```

### 4.2. Ola1 rules engine

New module: `study06.apply_wave_rules`

Responsibilities:

- Read `wave1_blocks.json`.
- Load `proxies_csv` and `zoo_matches_csv`.
- Apply filters, sort, take `top_n`.
- Write `simple_blocks.json` with the format you already used (the 5 pions).

At the same time, generate a CSV of rejected candidates:

```text
data/processed/blocks/simple_blocks_rejected.csv
```

with columns like:

```text
run_id,reason,structure_tier,s2_state,best_d_total,...
```

---

## 5. Ola2: compounds + DOFT+SM rules

### 5.1. Compound templates

File: `data/raw/blocks/compound_templates.json`

```json
[
  {
    "name": "baryon_triangle",
    "type": "baryon",
    "nodes": 3,
    "edges": [[0,1],[1,2],[2,0]]
  },
  {
    "name": "baryon_chain",
    "type": "baryon",
    "nodes": 3,
    "edges": [[0,1],[1,2]]
  },
  {
    "name": "meson_dimer",
    "type": "meson_complex",
    "nodes": 2,
    "edges": [[0,1]]
  }
]
```

### 5.2. Ola2 rules in JSON

File: `data/raw/config/rules/wave2_compounds.json`

```json
{
  "wave": "ola2",

  "blocks_input": "data/processed/blocks/simple_blocks.json",
  "templates_json": "data/raw/blocks/compound_templates.json",
  "sm_catalog": "data/raw/sm_catalog/particles.json",

  "targets": [
    {
      "name": "proton",
      "type": "baryon",
      "templates": ["baryon_triangle", "baryon_chain"],
      "allowed_block_families": ["pion_like"],
      "blocks_per_compound": 3,

      "fingerprint_constraints": {
        "max_rel_delta_R_S1_Q": 0.5,
        "max_rel_delta_R_S2_S1": 0.5,
        "max_rel_delta_R_S3_S2": 0.5
      },

      "environment_ranges": {
        "k_edge": [0.1, 5.0],
        "g_edge": [0.0, 2.0],
        "tau_edge": [0.1, 10.0]
      },

      "evaluation": {
        "min_structure_tier": "level2",
        "allowed_s2_states": ["latent", "structural"],
        "d_total_yes": 3.0,
        "d_total_possible": 5.0
      },

      "output": {
        "compounds_csv": "data/processed/ola2/raw/compounds_proton.csv",
        "viability_csv": "data/processed/reports/ola2_viability/viability_proton.csv"
      }
    }
  ]
}
```

### 5.3. Ola2 engine: `run_ola2_compounds`

Responsibilities:

Read:

- `simple_blocks.json`,
- `compound_templates.json`,
- `wave2_compounds.json`,
- `sm_catalog`.

For each target (proton):

- For each `runs-per-target` (CLI or rules parameter):
  - choose a compatible template (triangle/chain),
  - sample 3 `pion_like` blocks,
  - build a composite DOFT system (3 × 3 layers),
  - assign couplings according to `environment_ranges`,
  - run the same integrator as Ola1,
  - extract:
    - composite band,
    - composite `lock_quality_Q/S1/S2`,
    - `s2_band_fraction_compound`,
    - `structure_tier_compound`,
    - `s2_state_compound`,
    - deformation of internal ratios (per block),
    - `d_total_target` (match to proton),
    - `enough_levels` (according to SM catalog).

Save to `compounds_proton.csv`.

### 5.4. Ola2 labeller: `label_ola2_viability`

Reads `compounds_proton.csv` and applies:

- **NO** if:
  - `structure_tier_compound < level2`, or
  - `s2_state_compound == "none"`, or
  - `enough_levels == false`, or
  - deformation of internal ratios > tolerance.

- **YES** if:
  - passes the NO checks, and
  - `d_total_target < d_total_yes`.

- **POSSIBLE** if:
  - passes the NO checks, and
  - `d_total_yes ≤ d_total_target < d_total_possible`.

Writes:

```text
viability_proton.csv
```

with:

```text
target,template_name,run_id,block_ids,label,d_total_target,structure_tier_compound,s2_state_compound,max_rel_delta_R_*
```

---

## 6. Unified pipeline and name cleanup

### 6.1. `data/raw/config/pipeline/sequence.json`

Typical sequence:

```json
[
  {
    "step": "ola1_sweep",
    "kind": "sweep",
    "module": "study05.run_sweep",
    "args": {
      "case": "Core3L_Hadron",
      "runs": 2000,
      "seed": 123,
      "band_min": 0.1,
      "band_max": 3.0,
      "layer_states": "data/raw/config/layer_states.yaml",
      "output_root": "data/processed/ola1"
    }
  },
  {
    "step": "ola1_proxies",
    "kind": "postprocess",
    "module": "study05.analyze_proxies",
    "args": {
      "case": "Core3L_Hadron",
      "output": "data/processed",
      "families": ["nucleon_like", "rho_like", "pion_like"]
    }
  },
  {
    "step": "ola1_match_sm",
    "kind": "postprocess",
    "module": "study06.match_sm_ola1",
    "args": {
      "proxies_csv": "data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv",
      "sm_catalog": "data/raw/sm_catalog/particles.json",
      "output": "data/processed/Core3L_Hadron/ola1_matches"
    }
  },
  {
    "step": "ola1_promote_blocks",
    "kind": "rules",
    "module": "study06.apply_wave_rules",
    "args": {
      "rules_json": "data/raw/config/rules/wave1_blocks.json"
    }
  },
  {
    "step": "ola2_compounds",
    "kind": "rules",
    "module": "study06.run_ola2_compounds",
    "args": {
      "rules_json": "data/raw/config/rules/wave2_compounds.json"
    }
  }
]
```

### 6.2. Extra cleanup

- Rename `CaseB_debug_*` to `Core3L_Hadron_*` in:
  - data paths,
  - plot labels,
  - any README.

- Move test scripts (`*_debug`, `test_*`, old scans) to:

```text
legacy/scripts/
```

with a short README: “not used in pipeline”.

---

## 7. How to test that the refactor didn’t break anything essential

Run the complete pipeline:

```bash
PYTHONPATH=src python3 -m study06.run_pipeline   --sequence data/raw/config/pipeline/sequence.json
```

Check:

- `simple_blocks.json`:
  - still has pion-like blocks with lock in Q and S2 off.
- `simple_blocks_rejected.csv`:
  - coherent reasons (`tier_too_low`, `distance_high`, etc.).

If Ola2 is already implemented:

- `compounds_proton.csv` and `viability_proton.csv` exist.
- There are at least some `POSSIBLE` or `YES` (even if just a few).
