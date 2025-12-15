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

## Instantaneous Disorder/Randomness (Ensemble)

This is what you see in a “snapshot” of the system: how spread out or mixed the states are at that instant. This can be measured without any temporal trajectory. In physics it is related to mixing entropy, heterogeneity, fluctuations between subsystems, etc.

---

## Dynamical Chaos (Temporal)

This is **not** “being disordered” in a snapshot; it is the complexity/instability of the evolution: sensitivity to initial conditions, growth of uncertainty, emergence of unpredictable patterns in time. To measure it you need a causal trajectory \(x_t\). Without that trajectory, any temporal metric (Permutation Entropy, Lyapunov proxy, etc.) ends up measuring artifacts of the log or of the RNG.

---

## Lock Entropy (Instantaneous Measure)

Each block has a vector of “qualities” \((Q, S1, S2)\). To avoid depending on scale, it is normalized:

\[
p_i = \frac{v_i}{\sum_j v_j}, \quad v = (Q, S1, S2)
\]

and the normalized entropy is defined as:

\[
H_{\text{lock}} = -\frac{1}{\ln 3} \sum_{i=1}^{3} p_i \ln(p_i) \in [0, 1]
\]

Interpretation:

- \(H_{\text{lock}} \approx 0\): a dominant “lock” (more decided state / less mixing).
- \(H_{\text{lock}} \approx 1\): high mixing between components (less decided / more spread-out state).

This is a measure of instantaneous disorder (ensemble-type): valid whether the runs are independent or there is inheritance.

---

## Dynamical Chaos (Correct Temporal Measure)

To measure dynamical chaos in a way that is “agnostic to the narrative”, we use a measure based on local orderings of the time series, for example **Permutation Entropy** (Bandt–Pompe) on a macroscopic observable \(x_t\) defined per tick within a run:

\[
x_t = \operatorname{mean}_{\text{blocks}}(H_{\text{lock}}(t))
\]

Permutation Entropy is high when the sequence exhibits locally complex patterns (low predictability of orderings), and low when there is regularity/periodicity. It is a robust proxy of temporal complexity.  

**Critical:** it only has physical meaning if \(x_t\) is causal (ticks within a run, or runs with explicit inheritance).

---

## What We Do If the Experiment Is Stateless

If Wave 2 (Ola2) produces i.i.d. runs (without causal continuity), then:

- We report ensemble entropy/heterogeneity (valid).
- We do **not** report “dynamical chaos” (PE) over runs, because that would be measuring the RNG/ordering. In that case `PE` remains `null` and the reason is reported explicitly.

---

## Complete Spec for Implementation (Single Scope)

### Objective

For each run, append to the sweep report an `entropy_chaos` block that includes:

- instantaneous metrics (always valid),
- dynamical metrics (only if there are ticks/causal series),
- ensemble fallback if there are no ticks,

and which makes it traceable whether the run is `dynamic` or `ensemble`.

---

## A) Data to Log (Minimum Necessary)

### A1) Per Block (if you already have it, perfect)

Fields already present:

- `lock_quality.Q`, `lock_quality.S1`, `lock_quality.S2`
- `structure_tier`

Optional: `match_score.*` if you want correlations, not necessary for this spec.

### A2) Per Tick Within the Run (NEW – Needed for Correct “Chaos”)

For each tick in `0..T-1` (e.g. `T = 120`):

Store aggregates per tick (no need to dump full per-block data):

- `mean_H_lock_norm_tick`
- `std_H_lock_norm_tick` (optional but useful)
- `fraction_structured_tick` (optional)
- `mean_Q_tick` (optional)

**Important:** if, by architecture, an internal tick does not exist today, it must be instrumented. Without this, dynamical “chaos” cannot be measured properly.

---

## B) Computations

### B1) Lock Entropy per Block

Input: `Q, S1, S2`  
Constant: `eps = 1e-12`  

Computation:

```python
s = Q + S1 + S2
if s < eps:
    p = [1/3, 1/3, 1/3]
else:
    p = [Q/s, S1/s, S2/s]

H_lock = -(
    p[0] * ln(p[0] + eps)
  + p[1] * ln(p[1] + eps)
  + p[2] * ln(p[2] + eps)
) / ln(3)
```

### B2) Instantaneous Aggregates per Run (Always)

Over all blocks of the run:

- `mean_H_lock_norm`
- `std_H_lock_norm`
- `p90_H_lock_norm`
- `fraction_structured = count(structure_tier != "none") / N`
- `mean_Q`, `std_Q` (optional, cheap)

**Ensemble extras** (recommended, cheap and useful if stateless):

- `mixture_entropy_blocks_norm`:

  - histogram of `H_lock` in `B = 30` bins in `[0, 1]`
  - `p_bin = count / bin_total`
  - \(H_{\text{bins}} = -\sum p_{\text{bin}} \ln(p_{\text{bin}} + \text{eps}) / \ln(B)\)

- `structure_mix_norm`:

  - count tiers (`none`, `level1`, `level2`, …)
  - \(H_{\text{tier}} = -\sum p_{\text{tier}} \ln(p_{\text{tier}} + \text{eps}) / \ln(K)\), where \(K\) is the number of categories present.

### B3) Dynamical Chaos per Run (Only If There Are Ticks)

Define the causal series:

\[
x_t = \text{mean\_H\_lock\_norm\_tick}[t], \quad t = 0..T-1
\]

Compute normalized Permutation Entropy (Bandt–Pompe):

**Parameters:**

- embedding dimension `m = 5`
- delay `tau = 1`
- number of patterns: \(m!\)

For each window index \(t\) such that there are \(m\) points, construct the vector

\[
v = [x_t, x_{t+\tau}, \dots, x_{t+(m-1)\tau}]
\]

Obtain the ordinal pattern (ranking). Tie handling:

- simple/robust option: if there are exact ties, break them with the index (stable order).

Count pattern frequencies \(p(\text{pattern})\).

Entropy:

\[
PE = -\sum p \ln(p + \epsilon) / \ln(m!)
\]

Output: `PE_tick_norm = PE`.

Validity rules:

- if \(T < m \cdot \tau + 1\), set `PE_tick_norm = null` and `chaos_mode = "ensemble"`.

---

## C) Mode Detection (So We Don’t Fool Ourselves)

Set in each run:

- `has_ticks =` (whether there exists a series `mean_H_lock_norm_tick` with `T >= m * tau + 1`)

If `has_ticks`:

- `chaos_mode = "dynamic"`
- compute `PE_tick_norm`

If not:

- `chaos_mode = "ensemble"`
- `PE_tick_norm = null`
- keep `mixture_entropy_blocks_norm` and `structure_mix_norm` as honest substitutes.

---

## D) Output Format (Append to the Sweep Report JSON)

Add to the run object:

```json
{
  "entropy_chaos": {
    "eps": 1e-12,
    "mean_H_lock_norm": 0.0,
    "std_H_lock_norm": 0.0,
    "p90_H_lock_norm": 0.0,
    "fraction_structured": 0.0,
    "mean_Q": 0.0,
    "std_Q": 0.0,

    "mixture_entropy_blocks_norm": 0.0,
    "structure_mix_norm": 0.0,

    "chaos_mode": "dynamic|ensemble",
    "PE_tick_norm": null,
    "T_ticks": null,

    "notes": "PE computed only on causal tick series; stateless runs use ensemble metrics."
  }
}
```

If `chaos_mode = "dynamic"`:

- `PE_tick_norm`: float  
- `T_ticks`: int

If `chaos_mode = "ensemble"`:

- `PE_tick_norm = null`, `T_ticks = null`.

---

## E) Complexity and Cost

- Per-block computation: \(O(N)\) per run.
- Histogram: \(O(N)\).
- PE per tick: \(O(T \cdot m \log m)\) (with \(m = 5\) it is effectively constant). Very cheap.

---

## Result

With this:

- **Entropy** (`H_lock`) becomes your “thermometer” of mixture/decision of locks (instantaneous).
- **Chaos** (`PE`) becomes a correct dynamical measure, but only when there is causal continuity (ticks).
- If Wave 2 (Ola2) is stateless, the report is still useful (ensemble), without self-deception.

