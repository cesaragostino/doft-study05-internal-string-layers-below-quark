# 2. Ola2 “for real”: physical DOFT + sweep, no filtering, only tags

The programmer is right: right now Ola2 is only a combinatorial scorer (it mixes Ola1 runs, computes distances against the SM) → it is NOT the physical system of coupled particles.

What you actually want (and it makes sense) is:

- As in Ola1:
  - do **not** filter beforehand,
  - sweep as much as we can,
  - tag cases (YES/POSSIBLE/NO) in a CSV,
  - and if we want, only “promote” some of them, but without throwing data away.
- And also:
  - Ola2 should be nested oscillators:
    - Ola1 blocks (DOFT pions) coupled to each other → mini-cluster → new frequency.

---

## 2.1. Prerequisite: Ola1 blocks must be reconstructible

Right now `simple_blocks.json` has things like:

- `run_id`,
- `particle_name = "pion"`,
- `lock_quality_Q/S1/S2`,
- ratios `R_S1_Q`, `R_S2_S1`, etc.

But to make a *physical* Ola2, we need to:

- be able to reconstruct the internal DOFT state of the block.

That is, for each block, we must at least know:

- base frequencies per layer (`omega_Q`, `omega_S1`, `omega_S2`),
- masses / equivalents,
- damping (`gamma`),
- memory parameters if any (`tau_mem`, amplitudes),
- internal couplings of the block.

This has to come from Ola1.  
In spec terms:

- adapt `promote_simple_blocks` so that each block writes a field like:

```json
"theta_internal": {
  "layers": {
    "Q":  { "omega": ..., "mass": ..., "gamma": ..., "tau_mem": ... },
    "S1": { "omega": ..., "mass": ..., "gamma": ..., "tau_mem": ... },
    "S2": { "omega": ..., "mass": ..., "gamma": ..., "tau_mem": ... }
  },
  "internal_couplings": [
    { "from": "Q",  "to": "S1", "k": ..., "g": ..., "tau": ... },
    { "from": "S1", "to": "S2", "k": ..., "g": ..., "tau": ... }
  ]
}
```

Or alternatively:

- store a `run_id` and a snapshot of that run’s parameters, but in practice it is cleaner to embed `theta_internal` directly in the block.

Without that, Ola2 can only combine “paper spectra”, not real DOFT states.

---

## 2.2. Physical Ola2 engine: `study06.run_ola2_compounds`

Now, how Ola2 needs to behave to be what you want:

Example CLI:

```bash
PYTHONPATH=src python3 -m study06.run_ola2_compounds   --sm-universe data/raw/sm_universe.json   --blocks-json data/processed/blocks/simple_blocks.json   --templates-json blocks/compound_templates.json   --rules-json config/rules/wave2_compounds.json   --runs-per-target 1000   --seed 123   --output-root data/ola2
```

---

## 2.3. Internal logic (sweep, no filtering)

For each target defined in `wave2_compounds.json` (e.g. proton):

Load rules and inputs:

```python
rules = load_json(wave2_compounds.json)
target_rules = [... for "proton" ...]
templates = load_json(compound_templates.json)
blocks = load_json(simple_blocks.json)
u = load_json(sm_universe.json)
proton = [p for p in u["particles"] if p["name"] == "proton"]
```

Sweeping loop:

```python
for run_idx in range(runs_per_target):
    # (1) sample template
    # (2) sample blocks
    # (3) sample couplings
    # (4) build composite DOFT system
    # (5) integrate
    # (6) composite spectrum + proxies
    # (7) match against proton
    # (8) write CSV row
```

Nothing is discarded: each `run_idx` produces one row in `compounds_proton.csv`.

Key details:

### (1) Choose template

From `templates`, for example:

- `"baryon_triangle"` (3 nodes, edges `[[0,1],[1,2],[2,0]]`), or
- `"baryon_chain"` (3 nodes, edges `[[0,1],[1,2]]`).

One of them is chosen at random, or using some weighting.

### (2) Choose blocks (no hard pre-filter)

From `simple_blocks.json`, choose 3 blocks, for example:

- only those with `family == "pion_like"` for a proton,

but **without** discarding by `d_total`: if you want, you can *prioritize* the best ones, but it is fine to let some “bad” ones through to see what happens. The requirement is:

- sweep and tag, not cut aggressively beforehand.

You can do weighted sampling: better blocks have higher probability of being chosen, but not zero probability for the rest.

### (3) Sample couplings (environment sweep)

For each edge `(i, j)`:

- `k_edge[i,j] ~ Uniform(k_min, k_max)`
- `g_edge[i,j] ~ Uniform(g_min, g_max)`
- `tau_edge[i,j] ~ Uniform(tau_min, tau_max)`

Ranges come from `rules_json` (`environment_ranges`).

If we later see that the sweep produces only garbage, we tighten these ranges; but there is no logical filter that kills runs upfront.

### (4) Build the composite DOFT system

This is exactly what the programmer pointed out does not exist yet:

> “Ola2 still uses the lightweight combinatorial scorer; it does not re-run the DOFT integrator for compounds.”

What needs to be done:

- Build a `CompoundState` that has:
  - one global vector of positions `x` and velocities `v`,
  - for each block `b`:
    - DOFs: `Q_b`, `S1_b`, `S2_b`,
    - internal parameters (from the block’s `theta_internal`),
    - internal couplings of the block,
  - for each edge between blocks:
    - couplings (spring/memory terms) between DOFs of those blocks (e.g. between `Q_i` and `Q_j`, or `S1_i` and `S1_j`).

The integrator (the RK4 you already have) works exactly the same, just with more modes and more terms in `dv/dt`.

Coding psychology:

Create a function:

```python
def build_compound_system(blocks, template, sampled_couplings):
    # builds the mode list, internal links, external links
    return modes, links_internal, links_external
```

And another:

```python
def integrate_compound_system(modes, links_internal, links_external, integration_config):
    # uses the same integrator as Ola1 (same signature that already exists)
    return time_series, spectra, layer_energies, proxies
```

### (5) Integrate

Same as Ola1, with the `t_max` and `dt` from the core engine (or slightly larger if needed for the system to settle).

No filter like “if it destabilizes, kill the run”: if it blows up to ±∞, we tag it as `unstable` in the output and keep the record.

### (6) Extract composite spectrum + proxies

Same as Ola1, but at the composite level:

- `band_centers_comp`, `band_widths_comp`,
- `lock_quality_Q_comp`, `lock_quality_S1_comp`, `lock_quality_S2_comp`,
- `s2_band_fraction_comp`, `s2_state_compound`,
- `first_energy_comp`, `spacing_mean_comp`, etc.

All these fields are stored in each CSV row.

### (7) Match against SM (target proton)

Use the same scorer as `match_sm_ola1`, but applied to the composite spectrum:

- `d_total_target`,
- `d_spacing_target`,
- `enough_levels`.

### (8) Write CSV row (no discards)

Minimum fields per row:

- `target`, `run_idx`, `template_name`,
- `block_ids`, `block_families`,
- `k_edges`, `g_edges`, `tau_edges`,
- `lock_Q_comp`, `lock_S1_comp`, `lock_S2_comp`,
- `s2_band_fraction_comp`, `s2_state_comp`,
- `first_energy_comp`, `spacing_mean_comp`,
- `d_total_target`, `d_spacing_target`, `enough_levels`,
- `unstable_flag`.

File: `data/ola2/raw/compounds_proton.csv`.

No run is lost: everything is logged.

---

## 2.4. Viability tags (without deleting anything)

Then, a separate script:

- `study06.label_ola2_viability`:

It reads `compounds_proton.csv`.

For each row, it computes `label`:

- `NO` if:
  - `unstable_flag == 1`, or
  - `enough_levels == 0`, or
  - `s2_state_comp == "none"` (if we want to require active S2), or
  - `structure_tier_comp < level2`, etc.
- `YES` if:
  - it passes all the NO conditions, and
  - `d_total_target < d_yes_baryon` (threshold from the rules JSON).
- `POSSIBLE` if:
  - it is neither NO nor YES, and
  - `d_yes_baryon ≤ d_total_target < d_possible_baryon`.

It writes `reports/ola2_viability/viability_proton.csv` with:

```text
target,run_idx,template_name,block_ids,label,d_total_target,structure_tier_comp,s2_state_comp
```

Key point: this tagging does **not** remove rows, it only adds information.  
If later you want to “promote” compounds to Ola3, you create another script that takes only YES rows and writes another JSON, but you always keep the raw Ola2 CSV.

