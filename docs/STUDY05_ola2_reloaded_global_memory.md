# Final Spec for Wave 2 (Rehydration + Memory Field + Topology + Mass Defect)

## Inputs (per attempt)

**Genes (from Wave 1) for each block _i_:**

- \( M_i \) (effective mass)
- \( \omega_i \) or \( F_m \)
- `lock_quality` \((Q, S1, S2)\) + `H_lock_norm` if it exists
- `theta0` (if it exists; if not, random)

**Geometric template (from `compound_templates.json`):**

- \( N \) nodes
- `edges`: list of pairs \([a, b]\) (assume undirected unless the template states otherwise)
- (if present) weights per edge; if not, weight = 1

---

## 1) Rehydration (initial state per oscillator)

For each oscillator \( i \):

\[
\theta_i(0) = \theta_{0,i} + \mathcal{N}(0, \sigma_\theta)
\]

(if there is no \(\theta_0\): sample uniformly in \([0, 2\pi)\))

\[
\omega_i = \omega_{\text{eff}}
\]

**Recommended parameters:**

- `sigma_theta_init = 0.5` rad (in config)

---

## 2) Topology: build \( w_{ij} \) from the template (CRITICAL)

Create adjacency matrix / structure: \( A[i][j] = 1 \) only if \((i, j)\) is in `edges` (or \((j, i)\)).

Define weights:

**Robust (recommended) option – degree normalization**

\[
w_{ij} =
\begin{cases}
\frac{1}{\deg(i)} & \text{if } A_{ij} = 1 \\[4pt]
0 & \text{otherwise}
\end{cases}
\]

This prevents a node with more neighbors from “receiving more total force” just because of higher degree.

---

## 3) Global memory (field \( Z(t) \) with relaxation \( \tau \))

Maintain a complex field \( Z(t) \in \mathbb{C} \) per attempt:

\[
Z(t + \Delta t) = Z(t) + \frac{\Delta t}{\tau}
\left(
\frac{1}{N} \sum_{i=1}^N e^{j \theta_i(t)} - Z(t)
\right)
\]

**Config:**

- `dt = 1`
- `tau_field = 20` (default; configurable)

---

## 4) Phase dynamics per tick (with topology + field + noise)

At each tick:

\[
\theta_i(t + \Delta t) = \theta_i(t)
+ \omega_i \Delta t
+ K \Delta t \sum_{j \ne i} w_{ij} \sin(\theta_j - \theta_i)
+ \kappa \Delta t \,\Im\!\bigl( Z(t) e^{-j \theta_i} \bigr)
+ \sigma(t)\,\Delta t\,\eta_i
\]

where \( \eta_i \sim \mathcal{N}(0, 1) \).

**Parameters:**

- `K_local = 0.15`
- `kappa_global = 0.25`

**Temperature / noise:** \(\sigma(t)\) with annealing (recommended):

- `sigma0 = 0.30`
- \(\sigma(t) = \sigma_0 \exp(-t / \sigma_{\text{tc}})\)
- `sigma_tc = 60`
- `T_ticks = 120`

---

## 5) Observables and success criterion (dynamic locking)

Compute per tick:

### Global coherence

\[
R(t) = \left| \frac{1}{N} \sum_{i=1}^N e^{j \theta_i(t)} \right|
\]

### Relative phase stability (over window \( W \))

For each edge \((i, j)\) in the template:

\[
\Delta \theta_{ij}(t) = \text{wrap}(\theta_i - \theta_j)
\]

In the final window \( W \) (e.g. \( W = 20 \) ticks):

- `phase_var_lastW = mean_edges( Var_t(Δθ_ij) )`

### Success

- \( R_{\text{mean,lastW}} > 0.85 \) and  
- `phase_var_lastW < 0.02` (rad²)

(optionally) also: \( R_{\text{final}} > 0.90 \)

---

## 6) Mass defect / binding energy (CRITICAL for Wave 3)

Define a scalar “lock quality” for the attempt:

\[
\text{QualityLock} = \operatorname{clamp}\bigl( \text{mean}(Q_i), 0, 1 \bigr)
\]

Alternative if you prefer:

\[
\text{QualityLock} = 1 - \text{mean}(H_{\text{lock,norm}, i})
\]

(assuming \(H_{\text{lock,norm}}\) is well defined).

Define an effective binding energy (in mass units, without explicitly adding \(c\)):

\[
E_{\text{bind,mass}} = \gamma \cdot \left( \sum_i M_i \right) \cdot R_{\text{final}} \cdot \text{QualityLock}
\]

and final mass:

\[
M_{\text{final}} = \sum_i M_i - E_{\text{bind,mass}}
\]

**Important notes:**

- `gamma` configurable. Your suggestion `0.007` is reasonable as an order of magnitude (He‑4 is around ~0.007–0.008 of the total), but leave it as a parameter for calibration.
- Defensive clamps:
  - `E_bind_mass = clamp(E_bind_mass, 0, gamma_max * sumM)` with e.g. `gamma_max = 0.02`
  - `M_final >= M_min_physical` (do not allow negative or unphysically low mass)
- Also log: `mass_defect = sumM - M_final`

This gives you an alpha with a coherent mass and, more importantly, a quantitative channel so that Wave 3 does not break due to “wrong mass”.

---

## 7) Wave 2 metrics that do **not** measure RNG (valid over internal ticks)

Over the causal series inside the attempt:

- `PE_tick_norm` on \( x_t = R(t) \) (Permutation Entropy with \( m = 5 \), `tau = 1`)
- `memory_score_k10` with AR(1) vs AR(10) on \( R(t) \) (MSE difference)

**Important (your comment):**  
Do **not** run PE over independent runs; only over engine ticks (or over an actually hereditary evolution).

---

## 8) JSON output to append to the sweep report

Append per attempt:

```json
"ola2": {
  "template_id": "nuclear_tetra",
  "engine": {
    "dt": 1,
    "T_ticks": 120,
    "W": 20,
    "tau_field": 20,
    "K_local": 0.15,
    "kappa_global": 0.25,
    "sigma0": 0.30,
    "sigma_tc": 60,
    "sigma_theta_init": 0.5,
    "gamma": 0.007
  },
  "topology": {
    "edges_count": 6,
    "degree": [ ... ]
  },
  "metrics": {
    "R_final": 0.0,
    "R_mean_lastW": 0.0,
    "phase_var_lastW": 0.0,
    "PE_tick_norm": 0.0,
    "memory_score_k10": 0.0,
    "QualityLock": 0.0
  },
  "mass": {
    "sumM": 0.0,
    "E_bind_mass": 0.0,
    "mass_defect": 0.0,
    "M_final": 0.0
  },
  "result": {
    "success": true,
    "reason": "locked|no_lock|timeout|clamp"
  }
}
```

