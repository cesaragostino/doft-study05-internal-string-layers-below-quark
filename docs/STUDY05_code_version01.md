# Study05 – Design Changes and Full Dynamic Model

## 1. Key Design Changes

### 1.1. More Modes in Q

**Before:**

- `N_Q = 1` → always a single mode at ~1 GeV.

**New:**

- Q is also modeled as a short 1D string (same as S1, S2, S3).

Define:

- \(N_Q \in \{3,4,5\}\) (for example, default = 5).

The base frequency \(f_Q\) stays in \([10^{23}, 10^{24}]\) Hz, but:

- Couplings inside Q (`K_Q`) are chosen so that the normal modes of Q end up **clustered in the 0–3 GeV band** (not too far apart).

This alone should already give you several modes in the hadronic band.

---

### 1.2. Include Memory / Delays in the Dynamic Matrix

**So far:**

- You only used the matrix `D` of \(\omega^2\) with elastic couplings; memory was not included.

**New:**

- Rewrite the system in first-order state-space form, **including auxiliary variables** for the exponential kernels.

Each exponential in the kernel (each pair \((\tau, A)\)) adds **one extra variable**.

Then you diagonalize the matrix **A** (not D) and obtain **complex eigenvalues** \(\lambda\):

- \(\omega \approx \operatorname{Im}(\lambda)\),
- damping \(\sim \operatorname{Re}(\lambda)\).

This way, delays/memory genuinely affect the frequencies.

---

## 2. Global Project Structure

Suggested layout (Python, but easily adaptable):

- `config.py` → global parameters, ranges, physical constants.
- `layers.py` → layer and mode generation (`Layer`, `Mode`).
- `couplings.py` → intra-layer + inter-layer + memory.
- `state_space.py` → construction of the state matrix **A** (with memory).
- `sweep.py` → Monte Carlo loop over configurations.
- `analysis.py` → band statistics, spacings, locks.
- `plots.py` → spectra, histograms, heatmaps.
- `run_sweep.py` → main script (CLI).

Below is what’s essential for the implementation.

---

## 3. Full Mathematical Model (with Memory)

### 3.1. State Variables

For each physical mode \(x_i\):

- \(x_i\) → position
- \(v_i = \dot{x}_i\) → velocity

For each exponential memory term between a **deep mode** \(d\) and a **shallow mode** \(s\):

- \(z_{a, d\to s}\) → auxiliary memory variable

State size:

- \(n_x = n_{\text{modes}}\)
- \(n_v = n_{\text{modes}}\)
- \(n_z = \text{total number of memory terms}\)

- \(\text{dim\_state} = n_x + n_v + n_z\)

---

### 3.2. Equations

Schematic example for a shallow mode \(s\):

\[
m_s \, \ddot x_s
+ \omega_s^2 x_s
+ \sum_j K_{sj} (x_s - x_j)
+ \sum_{d,a} A_a(d \to s) \, z_{a, d\to s}
= 0
\]

Memory variables:

\[
\dot z_{a, d\to s}
=
- \frac{1}{\tau_a} z_{a, d\to s}
+ x_d
\]

In first-order form:

- \(\dot x = v\)
- \(\dot v = -\frac{1}{m_s} (\omega_s^2 x_s + \dots + \sum A z)\)
- \(\dot z = - z / \tau + x_d\)

The code can build a matrix **A** that satisfies:

\[
\dot Y = A Y, \quad
Y = (x_1, \dots, x_N, v_1, \dots, v_N, z_1, \dots, z_{n_z})^T
\]

Then:

```python
eigvals, eigvecs = np.linalg.eig(A)
frequencies = np.abs(np.imag(eigvals))  # rad/s
```

---

## 4. Concrete Spec for Implementation

### 4.1. Layers and Frequencies

Layers:

- Case A: Q, S1, S2
- Case B: Q, S1, S2, S3

Base frequency:

- `f_Q`: log-uniform in `[10**23, 10**24]` Hz.

Layer ratio:

- `R_layer = f_deep / f_shallow`: log-uniform in `[1e2, 1e4]`.

Formula:

```python
# sample log-uniform
def sample_R():
    return 10 ** np.random.uniform(2, 4)

f_Q  = 10 ** np.random.uniform(23, 24)
R_S1_Q  = sample_R()
R_S2_S1 = sample_R()

f_S1 = R_S1_Q * f_Q
f_S2 = R_S2_S1 * f_S1
# CaseB:
# R_S3_S2 = sample_R()
# f_S3 = R_S3_S2 * f_S2
```

---

### 4.2. N per Layer and Complexity C

- \(N_Q \in \{3,4,5\}\), default 5.
- \(N_{S1}, N_{S2}, N_{S3} \in \{3,4,5\}\).

Complexity:

\[
C = n_{\text{modes, explicit}} + n_{\text{memory terms}}
\]

```python
assert C <= 10  # discard configuration otherwise
```

---

### 4.3. String-Like Mode Generation per Layer

Same as before, but now **also for Q**:

```python
def build_string_layer_modes(layer, base_freq_hz, N):
    omega_base = 2 * np.pi * base_freq_hz
    modes = []
    for i in range(N):
        delta = np.random.uniform(-0.05, 0.05)    # ±5% for Q
        omega_i = omega_base * (1.0 + delta)
        mass_i  = 1.0
        gamma_i = omega_base * np.random.uniform(1e-4, 1e-2)
        modes.append(Mode(layer, i, omega_i, mass_i, gamma_i))
    return modes
```

For deeper layers you can keep ±10% offsets.

---

### 4.4. Intra-Layer Couplings

Same as before (1D chain):

```python
def build_string_couplings(layer, N, k_scale=1.0):
    couplings = []
    for i in range(N - 1):
        k_ij = k_scale * np.random.uniform(0.5, 1.5)
        couplings.append(Coupling((layer, i), (layer, i+1), k_ij))
    return couplings
```

For Q you can use a **smaller `k_scale`** so that the modes cluster in energy (i.e., the band does not spread too much).

---

### 4.5. Inter-Layer + Memory

Keep your current function, but now tau and A are **actually used** to build the `z` equations:

```python
def build_inter_layer_coupling(deep_layer, shallow_layer, N_deep, N_shallow, f_deep):
    M = np.random.choice([1, 2])  # at least 1 memory term if coupling exists
    taus, amps = [], []
    for _ in range(M):
        tau = np.random.uniform(0.5, 5.0) / (2 * np.pi * f_deep)
        A   = np.random.uniform(0.1, 1.0)
        taus.append(tau)
        amps.append(A)

    kernel = MemoryKernel(taus=taus, amps=amps)

    # diagonal links i->i
    max_links = min(N_deep, N_shallow)
    matrix = {}
    for idx in range(max_links):
        strength = np.random.uniform(0.1, 1.0)
        matrix[(idx, idx)] = strength

    delay = np.random.uniform(0.5, 2.0) / (2 * np.pi * f_deep)

    return InterLayerCoupling(deep_layer, shallow_layer, matrix, kernel, delay)
```

For v0.1 you can ignore the explicit delay in **A** (it will be reflected effectively via memory); if you want to go further, you can approximate delay with phases, but the `z(t)` variables already capture a good part of the effect.

---

### 4.6. Building the State Matrix A

Indexing scheme:

```python
# modes: 0..N_modes-1
# x:     0..N_modes-1
# v:     N_modes..2*N_modes-1
# z:     2*N_modes..2*N_modes+n_z-1
```

Filling:

```python
A = np.zeros((dim_state, dim_state))

# dx/dt = v
for i in range(N_modes):
    A[i, N_modes + i] = 1.0

# dv/dt for each mode
for m_i in modes:
    idx_x = index_map[(m_i.layer, m_i.index)]
    idx_v = N_modes + idx_x

    # -omega^2 x / m
    A[idx_v, idx_x] -= (m_i.omega0**2) / m_i.mass

# intra-layer springs
for c in intra_layer_couplings:
    i = index_map[c.i]
    j = index_map[c.j]
    ki = c.k_ij
    # spring contributions: (x_i - x_j)
    A[N_modes + i, i] -= ki
    A[N_modes + i, j] += ki
    A[N_modes + j, j] -= ki
    A[N_modes + j, i] += ki

# memory: z_dot = -z/tau + x_deep, dv/dt += sum A z
z_idx = 2 * N_modes
for ic in inter_layer_couplings:
    deep = ic.deep_layer
    shallow = ic.shallow_layer
    taus = ic.memory_kernel.taus
    amps = ic.memory_kernel.amps

    for (i_deep, j_sh) in ic.coupling_matrix:
        idx_deep = index_map[(deep, i_deep)]
        idx_sh_x = index_map[(shallow, j_sh)]
        idx_sh_v = N_modes + idx_sh_x

        for a, (tau_a, A_a) in enumerate(zip(taus, amps)):
            idx_z = z_idx
            z_idx += 1

            # z_dot = -z/tau + x_deep
            A[idx_z, idx_z] = -1.0 / tau_a
            A[idx_z, idx_deep] = 1.0

            # dv_sh/dt += (A_a * z) / m_sh
            m_sh = modes[idx_sh_x].mass
            A[idx_sh_v, idx_z] += A_a / m_sh
```

Diagonalize **A**:

```python
eigvals, eigvecs = np.linalg.eig(A)
omegas = np.abs(np.imag(eigvals))   # rad/s
freqs  = omegas / (2 * np.pi)
# Energies: E = ħ * omega (in Joules), then convert to GeV
```

---

## 5. Improved Statistical Checks

### 5.1. Window and Targets

Hadronic window:

- \([E_{\min}, E_{\max}] = [0, 3]\) GeV (configurable).

Target:

- 3 ≤ `band_count` ≤ 12 modes in that window.

Per run:

```python
band_energies = energies[(energies >= E_min) & (energies <= E_max)]
band_count = len(band_energies)
if band_count < 3:
    # discard run for spacing analysis
    ...
```

The JSON you already defined has this structure; only the acceptance criterion needs to be updated.

---

### 5.2. Spacings and Statistics

When `band_count >= 3`:

```python
spacings = np.diff(np.sort(band_energies))
# accumulate in a global array across runs
```

Then compute:

- Mean, standard deviation, histogram,
- and visually compare whether spacings tend to a typical scale or look completely random.

---

### 5.3. Counts per Layer / Locks

Once you have eigenvectors:

For each mode in the band, you can compute:

```python
# energy weight per layer
weight_per_layer = {
    Layer.Q:  ...,
    Layer.S1: ...,
    Layer.S2: ...,
    # ...
}
```

by summing \(|\text{amplitude}|^2\) of the `x_i` components of that layer.

A “strong Q–S1 lock” is seen when **one mode** has significant weight in both layers.

You can build distributions of:

- how many modes in the band are “Q–S1 locks”,
- how many are “Q-only”, etc.

---

## 6. Representative Plots

In addition to the plot you already have:

### 6.1. Hadronic Spectrum for a Good Run

- Lollipop/stem plot of mode energies in 0–3 GeV.
- Color-code:

  - modes locked (Q+S1),
  - vs Q-only modes.

### 6.2. Histogram of Spacings \(\Delta E\)

- For all accepted runs.

### 6.3. Layer–Mode Heatmap

- X-axis: mode energy (sorted).
- Y-axis: layers (Q, S1, S2, S3).
- Color: weight of each layer in that mode.

This should make it visible when the model begins to produce something resembling **towers of hadronic resonances** with internal locks.

