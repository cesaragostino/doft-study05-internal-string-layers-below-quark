# Study05 – S2-Friendly Region Analysis (Specification)

## 1. Context: `CaseB_debug_all_runs_proxies.csv`

We **do not** touch the simulator.

We **do not** force families into the sampling.

We only define a region in proxy space where S2 appears much more often, and compare it with the rest.

Idea:

- Define an **“S2-friendly” region** with simple cuts on:
  - `first_energy`
  - `spacing_mean`
  - `Nucleon_like_d_spacing`
- Then measure:
  - p(S2 | region)
  - p(S2 | outside)
  - Statistics of the other proxies inside / outside.

This gives us a map: **“where S2 lives in proxy space.”**

---

## 2. Numbers we already have (the ones we will use)

From the 200 runs:

### Runs **without** S2

- `spacing_mean` ≈ 0.40, σ ≈ 0.14  
- `first_energy` ≈ 1.02, σ ≈ 0.34  
- `Nucleon_like_d_spacing` ≈ 5.04, σ ≈ 2.10  

### Runs **with** S2

- `spacing_mean` ≈ 0.55, σ ≈ 0.17  
- `first_energy` ≈ 0.53, σ ≈ 0.22  
- `Nucleon_like_d_spacing` ≈ 6.85, σ ≈ 2.16  

And we tried the following cut:

- `first_energy` < 0.8 GeV  
- `spacing_mean` > 0.45 GeV  
- `Nucleon_like_d_spacing` > 6.0 GeV  

Results of that cut (computed on your data):

- In the region (`in_region2 = True`): 22 runs  
  - p(S2 | region) ≈ 0.32
- Outside the region: 178 runs  
  - p(S2 | outside) ≈ 0.10

So: **inside** that little proxy box, the probability that S2 dominates is ~3× higher.  
It’s a simple cut and it already shows structure.

---

## 3. Specification for the new pipeline step

### 3.1. New script: `study05/analyze_s2_region.py`

Suggested CLI:

```bash
PYTHONPATH=src python3 -m study05.analyze_s2_region \
  --case CaseB_debug \
  --proxies-csv reports/CaseB_debug_pipeline/CaseB_debug_all_runs_proxies.csv \
  --first-energy-max 0.8 \
  --spacing-mean-min 0.45 \
  --nucleon-d-spacing-min 6.0 \
  --output reports/CaseB_debug_pipeline/s2_region
```

Parameters:

- `--case`: just for labeling in the summary.
- `--proxies-csv`: path to the big CSV of all runs.
- Thresholds:
  - `--first-energy-max` (default 0.8)
  - `--spacing-mean-min` (default 0.45)
  - `--nucleon-d-spacing-min` (default 6.0)
- `--output`: output base directory.

---

### 3.2. Internal logic

1. Read `CaseB_debug_all_runs_proxies.csv` into a DataFrame.

2. Define the region mask:

```python
in_region = (
    (df["first_energy"] < first_energy_max) &
    (df["spacing_mean"] > spacing_mean_min) &
    (df["Nucleon_like_d_spacing"] > nucleon_d_spacing_min)
)
```

3. Create a boolean column:

```python
df["in_s2_region"] = in_region
```

4. Compute basic counts:

```python
n_total = len(df)
n_region = in_region.sum()
n_out = n_total - n_region

has_s2 = df["has_s2_dominant"] == 1
k_region = (has_s2 & in_region).sum()
k_out = (has_s2 & ~in_region).sum()
```

5. Compute proportions and binomial errors:

```python
def frac_ci(k, n):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    se = (p * (1 - p) / n) ** 0.5
    return p, p - 1.96 * se, p + 1.96 * se

p_region, lo_region, hi_region = frac_ci(k_region, n_region)
p_out, lo_out, hi_out = frac_ci(k_out, n_out)
```

6. Compute proxy statistics inside / outside:

For each key column, e.g.:

- `first_energy`
- `spacing_mean`
- `Nucleon_like_d_spacing`
- `R_S1_Q`
- `R_S2_S1`
- `band_count`
- etc.

```python
stats = {}
for col in ["first_energy", "spacing_mean", "Nucleon_like_d_spacing",
            "R_S1_Q", "R_S2_S1", "band_count"]:
    stats[col] = {
        "region_mean": float(df.loc[in_region, col].mean()),
        "region_std": float(df.loc[in_region, col].std()),
        "out_mean": float(df.loc[~in_region, col].mean()),
        "out_std": float(df.loc[~in_region, col].std())
    }
```

7. Save a summary JSON:  
`reports/CaseB_debug_pipeline/s2_region_summary.json`:

```json
{
  "case": "CaseB_debug",
  "cuts": {
    "first_energy_max": 0.8,
    "spacing_mean_min": 0.45,
    "nucleon_d_spacing_min": 6.0
  },
  "counts": {
    "n_total": 200,
    "n_region": 22,
    "n_out": 178,
    "k_region_s2": k_region,
    "k_out_s2": k_out
  },
  "s2_fractions": {
    "region": {
      "p": p_region,
      "ci95": [lo_region, hi_region]
    },
    "out": {
      "p": p_out,
      "ci95": [lo_out, hi_out]
    }
  },
  "proxy_stats": {
    "...": "as in the Python snippet above"
  }
}
```

8. Also save two CSVs:

- `s2_region_in.csv`: `df[in_region]`
- `s2_region_out.csv`: `df[~in_region]`

So you can inspect individual runs inside / outside the region.

---

### 3.3. Optional plots

In the same script (or a separate one), you can generate:

1. **Scatter `first_energy` vs `spacing_mean`:**
   - Color by `has_s2_dominant` (0/1).
   - Different marker or edge for `in_s2_region`.

2. **Comparative histograms of `spacing_mean`:**
   - One curve for runs `in_region`.
   - Another for `out_region`.

3. **Simple bar chart of p(S2):**
   - Bar 1: region (with 1σ error bar).
   - Bar 2: outside (with 1σ error bar).

All saved under:  
`reports/CaseB_debug_pipeline/s2_region/`.

---

## 4. What we do with this

With that script working, you will have:

- A clear number:

  > “In the S2-friendly region (defined by those cuts) S2 dominates in ~0.32 ± something,  
  > vs ~0.10 ± something outside.”

- A summary of how structural proxies (`R_S2_S1`, `band_count`, etc.) change inside / outside.

This already tells you:

- Whether S2 is associated with “nucleon-like runs with low, well-separated levels.”
- Whether there are other combinations of proxies worth trying as an alternative region
  (you can play with thresholds **without** touching the simulator).

Once this is running and we see the first `s2_region_summary.json`, we can iterate on:

- Adjusting cuts (maybe deriving them from percentiles instead of fixed numbers).
- Defining more than one candidate region.
- And later, when you introduce S3, repeating this analysis while also looking at
  `s3_band_fraction` and more “atomic” proxies.
