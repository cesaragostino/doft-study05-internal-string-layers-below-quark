# 1. Concept: New “Family” Layer

On top of CaseA/CaseB/... we introduce a configuration layer:

**FamilySpec → generates DOFT parameter constraints/priors  
+ a matching criterion against the simulated spectrum.**

**Goal:**

Given a set of experimental data for a family (m₀, m₁, m₂, Γ, type):

- run the simulator conditioned on that family, and  
- measure, within the runs that resemble that family, how S2 behaves  
  (fraction of runs with S2 active, typical energies, etc.).

---

## 2. New Data Structures

### 2.1. `FamilySpec`

New module, e.g. `study05/families.py`:

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class FamilySpec:
    name: str
    hadron_type: str      # "meson", "baryon", "exotic", etc.
    masses_gev: List[float]  # [M0, M1, M2, ...] ordered
    widths_gev: Optional[List[float]] = None  # [Γ0, Γ1, ...] optional
    jpc: Optional[str] = None                 # "1--", "0-+", etc., optional
    energy_window: Tuple[float, float] = (0.2, 3.0)  # energy band to analyze
```

### 2.2. `FamilyFingerprint`

Derived from `FamilySpec`, for fast comparisons:

```python
@dataclass
class FamilyFingerprint:
    n_levels_target: int           # how many relevant levels in the window
    target_spacings: List[float]   # ΔM_i = M_{i+1} - M_i
    spacing_tol: float             # relative tolerance (e.g. 20%)
    target_widths: Optional[List[float]] = None  # if Γ are used
```

Construction function:

```python
def build_fingerprint(spec: FamilySpec) -> FamilyFingerprint:
    # filter masses_gev inside energy_window
    # compute ΔM_i
    # choose spacing_tol (e.g. 0.2 * mean(ΔM))
```

---

## 3. Map Family → DOFT Parameter Priors

New function:

```python
@dataclass
class FamilyPriors:
    # restricted ranges for ratios and couplings
    R_S1_Q_range: Tuple[float, float]
    R_S2_S1_range: Tuple[float, float]
    g_QS1_scale_range: Tuple[float, float]
    g_S1S2_scale_range: Tuple[float, float]
    memory_strength_range: Tuple[float, float]
    # optional: suggested N_Q, N_S1, N_S2
```

Main function:

```python
def make_priors_for_family(spec: FamilySpec) -> FamilyPriors:
    ...
```

Heuristic (summary):

- Compute ΔM_exp = list of experimental spacings (in the window).
- `n_levels_target = len(ΔM_exp) + 1`.

Simple rules:

- If `n_levels_target == 2` (two clear levels):

  - “2-band” family → Q+S1, S2 almost off.
  - `R_S1_Q_range` relatively narrow (e.g. `[2, 3]`).
  - `R_S2_S1_range` high (e.g. `[2.5, 4.0]`) to push S2 out of the window.
  - `g_S1S2_scale_range` moderate.

- If `n_levels_target >= 3`:

  - “3-band” family → we *want* S2 active.
  - `R_S1_Q_range`: tuned so that ΔE_sim ≈ average ΔM_exp.  
    Example: if `ΔM_exp_mean ≈ 0.6 GeV`, use the range where we already saw S2 appear (from CaseB sweeps).
  - `R_S2_S1_range`: centered in the band where the sweep showed S2 (e.g. `[1.6, 2.0]`).
  - `g_S1S2_scale_range`: somewhat larger than `g_QS1` (×1.5–2 factor).
  - `memory_strength_range`: if widths Γ are large → increase range; if Γ are very small → decrease.

In addition, `hadron_type` can modulate topology:

- `"meson"` → 1D chain (what you already have).
- `"baryon"` → for now: same chain but with stronger internal couplings (multiply all `g` by 1.5–2).  
  Later this could become a different graph.

This does **not** perform a perfect “fit”, but it focuses the sweep on the parameter region that makes sense for that family.

---

## 4. Changes in `run_sweep`

### 4.1. CLI

Add flags:

```bash
--family-name <NAME>      # e.g. Nucleon, Rho, Pion, etc.
--family-config <PATH>    # optional: external JSON with FamilySpec
```

Usage:

- If `--family-config` is provided, load that JSON as `FamilySpec`.
- Else, if `--family-name` is provided, look it up in an internal dictionary of predefined families.
- If neither is provided, behavior is the current one (agnostic sweep).

### 4.2. Per-run Pipeline

For each run:

**Parameter sampling:**

- Instead of using global Case ranges, use `FamilyPriors` ranges  
  (or the intersection Case ∩ FamilyPriors).

**Simulation:**

- Same as now → you obtain `energies_gev`, `layer_weights`, etc.

**Simulated fingerprint:**

```python
sim_levels = energies_gev_in_window_sorted
sim_spacings = np.diff(sim_levels)
```

**“Family likeness” score:**

```python
score_spacing = compare_spacings(sim_spacings, target_spacings, spacing_tol)
# e.g. normalized RMSE or simply "all(|ΔE_sim - ΔM_exp| < tol)"
```

Tag:

```python
is_family_match = score_spacing_ok and (
    len(sim_levels) == n_levels_target or close
)
```

**S2 statistics:**

- Determine the dominant layer of each band (as you already do).
- Count whether at least one band is S2-dominated.

In the family summary, separate:

- `runs_family_match_total`
- `runs_family_match_with_s2`
- `runs_family_match_without_s2`
- `runs_off_family_with_s2` (to see S2 “false positives”).

### 4.3. Extended JSON Output

In `study05_sweep_results.json`, inside `"summary"`:

```json
"family": {
  "name": "Nucleon_like",
  "n_levels_target": 3,
  "target_spacings": [0.5, 0.6],
  "spacing_tol": 0.15
},
"family_match_stats": {
  "runs_family_match_total": 42,
  "runs_family_match_with_s2": 28,
  "runs_family_match_without_s2": 14,
  "runs_off_family_with_s2": 5
}
```

Optionally, per run:

- Add a field `family_match: true/false` to each `run_result` entry.

---

## 5. What Do *You* Do With This?

- You look up in tables (PDG) the first 2–3 masses of a family  
  (e.g. nucleons, rho, etc.).
- You build a `family_config` JSON, for example:

```json
{
  "name": "Nucleon_like",
  "hadron_type": "baryon",
  "masses_gev": [0.939, 1.44, 1.71],
  "widths_gev": [0.0, 0.35, 0.1],
  "energy_window": [0.2, 3.0]
}
```

- You run:

```bash
PYTHONPATH=src python3 -m study05.run_sweep     --case CaseB_debug     --runs 1000     --family-config nucleon_like.json
```

- You inspect the summary:

  - what fraction of runs that mimic the nucleon require S2,
  - how the energies of S2-dominant bands are distributed,
  - how the spacings change compared to the agnostic sweep.

This is exactly “typing by family” and using the model to see how S2 fluctuates depending on the particle family.
