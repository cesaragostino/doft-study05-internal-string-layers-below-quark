# Study05 – DOFT Internal Layers Simulator (Code-Oriented Spec)

## 1. Short Model Description (for Code Header)

**Study05 – DOFT internal layers simulator**

**Goal:**

Simulate a small hierarchy of delayed coupled oscillators representing internal layers below the quark scale (S1, S2, optional S3), plus an effective **quark/hadron layer Q**.  
Each internal layer is modeled as a short 1D string of coupled oscillators.

**Key constraints:**

- Frequency ratios per layer: `R_layer` in \([10^2, 10^4]\)
- Base quark/hadron frequency: `f_Q` in \([10^{23}, 10^{24}]\) Hz
- Two configuration families:
  - **Case A**: 2 internal layers (S1, S2)
  - **Case B**: 3 internal layers (S1, S2, S3)
- Complexity index: \(C \le 8\) (or \(\le 10\) max)

  \[
  C = \text{total explicit modes} + \text{total memory terms}
  \]

**Outputs:**

- Effective mode spectrum at layer Q (frequencies and “masses” \(\sim \hbar\omega / c^2\))
- Quality factors / lifetimes (if damping is included)
- Basic statistics of mode spacings and band structure
- Plots representing “locks” and hadron-like spectra

---

## 2. Suggested Data Structures

### 2.1. Layer Enum

```python
from enum import Enum, auto

class Layer(Enum):
    Q  = auto()   # quark/hadron effective layer
    S1 = auto()   # first internal string-like layer
    S2 = auto()   # second internal layer
    S3 = auto()   # optional third internal layer (deepest)
```

---

### 2.2. `Mode` Class

```python
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Mode:
    layer: Layer
    index: int           # mode index inside the layer (0..N_layer-1)
    omega0: float        # natural frequency (rad/s) before coupling
    mass: float          # effective mass (arbitrary units)
    gamma: float         # damping coefficient
```

---

### 2.3. `MemoryKernel` Class

```python
@dataclass
class MemoryKernel:
    # Exponential memory kernel: K(t) ~ sum_a A_a * exp(-t / tau_a)
    taus: List[float]    # time constants tau_a
    amps: List[float]    # amplitudes A_a
```

---

### 2.4. Couplings (Intra-Layer and Inter-Layer)

```python
@dataclass
class Coupling:
    # Coupling between two modes (i -> j)
    i: Tuple[Layer, int]    # (layer, index)
    j: Tuple[Layer, int]
    k_ij: float             # coupling strength (spring-like)
```

```python
@dataclass
class InterLayerCoupling:
    # Coupling between layers deep_layer -> shallow_layer with delay
    deep_layer: Layer
    shallow_layer: Layer
    coupling_matrix: Dict[Tuple[int, int], float]  # (i_deep, j_shallow) -> C_ij
    memory_kernel: MemoryKernel
    delay: float            # tau_{deep -> shallow}
```

---

### 2.5. Full Simulation Configuration

```python
@dataclass
class SimulationConfig:
    case_name: str                 # "CaseA_2layers" or "CaseB_3layers"
    f_Q: float                     # base frequency for layer Q (Hz)
    R_S1_Q: float                  # ratio f_S1 / f_Q
    R_S2_S1: float                 # ratio f_S2 / f_S1
    R_S3_S2: float = None          # only for CaseB (3 layers)

    N_Q: int = 1                   # modes in Q (usually 1)
    N_S1: int = 3                  # 3..7 recommended
    N_S2: int = 3
    N_S3: int = 3                  # only for CaseB

    modes: List[Mode] = None
    intra_layer_couplings: List[Coupling] = None
    inter_layer_couplings: List[InterLayerCoupling] = None
```

---

## 3. Parameter Generation (Sweep)

### 3.1. Frequency Ranges

```python
import numpy as np

def sample_base_frequencies(case: str):
    """Sample base frequencies and layer ratios for a given case.

    Returns
    -------
    f_Q : float
        Base frequency for Q (Hz).
    f_layers : Dict[Layer, float]
        Base frequency per layer (Hz).
    R_S1_Q, R_S2_S1, R_S3_S2 : float or None
        Layer frequency ratios.
    """
    # Sample f_Q in log space between 1e23 and 1e24 Hz
    log_fQ = np.random.uniform(23, 24)
    f_Q = 10 ** log_fQ

    # Sample R_layer in [1e2, 1e4] (log-uniform)
    def sample_R():
        return 10 ** np.random.uniform(2, 4)

    R_S1_Q  = sample_R()
    R_S2_S1 = sample_R()

    f_layers = {Layer.Q: f_Q}
    f_layers[Layer.S1] = R_S1_Q * f_Q
    f_layers[Layer.S2] = R_S2_S1 * f_layers[Layer.S1]

    R_S3_S2 = None
    if case == "CaseB_3layers":
        R_S3_S2 = sample_R()
        f_layers[Layer.S3] = R_S3_S2 * f_layers[Layer.S2]

    return f_Q, f_layers, R_S1_Q, R_S2_S1, R_S3_S2
```

---

### 3.2. Build Modes per Layer (String-Like)

```python
def build_string_layer_modes(layer: Layer, base_freq_hz: float, N: int) -> List[Mode]:
    modes = []
    omega_base = 2 * np.pi * base_freq_hz

    # small random offsets in frequency (±10%)
    for i in range(N):
        delta = np.random.uniform(-0.1, 0.1)
        omega_i = omega_base * (1.0 + delta)
        mass_i = 1.0  # can be kept as 1 for now
        gamma_i = omega_base * np.random.uniform(1e-3, 1e-1)  # small damping

        modes.append(Mode(layer=layer, index=i, omega0=omega_i, mass=mass_i, gamma=gamma_i))
    return modes
```

---

### 3.3. Intra-Layer Couplings (1D Chain)

```python
def build_string_couplings(layer: Layer, N: int) -> List[Coupling]:
    couplings = []
    k0 = 1.0  # base spring constant (can be scaled later)

    for i in range(N - 1):
        k_ij = k0 * np.random.uniform(0.5, 1.5)
        couplings.append(Coupling(
            i=(layer, i),
            j=(layer, i + 1),
            k_ij=k_ij
        ))
    return couplings
```

---

### 3.4. Memory and Inter-Layer Coupling

```python
def build_inter_layer_coupling(deep_layer: Layer, shallow_layer: Layer,
                               N_deep: int, N_shallow: int,
                               f_deep: float) -> InterLayerCoupling:
    # memory: 0, 1 or 2 exponentials (to control complexity)
    M = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])

    taus, amps = [], []
    for _ in range(M):
        # time constants ~ [0.1, 10] / omega_deep
        tau = np.random.uniform(0.1, 10.0) / (2 * np.pi * f_deep)
        A = np.random.uniform(0.1, 1.0)
        taus.append(tau)
        amps.append(A)

    kernel = MemoryKernel(taus=taus, amps=amps)

    # coupling matrix: sparse, few non-zero entries
    coupling_matrix = {}
    max_links = min(N_deep, N_shallow)
    for idx in range(max_links):
        strength = np.random.uniform(0.1, 1.0)
        coupling_matrix[(idx, idx)] = strength

    # base delay ~ 1 / omega_deep
    delay = np.random.uniform(0.5, 2.0) / (2 * np.pi * f_deep)

    return InterLayerCoupling(
        deep_layer=deep_layer,
        shallow_layer=shallow_layer,
        coupling_matrix=coupling_matrix,
        memory_kernel=kernel,
        delay=delay
    )
```

---

### 3.5. Complexity Index \(C\)

```python
def compute_complexity(modes: List[Mode], inter_couplings: List[InterLayerCoupling]) -> int:
    n_modes = len(modes)
    n_memory_terms = sum(len(ic.memory_kernel.taus) for ic in inter_couplings)
    return n_modes + n_memory_terms
```

---

## 4. Effective Spectrum at Q

For v0.1, the implementation can:

- Build the linearized dynamical matrix ignoring memory, or
- Approximate memory using auxiliary variables (equivalent to enlarging the system) and then diagonalize.

### 4.1. Simple Scheme (No Explicit Memory, First Iteration)

```python
import numpy as np

def build_dynamical_matrix(modes: List[Mode], intra_couplings: List[Coupling]) -> np.ndarray:
    """Build a simple dynamical matrix D such that
        d2x/dt2 = -D x
    ignoring damping and memory to get approximate eigenfrequencies.
    """
    index_map = { (m.layer, m.index): idx for idx, m in enumerate(modes) }
    N = len(modes)
    D = np.zeros((N, N))

    # diagonal terms: omega0^2
    for idx, m in enumerate(modes):
        D[idx, idx] = m.omega0 ** 2

    # add coupling contributions
    for c in intra_couplings:
        i = index_map[c.i]
        j = index_map[c.j]
        k = c.k_ij
        D[i, i] += k
        D[j, j] += k
        D[i, j] -= k
        D[j, i] -= k

    return D

def compute_eigenfrequencies(D: np.ndarray) -> np.ndarray:
    vals, _ = np.linalg.eigh(D)
    # Only positive eigenvalues correspond to omega^2
    vals = np.clip(vals, a_min=0, a_max=None)
    omegas = np.sqrt(vals)
    return omegas
```

Later you can filter modes “localized” in layer Q using simple heuristics (e.g. modes with the largest component on the Q mode, if that is explicitly included in the matrix).

---

## 5. Minimal Statistical Checks

After many samples, the implementation should compute some basic diagnostics.

### 5.1. Check that \(C \le 8–10\)

- Reject configurations with `compute_complexity(...) > 8`.
- Track what fraction of attempts stays within the allowed range.

---

### 5.2. Mode Spacing Statistics at Q

For each valid simulation:

1. Get the effective frequencies in the “hadron-like” band  
   (e.g. convert to energies and keep those between 0 and 3 GeV).
2. Sort energies: \(E_1 < E_2 < \dots < E_k\).
3. Compute spacings:

   \[
   \Delta E_i = E_{i+1} - E_i
   \]

4. Collect all \(\Delta E_i\) across many runs and compute:

   - Histogram of \(\Delta E\),
   - Mean and standard deviation,
   - Whether there is a peak around ~0.5–1 GeV.

```python
def compute_mode_spacings(energies: np.ndarray) -> np.ndarray:
    energies = np.sort(energies)
    if len(energies) < 2:
        return np.array([])
    return np.diff(energies)
```

---

### 5.3. Mode Density in the Band

For each run, count how many modes fall in [0, 3 GeV].  
Then:

- Build a histogram / boxplot of this count over many runs.

The idea is that this should represent the “population” of hadronic resonances in that range:  
not 1, not 10⁵, but “a few to a few tens”.

---

## 6. Recommended Plots (Lock Representation)

The implementation can use `matplotlib` to generate:

### 6.1. Mode Spectrum (“Lines” or Lollipop Plot)

- X-axis: mode index.
- Y-axis: mode energy (\(E = \hbar\omega\)).

Highlight with different colors:

- Modes dominant in Q,
- Modes from internal layers.

```python
import matplotlib.pyplot as plt

def plot_spectrum(energies: np.ndarray, title: str = "Mode spectrum"):
    plt.figure()
    x = np.arange(len(energies))
    plt.stem(x, energies, use_line_collection=True)
    plt.xlabel("Mode index")
    plt.ylabel("Energy (arbitrary units)")
    plt.title(title)
    plt.tight_layout()
```

---

### 6.2. Spacing Histogram

```python
def plot_spacing_histogram(all_spacings: np.ndarray, title: str = "Mode spacings"):
    plt.figure()
    plt.hist(all_spacings, bins=50, density=True)
    plt.xlabel("ΔE")
    plt.ylabel("Probability density")
    plt.title(title)
    plt.tight_layout()
```

---

### 6.3. “Layer vs Frequency” Heatmap (Lock Visualization)

- X-axis: mode (or energy) within a run.
- Y-axis: layer (Q, S1, S2, S3).
- Color: relative amplitude of that mode in each layer (once eigenvectors are available).

This makes the locked modes between layers visually obvious.
