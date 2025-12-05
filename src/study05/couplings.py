"""Coupling utilities for Study05."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .layers import Layer, Mode
from .config import rng_or_default


@dataclass
class MemoryKernel:
    taus: List[float]
    amps: List[float]


@dataclass
class Coupling:
    i: Tuple[Layer, int]
    j: Tuple[Layer, int]
    k_ij: float


@dataclass
class InterLayerCoupling:
    deep_layer: Layer
    shallow_layer: Layer
    coupling_matrix: Dict[Tuple[int, int], float]
    memory_kernel: MemoryKernel
    delay: float


def build_string_couplings(
    layer: Layer, N: int, k_scale: float = 1.0, rng: np.random.Generator | None = None
) -> List[Coupling]:
    rng = rng_or_default(rng)
    couplings: List[Coupling] = []
    for i in range(max(0, N - 1)):
        k_ij = k_scale * rng.uniform(0.5, 1.5)
        k_ij *= rng.uniform(0.95, 1.05)  # mild disorder to break degeneracies
        couplings.append(Coupling(i=(layer, i), j=(layer, i + 1), k_ij=float(k_ij)))
    return couplings


def build_inter_layer_coupling(
    deep_layer: Layer,
    shallow_layer: Layer,
    N_deep: int,
    N_shallow: int,
    f_deep: float,
    rng: np.random.Generator | None = None,
) -> InterLayerCoupling:
    rng = rng_or_default(rng)
    M = rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
    taus, amps = [], []
    for _ in range(int(M)):
        tau = rng.uniform(0.5, 5.0) / (2 * np.pi * f_deep)
        A = rng.uniform(0.1, 1.0)
        taus.append(float(tau))
        amps.append(float(A))

    kernel = MemoryKernel(taus=taus, amps=amps)

    max_links = min(N_deep, N_shallow)
    coupling_matrix: Dict[Tuple[int, int], float] = {}
    for idx in range(max_links):
        strength = rng.uniform(0.2, 3.0)
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
