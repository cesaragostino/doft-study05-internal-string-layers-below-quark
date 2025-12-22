"""Plotting helpers for Study05 (optional, requires matplotlib)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np


def _try_import_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        return None
    return plt


def plot_spectrum(energies: np.ndarray, output_path: Path, title: str = "Mode spectrum") -> None:
    plt = _try_import_matplotlib()
    if plt is None:
        return
    plt.figure()
    x = np.arange(len(energies))
    plt.stem(x, energies)
    plt.xlabel("Mode index")
    plt.ylabel("Energy (GeV)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_spacing_histogram(spacings: np.ndarray, output_path: Path) -> None:
    plt = _try_import_matplotlib()
    if plt is None:
        return
    plt.figure()
    plt.hist(spacings, bins=40, density=True)
    plt.xlabel("ΔE (GeV)")
    plt.ylabel("Probability density")
    plt.title("Mode spacings")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_layer_heatmap(
    energies: Sequence[float],
    weights: List[Dict[str, float]],
    layers_order: Sequence[str],
    output_path: Path,
    title: str = "Layer weights",
) -> None:
    plt = _try_import_matplotlib()
    if plt is None:
        return
    if len(energies) == 0 or len(weights) == 0:
        return

    mat = np.zeros((len(layers_order), len(energies)))
    for j, w in enumerate(weights):
        for i, layer_name in enumerate(layers_order):
            mat[i, j] = w.get(layer_name, 0.0)

    plt.figure()
    extent = [min(energies), max(energies), -0.5, len(layers_order) - 0.5]
    plt.imshow(mat, aspect="auto", origin="lower", extent=extent, cmap="magma")
    plt.yticks(range(len(layers_order)), layers_order)
    plt.xlabel("Energy (GeV)")
    plt.ylabel("Layer")
    plt.title(title)
    plt.colorbar(label="Weight")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
