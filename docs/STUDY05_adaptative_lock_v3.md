# DOFT Adaptive Locking Engine (v3)

This document has two parts:

1. Theoretical–physical document for this “adaptive locking engine” (v3).  
2. Implementation spec for the programmer (which JSON, which new variables, what changes in the code).

---

## 1. Physical–mathematical specification (to document DOFT v3)

### 1.1. Central idea

In v2:

- We chose \(\omega\) (frequencies) and \(K\) (couplings) at random within ranges.
- We integrated the system and then measured whether there was “lock” or not (post–hoc).

In v3:

- \(\omega(t)\) and \(K(t)\) stop being fixed parameters.
- They have their own slow dynamics that pushes the system towards regions of stable resonance (Arnold tongues).

The engine stops being a “parameter Monte Carlo” and becomes a self–adjusting system:

- what almost resonates gets reinforced;  
- what doesn’t, gets suppressed.  

**Lock becomes an attractor, not an accident.**

---

### 1.2. Fast equations (same as v2, but with \(K(t), \omega(t)\))

For each mode \(i\) of each layer (Q, S1, S2) we keep the “fast” DOFT:

\[
m_i\,\ddot{x}_i
+ 2\gamma_i\,\dot{x}_i
+ \omega_i(t)^2\,x_i
+ \sum_j K_{ij}(t)(x_i - x_j)
+ F_{\text{mem},i}(t)
= \xi_i(t)
\]

where:

- \(x_i\) is the displacement of mode \(i\).
- \(\omega_i(t)\) is the effective natural frequency at that instant.
- \(K_{ij}(t)\) is the elastic coupling between modes \(i\) and \(j\).
- \(F_{\text{mem},i}\) is the whole v2 memory/multiscale part (already implemented).
- \(\xi_i(t)\) is noise.

None of this is broken; we just turn \(\omega_i\) and \(K_{ij}\) into slow variables.

---

### 1.3. Slow variables: phases, ratios and locking order

To exploit Arnold tongues we need:

- Instantaneous phase of each mode: \(\phi_i(t)\).  
  A simple approximation:

  \[
  \phi_i(t) = \operatorname{atan2}\big(\dot{x}_i\,/\,\omega_i,\; x_i\big)
  \]

- For each pair \((i, j)\) we want to “monitor”, we define a target rational relation \(p:q\)  
  (1:1, 2:1, 3:2, etc).

We define the lock argument:

\[
\theta_{ij}(t) = p\,\phi_j(t) - q\,\phi_i(t)
\]

If the system is locked in \(p:q\), \(\theta_{ij}(t)\) tends to be almost constant.

We define a locking order in a time window:

\[
L_{ij}
=
\frac{1}{T_{\text{win}}}
\int_t^{t+T_{\text{win}}}
\cos\big(\theta_{ij}(s)\big)\,ds
\]

- \(L_{ij} \approx 1\): strong \(p:q\) lock.  
- \(L_{ij} \approx 0\): no phase correlation.

In implementation we use a discrete average over a window of \(N\) steps.

---

### 1.4. Slow dynamics of \(K\) (“resonance Hebb rule”)

We want that, if two modes spontaneously align, the system strengthens the coupling between them.

Proposed rule:

\[
\dot{K}_{ij}
=
\varepsilon_K (L_{ij} - L_0)
-
\lambda_K K_{ij}
\]

- \(\varepsilon_K > 0\): learning rate (very small).
- \(L_0\): “indifference threshold” (e.g. 0.2).

If \(L_{ij} > L_0\): \(K_{ij}\) increases.  
If \(L_{ij} < L_0\): \(K_{ij}\) decreases.

- \(\lambda_K > 0\): decay term that prevents \(K\) from blowing up.

Physical interpretation:

- If two modes vibrate with phase coherence, the medium “hardens” the spring between them.
- If their phases are chaotic, the coupling goes to zero: they decouple.

This is exactly “natural selection” in coupling space.

---

### 1.5. Slow dynamics of \(\omega\) (tuning towards rational tongues)

For the system to slide towards a rational fraction, we need the frequencies to adjust slightly when there is near–lock (beats).

A simple option:

\[
\dot{\omega}_i
=
-\varepsilon_\omega
\sum_{j \in N(i)} w_{ij}\,\sin(\theta_{ij})
\]

- \(\varepsilon_\omega > 0\): frequency adjustment rate (very small).
- \(w_{ij}\): weight for each neighbor \(j\).

Intuition:

- If \(\theta_{ij} > 0\) (mode \(i\) is “ahead”), the sign of \(\sin(\theta)\) corrects \(\omega_i\)
  in the direction that reduces the derivative of that relative phase.
- The system tends to a point where \(\sin(\theta_{ij}) \to 0\), i.e. \(\theta_{ij}\) constant → stable locking.

With this, \(\omega\) and \(K\) move slowly in the \((\omega, K)\) plane looking for Arnold tongues that maximize \(L_{ij}\).

---

### 1.6. Scale separation

Fundamental to avoid blow–ups:

- **Fast dynamics**: integration step \(dt\), typical frequency \(\omega \sim 1\).
- **Slow dynamics**: updates of \(K\) and \(\omega\) every

  \[
  T_{\text{win}} =
  N_{\text{cycles}} \times \frac{2\pi}{\omega_{\text{ref}}}
  \]

  with \(N_{\text{cycles}} \sim 10–50\).

Parameters \(\varepsilon_K, \varepsilon_\omega\) are very small:  
during one integration block, the change in \(K\) and \(\omega\) must be \(\ll 1\%\).

Result:

- the fast equations see \(K\) and \(\omega\) as almost constant within each window;
- the slow equations see averages of the lock.

---

### 1.7. What “matter” is in this scheme

In DOFT v3, a **stable block** (candidate simple particle):

- Has one or more pairs \((i,j)\) with:
  - \(L_{ij} > L_{\text{lock,min}}\) (e.g. 0.8) during a large fraction of time.
- Has effective frequency ratios \(\Omega_i / \Omega_j \approx p/q\) where \(p,q\) are small (1, 2, 3…).
- Its energy spectrum has well defined discrete peaks within the physical window (0.1–3 GeV).
- Memory energy stabilizes (no chaotic runaway).

This replaces the ad–hoc “lock\_quality” with something that is a **dynamical property of the system**.

---

## 2. Implementation specification (concrete changes)

### 2.1. New parameters in the engine (JSON)

Extend `engine_core3.json` with a section:

```json
"adaptive_lock": {
  "enabled": true,

  "window_cycles": 20,
  "ref_frequency_layer": "Q",          // to estimate base period
  "ref_mode_index": 0,

  "epsilon_K": 1e-3,
  "lambda_K": 1e-3,
  "L0": 0.2,
  "K_min": 0.0,
  "K_max": 5.0,

  "epsilon_omega": 1e-4,
  "omega_min": 0.1,
  "omega_max": 5.0,

  "lock_pairs": [
    {
      "name": "Q_S1_1to1",
      "layer_i": "Q",   "mode_i": 0,
      "layer_j": "S1",  "mode_j": 0,
      "p": 1, "q": 1,
      "weight": 1.0
    },
    {
      "name": "Q_S2_1to2",
      "layer_i": "Q",   "mode_i": 0,
      "layer_j": "S2",  "mode_j": 0,
      "p": 1, "q": 2,
      "weight": 0.5
    }
  ]
}
```

Notes:

- `lock_pairs` defines which mode pairs are used to compute locks and adapt parameters.
- `p, q` are the locking rational integers. You can start with only 1:1 between layers.
- Later you can add more entries for 2:1, 3:2, etc.

---

### 2.2. New variables the simulator must handle

In `study05.simulation`:

For each mode `i`:

- `omega_i` (already exists, but now mutable).
- `phase_i` estimated at each step (from `x_i`, `v_i`).

For each pair `(i, j)` referenced in `lock_pairs`:

- `K_ij` (coupling) – if there is already a coupling between those layers, use it; if not, create a new term.

Window accumulators:

- `sum_cos_theta_ij`
- `n_samples_ij`

Window counters:

- `t_window_start`
- `n_steps_in_window`

---

### 2.3. Modification of the integration loop

Pseudocode inside `simulate(...)` (fast time):

```python
state = init_state(...)
params = init_params_from_json(...)

# Initialize K_ij for each lock_pair (e.g. from ranges or an initial value)
lock_state = init_lock_state(engine.adaptive_lock, params)

t = 0.0
while t < t_max:
    # 1) One fast DOFT integration step (RK4 or your existing integrator)
    state = step_fast_doft(state, params, dt)

    # 2) Estimate instantaneous phase for each tracked mode
    for m in tracked_modes:
        x = state.x[m]
        v = state.v[m]
        omega = params.omega[m]
        phase[m] = math.atan2(v / max(omega, eps), x)

    # 3) Accumulate cos(theta) for each pair
    for pair in lock_pairs:
        i, j, p, q = pair.i, pair.j, pair.p, pair.q
        theta = p * phase[j] - q * phase[i]
        pair.sum_cos += math.cos(theta)
        pair.n_samples += 1

    t += dt
    steps_in_window += 1

    # 4) Every time we complete window_cycles periods → update K and omega
    if t - window_start >= T_window:
        update_adaptive_parameters(lock_pairs, params, engine.adaptive_lock)
        reset_window_accumulators(lock_pairs)
        window_start = t
```

---

### 2.4. Parameter update rule (code)

```python
def update_adaptive_parameters(lock_pairs, params, cfg):
    # 1) Compute L_ij average in the window
    for pair in lock_pairs:
        if pair.n_samples > 0:
            L_ij = pair.sum_cos / pair.n_samples
        else:
            L_ij = 0.0
        pair.L_last = L_ij

    # 2) Update K_ij
    for pair in lock_pairs:
        K = pair.K
        L_ij = pair.L_last
        dK = cfg.epsilon_K * (L_ij - cfg.L0) - cfg.lambda_K * K
        K_new = K + dK
        # clamp
        K_new = min(max(K_new, cfg.K_min), cfg.K_max)
        pair.K = K_new
        # write K_new into the parameter structure used by step_fast_doft
        apply_K_to_couplings(pair, params)

    # 3) Update omega_i (sum of contributions of all pairs involving it)
    d_omega = {i: 0.0 for i in all_tracked_modes}
    for pair in lock_pairs:
        i, j, p, q = pair.i, pair.j, pair.p, pair.q
        # use an approximate mean theta based on L_ij
        # here the sign of sin(theta) at the end of the window is enough
        # if you also store sin(theta) averages, even better
        theta_mean = math.acos(max(min(pair.L_last, 1.0), -1.0))  # crude approximation
        s = math.sin(theta_mean)
        d_omega[i] += -cfg.epsilon_omega * pair.weight * s * q
        d_omega[j] +=  cfg.epsilon_omega * pair.weight * s * p

    for i in d_omega:
        omega = params.omega[i] + d_omega[i]
        omega = min(max(omega, cfg.omega_min), cfg.omega_max)
        params.omega[i] = omega
```

Note: you can refine how you approximate the mean `sin(theta)` by also storing `sum_sin_theta` exactly like `sum_cos_theta`. The physical spec only requires that the correction be smooth and tend to make \(\theta_{ij}\) constant.

---

### 2.5. New outputs (for `run_sweep` and proxies)

For each run, the simulator must return, in addition to what it already returns:

For each `lock_pair`:

- `L_ij_final` (average lock order over the last N windows).
- `K_ij_final`.
- `omega_i_final`, `omega_j_final`.
- `ratio_eff = omega_i_final / omega_j_final`.
- `locked_flag = 1` if `L_ij_final > L_lock_min` and `|ratio_eff - p/q| < tol_ratio`, else `0`.

In the sweep result JSON:

```json
"adaptive_lock": {
  "pairs": [
    {
      "name": "Q_S1_1to1",
      "L_mean": 0.87,
      "K_final": 1.23,
      "omega_i_final": 0.65,
      "omega_j_final": 0.66,
      "ratio_eff": 0.98,
      "locked": true
    }
    // ...
  ]
}
```

In the proxies CSV (`*_all_runs_proxies.csv`), new columns:

- `lock_Q_S1_L`
- `lock_Q_S1_ratio`
- `lock_Q_S1_locked`

etc. (a family of columns per pair).

This lets you:

- Filter “good blocks” simply with `locked == 1` and ratio close to what the SM particle requires.
- Correlate dynamic lock with `S2_state`, `structure_tier`, etc., as you already do.

---

### 2.6. Compatibility and flags

If `"adaptive_lock.enabled": false`, the engine must ignore all this logic and behave like v2 (fixed \(K\) and \(\omega\)).

`run_sweep` does not need to change its CLI; it only needs to:

- pass the full config (with `adaptive_lock`) to the simulator;
- read lock metrics from the result and add them to:
  - the JSON of each run,
  - the combined proxies CSV.

---

### 2.7. What to check in quick tests

Before launching large sweeps:

**Test 1: 2 oscillators Q–S1**

- Only one pair in `lock_pairs` with `p = q = 1`.
- Initialize \(\omega_Q, \omega_{S1}\) slightly different, \(K\) small.

Check that:

- \(K\) grows to an equilibrium value.
- \(\omega_Q\) and \(\omega_{S1}\) converge to a ~1:1 ratio.
- \(L_{ij} \to \sim 1\).

---

**Test 2: 3 layers Q–S1–S2**

- Use 2 pairs: Q–S1 (1:1), Q–S2 (1:2).

Check if the system falls into a configuration where:

- Q and S1 lock 1:1,
- S2 sits at ~2×Q (or whatever emerges),
- the spectra have rational peaks.

If those tests yield coherent behaviour, only then is it worth launching an Ola1 sweep with this engine and seeing which building blocks appear.
