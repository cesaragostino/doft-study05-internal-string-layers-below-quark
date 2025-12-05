"""Layer definitions and mode generation for Study05."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple

import numpy as np

from .config import LOG_FQ_MAX, LOG_FQ_MIN, LOG_R_MAX, LOG_R_MIN, rng_or_default, sample_log_uniform


class Layer(Enum):
    Q = auto()
    S1 = auto()
    S2 = auto()
    S3 = auto()


@dataclass
class Mode:
    layer: Layer
    index: int
    omega0: float  # rad/s
    mass: float
    gamma: float


def sample_base_frequencies(case: str, rng: np.random.Generator | None = None):
    """Sample base frequencies and ratios according to the spec."""
    rng = rng_or_default(rng)

    f_Q = sample_log_uniform(LOG_FQ_MIN, LOG_FQ_MAX, rng)

    def sample_R():
        return 10 ** rng.uniform(LOG_R_MIN, LOG_R_MAX)

    R_S1_Q = sample_R()
    R_S2_S1 = sample_R()

    f_layers: Dict[Layer, float] = {Layer.Q: f_Q}
    f_layers[Layer.S1] = R_S1_Q * f_Q
    f_layers[Layer.S2] = R_S2_S1 * f_layers[Layer.S1]

    R_S3_S2 = None
    if case == "CaseB_3layers":
        R_S3_S2 = sample_R()
        f_layers[Layer.S3] = R_S3_S2 * f_layers[Layer.S2]

    return f_Q, f_layers, R_S1_Q, R_S2_S1, R_S3_S2


def build_string_layer_modes(
    layer: Layer,
    base_freq_hz: float,
    N: int,
    rng: np.random.Generator | None = None,
) -> List[Mode]:
    """Generate modes for a 1D string-like layer."""
    rng = rng_or_default(rng)
    omega_base = 2 * np.pi * base_freq_hz
    modes: List[Mode] = []

    delta_span = 0.05 if layer == Layer.Q else 0.1
    gamma_min = 1e-4 if layer == Layer.Q else 1e-3
    gamma_max = 1e-2 if layer == Layer.Q else 1e-1

    for i in range(N):
        delta = rng.uniform(-delta_span, delta_span)
        omega_i = omega_base * (1.0 + delta)
        gamma_i = omega_base * rng.uniform(gamma_min, gamma_max)
        modes.append(
            Mode(
                layer=layer,
                index=i,
                omega0=float(omega_i),
                mass=1.0,
                gamma=float(gamma_i),
            )
        )
    return modes


def make_index_map(modes: List[Mode]) -> Dict[Tuple[Layer, int], int]:
    return {(m.layer, m.index): idx for idx, m in enumerate(modes)}
