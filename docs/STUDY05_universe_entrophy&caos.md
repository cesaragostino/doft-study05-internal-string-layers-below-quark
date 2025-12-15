# Scientific Text for Report Annex (Entropy + Chaos)

In a many–degree-of-freedom system out of equilibrium, *temperature* does not need to be a primary variable. Instead, one can measure (i) instantaneous state uncertainty and (ii) temporal complexity/irregularity of that uncertainty.

---

## Lock Entropy (Instantaneous Uncertainty)

Given a vector of `lock_quality` per block  
\(p = (Q, S1, S2)\) (normalized so that \(\sum_i p_i = 1\)), the Shannon entropy

\[
H_{\text{lock}} = -\sum_i p_i \log(p_i)
\]

measures how “decided” the block is:

- \(H_{\text{lock}} \to 0\) implies a clear lock (one component dominates),
- high values imply ambiguity (mixing between \(Q, S1, S2\)).

It can be normalized as

\[
H_{\text{lock}}^{(\text{norm})}
=
\frac{H_{\text{lock}}}{\log 3}
\in [0, 1]
\]

to compare runs.

---

## Chaos as Temporal Complexity (Dynamic Proxy)

To capture “chaos” as irregularity in the evolution (not just instantaneous uncertainty), we use **Permutation Entropy** on a scalar time series \(x_n\) (for example \(x_n = \langle H_{\text{lock}}^{(\text{norm})} \rangle\) per run). This metric detects loss of temporal structure and increasing complexity of the generator without requiring an explicit physical model.

Normalized, it also lies in \([0, 1]\): high values imply a more “chaotic/irregular” evolution.

---

## Single Spec for the Programmer (Full Scope)

### Objective

For each run of the sweep, compute and append to the output file an “Entropy+Chaos” block of metrics at block and run level, using only what already exists in the current JSON (lock_quality, tiers, etc.) and a short window of internal history.

---

## Inputs (Per Block, Per Run)

For each block in the run:

- `lock_quality.Q`, `lock_quality.S1`, `lock_quality.S2` (floats, may be very close to 0),
- `structure_tier` (string: `"none"`, `"level1"`, `"level2"`, …),
- optionally: `s2_state` (for stats), `match_score.d_total` (for correlations if you want).

---

## Outputs (Appended Per Run to Log/Report)

Add to the run summary the following keys (suggested names):

### A) Per-Block Metrics (if you keep detailed data; otherwise at least aggregates)

- `H_lock` (float): Shannon entropy in nats,
- `H_lock_norm` (float): `H_lock / ln(3)` in \([0, 1]\),
- `A_lock` (float): simple ambiguity = \(1 - \max(p)\) in \([0, 2/3]\) (can be normalized),
- `p_lock_max` (float): \(\max(p)\) (how dominant the lock is).

### B) Aggregated Metrics Per Run

- `n_blocks`,
- `mean_H_lock_norm`, `std_H_lock_norm`, `p90_H_lock_norm`,
- `mean_A_lock`, `std_A_lock`,
- `mean_Q`, `std_Q` (and similarly for `S1`, `S2` if desired),
- `fraction_structured` = (# blocks with `structure_tier != "none"`) / `n_blocks`,
- `fraction_s2_latent` = (# blocks with `s2_state == "latent"`) / `n_blocks` (if applicable).

**Production (change run to run)**

- `delta_mean_H_lock_norm` = `mean_H_lock_norm(run) - mean_H_lock_norm(prev_run)`,
- `delta_fraction_structured` = `fraction_structured(run) - fraction_structured(prev_run)`.

---

## C) Dynamic Chaos (Permutation Entropy Over the Per-Run Series)

Define a scalar series per run:

- `x_run = mean_H_lock_norm` (one number per run).

Maintain a circular buffer with the last \(W\) values of `x_run` (e.g. \(W = 256\) or 512). When the buffer is full, compute:

- `PE_run_norm` = normalized Permutation Entropy in \([0, 1]\) with parameters:

  - embedding dimension `m = 5`,
  - delay `tau = 1`,
  - normalization by `ln(m!)`.

Store per run:

- `PE_run_norm` (if there are not yet \(W\) data points, store `null`).

---

## Exact Definitions (to Avoid Ambiguity)

### 1) Preparation of Vector `p` per Block

```python
eps = 1e-12
p_raw = [Q, S1, S2]   # if any is missing, use 0.0
s = Q + S1 + S2
if s <= eps:
    p = [1.0, 0.0, 0.0]   # fallback
else:
    p = [Q/s, S1/s, S2/s]
```

### 2) Lock Entropy per Block

Natural log (nats):

\[
H_{\text{lock}} = -\sum_i p[i] \ln(p[i] + \text{eps})
\]

\[
H_{\text{lock}}^{(\text{norm})} = \frac{H_{\text{lock}}}{\ln 3}
\]

### 3) Simple Ambiguity (Additional Instantaneous Proxy)

```python
pmax = max(p)
A_lock = 1 - pmax
A_lock_norm = A_lock / (2.0/3.0)  # optional, yields [0,1]
```

Interpretation:

- `H_lock_norm` and `A_lock_norm` capture “uncertainty/mixture” of the lock in the run.
- If you want “two different numbers”, here they are: entropy (H) and ambiguity (A) (instantaneous),
  plus dynamic chaos (PE) (temporal).

### 4) Permutation Entropy (Per Run, Over `x_run`)

With buffer

\[
X = [x_{t-W+1}, \dots, x_t]:
\]

For each position \(j\), take the vector

\[
v = (x_j, x_{j+\tau}, \dots, x_{j + (m-1)\tau}).
\]

Obtain the **ordinal pattern** (ranking) of the vector (if there are ties, break them with a minimal jitter or a stable rule).

Count frequencies of each pattern (there are \(m!\) patterns).

Compute:

\[
PE = -\sum_{\text{patterns}} p(\text{pattern}) \log(p(\text{pattern}) + \text{eps})
\]

\[
PE_{\text{norm}} = \frac{PE}{\ln(m!)}
\]

Recommended fixed parameters: `W = 256`, `m = 5`, `tau = 1`.

---

## Recommended Output Format (to Append to the Sweep File)

If your sweep already generates a JSON per run, add inside:

```json
"entropy_chaos": {
  "n_blocks": ...,
  "mean_H_lock_norm": ...,
  "std_H_lock_norm": ...,
  "p90_H_lock_norm": ...,
  "mean_A_lock": ...,
  "std_A_lock": ...,
  "mean_Q": ...,
  "std_Q": ...,
  "fraction_structured": ...,
  "fraction_s2_latent": ...,
  "delta_mean_H_lock_norm": ...,
  "delta_fraction_structured": ...,
  "PE_run_norm": ...
}
```

---

## Practical Note (Important So You Don’t Lose 4 Days)

This adds very little cost:

- `H_lock_norm` and aggregates: \(O(n_{\text{blocks}})\) per run (cheap).
- `PE_run_norm`: only when the buffer is full, \(O(W)\) (also cheap with \(W = 256\)).
