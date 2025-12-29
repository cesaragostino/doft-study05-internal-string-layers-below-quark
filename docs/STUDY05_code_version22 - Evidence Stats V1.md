# New Chapter — Evidence Stats V1  
*(Denominator + Topology Controls)*

## Goal

Convert append-only logs into **publishable statistics**:

- denominators by size / topology / template  
- viable rate with binomial confidence intervals  
- controls (N, factor_7, edge density, template family)

---

## Inputs (source of truth)

- `data/processed/olaN/raw/attempts.jsonl` (Explorer)  
- `data/processed/olaN/raw/evaluations.jsonl` (Sweep, when available)  
- `data/config/olaN/olaN_templates.json` (topology metadata)  
- `data/config/olaN/olaN_taxonomy.json` (definition of “viable” / “LOCKED”, versioned)

---

## Constants Classification (Explorer Metrics)

### A) Numerical safety (no “hyperparameters”)

These are **numerical guardrails**; they do not affect values except in degeneracies:

- `CHAOS_EPS = 1e-12` (avoid `log(0)` / clip)
- `MEM_EPS = 1e-12` (avoid division by zero)

### B) Metric-definition constants (metrics_v1)

These **do affect** metric values and therefore gating.  
Treat them as **versioned choices** (change → version bump).

- `_permutation_entropy(m=5, tau=1)`
- phase entropy bins: `bins=12`
- `QualityLock` scale: `std_max=0.5`

### C) Engine parameters (operational/config)

These come from config and are the Kuramoto knobs:

- `dt`, `T_ticks`, `W`, `K_local`, `kappa_global`, `tau_field`, `sigma0`, `sigma_tc`, `sigma_theta_init`

---

## Outputs

- `data/processed/olaN/catalog/stats_attempts_rollup.csv`  
- `data/processed/olaN/catalog/stats_viable_rate.csv`  
- `data/processed/olaN/catalog/stats_models.json` (coefficients + diagnostics)  
- `data/processed/olaN/catalog/stats_report.md` (tables + conclusions)

---

## Steps (ordered, no options)

### Step S1 — Define the *attempt universe* (denominator)

**Rule:** the denominator is measured over **attempts**, not over “candidates”.

For each record in `attempts.jsonl` (`role = explorer`), extract:

- `ola`  
- `template_name`  
- `N` = number of nodes (from template registry or record)  
- `eval_id`  
- `entity_id`  
- `engine_params_bin_id`  
- `taxonomy_version / thresholds_version` (if applicable)  
- `timestamp_utc`

Construct:

```
attempts_total(N, template) = count(distinct eval_id)
```

(`eval_id` already guarantees de-duplication under resume.)

---

### Step S2 — Define *viable* (numerator) with explicit versioning

Do **not** mix physics with operational criteria.

Define a boolean function:

```
is_viable(record, taxonomy_version)
```

based on:

- thresholds from `olaN_taxonomy.json`  
  (or `tagging_thresholds` if taxonomy is not yet available)
- fields such as:
  - `R_mean_lastW`
  - `phase_var_lastW`
  - `QualityLock`
  - `memory_score_k10`
  - etc.

Store in the output:

- `viables(N, template)`
- `taxonomy_version` used for this stats run (for reproducibility)

---

### Step S3 — Compute viable rate + binomial CI

For each group `(N, template_name)`:

```
p_hat = viables / attempts_total
```

Compute binomial confidence intervals  
(**Wilson 95% CI recommended** for stability near extremes).

Store:

- `attempts_total`  
- `viables`  
- `viable_rate`  
- `ci_low`  
- `ci_high`

---

### Step S4 — Add topology covariates (control variables)

Enrich each template with deterministic features:

- `N` (nodes)  
- `E` (edges)  
- `edge_density = 2E / (N * (N - 1))`  
- `template_family` (if defined; otherwise use `template_name` as proxy)  
- `has_factor_7` (boolean; **must be deterministic and versioned**)

Typical definitions:
- `N % 7 == 0`, or  
- “contains factor-7 substructure” if defined via graph rules  

This must be a **fixed, documented function**.

Intermediate output:  
dataset with **one row per `(N, template)`**, containing `p_hat` and covariates.

---

### Step S5 — Model 1: baseline size effect

Fit:

```
viables ~ Binomial(attempts_total, p)
logit(p) = a + b * N
```

(Preferred over log-linear fits.)

Store:

- coefficients `a`, `b`  
- standard errors / confidence intervals  
- deviance / pseudo-R²

---

### Step S6 — Model 2: *factor_7* effect with controls

Fit:

```
viables ~ Binomial(attempts_total, p)
logit(p) = a + b * N + γ * I(has_factor_7)
           + δ * edge_density + template_family_effects
```

**Paper criterion:**

- report `γ` with CI and p-value  
- if `γ < 0` robustly and CI does not cross 0 →  
  **evidence of a “factor-7 penalty” controlling for size/topology**

---

### Step S7 — Sanity checks (to avoid obvious criticism)

- table of `attempts_total` by `(N, template)` to show coverage  
- plot / table: `viable_rate` vs `N` with CI  
- basic residual checks  
  (no heavy auditing required — hygiene only)

---

## Where this plugs into the pipeline  
*(without touching Explorer / Sweep)*

Add a step to `run_sequence.json` **after** `olaN_taxonomy`:

```
core_stats_build
```

A new script that:

- only reads logs and catalogs  
- produces statistics deterministically  

Nothing here modifies the engine.  
This is **pure, reproducible post-processing**.
