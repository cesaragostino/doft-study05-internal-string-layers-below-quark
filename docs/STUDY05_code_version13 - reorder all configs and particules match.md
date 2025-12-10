# Cleanup and configuration consolidation (few files, all under `data/raw/`)

Goals:

- Clean up configs (few files, all in `data/raw/`).
- Leave Ola1 well defined:
  - simple mesons → `simple_blocks.json`
  - complex cores with strong S2 → `complex_cores.json`
- Make Ola2 truly able to **produce and evaluate** complex objects (proton-like compounds), without filters that kill everything.

---

## 0. Config cleanup (few files, all in `data/raw/`)

### 0.1. Configuration files that must exist (and only these)

Location: `data/raw/`

- `data/raw/layer_states.yaml`
- `data/raw/sm_universe.json`
- `data/raw/compound_templates.json`
- `data/raw/wave2_compounds.json`

Optional later: `data/raw/precision_policy.yaml`, but for now we leave it out to avoid multiplying configs.

---

### 0.2. Things to delete or stop using

No more:

- `data/raw/sm_catalog/particles.json`
- `data/raw/config/*.json`
- `data/raw/legacy/sm_families/*.json`  
  (if you want to keep them as historical artifacts, fine, but the **code must NOT** consult them).

`analyze_proxies`, `run_sweep`, `match_sm_ola1`, `promote_simple_blocks`, `run_ola2_compounds`, etc.  
→ must only use:

- `data/raw/layer_states.yaml`
- `data/raw/sm_universe.json`
- `data/raw/compound_templates.json`
- `data/raw/wave2_compounds.json`

---

### 0.3. Update default paths in code

`study05.run_sweep`:

- `--layer-states` default → `data/raw/layer_states.yaml`.

`study06.match_sm_ola1`:

- `--sm-catalog` default → `data/raw/sm_universe.json`.

`study06.promote_simple_blocks`:

- `--sm-catalog` default → `data/raw/sm_universe.json`.

`study06.run_ola2_compounds`:

- `--sm-universe` default → `data/raw/sm_universe.json`
- `--templates-json` default → `data/raw/compound_templates.json`
- if `blocks_input` is missing in `wave2_compounds.json`, default → `data/processed/blocks/simple_blocks.json`.

---

## 1. Adjustments in Ola1 (Core3L + proxies + simple blocks)

### 1.1. `data/raw/layer_states.yaml` (define thresholds properly)

Replace the current YAML with one based on **relative fractions**:

```yaml
lock_thresholds:
  # fraction of Q, S1, S2 within the “structural” part (Q+S1+S2+S3)
  T_Q_rel_min: 0.5
  T_S1_rel_min: 0.10
  T_S2_rel_min: 0.10

s2_state:
  none_max_fraction: 1.0e-3
  latent_max_fraction: 0.15
```

Code in `run_sweep`:

Compute:

```python
total_struct = lock_Q + lock_S1 + lock_S2 + lock_S3
# if total_struct == 0, structure_tier = "none"

q_rel  = lock_Q  / total_struct
s1_rel = lock_S1 / total_struct
s2_rel = lock_S2 / total_struct
```

`structure_tier`:

```python
if q_rel < T_Q_rel_min:
    tier = "none"
elif s1_rel < T_S1_rel_min and s2_rel < T_S2_rel_min:
    tier = "level1"   # only Q dominant
elif s1_rel >= T_S1_rel_min and s2_rel < T_S2_rel_min:
    tier = "level2"   # Q+S1 structured
else:
    tier = "level3"   # Q+S1+some S2
```

`s2_state` (same as you had, but ensure it uses the new YAML):

```python
if s2_band_fraction < none_max_fraction:
    s2_state = "none"
elif s2_band_fraction < latent_max_fraction:
    s2_state = "latent"
else:
    s2_state = "structural"
```

Store these fields in the results JSON and in the proxies CSV:

- `lock_quality_Q`, `lock_quality_S1`, `lock_quality_S2`
- `structure_tier`
- `s2_band_fraction`, `s2_state`

---

### 1.2. `study05.analyze_proxies` (clean and complete CSV)

Make sure that:

- It uses `csv.DictWriter` (you already do) so `band_energies_gev` does not break columns.

It should write at least these columns (they are already there, but make sure they stay stable):

- `run_id`
- `R_S1_Q`, `R_S2_S1`, `R_S3_S2`
- `band_count`, `band_energies_gev`
- `first_energy`, `second_energy`, `third_energy`
- `spacing_mean`, `spacing_std`

- `lock_quality_Q`, `lock_quality_S1`, `lock_quality_S2`
- `structure_tier`
- `s2_band_fraction`, `s2_state`
- `s3_band_fraction`, `s3_state`

For each SM family:

- `<family>_d_total`
- `<family>_d_spacing`
- `<family>_has_enough_levels`
- `<family>_is_match`
- `<family>_n_levels_sim`

All of this already appears in `Core3L_Hadron_all_runs_proxies.csv`, but it’s crucial that it remains stable.

---

### 1.3. `study06.match_sm_ola1` (already almost fine)

It must read `data/raw/sm_universe.json` and, for each particle and family, fill columns like:

- `pion_like_d_total`, `pion_like_is_match`, etc.
- `nucleon_like_d_total`, …

The matching logic (computing `d_total`, `enough_levels`) already exists; extract it into a helper to reuse it in Ola2 and in the new “complex cores” script (see point 2):

```python
# study06/sm_matching.py
def compute_match_stats(band_energies, target_masses, tolerances) -> dict:
    ...
    return {
      "d_total": ...,
      "d_spacing": ...,
      "n_levels_sim": ...,
      "has_enough_levels": True/False,
    }
```

---

## 2. New: catalog complex cores with strong S2 (`complex_cores.json`)

We want to rescue exactly the runs we saw before:

- `s2_state == "structural"`
- `structure_tier == "level3"`
- S2 ≈ 1/3 and Q ≈ 2/3, etc.

### 2.1. Script: `study06.catalog_complex_cores`

Suggested CLI:

```bash
PYTHONPATH=src python3 -m study06.catalog_complex_cores   --proxies-csv data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv   --sm-universe data/raw/sm_universe.json   --output data/processed/blocks/complex_cores.json
```

Logic:

- Read `proxies-csv`.

Select candidates:

```python
mask = (s2_state == "structural") & (structure_tier == "level3")
candidates = df[mask]
```

For each candidate, evaluate match against SM baryons:

- baryons: particles with `type == "baryon"` in `sm_universe`.

Use `compute_match_stats(...)` with `band_energies_gev` from the run and `masses_gev` for each baryon.

Do **not** require `has_enough_levels == True` as a hard condition:

- store that info, but you can accept candidates with few levels (incomplete baryon) as “exploratory”.

Promotion criteria for `complex_cores`:

For each run and each baryon target:

- `s2_state == "structural"`
- `structure_tier == "level3"`
- `match.d_total < d_yes_baryon_core` (e.g. 0.6 to start)

Keep only the **best baryon per run** (minimum `d_total`).

For each accepted core:

Build an entry in `complex_cores.json`:

```json
{
  "core_id": "core3L_run_0236",
  "origin_run_id": 236,
  "matched_particle": "proton",
  "family": "nucleon_like",
  "type": "baryon_candidate",

  "structure": {
    "structure_tier": "level3",
    "lock_quality": {
      "Q": ...,
      "S1": ...,
      "S2": ...
    },
    "s2_band_fraction": ...,
    "s2_state": "structural"
  },

  "match_score": {
    "d_total": ...,
    "d_spacing": ...,
    "has_enough_levels": true,
    "target_name": "proton"
  },

  "theta_internal": {
    // same format as simple_blocks; if possible, fill more:
    "R_S1_Q": ...,
    "R_S2_S1": ...,
    "R_S3_S2": ...,
    "g_couplings": ...,
    "memory_taus": ...,
    "memory_amps": ...
  }
}
```

Important: do **not** use `complex_cores` as Ola2 blocks yet if you don’t want to; first we want to catalog them. Ola2 still uses `simple_blocks.json`. Later we can decide whether to add a direct `"baryon_core"` mode.

---

## 3. Adjustments in simple block promotion (Ola1 → `simple_blocks.json`)

Script: `study06.promote_simple_blocks`

### 3.1. Separate mesons / quarks / baryons

Change the logic to:

**Mesons** (`type == "meson"`)  
→ they remain the natural candidates for `simple_blocks.json`.

Rules:

```python
if particle.type == "meson":
    require structure_tier >= "level2"     # Q+S1 built
    require s2_state in {"none", "latent"} # S2 not dominant
    require match.enough_levels
    require match.d_total < d_yes_meson    # e.g. 0.3
```

**Effective quarks** (`type == "effective_quark"`)  
→ we also want them in `simple_blocks.json` as building blocks for Ola2.

Softer rules:

```python
if particle.type == "effective_quark":
    require structure_tier >= "level1"     # Q solid, S1/S2 can be small
    # s2_state can be anything (none/latent/structural)
    require match.d_total < d_yes_quark    # e.g. 0.5
```

**Baryons** (`type == "baryon"`)  
→ do **not** put them into `simple_blocks.json`; we handle them via `complex_cores.json` (point 2).

---

### 3.2. Contents of `simple_blocks.json`

Keep the current format:

```json
[
  {
    "block_id": "...",
    "origin_run_id": ...,
    "particle_name": "...",
    "family": "...",
    "type": "meson" or "effective_quark",
    "structure_tier": "level1/2/3",
    "lock_quality": { "...": "..." },
    "s2_state": "...",
    "s2_band_fraction": ...,
    "match_score": { "...": "..." },
    "theta_internal": {
      "R_S1_Q": ...,
      "R_S2_S1": ...,
      "R_S3_S2": ...,
      "g_couplings": null or [...],
      "memory_taus": null or [...],
      "memory_amps": null or [...]
    }
  }
]
```

And, very important: if it’s easy, also include:

- base frequencies per layer (`f_Q`, `f_S1`, `f_S2`),
- damping (`gamma_Q`, etc.),

so that Ola2 has more **real physical information**, not just ratios.

---

## 4. Adjustments in Ola2 (compounds + viability)

### 4.1. `data/raw/wave2_compounds.json`

You already have this mostly right. Make sure that:

- `blocks_input` is explicit:

```json
"blocks_input": "data/processed/blocks/simple_blocks.json"
```

Baryonic targets (proton, neutron, delta_1232) are declared like this:

```json
{
  "name": "proton",
  "particle_name": "proton",
  "type": "baryon",
  "templates": ["baryon_triangle", "baryon_chain"],
  "allowed_block_families": ["quark_like", "pion_like", "rho_like"],
  "runs_per_target": 1000,
  "d_yes_baryon": 0.25,
  "d_possible_baryon": 0.45
}
```

---

### 4.2. `study06.run_ola2_compounds`

Make sure that it:

- Reads `blocks_input` (default `data/processed/blocks/simple_blocks.json`).
- Filters blocks by `family ∈ allowed_block_families`.

If `prefer_quark_like_for_baryons = true` in `wave2_compounds.json`, then:

- select `quark_like` blocks whenever available,
- and only fill with pions/rho when not enough quarks exist.

Reuse the matching helpers (`compute_match_stats`) to compute:

- `match_d_mass`, `match_d_spacing`, `match_d_total`,
- `enough_levels` for each compound.

Relax `enough_levels` for baryons:

- If the target has 4 masses (e.g. `m_proton = [0.939, 1.44, 1.71, 1.88]`) and the compound only produces 2–3 levels in the window, allow a `has_enough_levels_partial = True` if at least 2 levels line up.

Store both:

- `has_enough_levels_full` (as before),
- `has_enough_levels_partial` (for experimentation).

Save in `compounds_<target>.csv` (as you already do) at least:

- `run_id`, `target`, `template_name`,
- `block_ids`, `block_families`,
- `enough_levels_full`, `enough_levels_partial`,
- `match_d_mass`, `match_d_spacing`, `match_d_total`,
- `structure_tier_compound`, `lock_Q_compound`, `lock_S1_compound`, `lock_S2_compound`,
- `s2_band_fraction_compound`.

---

### 4.3. `study06.label_ola2_viability` (`viability_proton.csv`)

Loosen the logic a bit while we are still in exploration:

- Do **not** discard automatically when `enough_levels_full = False`.

Use:

```python
if not enough_levels_partial:
    label = "NO"
else:
    if match_d_total < d_yes_baryon:
        label = "YES"
    elif match_d_total < d_possible_baryon:
        label = "POSSIBLE"
    else:
        label = "NO"
```

Also store `structure_tier_compound` and `s2_band_fraction_compound` so you can later inspect whether YES/POSSIBLE compounds have a live composite S2 or if they are just spectral tricks without real structure.

---

## 5. Final pipeline (one pass, no deprecated versions)

When the programmer finishes these changes, the “clean” flow should be:

### Ola1 – Core3L + proxies

```bash
PYTHONPATH=src python3 -m study05.run_sweep   --case Core3L_Hadron --runs 2000 --seed 123   --band-min 0.1 --band-max 3.0   --layer-states data/raw/layer_states.yaml --no-plots

PYTHONPATH=src python3 -m study05.analyze_proxies   --case Core3L_Hadron   --output data/processed/Core3L_Hadron/combined
```

### SM matching on Ola1

```bash
PYTHONPATH=src python3 -m study06.match_sm_ola1   --proxies-csv data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv   --sm-catalog data/raw/sm_universe.json   --output data/processed/Core3L_Hadron/ola1_matches
```

### Promotion of simple blocks (mesons + effective quarks)

```bash
PYTHONPATH=src python3 -m study06.promote_simple_blocks   --proxies-csv data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv   --zoo-matches-csv data/processed/Core3L_Hadron/ola1_matches/zoo_matches.csv   --sm-catalog data/raw/sm_universe.json   --output data/processed/blocks/simple_blocks.json
```

### Catalog of complex cores with strong S2

```bash
PYTHONPATH=src python3 -m study06.catalog_complex_cores   --proxies-csv data/processed/Core3L_Hadron/combined/Core3L_Hadron_all_runs_proxies.csv   --sm-universe data/raw/sm_universe.json   --output data/processed/blocks/complex_cores.json
```

### Ola2 – baryonic compounds (proton, neutron, delta…)

```bash
PYTHONPATH=src python3 -m study06.run_ola2_compounds   --blocks-json data/processed/blocks/simple_blocks.json   --wave2-config data/raw/wave2_compounds.json   --sm-universe data/raw/sm_universe.json   --templates-json data/raw/compound_templates.json   --output-root data/processed/ola2
```

### Ola2 viability labeling

```bash
PYTHONPATH=src python3 -m study06.label_ola2_viability   --compounds-csv data/processed/ola2/compounds_proton.csv   --sm-universe data/raw/sm_universe.json   --output data/processed/ola2/viability_proton.csv
```
