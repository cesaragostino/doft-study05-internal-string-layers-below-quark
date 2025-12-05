"""Global parameters and constants for Study05 v0.1."""

from __future__ import annotations

import numpy as np

# Physical constants
HBAR_EV_S = 6.582_119_569e-16
HBAR_GEV_S = HBAR_EV_S * 1e-9
C_LIGHT = 299_792_458.0
GEV_TO_J = 1.602_176_634e-10

# Frequency ranges
LOG_FQ_MIN = 23.0
LOG_FQ_MAX = 24.0
LOG_R_MIN = 2.0  # log10(1e2)
LOG_R_MAX = 4.0  # log10(1e4)

# Defaults for modes per layer
DEFAULT_N_Q = 4
DEFAULT_N_INTERNAL = 3

# Band window for hadronic spectrum (GeV)
DEFAULT_BAND_MIN = 0.0
DEFAULT_BAND_MAX = 3.0

# Complexity cap (can be tightened via CLI; spec suggests 10, default 12 to allow N choices)
DEFAULT_MAX_COMPLEXITY = 12


def rng_or_default(rng: np.random.Generator | None = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def sample_log_uniform(low: float, high: float, rng: np.random.Generator | None = None) -> float:
    rng = rng_or_default(rng)
    return 10 ** rng.uniform(low, high)
