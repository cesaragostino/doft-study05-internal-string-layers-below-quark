# Ola2 Differential Engine — Unified DOFT Dynamics (English Translation)

## Overview

In Ola2, the differential engine does **not** need to be a separate or alternative universe. The cleanest—and most defensible—approach is the following:

- **Ola1** defines the local model of an individual (one node) with its three layers **Q / S1 / S2**, plus internal memory and delays.
- **Ola2** assembles a network of those individuals (nodes) and adds **inter-node coupling terms** (edges) determined by the topology of the template.

In other words, **the differential equations remain the same**; the system simply transitions from *one individual* to *G coupled individuals*.

Below is a generic, implementable definition fully compatible with what is already exported (e.g., `energies_series`).

---

## 1. Minimal State for the Ola2 Differential System

For each node \( i = 1..N \) (each node is a DOFT block/individual) and each layer
\( \ell \in \{ Q, S1, S2 \} \):

- Phase: \( \theta_{i,\ell}(t) \)
- (Optional) amplitude/energy: \( E_{i,\ell}(t) \) if the model evolves it explicitly
- Memory state(s): \( m_{i,\ell}(t) \) if DOFT uses dynamic memory

### Global outputs (kept for Ola1 compatibility)

\[
E_{\ell}(t) = \sum_i E_{i,\ell}(t)
\]

This directly defines:

```text
energies_series[t] = [E_Q(t), E_S1(t), E_S2(t)]
```

As a result, metrics such as:

```text
lock_s1_series(t) = E_S1 / (E_Q + E_S1 + E_S2)
```

remain **identical and comparable across olas**.

---

## 2. Differential Dynamics (Canonical Form)

### 2.1 Intra-node Term (Same as Ola1)

Ola1 already defines internal coupling between layers of the same node:

\[
F^{\text{intra}}_{i,\ell}(\theta_{i,Q}, \theta_{i,S1}, \theta_{i,S2}, m_{i,*}, \ldots)
\]

This term is **unchanged** and reused as-is.

---

### 2.2 Inter-node Term (New in Ola2)

For each edge \( i \leftrightarrow j \) in the Ola2 template, add:

\[
F^{\text{inter}}_{i,\ell}(t) = \sum_{j \in N(i)} \sum_{\ell'} K^{\ell,\ell'}_{ij}
\, G_{\ell,\ell'}(\cdot)
\sin\big( \theta_{j,\ell'}(t - \tau_{ij}) - \theta_{i,\ell}(t) \big)
\]

Where:

- \( K^{\ell,\ell'}_{ij} \): coupling matrix/tensor (can be simple)
- \( \tau_{ij} \): edge delay
- \( G_{\ell,\ell'} \): optional gating (energy-based or layer-activation)

#### Minimal viable version (recommended start)

Only couple **S1 ↔ S1** across nodes:

\[
F^{\text{inter}}_{i,S1}(t) = \sum_{j \in N(i)} K_{ij}
\sin\big( \theta_{j,S1}(t - \tau_{ij}) - \theta_{i,S1}(t) \big)
\]

and initially:

\[
F^{\text{inter}}_{i,Q} = F^{\text{inter}}_{i,S2} = 0
\]

This directly recovers Kuramoto as the special case \( \tau = 0 \).

---

### 2.3 Full Equation (Per Layer)

\[
\frac{d\theta_{i,\ell}}{dt} = \omega_{i,\ell}
+ F^{\text{intra}}_{i,\ell}
+ F^{\text{inter}}_{i,\ell}(t)
+ F^{\text{mem}}_{i,\ell}(t)
\]

Optional explicit memory dynamics:

\[
\frac{dm_{i,\ell}}{dt} = -\lambda_{\ell} m_{i,\ell}
+ \kappa_{\ell} H\big(F^{\text{inter}}_{i,\ell}(t)\big)
\]

where \( H \) may be identity, absolute value, power law, etc., depending on DOFT.

---

## 3. Structural Couplings from Templates

The Ola2 template defines a graph \( G \):

- Neighbor sets \( N(i) \)
- Edge set \( E \)
- (Optional) edge classes

### Parameterization options

- **A. Uniform per template**
  ```text
  K_ij = K
  τ_ij = τ
  ```

- **B. Degree-normalized (numerically stable)**
  ```text
  K_ij = K / d_i   or   K / sqrt(d_i d_j)
  ```

- **C. Bond-class based**
  ```text
  K_ij ∈ {K_strong, K_weak}
  ```

Key principle: **topology enters via edge patterns, not by changing the engine**.

---

## 4. From Kuramoto Candidates to Differential Sweeps

Kuramoto candidates already identify promising templates. The differential engine should perform **local exploration**, not blind search.

### Base parameter vector

```text
p0 = (K_scale, τ_scale, λ_mem, κ_mem, ω_spread, noise)
```

### Neighborhood definition

```text
K_scale ∈ [0.8, 1.2]
τ_scale ∈ [0.8, 1.2]
λ_mem   ∈ [0.5, 2.0]   (log-uniform)
...
```

Perform:

```text
sweep over seeds × sweep over parameter neighborhood
```

Golden rule: **the differential refines Kuramoto candidates; it does not search blindly**.

---

## 5. Metrics Reported by the Ola2 Differential (Ola1-compatible)

To keep full alignment across olas, retain:

- `energies_series[t] = [E_Q(t), E_S1(t), E_S2(t)]`
- `participation_entropy` over \( E_{\ell}(t) \) in the final window
- `lock_s1_series(t) = E_S1 / (E_Q + E_S1 + E_S2)`
- `PE_lockS1_norm` (canonical chaos metric)

### Lock metrics

Kuramoto-style order parameter on differential phases:

\[
R(t) = \left| \frac{1}{N} \sum_i e^{i \theta_{i,S1}(t)} \right|
\]

From this compute:

- `R_mean_lastW`
- `phase_var_lastW` (linear or circular variance)
- `QualityLock` (temporal stability over window W)

With these definitions, **Kuramoto and differential dynamics speak the same language**.

