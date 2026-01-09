"""Canonical build plan helpers (V1)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from core.ids.hashing import hash_text, stable_dumps
from core.ids.engine_bins import is_engine_params_bin_id, parse_engine_params_bin_id
from core.templates.registry import canonicalize_edges


def canonicalize_plan(
    assignment_ids: List[str],
    edges: List[List[int]],
) -> Tuple[List[str], List[List[int]]]:
    """Return canonical node order (sorted) and remapped edges."""
    indexed = list(enumerate(assignment_ids))
    indexed.sort(key=lambda it: (str(it[1]), it[0]))
    old_to_new = {old_idx: new_idx for new_idx, (old_idx, _) in enumerate(indexed)}
    canonical_nodes = [val for _, val in indexed]

    remapped: List[List[int]] = []
    for e in edges or []:
        if len(e) < 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i == j:
            continue
        if i not in old_to_new or j not in old_to_new:
            continue
        remapped.append([old_to_new[i], old_to_new[j]])
    remapped = canonicalize_edges(remapped)
    return canonical_nodes, remapped


def build_plan_payload(
    ola_level: int,
    template_name: str,
    canonical_node_order: List[str],
    edges: List[List[int]],
    edge_weights_mode: str,
    edge_weight_pattern: Optional[List[float]],
    assignment_block_ids: List[str],
    block_key_used: str = "block_id",
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ola_level": int(ola_level),
        "template_name": template_name,
        "canonical_node_order": canonical_node_order,
        "assignment": {"block_ids": list(assignment_block_ids), "block_key_used": block_key_used},
        "edges": canonicalize_edges(edges),
        "edge_weights_mode": edge_weights_mode,
    }
    if edge_weight_pattern is not None:
        payload["edge_weight_pattern"] = edge_weight_pattern
    return payload


def entity_id_from_plan(payload: Dict[str, Any]) -> str:
    return hash_text(stable_dumps(payload))


def engine_params_bin_id(
    k_local_idx: int,
    kappa_idx: int,
    tau_idx: int,
    sigma0_idx: int,
    sigma_tc_idx: int,
) -> str:
    return f"K{k_local_idx}_k{kappa_idx}_tau{tau_idx}_s0{sigma0_idx}_stc{sigma_tc_idx}"
