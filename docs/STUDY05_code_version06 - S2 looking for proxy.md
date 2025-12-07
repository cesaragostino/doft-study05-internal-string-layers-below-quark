# 3. Proposed New Architecture (what you need to implement)

## 3.1. Agnostic sweeps (no family)

`study05.run_sweep` works as follows:

**Inputs:** `--case`, `--runs`, `--seed`, `--band-min`, `--band-max`.

It does **not** use `--family-name` or `--family-config` to generate parameters.

For each run:

- Sample DOFT parameters from the case (as before).
- Simulate.
- Store a complete record.

**Per-run record** (JSON / CSV row, key fields):

**Input parameters (proxies for internal structure):**

- `R_S1_Q`, `R_S2_S1` (and if there is S3: `R_S3_S2`),
- coupling strengths `g_QS1`, `g_S1S2`, etc.,
- memory parameters `tau_*`, amplitudes, etc.

**Summary of the spectrum in the hadronic window:**

- `band_count`,
- `energies_gev` (list),
- `layer_dominant` per band (`Q` / `S1` / `S2`),
- statistics:
  - `spacing_mean`, `spacing_std`, `spacing_min`, `spacing_max`.

**S2 / S3 indicators:**

- `has_s2_dominant` (bool),
- `s2_band_fraction = (# bands dominated by S2 / band_count)`,
- same for S3 when it exists.

You store everything in something like:

```text
data/processed/<case>/global/study05_sweep_results.json
```

(containing the full list of runs).

Up to this point: **no family proxy and no PDG input has touched the sampling.**

---

## 3.2. Offline analysis of proxies and families

New module: `study05/analyze_proxies.py`

### 3.2.1. Inputs

```bash
PYTHONPATH=src python3 -m study05.analyze_proxies   --case CaseB_debug   --families Nucleon_like Rho_like Pion_like   --output reports/CaseB_debug_proxies
```

It loads:

- the global sweep `data/processed/<case>/global/...`,
- the `FamilySpec` for each specified family.

### 3.2.2. For each run

Load what you already have (parameters + spectrum + S2/S3).

**Compute “pure” spectrum proxies (no family):**

- `spacing_mean`, `spacing_std` (already there),
- `first_energy`, `second_energy`, … (the first 3 bands),
- `n_levels_in_window` (same as `band_count`),
- `s2_band_fraction`, `s3_band_fraction`, …

**Compute metrics per family (without touching the simulation):**

For each family **F**:

- Filter energy levels within `family.energy_window`.
- If `n_levels_sim < n_levels_target(F)`:
  - mark `has_enough_levels_F = False`,
  - set `d_total_F = NaN` (or undefined).
- If there are enough levels:
  - compute `FamilyFingerprint(F)` (as before),
  - compute separate, non-collapsed metrics:
    - `delta_mean_spacing_F = spacing_mean_sim - spacing_mean_exp_F`,
    - a vector `delta_spacings_F[i] = ΔE_sim[i] - ΔM_exp[i]` normalized by `spacing_tol`,
    - optionally: width metrics.
  - build `d_total_F` as a sum or L2 norm, but you **don’t** need to force it to a single scalar if you don’t want; you can store each component.

Result: one big row per run containing:

- DOFT proxies (`R`, `g`, `taus`, etc.),
- spectral proxies (`spacing_mean`, `spacing_std`, `#levels`, etc.),
- for each family **F**:
  - `has_enough_levels_F` (bool),
  - `delta_mean_spacing_F`,
  - `d_total_F` (if you define it),
  - etc.

This is stored in a large CSV, e.g.:

```text
reports/CaseB_debug_proxies/all_runs_proxies.csv
```

Each row = one run, each column = one proxy / metric.

Nothing is filtered out or discarded; everything remains explorable.

---

## 3.3. Correlation analysis (the important part)

On that CSV, you do:

### Simple (numerical) correlations

For example, Pearson / Spearman between:

- `has_s2_dominant` (0/1)
- and each proxy:
  - `spacing_mean`,
  - `R_S2_S1`,
  - `delta_mean_spacing_Nucleon_like`,
  - etc.

Result: a table like:

```text
proxy, corr_with_s2, corr_p_value
spacing_mean, 0.45, 1e-5
R_S2_S1, -0.30, 0.002
delta_mean_spacing_Nucleon_like, -0.10, 0.12
...
```

This answers: **which proxies are actually aligned with the appearance of S2, without having forced them beforehand.**

### Conditional comparisons

Take all runs with `S2_active = 1` vs `S2_active = 0`, and compare the distributions of:

- `R_S2_S1`,
- `spacing_mean`,
- `delta_mean_spacing_F` for each family **F**.

You do this with boxplots, overlaid histograms, etc.

### Clustering / structure map (if you want to go further)

Build a feature vector per run:

```text
[spacing_mean, spacing_std, s2_band_fraction, R_S2_S1,
 delta_mean_spacing_Nucleon_like, delta_mean_spacing_Rho_like, ...]
```

Run a K-means or hierarchical clustering.

Check whether the clusters align with:

- presence/absence of S2,
- closeness to each family.

All of this is **post-processing only**. The simulator knows nothing about families or proxies; it just spits out data. You then “look first” and decide which region to focus on.
