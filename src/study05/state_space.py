"""State-space construction including memory auxiliaries."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .couplings import Coupling, InterLayerCoupling
from .layers import Layer, Mode, make_index_map


def count_memory_terms(inter_couplings: List[InterLayerCoupling]) -> int:
    """Count auxiliary z variables (per link per exponential)."""
    total = 0
    for ic in inter_couplings:
        n_links = len(ic.coupling_matrix)
        total += n_links * len(ic.memory_kernel.taus)
    return total


def build_state_matrix(
    modes: List[Mode],
    intra_couplings: List[Coupling],
    inter_couplings: List[InterLayerCoupling],
) -> Tuple[np.ndarray, Dict[Tuple[Layer, int], int], int]:
    """Construct the first-order state matrix A including memory auxiliaries."""
    index_map = make_index_map(modes)
    N = len(modes)
    n_z = count_memory_terms(inter_couplings)
    dim = 2 * N + n_z
    A = np.zeros((dim, dim))

    # dx/dt = v
    for i in range(N):
        A[i, N + i] = 1.0

    # dv/dt base terms: -omega^2 x / m
    for m in modes:
        idx_x = index_map[(m.layer, m.index)]
        idx_v = N + idx_x
        A[idx_v, idx_x] -= (m.omega0**2) / m.mass

    # Intra-layer springs (1D chain, symmetric)
    for c in intra_couplings:
        i = index_map[c.i]
        j = index_map[c.j]
        k = c.k_ij

        mi = modes[i].mass
        mj = modes[j].mass

        A[N + i, i] -= k / mi
        A[N + i, j] += k / mi

        A[N + j, j] -= k / mj
        A[N + j, i] += k / mj

    # Inter-layer memory: each (link, tau) creates one z variable
    z_idx = 2 * N
    for ic in inter_couplings:
        deep = ic.deep_layer
        shallow = ic.shallow_layer
        taus = ic.memory_kernel.taus
        amps = ic.memory_kernel.amps

        for (i_deep, j_sh), strength in ic.coupling_matrix.items():
            idx_deep = index_map[(deep, i_deep)]
            idx_sh_x = index_map[(shallow, j_sh)]
            idx_sh_v = N + idx_sh_x
            m_sh = modes[idx_sh_x].mass

            for tau_a, A_a in zip(taus, amps):
                idx_z = z_idx
                z_idx += 1

                # z_dot = -z / tau + strength * x_deep
                A[idx_z, idx_z] = -1.0 / tau_a
                A[idx_z, idx_deep] = strength

                # dv_sh/dt += strength * A_a * z / m_sh
                A[idx_sh_v, idx_z] += strength * A_a / m_sh

    return A, index_map, n_z


def eigen_spectrum(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute eigenvalues and right eigenvectors of the state matrix."""
    eigvals, eigvecs = np.linalg.eig(A)
    return eigvals, eigvecs
