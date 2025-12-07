0. Quick check of the region with the 3 seeds
===========================================

From the combined `s2_region_summary.json`:

- `n_total = 600`
- `n_region = 67`
- `n_out = 533`

Dominant S2:

- in region: `21/67` → `p ≈ 0.313` (CI95 ≈ `[0.20, 0.42]`)
- outside: `62/533` → `p ≈ 0.116` (CI95 ≈ `[0.089, 0.144]`)

This is the same as before but with more statistics:
the region increases the probability of S2 by a factor of ~2.7 and the difference is stable.
In addition, the proxy means remain:

- `first_energy` region: `0.62` vs outside: `0.97`
- `spacing_mean` region: `0.53` vs outside: `0.41`
- `nucleon_like_d_spacing` region: `8.0` vs outside: `4.9`

In other words, the S2-friendly patch is real.

Let’s move to Phase 2.

---

Phase 2 – Threshold-scan analyzer (and zoo map)
===============================================

Below is a precise spec to implement the missing analyzer.

1. Script: `study05/analyze_s2_scan.py`
--------------------------------------

**Goal**  
Without running more simulations, scan different boxes in the proxy space  
(`first_energy`, `spacing_mean`, `nucleon_like_d_spacing`) and measure:

- size of the region,
- `p(S2 | region)`,
- `p(S2 | outside)`,
- z-score of the difference.

### 1.1. CLI

PYTHONPATH=src python3 -m study05.analyze_s2_scan \
  --proxies-csv reports/CaseB_debug_combined/CaseB_debug_all_runs_proxies.csv \
  --output reports/CaseB_debug_combined/s2_scan

Optional parameters (with reasonable defaults):

  --first-grid 0.6 0.7 0.8 0.9 \
  --spacing-grid 0.40 0.45 0.50 \
  --dspacing-grid 5.5 6.0 6.5

### 1.2. Internal logic

Read the large CSV with all runs (600 rows).

Minimum required columns:

- `first_energy`
- `spacing_mean`
- `Nucleon_like_d_spacing`
- `has_s2_dominant` (0/1)

For each triple of cuts:

for f_max in first_grid:
    for s_min in spacing_grid:
        for d_min in dspacing_grid:
            in_region = (
                (df["first_energy"] < f_max) &
                (df["spacing_mean"] > s_min) &
                (df["Nucleon_like_d_spacing"] > d_min)
            )
            ...

Compute counts:

n_total = len(df)
n_region = in_region.sum()
n_out = n_total - n_region

has_s2 = df["has_s2_dominant"] == 1
k_region = (has_s2 & in_region).sum()
k_out = (has_s2 & ~in_region).sum()

If `n_region == 0` or `n_out == 0`, skip that combination or mark it as invalid.

Proportions and errors:

def frac_and_se(k, n):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    se = (p * (1 - p) / n) ** 0.5
    return p, se

p_reg, se_reg = frac_and_se(k_region, n_region)
p_out, se_out = frac_and_se(k_out, n_out)

delta_p = p_reg - p_out
se_delta = (se_reg**2 + se_out**2) ** 0.5
z_score = 0.0 if se_delta == 0 else delta_p / se_delta

Save the result of each box in a list of dicts:

rows.append({
    "first_max": f_max,
    "spacing_min": s_min,
    "dspacing_min": d_min,
    "n_total": n_total,
    "n_region": int(n_region),
    "k_region_s2": int(k_region),
    "p_region": p_reg,
    "se_region": se_reg,
    "n_out": int(n_out),
    "k_out_s2": int(k_out),
    "p_out": p_out,
    "se_out": se_out,
    "delta_p": delta_p,
    "z_score": z_score,
})

Export to CSV:

reports/CaseB_debug_combined/s2_scan_results.csv

### 1.3. Downstream usage

With that CSV you can:

- sort by `z_score` in descending order to see which boxes:
  - have good signal (high z),
  - and are not too small (`n_region` acceptable).
- pick 1–2 “best” patches, not just the original one.

2. Optional script: `study05/fit_s2_logit.py` (if you want a soft boundary)
---------------------------------------------------------------------------

This is optional but useful.

**Goal**  
Fit a simple logistic regression that predicts `has_s2_dominant` using the proxies.  
Not to use it in simulation, but to see the shape of the boundary in the plane.

### 2.1. CLI

PYTHONPATH=src python3 -m study05.fit_s2_logit \
  --proxies-csv reports/CaseB_debug_combined/CaseB_debug_all_runs_proxies.csv \
  --output reports/CaseB_debug_combined/s2_logit

### 2.2. Summary of the logic

- Features:  
  `X = [first_energy, spacing_mean, Nucleon_like_d_spacing]`
- Target:  
  `y = has_s2_dominant` (0/1)

Fit a logistic model (you can use `sklearn.linear_model.LogisticRegression`).

Save:

- coefficients β (to interpret signs),
- training score (AUC, accuracy),
- optionally, a probability grid `p(S2)` in the plane
  (`first_energy`, `spacing_mean`) to plot contour lines.

This tells you whether the boundary is more or less linear or whether we need something more complex; but again, it is 100% post-processing.
