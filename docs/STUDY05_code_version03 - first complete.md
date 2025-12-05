# Study05 Simulator – Internal Layers with Breathing Structure (Spec)

## 0. Goal of the Study05 Simulator

Numerical simulator for a DOFT system with:

- Internal string-like layers below the quark level (S1, S2, optional S3).
- An effective Q layer (quark/hadron).
- Oscillators with delays between layers and internal memory.
- Each layer has a slow “structure” variable that breathes as a function of the energy flowing through that layer.

**Outputs:**

- Effective mode spectra (energy in GeV).
- Per-layer weights of each mode (Q–S1–S2 locks).
- Statistics of mode spacings in a hadronic band (0–3 / 0–5 GeV).
- Time evolution of the “breathing” of each layer.

---

## 1. Layers, Modes, and Complexity

### 1.1. Layers (enum)

```python
from enum import Enum, auto

class Layer(Enum):
    Q  = auto()   # effective quark/hadron layer
    S1 = auto()   # first internal (string-like) layer
    S2 = auto()   # second internal (deeper) layer
    S3 = auto()   # optional third internal layer (you can keep it disabled for now)
```

### 1.2. Number of modes per layer

Reasonable initial values (tunable via CLI):

- `N_Q = 3` or `4`
- `N_S1 = 3`
- `N_S2 = 2`
- `N_S3 = 0` for now (or `2` if you later want to enable it)

Idea: the total number of explicit modes should be at most about 8–10.

```python
from dataclasses import dataclass

@dataclass
class LayerConfig:
    N: int          # number of modes in the chain
    omega_base: float  # dimensionless base frequency
```

### 1.3. Complexity C

We define the effective complexity only for the fast modes + memory:

```python
C = n_modes_explicit + n_memory_terms  # we do not count b_L nor energy filters
C_max = 10
```

If a parameter proposal yields `C > C_max`, it is discarded and resampled.

---

## 2. Frequency Scale (All Dimensionless)

To avoid dealing with 10^23 Hz, everything is done in dimensionless units. Later we remap to GeV.

### 2.1. Base frequency of Q

```python
omega_Q_base = 1.0  # internal unit
```

### 2.2. Ratios per layer (hierarchical but moderate)

```python
import numpy as np

def sample_R():
    # ratio ~ 2 to 10 (tunable)
    return 10 ** np.random.uniform(0.3, 1.0)  # ~2 to 10

R_S1_Q  = sample_R()
R_S2_S1 = sample_R()
# R_S3_S2 = sample_R() if you use S3

omega_S1_base = R_S1_Q  * omega_Q_base
omega_S2_base = R_S2_S1 * omega_S1_base
# omega_S3_base = R_S3_S2 * omega_S2_base
```

Typical frequency ranges:

- Q ~ 1  
- S1 ~ 2–10  
- S2 ~ 4–100  

This already gives hierarchy without going crazy.

---

## 3. Physical Modes per Layer

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Mode:
    layer: Layer
    index: int
    omega0: float   # dimensionless base frequency (before breathing)
    mass: float     # effective mass (1.0 for now)
    gamma: float    # linear damping (fraction of omega)
```

Generation:

```python
def build_layer_modes(layer: Layer, omega_base: float, N: int) -> List[Mode]:
    modes = []
    for i in range(N):
        if layer == Layer.Q:
            delta = np.random.uniform(-0.05, 0.05)   # ±5%
        else:
            delta = np.random.uniform(-0.10, 0.10)   # ±10%

        omega_i = omega_base * (1.0 + delta)
        mass_i  = 1.0
        gamma_i = omega_i * np.random.uniform(1e-3, 1e-2)  # small damping

        modes.append(Mode(layer, i, omega_i, mass_i, gamma_i))
    return modes
```

---

## 4. Intra-layer Couplings (1D Chains)

```python
from typing import Tuple, Dict

@dataclass
class Coupling:
    i: Tuple[Layer, int]
    j: Tuple[Layer, int]
    k_ij0: float  # base stiffness (will be modulated by b_L)
```

Generation:

```python
def build_intra_layer_couplings(layer: Layer, omega_base: float, N: int) -> List[Coupling]:
    couplings = []
    # kappa_L factor you can tune (0.1–1.0)
    k_scale = np.random.uniform(0.2, 1.0) * omega_base**2

    for i in range(N - 1):
        k_ij0 = k_scale * np.random.uniform(0.5, 1.5)
        couplings.append(Coupling((layer, i), (layer, i+1), k_ij0))
    return couplings
```

---

## 5. Inter-layer Couplings + Memory

```python
@dataclass
class MemoryKernel:
    taus0: List[float]   # base times (optionally modulated by b_L)
    amps0: List[float]   # base amplitudes (ditto)

@dataclass
class InterLayerCoupling:
    deep_layer: Layer
    shallow_layer: Layer
    links: Dict[Tuple[int, int], MemoryKernel]  # (i_deep, j_shallow) -> kernel
    g0: float  # base strength scale of this link
```

Generation:

```python
def build_inter_layer_coupling(deep_layer: Layer, shallow_layer: Layer,
                               N_deep: int, N_shallow: int,
                               omega_deep_base: float) -> InterLayerCoupling:
    links = {}
    # coupling scale comparable to shallow diagonals
    g0 = np.random.uniform(0.2, 2.0) * omega_deep_base**2

    max_links = min(N_deep, N_shallow)
    for idx in range(max_links):
        M = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])  # number of exponentials
        taus0, amps0 = [], []
        for _ in range(M):
            tau0 = np.random.uniform(0.1, 5.0) / omega_deep_base
            A0   = np.random.uniform(0.1, 1.0)
            taus0.append(tau0)
            amps0.append(A0)
        if M > 0:
            links[(idx, idx)] = MemoryKernel(taus0=taus0, amps0=amps0)

    return InterLayerCoupling(deep_layer, shallow_layer, links, g0)
```

Each exponential term produces one auxiliary variable `z_k`.

---

## 6. Structural Breathing per Layer

For each layer `L` we create two slow variables:

- `b_L(t)` → “configuration/stiffness” of the layer.
- `e_L(t)` → filtered energy (running average).

```python
@dataclass
class StructuralState:
    b: float       # current state
    e: float       # filtered energy
    tau_e: float   # energy filter time
    tau_b: float   # structural response time
    alpha_b: float # sensitivity of b to energy
    e_ref: float   # reference energy (neutral point)
```

Continuous evolution:

**Instantaneous energy of layer L:**

```python
def instant_energy_layer(L, modes, x, v, global_index):
    E = 0.0
    for m in modes_of_layer(L, modes):
        idx = global_index[(m.layer, m.index)]
        E += 0.5 * m.mass * v[idx]**2 + 0.5 * m.mass * m.omega0**2 * x[idx]**2
    return E
```

**Energy filter (e_L):**

\[
\dot{e}_L = \frac{E_L^{\text{inst}} - e_L}{\tau_e}
\]

**Structural breathing (b_L):**

\[
\dot{b}_L = \frac{-b_L + \alpha_b \left(e_L - e_{\text{ref}}\right)}{\tau_b}
\]

(If you want something more “oscillatory”, you can later move this to second order, but with first order you already get breathing if the energy varies.)

**Modulation of fast parameters:**

Frequencies:

\[
\omega_{L,i}^2(t) = \omega_{L,i0}^2 \left[1 + \varepsilon_\omega\, b_L(t)\right]
\]

Intra-layer stiffness:

\[
k_{ij}(t) = k_{ij0} \left[1 + \varepsilon_K\, b_L(t)\right]
\]

Optional: memory times/amplitudes:

\[
\tau_a(t) = \tau_{a0} \left[1 + \varepsilon_\tau\, b_L(t)\right],\quad
A_a(t)    = A_{a0} \left[1 + \varepsilon_A\, b_L(t)\right]
\]

with small epsilons (e.g. 0.1–0.3).

Typical values:

- `tau_e ~ 50–200` (in units of `1/omega_Q_base`)
- `tau_b ~ 200–1000`
- `alpha_b ~ 0.01–0.1`
- `e_ref` chosen as a typical initial energy.

---

## 7. Full State Variables

State vector \(Y(t)\):

- `x_p(t)` – positions of each physical mode (`p = 0..N_modes−1`).
- `v_p(t)` – velocities.
- `z_k(t)` – memory variables (`k = 0..N_z−1`).
- `b_L(t), e_L(t)` – for `L = Q, S1, S2` (and `S3` if present).

Structure:

```python
import numpy as np
from typing import Dict

@dataclass
class State:
    x: np.ndarray  # shape (N_modes,)
    v: np.ndarray  # shape (N_modes,)
    z: np.ndarray  # shape (N_z,)
    b: Dict[Layer, float]
    e: Dict[Layer, float]
```

---

## 8. Equations of Motion

### 8.1. For x and v (fast modes)

For each mode `p` with `Mode m` in layer `L`:

```python
def dv_dt(p, state, modes, intra_couplings, inter_couplings, struct_state, mapping):
    m = modes[p]
    layer = m.layer
    bL = struct_state.b[layer]
    eps_omega = ...  # global parameter

    # effective frequency with breathing
    omega_eff2 = m.omega0**2 * (1.0 + eps_omega * bL)

    # base force
    F = - omega_eff2 * state.x[p] - m.gamma * state.v[p]

    # intra-layer springs
    for c in intra_couplings_of_layer(layer):
        if mapping[c.i] == p or mapping[c.j] == p:
            i = mapping[c.i]
            j = mapping[c.j]
            k0 = c.k_ij0
            eps_K = ...
            k_eff = k0 * (1.0 + eps_K * bL)
            if p == i:
                F += -k_eff * (state.x[i] - state.x[j])
            elif p == j:
                F += -k_eff * (state.x[j] - state.x[i])

    # memory: sum A_a(t) * z_k
    for each_z_k_that_couples_to_p:
        kernel = ...
        A0 = ...
        bL_mem = struct_state.b[layer_corresponding_to_kernel]
        eps_A = ...
        A_eff = A0 * (1.0 + eps_A * bL_mem)
        F += - A_eff * state.z[k]

    # divide by mass
    return F / m.mass

def dx_dt(p, state):
    return state.v[p]
```

### 8.2. For z (memory)

For each `z_k` associated with `(deep d_idx, shallow s_idx)` and kernel `(taus0, amps0)`:

```python
def dz_dt(k, state, deep_layer, struct_state, tau0, d_idx):
    eps_tau = ...
    b_deep = struct_state.b[deep_layer]
    tau_eff = tau0 * (1.0 + eps_tau * b_deep)

    x_deep = state.x[d_idx]
    return -state.z[k] / tau_eff + x_deep
```

### 8.3. For e_L and b_L

```python
def de_dt(L, state, struct_state, modes, mapping):
    tau_e = struct_state.tau_e[L]
    eL = struct_state.e[L]
    E_inst = instant_energy_layer(L, modes, state.x, state.v, mapping)
    return (E_inst - eL) / tau_e

def db_dt(L, struct_state):
    tau_b   = struct_state.tau_b[L]
    bL      = struct_state.b[L]
    eL      = struct_state.e[L]
    e_ref   = struct_state.e_ref[L]
    alpha_b = struct_state.alpha_b[L]
    return (-bL + alpha_b * (eL - e_ref)) / tau_b
```

---

## 9. Numerical Integration

Use an explicit integrator such as Runge–Kutta 4 (RK4) or a fixed-step integrator.

Suggested parameters:

- `dt ~ 0.01` (in units of `1/omega_Q_base`).
- Total simulation time: `T_total ~ 5000–10000` (many Q cycles but not infinite).
- Discard an initial transient (e.g. first 20–30% of the time) before spectral analysis.

Loop:

```python
state = init_state_random(modes, struct_state)
for step in range(n_steps):
    t = step * dt
    state = rk4_step(state, dt, ...)
    if step > n_transient and step % sample_stride == 0:
        store_x_Q(t, state.x, ...)  # and optionally b_L(t), e_L(t)
```

---

## 10. Spectrum and Per-layer Weights

Using the time series of `x_Q(t)` (for example, one or several Q modes):

1. Remove the mean.
2. Apply a window (Hann, etc.).
3. FFT → \(|X(f)|^2\).
4. Find peaks above a threshold; each peak is an observable mode.

**Energies:**

- Choose a reference peak `f_anchor`.
- Set `E_anchor_target = 2.0 GeV`.
- Compute:

  ```python
  E_scale = E_anchor_target / (2 * np.pi * f_anchor_adim)
  ```

- For each peak at dimensionless frequency `omega_i_adim` (rad/s dimensionless):

  ```python
  E_i = omega_i_adim * E_scale
  ```

**Layer weights:**

For each peak, you can approximate eigenvectors by:

- Projecting `X(f)` on the stored `x_p(t)` (more involved), or  
- In a simpler first iteration, keep the approach you already used: eigenvalues/eigenvectors of the frozen linear matrix (with `b_L` fixed at a snapshot) and use those eigenvectors to compute per-layer weights.

The important point for the code is that the data structures already support both approaches.

---

## 11. Metrics and Plots

**Hadronic band selection:**

- CLI inputs: `band_min`, `band_max` in GeV (e.g. `0–3` or `0–5`).
- For each run:

  ```python
  band = energies_gev[(energies_gev >= band_min) &
                      (energies_gev <= band_max)]
  band = np.sort(band)
  band_count = len(band)
  ```

- Require `band_count >= 3` to consider the run valid for spacing analysis.

**Spacings:**

```python
spacings = np.diff(band)
# optional: filter tiny ΔE (numerical degeneracies)
spacings = spacings[spacings > 1e-4]  # e.g. 0.0001 GeV
```

Accumulate spacings across all valid runs and compute:

- Global histogram of ΔE.
- Mean and standard deviation of ΔE.
- Mode count per run (`band_count`).

**Layer-weight heatmap:**

- x-axis: energy of each mode in the band.
- y-axis: layers (Q, S1, S2, S3).
- color: normalized weight of each layer in the corresponding mode.

**Breathing curves:**

- `b_L(t)`, `e_L(t)` for each layer, for a few representative runs.

With this you have:

- The linear core with memory,
- Layer-wise structural breathing,
- And the full simulation + analysis pipeline. 
