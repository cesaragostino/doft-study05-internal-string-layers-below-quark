# 1. S2: what is already in place and how we fix it

For S2 I would consider it “closed” like this, at the interface level:

In the results of each run (sweep):

- `has_s2_dominant` (0/1)
- `s2_band_fraction`: weight of S2 in the hadronic band (0–1).
- `s2_total_fraction`: total weight of S2 in the whole spectrum.
- `first_energy`, `spacing_mean`, `Nucleon_like_d_spacing` (you already have these).
- `s2_zone ∈ {core, friendly, extended, out}` (catalog label).

And at the analysis level:

- `tag_s2_zones.py` → adds `s2_zone`.
- `catalog_families_s2.py` → crosses S2 with families (`closest_family`).

I wouldn’t touch that anymore: this becomes our “pattern” for inner layers.

---

# 2. S3: what makes it different and what we need

S3 is NOT just “another layer that may or may not be dominant”.
In this model S3 can play two very different roles:

1. **Structural layer (like S2):**  
   contributes a well-defined band in the hadronic range.

2. **Noise / high-frequency sink:**  
   absorbs part of the energy in very spread-out modes or outside the window we look at, without forming a clear band.

So for S3 we need:

- everything S2 has (`band_fraction`, dominant flag), plus:
- explicit noise metrics and per-layer state classification.

## 2.1. S3 states per run

For each run, S3 should end up in one of these states:

- `S3_STATE_ABSENT`  
  → total weight of S3 is almost zero.

- `S3_STATE_STRUCTURAL_DOMINANT`  
  → there is a hadronic band, and S3 is the main contribution.

- `S3_STATE_STRUCTURAL_SUB`  
  → S3 contributes to the band but does not dominate (e.g. 10–40% of the weight).

- `S3_STATE_NOISE_TAIL`  
  → S3 carries almost no weight in the band, but has a lot of energy spread
    over out-of-band modes or very dispersed modes.

- `S3_STATE_MIXED` (optional)  
  → some band and some noise, without either component being clearly dominant.

This should **not** be hard-coded: ideally thresholds come from a config (e.g. `layer_states.yaml`),
but we do need to fix the logic now.

## 2.2. Minimum metrics to classify S3

In addition to what you already compute per layer for S2, for S3 we need at least:

- `s3_band_fraction`:  
  weight of S3 in the selected hadronic band (0–1).

- `s3_outband_fraction`:  
  weight of S3 outside the hadronic band (0–1).

- `s3_band_compactness`:  
  something like `1 / σ_E` or `σ_E^{-1}`, where `σ_E` is the standard deviation of the energies
  of the modes where S3 has weight.  
  Intuition: strong band → high compactness (peaked); noise → low compactness (spread out).

- `s3_highfreq_fraction`:  
  weight of S3 above some energy cutoff (e.g. > 3 GeV or > `band_max`).

With that you can define rules like:

- **Dominant:**  
  `s3_band_fraction >= 0.5` and `s3_band_compactness >= C_dom`.

- **Sub:**  
  `0.1 <= s3_band_fraction < 0.5` and `s3_band_compactness >= C_sub`.

- **Noise_tail:**  
  `s3_band_fraction < 0.1` and (`s3_outband_fraction` or `s3_highfreq_fraction`) large, and compactness low.

- **Absent:**  
  `s3_total_fraction` very small (`< ε`).

We don’t need to fix the exact numbers `C_dom`, `C_sub`, `ε` today; the important part is that the architecture expects this type of metrics.

---

# 3. Specification for the developer

## 3.1. Per-layer data structure (generic)

Instead of having loose fields `s2_...` and then inventing `s3_...`, it’s better that from now on
the code thinks in terms of indexed layers.

Something like:

```python
# Pseudocode / conceptual dataclass
LayerSummary = {
    "name": "Q" | "S1" | "S2" | "S3",
    "band_fraction": float,
    "total_fraction": float,
    "band_compactness": float,
    "outband_fraction": float,
    "highfreq_fraction": float,
    "is_dominant": bool,
    "state": "absent" | "structural_dominant" | "structural_sub" | "noise_tail" | "mixed"
}

RunSummary = {
    "case": "CaseB_4layers",
    "seed": int,
    "params": {...},
    "band_count": int,
    "spacing_mean": float,
    "first_energy": float,
    ...
    "layers": {
        "Q":  LayerSummary,
        "S1": LayerSummary,
        "S2": LayerSummary,
        "S3": LayerSummary,
    },
    # “flat” fields for CSV:
    "has_s2_dominant": 0/1,
    "has_s3_dominant": 0/1,
    "s2_band_fraction": float,
    "s3_band_fraction": float,
    "s3_state": str,
    ...
}
```

Internally you work with `layers["S2"]`, `layers["S3"]`, etc., and when writing the CSV
you “flatten” the most commonly used fields.

## 3.2. Concrete fields to add in the 4-layer sweep output

In addition to what already exists for S2 and global:

Per layer (flat columns):

- `s2_band_fraction`, `s2_total_fraction`, `s2_band_compactness`,  
  `s2_outband_fraction`, `s2_highfreq_fraction`, `s2_state`

- `s3_band_fraction`, `s3_total_fraction`, `s3_band_compactness`,  
  `s3_outband_fraction`, `s3_highfreq_fraction`, `s3_state`

Flags:

- `has_s2_dominant = 1` if `s2_state == "structural_dominant"`.
- `has_s3_dominant = 1` if `s3_state == "structural_dominant"`.

Later, if you want to study noise:

- `has_s3_noise = 1` if `s3_state == "noise_tail"`.
- `has_noise_layer = 1` if any layer has `state == "noise_tail"`.

## 3.3. Files and directories (to keep S2/S3 separate)

I propose this structure for each `CaseX`:

```text
reports/CaseX/
  global/
    CaseX_all_runs_proxies.csv
    CaseX_sweep_summary.json
  s2/
    s2_region_summary.json
    s2_region_in.csv
    s2_region_out.csv
    s2_scan_results.csv
    family_zone_summary.csv   # S2 vs families
  s3/
    s3_state_summary.json
    s3_noise_summary.json
    s3_scan_results.csv       # analogous to S2 when we have it
    s3_family_zone_summary.csv
```

And in `data/` you keep:

```text
data/raw/CaseX/global/study05_sweep_params.json
data/processed/CaseX/global/study05_sweep_results.json
```

The key idea: S2 and S3 each have their own subtree, but they share the global CSV as source.

## 3.4. Analysis scripts (already designed as generic)

- `tag_s2_zones.py` (you already have it) → operates on `all_runs_proxies.csv` + S2 fields.

In the future, an analogous `tag_s3_zones.py`, but:

- it will use `has_s3_dominant`, `s3_band_fraction`, `s3_band_compactness`,
- and probably different cuts (to be defined after the first 4-layer sweep).

- `catalog_families_s2.py` → crosses S2 vs families.
- `catalog_families_s3.py` → same scheme, but using `s3_state`, `has_s3_dominant`, etc.

You can even make a single generic script:

```bash
python -m study05.catalog_families_layer   --layer S2   --proxies-csv ...

python -m study05.catalog_families_layer   --layer S3   --proxies-csv ...
```

where `--layer` decides which columns to look at (`has_s2_dominant` vs `has_s3_dominant`, etc.).

---

# 4. Noise: how we make it explicit from now on

So that the developer thinks “S3 can be noise” from the design:

- Explicitly include the `state` field in the `LayerSummary` interface with the values listed above.

- Define in a config (e.g. `config/layer_states.yaml`) something like:

```yaml
S2:
  band_fraction_dominant: 0.5
  band_fraction_sub: 0.1
  compactness_dom:  X2
  compactness_sub:  X1
  total_fraction_eps: 1e-3

S3:
  band_fraction_dominant: 0.4   # maybe more relaxed
  band_fraction_sub: 0.05
  compactness_dom:  Y2
  compactness_sub:  Y1
  total_fraction_eps: 1e-3
  noise_highfreq_min: 0.2       # if >20% of the energy is above the cutoff, favors "noise_tail"
```

That way the code is ready for S3 to be:

- “absent” in some runs,
- “band” in others,
- “noise_tail” in many, without changing the function signature.

---

## Summary

- S2 is already well-defined; we just need to continue with tagging and cataloguing as agreed.

- For S3, the key difference is that it can be structure **or** noise; therefore:
  - we give it its own metrics (band, outband, compactness, highfreq),
  - and a `state` with explicit cases (dominant, sub, noise_tail, absent).

We design from the start separate outputs and scripts for S2 and S3, but with a common
per-layer architecture, so the developer thinks about the system “as a whole” and not in patches.
