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
# Narrowed ratios to keep layers closer and promote mixing (5–50).
LOG_R_MIN = np.log10(5.0)
LOG_R_MAX = np.log10(50.0)

# Defaults for modes per layer
DEFAULT_N_Q = 4
DEFAULT_N_INTERNAL = 3

# Band window for hadronic spectrum (GeV)
DEFAULT_BAND_MIN = 0.0
# Slightly wider exploration band to find soft modes before focusing down.
DEFAULT_BAND_MAX = 5.0

# Complexity cap (can be tightened via CLI; spec suggests 10, default 12 to allow N choices)
DEFAULT_MAX_COMPLEXITY = 12


def rng_or_default(rng: np.random.Generator | None = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def sample_log_uniform(low: float, high: float, rng: np.random.Generator | None = None) -> float:
    rng = rng_or_default(rng)
    return 10 ** rng.uniform(low, high)
