"""Study05 – DOFT internal layers simulator core utilities.

This module implements the data structures and helper functions described in
``docs/STUDY05_code_header_and_structures.md``. It covers layer enums, mode and
coupling representations, random parameter generation, basic complexity checks,
and a lightweight dynamical-matrix builder to approximate mode spectra.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

import numpy as np

# Physical constants (in convenient units)
HBAR_EV_S = 6.582_119_569e-16
HBAR_GEV_S = HBAR_EV_S * 1e-9
C_LIGHT = 299_792_458.0
GEV_TO_J = 1.602_176_634e-10


class Layer(Enum):
    """Model layers ordered from shallow to deep."""

    Q = auto()  # quark/hadron effective layer
    S1 = auto()
    S2 = auto()
    S3 = auto()


@dataclass
class Mode:
    layer: Layer
    index: int  # mode index inside the layer (0..N_layer-1)
    omega0: float  # natural frequency (rad/s) before coupling
    mass: float  # effective mass (arbitrary units)
    gamma: float  # damping coefficient


@dataclass
class MemoryKernel:
    # Exponential memory kernel: K(t) ~ sum_a A_a * exp(-t / tau_a)
    taus: List[float]
    amps: List[float]


@dataclass
class Coupling:
    # Coupling between two modes (i -> j)
    i: Tuple[Layer, int]
    j: Tuple[Layer, int]
    k_ij: float  # coupling strength (spring-like)


@dataclass
class InterLayerCoupling:
    # Coupling between layers deep_layer -> shallow_layer with delay
    deep_layer: Layer
    shallow_layer: Layer
    coupling_matrix: Dict[Tuple[int, int], float]  # (i_deep, j_shallow) -> C_ij
    memory_kernel: MemoryKernel
    delay: float  # tau_{deep -> shallow}


@dataclass
class SimulationConfig:
    case_name: str  # "CaseA_2layers" or "CaseB_3layers"
    f_Q: float  # base frequency for layer Q (Hz)
    R_S1_Q: float  # ratio f_S1 / f_Q
    R_S2_S1: float  # ratio f_S2 / f_S1
    R_S3_S2: Optional[float] = None  # only for CaseB (3 layers)

    N_Q: int = 1  # modes in Q (usually 1)
    N_S1: int = 3  # 3..7 recommended
    N_S2: int = 3
    N_S3: int = 3  # only for CaseB

    modes: Optional[List[Mode]] = None
    intra_layer_couplings: Optional[List[Coupling]] = None
    inter_layer_couplings: Optional[List[InterLayerCoupling]] = None
    complexity: Optional[int] = None


def _require_rng(rng: Optional[np.random.Generator] = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def sample_base_frequencies(case: str, rng: Optional[np.random.Generator] = None):
    """Sample base frequencies and layer ratios for a given case."""
    rng = _require_rng(rng)

    log_fQ = rng.uniform(23, 24)
    f_Q = 10 ** log_fQ

    def sample_R():
        return 10 ** rng.uniform(2, 4)

    R_S1_Q = sample_R()
    R_S2_S1 = sample_R()

    f_layers = {Layer.Q: f_Q}
    f_layers[Layer.S1] = R_S1_Q * f_Q
    f_layers[Layer.S2] = R_S2_S1 * f_layers[Layer.S1]

    R_S3_S2 = None
    if case == "CaseB_3layers":
        R_S3_S2 = sample_R()
        f_layers[Layer.S3] = R_S3_S2 * f_layers[Layer.S2]

    return f_Q, f_layers, R_S1_Q, R_S2_S1, R_S3_S2


def build_string_layer_modes(
    layer: Layer, base_freq_hz: float, N: int, rng: Optional[np.random.Generator] = None
) -> List[Mode]:
    rng = _require_rng(rng)
    modes: List[Mode] = []
    omega_base = 2 * np.pi * base_freq_hz

    for i in range(N):
        delta = rng.uniform(-0.1, 0.1)
        omega_i = omega_base * (1.0 + delta)
        mass_i = 1.0
        gamma_i = omega_base * rng.uniform(1e-3, 1e-1)
        modes.append(
            Mode(layer=layer, index=i, omega0=float(omega_i), mass=mass_i, gamma=float(gamma_i))
        )
    return modes


def build_string_couplings(
    layer: Layer, N: int, rng: Optional[np.random.Generator] = None
) -> List[Coupling]:
    rng = _require_rng(rng)
    couplings: List[Coupling] = []
    k0 = 1.0

    for i in range(max(0, N - 1)):
        k_ij = k0 * rng.uniform(0.5, 1.5)
        couplings.append(
            Coupling(
                i=(layer, i),
                j=(layer, i + 1),
                k_ij=float(k_ij),
            )
        )
    return couplings


def build_inter_layer_coupling(
    deep_layer: Layer,
    shallow_layer: Layer,
    N_deep: int,
    N_shallow: int,
    f_deep: float,
    rng: Optional[np.random.Generator] = None,
) -> InterLayerCoupling:
    rng = _require_rng(rng)
    M = rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2])

    taus, amps = [], []
    for _ in range(int(M)):
        tau = rng.uniform(0.1, 10.0) / (2 * np.pi * f_deep)
        A = rng.uniform(0.1, 1.0)
        taus.append(float(tau))
        amps.append(float(A))

    kernel = MemoryKernel(taus=taus, amps=amps)

    coupling_matrix: Dict[Tuple[int, int], float] = {}
    max_links = min(N_deep, N_shallow)
    for idx in range(max_links):
        strength = rng.uniform(0.1, 1.0)
        coupling_matrix[(idx, idx)] = float(strength)

    delay = rng.uniform(0.5, 2.0) / (2 * np.pi * f_deep)

    return InterLayerCoupling(
        deep_layer=deep_layer,
        shallow_layer=shallow_layer,
        coupling_matrix=coupling_matrix,
        memory_kernel=kernel,
        delay=float(delay),
    )


def compute_complexity(modes: List[Mode], inter_couplings: List[InterLayerCoupling]) -> int:
    n_modes = len(modes)
    n_memory_terms = sum(len(ic.memory_kernel.taus) for ic in inter_couplings)
    return n_modes + n_memory_terms


def build_dynamical_matrix(
    modes: List[Mode],
    intra_couplings: List[Coupling],
    inter_couplings: Optional[List[InterLayerCoupling]] = None,
) -> np.ndarray:
    """Build a simple dynamical matrix ignoring damping and memory."""
    index_map = {(m.layer, m.index): idx for idx, m in enumerate(modes)}
    N = len(modes)
    D = np.zeros((N, N))

    for idx, m in enumerate(modes):
        D[idx, idx] = m.omega0 ** 2

    for c in intra_couplings:
        i = index_map[c.i]
        j = index_map[c.j]
        k = c.k_ij
        D[i, i] += k
        D[j, j] += k
        D[i, j] -= k
        D[j, i] -= k

    if inter_couplings:
        for ic in inter_couplings:
            for (i_deep, j_shallow), strength in ic.coupling_matrix.items():
                i = index_map.get((ic.deep_layer, i_deep))
                j = index_map.get((ic.shallow_layer, j_shallow))
                if i is None or j is None:
                    continue
                k = strength
                D[i, i] += k
                D[j, j] += k
                D[i, j] -= k
                D[j, i] -= k
    return D


def compute_eigenfrequencies(D: np.ndarray) -> np.ndarray:
    vals, _ = np.linalg.eigh(D)
    vals = np.clip(vals, a_min=0, a_max=None)
    omegas = np.sqrt(vals)
    return np.array(omegas)


def omega_to_energy_gev(omegas: np.ndarray) -> np.ndarray:
    """Convert angular frequencies (rad/s) to energies (GeV)."""
    return HBAR_GEV_S * np.asarray(omegas)


def energy_gev_to_mass_kg(energies_gev: np.ndarray) -> np.ndarray:
    energies_joule = np.asarray(energies_gev) * GEV_TO_J
    return energies_joule / (C_LIGHT**2)


def compute_mode_spacings(energies: np.ndarray) -> np.ndarray:
    energies = np.sort(np.asarray(energies))
    if energies.size < 2:
        return np.array([])
    return np.diff(energies)


def count_modes_in_band(energies: np.ndarray, min_gev: float, max_gev: float) -> int:
    energies = np.asarray(energies)
    mask = (energies >= min_gev) & (energies <= max_gev)
    return int(np.count_nonzero(mask))


def generate_configuration(
    case: str,
    rng: Optional[np.random.Generator] = None,
    n_q: int = 1,
    n_s1: int = 3,
    n_s2: int = 3,
    n_s3: int = 3,
    max_complexity: int = 8,
    attempts: int = 20,
) -> Optional[SimulationConfig]:
    """Generate a simulation configuration that satisfies the complexity limit."""
    rng = _require_rng(rng)
    case_name = "CaseB_3layers" if case == "CaseB_3layers" else "CaseA_2layers"
    include_s3 = case_name == "CaseB_3layers"

    for _ in range(attempts):
        f_Q, f_layers, R_S1_Q, R_S2_S1, R_S3_S2 = sample_base_frequencies(case_name, rng)

        modes: List[Mode] = []
        intra: List[Coupling] = []
        inter: List[InterLayerCoupling] = []

        modes.extend(build_string_layer_modes(Layer.Q, f_layers[Layer.Q], n_q, rng))
        intra.extend(build_string_couplings(Layer.Q, n_q, rng))

        modes.extend(build_string_layer_modes(Layer.S1, f_layers[Layer.S1], n_s1, rng))
        intra.extend(build_string_couplings(Layer.S1, n_s1, rng))
        inter.append(
            build_inter_layer_coupling(
                deep_layer=Layer.S1,
                shallow_layer=Layer.Q,
                N_deep=n_s1,
                N_shallow=n_q,
                f_deep=f_layers[Layer.S1],
                rng=rng,
            )
        )

        modes.extend(build_string_layer_modes(Layer.S2, f_layers[Layer.S2], n_s2, rng))
        intra.extend(build_string_couplings(Layer.S2, n_s2, rng))
        inter.append(
            build_inter_layer_coupling(
                deep_layer=Layer.S2,
                shallow_layer=Layer.S1,
                N_deep=n_s2,
                N_shallow=n_s1,
                f_deep=f_layers[Layer.S2],
                rng=rng,
            )
        )

        if include_s3:
            modes.extend(build_string_layer_modes(Layer.S3, f_layers[Layer.S3], n_s3, rng))
            intra.extend(build_string_couplings(Layer.S3, n_s3, rng))
            inter.append(
                build_inter_layer_coupling(
                    deep_layer=Layer.S3,
                    shallow_layer=Layer.S2,
                    N_deep=n_s3,
                    N_shallow=n_s2,
                    f_deep=f_layers[Layer.S3],
                    rng=rng,
                )
            )

        complexity = compute_complexity(modes, inter)
        if complexity > max_complexity:
            continue

        return SimulationConfig(
            case_name=case_name,
            f_Q=f_Q,
            R_S1_Q=R_S1_Q,
            R_S2_S1=R_S2_S1,
            R_S3_S2=R_S3_S2,
            N_Q=n_q,
            N_S1=n_s1,
            N_S2=n_s2,
            N_S3=n_s3,
            modes=modes,
            intra_layer_couplings=intra,
            inter_layer_couplings=inter,
            complexity=complexity,
        )
    return None


def summarise_spacings(spacings: np.ndarray) -> Dict[str, float]:
    if spacings.size == 0:
        return {"count": 0, "mean": float("nan"), "std": float("nan")}
    return {
        "count": int(spacings.size),
        "mean": float(np.mean(spacings)),
        "std": float(np.std(spacings)),
    }
