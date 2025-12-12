"""Sampling utilities for Study05 sweeps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from .config import DEFAULT_MAX_COMPLEXITY, DEFAULT_N_INTERNAL, DEFAULT_N_Q, rng_or_default
from .couplings import Coupling, InterLayerCoupling, compute_complexity
from .couplings import build_inter_layer_coupling, build_string_couplings
from .layers import Layer, Mode, build_string_layer_modes, sample_base_frequencies
from .state_space import build_state_matrix, count_memory_terms


@dataclass
class SimulationConfig:
    case_name: str
    f_Q: float
    R_S1_Q: float
    R_S2_S1: float
    R_S3_S2: Optional[float]
    N_Q: int
    N_S1: int
    N_S2: int
    N_S3: int
    modes: List[Mode]
    intra_layer_couplings: List[Coupling]
    inter_layer_couplings: List[InterLayerCoupling]
    complexity: int
    memory_terms: int


def generate_configuration(
    case: str,
    rng: np.random.Generator | None = None,
    n_q: int = DEFAULT_N_Q,
    n_s1: int = DEFAULT_N_INTERNAL,
    n_s2: int = 2,
    n_s3: int = 0,
    max_complexity: int = DEFAULT_MAX_COMPLEXITY,
    attempts: int = 30,
    k_scale_q: float | None = None,
    k_scale_internal: float | None = None,
    priors=None,
) -> tuple[Optional[SimulationConfig], Dict[str, int]]:
    """Generate a configuration satisfying the complexity constraint.

    Returns (config, meta) where meta contains the last sampled complexity breakdown.
    """
    rng = rng_or_default(rng)
    include_s3 = n_s3 > 0
    case_name = case
    meta = {"last_complexity": None, "last_memory_terms": None, "last_n_modes": None}

    for _ in range(attempts):
        ratio_overrides = None
        if priors:
            ratio_overrides = {
                "R_S1_Q_range": priors.R_S1_Q_range,
                "R_S2_S1_range": priors.R_S2_S1_range,
            }
            if priors.suggested_N:
                n_q = priors.suggested_N.get("Q", n_q)
                n_s1 = priors.suggested_N.get("S1", n_s1)
                n_s2 = priors.suggested_N.get("S2", n_s2)
                n_s3 = priors.suggested_N.get("S3", n_s3)
        f_Q, f_layers, R_S1_Q, R_S2_S1, R_S3_S2 = sample_base_frequencies(case_name, rng, ratio_overrides=ratio_overrides)

        modes: List[Mode] = []
        intra: List[Coupling] = []
        inter: List[InterLayerCoupling] = []

        modes.extend(
            build_string_layer_modes(
                Layer.Q,
                f_layers[Layer.Q],
                n_q,
                rng,
                damping_range=None,
            )
        )
        kq = k_scale_q if k_scale_q is not None else 0.2 * (f_layers[Layer.Q] ** 2)
        intra.extend(build_string_couplings(Layer.Q, n_q, k_scale=kq, rng=rng))

        modes.extend(
            build_string_layer_modes(
                Layer.S1,
                f_layers[Layer.S1],
                n_s1,
                rng,
                damping_range=None,
            )
        )
        g0_range_qs1 = None
        if priors:
            g0_range_qs1 = priors.g_QS1_scale_range

        k1 = k_scale_internal if k_scale_internal is not None else 0.5 * (f_layers[Layer.S1] ** 2)
        intra.extend(build_string_couplings(Layer.S1, n_s1, k_scale=k1, rng=rng))
        mem_override_qs1 = None
        if priors:
            mem_override_qs1 = mem_override_qs1 or {
                "terms": [
                    {"tau_range": (0.2, 0.8), "amp_range": priors.memory_strength_range},
                ]
            }
        inter.append(
            build_inter_layer_coupling(
                deep_layer=Layer.S1,
                shallow_layer=Layer.Q,
                N_deep=n_s1,
                N_shallow=n_q,
                omega_deep_base=f_layers[Layer.S1],
                rng=rng,
                g0_range=g0_range_qs1,
                memory_override=mem_override_qs1,
            )
        )

        modes.extend(
            build_string_layer_modes(
                Layer.S2,
                f_layers[Layer.S2],
                n_s2,
                rng,
                damping_range=None,
            )
        )
        g0_range_s2s1 = None
        if priors:
            g0_range_s2s1 = priors.g_S1S2_scale_range

        k2 = k_scale_internal if k_scale_internal is not None else 0.5 * (f_layers[Layer.S2] ** 2)
        intra.extend(build_string_couplings(Layer.S2, n_s2, k_scale=k2, rng=rng))
        mem_override_s2s1 = None
        if priors:
            mem_override_s2s1 = mem_override_s2s1 or {
                "terms": [
                    {"tau_range": (0.1, 0.5), "amp_range": priors.memory_strength_range},
                    {"tau_range": (1.0, 3.0), "amp_range": priors.memory_strength_range},
                ]
            }
        inter.append(
            build_inter_layer_coupling(
                deep_layer=Layer.S2,
                shallow_layer=Layer.S1,
                N_deep=n_s2,
                N_shallow=n_s1,
                omega_deep_base=f_layers[Layer.S2],
                rng=rng,
                g0_range=g0_range_s2s1,
                memory_override=mem_override_s2s1,
            )
        )

        if include_s3:
            modes.extend(build_string_layer_modes(Layer.S3, f_layers[Layer.S3], n_s3, rng))
            k3 = k_scale_internal if k_scale_internal is not None else 0.5 * (f_layers[Layer.S3] ** 2)
            intra.extend(build_string_couplings(Layer.S3, n_s3, k_scale=k3, rng=rng))
            inter.append(
                build_inter_layer_coupling(
                    deep_layer=Layer.S3,
                    shallow_layer=Layer.S2,
                    N_deep=n_s3,
                    N_shallow=n_s2,
                    omega_deep_base=f_layers[Layer.S3],
                    rng=rng,
                )
            )

        complexity = compute_complexity(modes, inter)
        memory_terms = count_memory_terms(inter)
        meta.update({"last_complexity": complexity, "last_memory_terms": memory_terms, "last_n_modes": len(modes)})
        if max_complexity > 0 and complexity > max_complexity:
            continue

        return SimulationConfig(
            case_name=case,
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
            memory_terms=memory_terms,
        ), meta
    return None, meta

def state_matrix_from_config(config: SimulationConfig):
    return build_state_matrix(
        modes=config.modes,
        intra_couplings=config.intra_layer_couplings,
        inter_couplings=config.inter_layer_couplings,
    )
