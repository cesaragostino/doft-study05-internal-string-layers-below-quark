"""Global parameters and constants for Study05 v0.1."""

from __future__ import annotations

import numpy as np

# Physical constants (kept for conversions if needed)
HBAR_EV_S = 6.582_119_569e-16
HBAR_GEV_S = HBAR_EV_S * 1e-9
C_LIGHT = 299_792_458.0
GEV_TO_J = 1.602_176_634e-10

# Dimensionless base frequency for Q
OMEGA_Q_BASE = 1.0

# Ratios (dimensionless) ~ 2..10 to keep layers closer and promote mixing
LOG_R_MIN = 0.3  # log10(2)
LOG_R_MAX = 1.0  # log10(10)

# Defaults for modes per layer
DEFAULT_N_Q = 3
DEFAULT_N_INTERNAL = 3

# Band window for hadronic spectrum (GeV)
DEFAULT_BAND_MIN = 0.0
# Wider exploration band to find soft modes before focusing down.
DEFAULT_BAND_MAX = 5.0

# Complexity cap (spec: 10)
DEFAULT_MAX_COMPLEXITY = 10


def rng_or_default(rng: np.random.Generator | None = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def sample_log_uniform(low: float, high: float, rng: np.random.Generator | None = None) -> float:
    rng = rng_or_default(rng)
    return 10 ** rng.uniform(low, high)
