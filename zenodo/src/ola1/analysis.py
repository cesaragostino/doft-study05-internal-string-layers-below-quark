"""Analysis helpers: energies, bands, spacings, and layer weights."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .config import C_LIGHT, GEV_TO_J, HBAR_GEV_S
from .layers import Layer, Mode


def eigvals_to_energies_gev(eigvals: np.ndarray) -> np.ndarray:
    omegas = np.abs(np.imag(eigvals))
    return HBAR_GEV_S * omegas


def energies_to_masses_kg(energies_gev: np.ndarray) -> np.ndarray:
    energies_joule = np.asarray(energies_gev) * GEV_TO_J
    return energies_joule / (C_LIGHT**2)


def select_band(energies: np.ndarray, e_min: float, e_max: float) -> np.ndarray:
    mask = (energies >= e_min) & (energies <= e_max)
    return np.sort(energies[mask])


def compute_spacings(energies: np.ndarray) -> np.ndarray:
    energies = np.sort(np.asarray(energies))
    if energies.size < 2:
        return np.array([])
    return np.diff(energies)


def summarise_spacings(spacings: np.ndarray) -> Dict[str, float]:
    if spacings.size == 0:
        return {"count": 0, "mean": float("nan"), "std": float("nan")}
    return {
        "count": int(spacings.size),
        "mean": float(np.mean(spacings)),
        "std": float(np.std(spacings)),
    }


def layer_weights(
    eigvecs: np.ndarray, modes: List[Mode], index_map: Dict[Tuple[Layer, int], int]
) -> List[Dict[str, float]]:
    """Compute per-layer weight (x-components) for each eigenvector."""
    N = len(modes)
    weights: List[Dict[str, float]] = []
    layer_indices: Dict[Layer, List[int]] = {}
    for mode in modes:
        layer_indices.setdefault(mode.layer, []).append(index_map[(mode.layer, mode.index)])

    for k in range(eigvecs.shape[1]):
        vec = eigvecs[:N, k]
        power_total = float(np.sum(np.abs(vec) ** 2)) + 1e-15
        weight_dict: Dict[str, float] = {}
        for layer, idxs in layer_indices.items():
            layer_power = float(np.sum(np.abs(vec[idxs]) ** 2))
            weight_dict[layer.name] = layer_power / power_total
        weights.append(weight_dict)
    return weights
