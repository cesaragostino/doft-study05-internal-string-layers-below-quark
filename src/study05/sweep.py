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
    n_s2: int = DEFAULT_N_INTERNAL,
    n_s3: int = DEFAULT_N_INTERNAL,
    max_complexity: int = DEFAULT_MAX_COMPLEXITY,
    attempts: int = 30,
    k_scale_q: float = 0.1,
    k_scale_internal: float = 1.0,
) -> Optional[SimulationConfig]:
    """Generate a configuration satisfying the complexity constraint."""
    rng = rng_or_default(rng)
    case_name = "CaseB_3layers" if case == "CaseB_3layers" else "CaseA_2layers"
    include_s3 = case_name == "CaseB_3layers"

    for _ in range(attempts):
        f_Q, f_layers, R_S1_Q, R_S2_S1, R_S3_S2 = sample_base_frequencies(case_name, rng)

        modes: List[Mode] = []
        intra: List[Coupling] = []
        inter: List[InterLayerCoupling] = []

        modes.extend(build_string_layer_modes(Layer.Q, f_layers[Layer.Q], n_q, rng))
        intra.extend(build_string_couplings(Layer.Q, n_q, k_scale=k_scale_q, rng=rng))

        modes.extend(build_string_layer_modes(Layer.S1, f_layers[Layer.S1], n_s1, rng))
        intra.extend(build_string_couplings(Layer.S1, n_s1, k_scale=k_scale_internal, rng=rng))
        inter.append(
            build_inter_layer_coupling(
                deep_layer=Layer.S1,
                shallow_layer=Layer.Q,
                N_deep=n_s1,
                N_shallow=n_q,
                f_deep=f_layers[Layer.S1],
                rng=rng,
            )
        )

        modes.extend(build_string_layer_modes(Layer.S2, f_layers[Layer.S2], n_s2, rng))
        intra.extend(build_string_couplings(Layer.S2, n_s2, k_scale=k_scale_internal, rng=rng))
        inter.append(
            build_inter_layer_coupling(
                deep_layer=Layer.S2,
                shallow_layer=Layer.S1,
                N_deep=n_s2,
                N_shallow=n_s1,
                f_deep=f_layers[Layer.S2],
                rng=rng,
            )
        )

        if include_s3:
            modes.extend(build_string_layer_modes(Layer.S3, f_layers[Layer.S3], n_s3, rng))
            intra.extend(build_string_couplings(Layer.S3, n_s3, k_scale=k_scale_internal, rng=rng))
            inter.append(
                build_inter_layer_coupling(
                    deep_layer=Layer.S3,
                    shallow_layer=Layer.S2,
                    N_deep=n_s3,
                    N_shallow=n_s2,
                    f_deep=f_layers[Layer.S3],
                    rng=rng,
                )
            )

        complexity = compute_complexity(modes, inter)
        if complexity > max_complexity:
            continue

        memory_terms = count_memory_terms(inter)
        return SimulationConfig(
            case_name=case_name,
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
        )
    return None


def state_matrix_from_config(config: SimulationConfig):
    return build_state_matrix(
        modes=config.modes,
        intra_couplings=config.intra_layer_couplings,
        inter_couplings=config.inter_layer_couplings,
    )
