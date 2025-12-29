"""Engine bin helpers (V1)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

_BIN_ID_RE = re.compile(r"^K(\d+)_k(\d+)_tau(\d+)_s0(\d+)_stc(\d+)$")


def is_engine_params_bin_id(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return bool(_BIN_ID_RE.match(value))


def parse_engine_params_bin_id(value: str) -> Tuple[int, int, int, int, int]:
    if not isinstance(value, str):
        raise ValueError("engine_params_bin_id must be a string")
    match = _BIN_ID_RE.match(value)
    if not match:
        raise ValueError(f"Invalid engine_params_bin_id: {value!r}")
    return tuple(int(g) for g in match.groups())


def make_engine_params_bin_id(
    k_local_idx: int,
    kappa_idx: int,
    tau_idx: int,
    sigma0_idx: int,
    sigma_tc_idx: int,
) -> str:
    return f"K{k_local_idx}_k{kappa_idx}_tau{tau_idx}_s0{sigma0_idx}_stc{sigma_tc_idx}"


def _bin_midpoint(edges: List[float], idx: int, label: str) -> float:
    if not edges or len(edges) < 2:
        raise RuntimeError(f"Missing bin edges for {label}")
    if idx < 0 or idx >= len(edges) - 1:
        raise RuntimeError(f"Bin index out of range for {label}: {idx}")
    lo, hi = float(edges[idx]), float(edges[idx + 1])
    return (lo + hi) / 2.0


def _resolve_param(
    defaults: Dict[str, Any],
    bins: Dict[str, Any],
    edges_key: str,
    idx: int,
    default_key: str,
) -> float:
    edges = bins.get(edges_key)
    if not isinstance(edges, list) or len(edges) < 2:
        return float(defaults.get(default_key, 0.0))
    return _bin_midpoint(edges, idx, edges_key)


def resolve_engine_params(
    defaults: Dict[str, Any],
    bins: Dict[str, Any],
    engine_params_bin_id: str,
) -> Dict[str, Any]:
    k_local_idx, kappa_idx, tau_idx, sigma0_idx, sigma_tc_idx = parse_engine_params_bin_id(
        engine_params_bin_id
    )
    params = {
        "dt": float(defaults.get("dt", 1.0)),
        "T_ticks": int(defaults.get("T_ticks", 200)),
        "W": int(defaults.get("W", 20)),
        "K_local": _resolve_param(defaults, bins, "K_local_edges", k_local_idx, "K_local"),
        "kappa_global": _resolve_param(defaults, bins, "kappa_edges", kappa_idx, "kappa_global"),
        "tau_field": _resolve_param(defaults, bins, "tau_field_edges", tau_idx, "tau_field"),
        "sigma0": _resolve_param(defaults, bins, "sigma0_edges", sigma0_idx, "sigma0"),
        "sigma_tc": _resolve_param(defaults, bins, "sigma_tc_edges", sigma_tc_idx, "sigma_tc"),
        "sigma_theta_init": float(defaults.get("sigma_theta_init", 0.5)),
    }
    return params


def neighbor_engine_params_bin_ids(
    base_bin_id: str,
    bins: Dict[str, Any],
    max_neighbor_bins: int,
) -> List[str]:
    if int(max_neighbor_bins) <= 0:
        return [base_bin_id]
    k_local_idx, kappa_idx, tau_idx, sigma0_idx, sigma_tc_idx = parse_engine_params_bin_id(base_bin_id)
    counts = (
        max(len(bins.get("K_local_edges", [])) - 1, 0),
        max(len(bins.get("kappa_edges", [])) - 1, 0),
        max(len(bins.get("tau_field_edges", [])) - 1, 0),
        max(len(bins.get("sigma0_edges", [])) - 1, 0),
        max(len(bins.get("sigma_tc_edges", [])) - 1, 0),
    )
    base = (k_local_idx, kappa_idx, tau_idx, sigma0_idx, sigma_tc_idx)
    neighbors: List[Tuple[int, Tuple[int, int, int, int, int]]] = []
    max_d = max(0, int(max_neighbor_bins))
    for d0 in range(-max_d, max_d + 1):
        for d1 in range(-max_d, max_d + 1):
            for d2 in range(-max_d, max_d + 1):
                for d3 in range(-max_d, max_d + 1):
                    for d4 in range(-max_d, max_d + 1):
                        dist = abs(d0) + abs(d1) + abs(d2) + abs(d3) + abs(d4)
                        if dist > max_d:
                            continue
                        idxs = (
                            base[0] + d0,
                            base[1] + d1,
                            base[2] + d2,
                            base[3] + d3,
                            base[4] + d4,
                        )
                        in_range = True
                        for val, count in zip(idxs, counts):
                            if val < 0 or val >= count:
                                in_range = False
                                break
                        if not in_range:
                            continue
                        neighbors.append((dist, idxs))
    neighbors.sort(key=lambda item: (item[0], item[1]))
    return [
        make_engine_params_bin_id(*idxs)
        for _, idxs in neighbors
    ]
