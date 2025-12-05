"""Coupling utilities for Study05."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .layers import Layer, Mode
from .config import rng_or_default


@dataclass
class MemoryKernel:
    taus0: List[float]
    amps0: List[float]


@dataclass
class Coupling:
    i: Tuple[Layer, int]
    j: Tuple[Layer, int]
    k_ij0: float


@dataclass
class InterLayerCoupling:
    deep_layer: Layer
    shallow_layer: Layer
    links: Dict[Tuple[int, int], MemoryKernel]  # (i_deep, j_shallow) -> kernel
    g0: float  # base strength scale


def build_string_couplings(
    layer: Layer, N: int, k_scale: float = 1.0, rng: np.random.Generator | None = None
) -> List[Coupling]:
    rng = rng_or_default(rng)
    couplings: List[Coupling] = []
    for i in range(max(0, N - 1)):
        k_ij = k_scale * rng.uniform(0.5, 1.5)
        k_ij *= rng.uniform(0.95, 1.05)  # mild disorder to break degeneracies
        couplings.append(Coupling(i=(layer, i), j=(layer, i + 1), k_ij0=float(k_ij)))
    return couplings


def build_inter_layer_coupling(
    deep_layer: Layer,
    shallow_layer: Layer,
    N_deep: int,
    N_shallow: int,
    omega_deep_base: float,
    rng: np.random.Generator | None = None,
) -> InterLayerCoupling:
    rng = rng_or_default(rng)
    links: Dict[Tuple[int, int], MemoryKernel] = {}
    g0 = rng.uniform(0.2, 2.0) * (omega_deep_base**2)

    max_links = min(N_deep, N_shallow)
    for idx in range(max_links):
        M = rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2])  # number of exponentials
        taus0, amps0 = [], []
        for _ in range(int(M)):
            tau0 = rng.uniform(0.1, 5.0) / omega_deep_base
            A0 = rng.uniform(0.1, 1.0)
            taus0.append(float(tau0))
            amps0.append(float(A0))
        links[(idx, idx)] = MemoryKernel(taus0=taus0, amps0=amps0)

    return InterLayerCoupling(
        deep_layer=deep_layer,
        shallow_layer=shallow_layer,
        links=links,
        g0=float(g0),
    )


def compute_complexity(modes: List[Mode], inter_couplings: List[InterLayerCoupling]) -> int:
    n_modes = len(modes)
    n_memory_terms = 0
    for ic in inter_couplings:
        for kernel in ic.links.values():
            n_memory_terms += len(kernel.taus0)
    return n_modes + n_memory_terms
