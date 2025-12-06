# 0. Objective

Extend Study05 so that, given a **FamilySpec** (Nucleon_like, Rho_like, etc.):

- The sweep generates **distance-to-family metrics per run**.  
- It splits results into **per-family directories**.  
- It generates **comparative summaries between families**, to see how S2 activation and spacing structure change.

---

## 1. Data Structures (Families and Fingerprints)

### 1.1. `FamilySpec` (already defined, but we fix the format)

JSON file (e.g. `config/Nucleon_like.json`):

```json
{
  "name": "Nucleon_like",
  "hadron_type": "baryon",
  "masses_gev": [0.939, 1.44, 1.71, 1.88],
  "widths_gev": [0.0, 0.35, 0.15, 0.25],
  "jpc": "1/2+",
  "energy_window": [0.2, 3.0]
}
```

Python class in `study05/families.py`:

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class FamilySpec:
    name: str
    hadron_type: str
    masses_gev: List[float]
    widths_gev: Optional[List[float]] = None
    jpc: Optional[str] = None
    energy_window: Tuple[float, float] = (0.2, 3.0)
```

### 1.2. `FamilyFingerprint`

Built from `FamilySpec`:

```python
@dataclass
class FamilyFingerprint:
    n_levels_target: int
    target_spacings: List[float]
    spacing_tol: float
    target_widths: Optional[List[float]] = None
```

Function:

```python
def build_fingerprint(spec: FamilySpec) -> FamilyFingerprint:
    # 1. Filter masses_gev inside spec.energy_window
    masses = [m for m in spec.masses_gev
              if spec.energy_window[0] <= m <= spec.energy_window[1]]
    masses = sorted(masses)

    # 2. ΔM
    spacings = [masses[i+1] - masses[i] for i in range(len(masses)-1)]
    n_levels_target = len(masses)

    # 3. Tolerance: e.g. 20% of the average spacing
    mean_spacing = sum(spacings) / len(spacings)
    spacing_tol = 0.2 * mean_spacing

    return FamilyFingerprint(
        n_levels_target=n_levels_target,
        target_spacings=spacings,
        spacing_tol=spacing_tol,
        target_widths=spec.widths_gev
    )
```

(If you want to keep a fixed tolerance you already used, just change the `spacing_tol` line.)

---

## 2. Distance-to-Family Metric per Run

New function in `families.py`:

```python
@dataclass
class FamilyDistance:
    n_levels_sim: int
    spacings_sim: List[float]
    d_spacing: float      # χ or normalized L1
    d_widths: Optional[float]
    d_total: float        # final combined score
    is_match: bool
```

Suggested implementation:

```python
from typing import List, Optional

def compute_family_distance(
    sim_levels: List[float],              # sorted energies_gev inside energy_window
    sim_widths: Optional[List[float]],    # optional
    fingerprint: FamilyFingerprint,
    use_widths: bool = False
) -> FamilyDistance:
    n_sim = len(sim_levels)
    sim_spacings = [sim_levels[i+1] - sim_levels[i]
                    for i in range(n_sim-1)]

    n_target = fingerprint.n_levels_target
    target_spacings = fingerprint.target_spacings

    # If there are not enough levels, it's already far
    if n_sim < n_target:
        return FamilyDistance(
            n_levels_sim=n_sim,
            spacings_sim=sim_spacings,
            d_spacing=1e9,
            d_widths=None,
            d_total=1e9,
            is_match=False
        )

    # Take only the first n_target simulated levels
    sim_spacings = sim_spacings[:n_target-1]

    # L1-type distance normalized by spacing_tol
    ds = 0.0
    for s_sim, s_target in zip(sim_spacings, target_spacings):
        ds += abs(s_sim - s_target) / fingerprint.spacing_tol

    ds = ds / (n_target - 1)

    dw = None
    if use_widths and fingerprint.target_widths is not None and sim_widths is not None:
        w_sim = sim_widths[:n_target]
        w_tgt = fingerprint.target_widths[:n_target]
        dw = 0.0
        for ws, wt in zip(w_sim, w_tgt):
            # avoid division by 0
            scale = max(wt, 1e-6)
            dw += abs(ws - wt) / scale
        dw = dw / n_target
        d_total = ds + dw
    else:
        d_total = ds

    # Match criterion (tunable): d_total < 1
    is_match = (d_total < 1.0)

    return FamilyDistance(
        n_levels_sim=n_sim,
        spacings_sim=sim_spacings,
        d_spacing=ds,
        d_widths=dw,
        d_total=d_total,
        is_match=is_match
    )
```

---

## 3. Changes in `run_sweep` (CLI + Per-Run Flow)

### 3.1. CLI

You already have `--family-name` and/or `--family-config`. Keep:

```bash
--family-name <NAME>
--family-config <PATH>
```

In `main()`:

- If `family-config` is given → load JSON → `FamilySpec`.  
- Else, if `family-name` is given → look it up in an internal predefined families dictionary.  
- Build `fingerprint = build_fingerprint(spec)`.

### 3.2. Per-Run Loop

For each run:

**Parameter generation**

- If `FamilyPriors` exist (what you already added), use their ranges instead of the Case’s, or take their intersection.

**Simulation**

- You obtain `energies_gev` + `layer_weights` as before.

**Per-run metrics:**

- Sort levels in the window `spec.energy_window`.  
- Compute:

  ```python
  family_dist = compute_family_distance(levels, widths, fingerprint)
  ```

**Dominant layer per band:**

```python
dominant_layer_per_band = np.argmax(layer_weights, axis=0)  # for example
has_s2_dominant = (2 in dominant_layer_per_band)  # if S2 is index 2
```

Store in the per-run result structure.

Example of internal JSON per run (simplified):

```json
{
  "run_id": 8,
  "energies_gev": [0.82, 1.6, 2.0],
  "dominant_layers": ["Q", "S1", "S2"],
  "family_distance": {
    "n_levels_sim": 3,
    "spacings_sim": [0.78, 0.4],
    "d_spacing": 1.3,
    "d_widths": null,
    "d_total": 1.3,
    "is_match": false
  }
}
```

(Your current code already stores similar things; this just extends the dict.)

### 3.3. Global Summary

From all `FamilyDistance` objects:

```text
runs_family_match_total      = number of runs with is_match == True
runs_family_match_with_s2    = number of those where has_s2_dominant == True
runs_family_match_without_s2 = number of those where has_s2_dominant == False
runs_off_family_with_s2      = number of runs with is_match == False & has_s2_dominant == True
```

Also, distance statistics:

```json
"family_distance_stats": {
  "d_total_mean": ...,
  "d_total_std": ...,
  "d_total_min": ...,
  "d_total_max": ...
}
```

All of this goes inside `"summary"` (where you already started adding things).

---

## 4. Per-Family Directories

Change the path logic so that, if a family is present, output is nested like this:

```text
data/
  raw/
    CaseB_debug/
      Nucleon_like/
        study05_sweep_params.json
  processed/
    CaseB_debug/
      Nucleon_like/
        study05_sweep_results.json
```

That is:

```python
from pathlib import Path

base_raw_dir = Path("data/raw") / case_name
base_processed_dir = Path("data/processed") / case_name

if family_spec is not None:
    base_raw_dir = base_raw_dir / family_spec.name
    base_processed_dir = base_processed_dir / family_spec.name
```

This way you do **not** break the previous layout:

- “Agnostic” runs stay directly under `CaseB_debug/`.  
- Per-family runs end up in subdirectories named by family.

---

## 5. Comparative Report Between Families

New script: `study05/report_families.py`

### 5.1. CLI

```bash
PYTHONPATH=src python3 -m study05.report_families \
  --case CaseB_debug \
  --families Nucleon_like Rho_like Pion_like \
  --output reports/CaseB_debug_families
```

Parameters:

- `--case`: Case name (`CaseB_debug`, `CaseC_4layers`, etc.).  
- `--families`: list of family names to include.  
- `--output`: output prefix.

### 5.2. What It Does

For each family **F**:

- Reads `data/processed/<case>/<F>/study05_sweep_results.json`.  
- Extracts from `summary`:

  - `band_count_mean`, `band_count_std`  
  - `spacing_stats.mean`, `spacing_stats.std`  
  - `runs_with_s2_dominant`  
  - `runs_family_match_total`  
  - `runs_family_match_with_s2`  
  - `runs_family_match_without_s2`  
  - `family_distance_stats.*` (if included)  
  - optionally: aggregated `dominant_layers` distribution if you store it.

Builds a comparative table (CSV and JSON).

Example CSV:

```text
family,band_count_mean,spacing_mean,spacing_std,
       runs_valid,runs_with_s2,
       runs_family_match_total,runs_family_match_with_s2,
       d_total_mean,d_total_min
Nucleon_like,4.43,0.33,0.34,100,25,0,0,1.8,0.9
Rho_like,3.9,0.25,0.20,100,18,5,3,1.1,0.5
Pion_like,2.7,0.60,0.45,100,3,0,0,2.5,1.3
```

Save as:

- `reports/CaseB_debug_families_summary.csv`  
- `reports/CaseB_debug_families_summary.json`

Generate comparative plots (optional but very useful):

- `spacing_hist_<family>.png` → spacing histogram per family (you already do this for one; just generalize).  
- `s2_fraction_bar.png` → bar plot with:

  - x-axis: family,  
  - y₁: `runs_with_s2_dominant / runs_valid`,  
  - y₂: `runs_family_match_with_s2 / max(runs_family_match_total, 1)`.

- `d_total_boxplot.png` → boxplot of `d_total` distribution per family.

All under `reports/CaseB_debug_families/`.

---

## 6. Ultra-Short Summary for the Programmer

Add modules/structures:

- `FamilySpec`, `FamilyFingerprint`, `FamilyDistance` in `families.py`.  
- `build_fingerprint()` and `compute_family_distance()`.

Extend `run_sweep`:

- Support `--family-name` / `--family-config`.  
- Condition parameter generation on `FamilyPriors` (if you already implemented them).  
- Per run: compute `FamilyDistance` + dominant layer; store them.  
- In `summary`: add `family`, `family_fingerprint`, `family_match_stats`, `family_distance_stats`.  
- Change output paths so they use `data/.../<case>/<family>/...` when a family is present.

New script `report_families`:

- Reads `study05_sweep_results.json` per family.  
- Produces comparative CSV/JSON + some PNGs (histograms, bars, boxplots).

With this you have everything needed to:

- run the same Case (e.g. `CaseB_debug`),  
- with different families (`Nucleon_like`, `Rho_like`, `Pion_like`), and  
- compare in one shot how S2 activation and spacing structure change → which is exactly the “per-particle structure” you want to see.
