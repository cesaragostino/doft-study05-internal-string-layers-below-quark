"""Explorer V4 search/plan layer (DOF-only)."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from core.ids.plan import build_plan_payload, canonicalize_plan, engine_params_bin_id, entity_id_from_plan
from core.templates.registry import canonicalize_edges


def choose_target(cfg: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    targets = cfg.get("targets") or []
    if not targets:
        raise RuntimeError("Explorer config missing targets")
    return rng.choice(targets)


def choose_template(target: Dict[str, Any], templates: Dict[str, Dict[str, Any]], rng: random.Random) -> Dict[str, Any]:
    names = target.get("templates") or []
    if not names:
        raise RuntimeError("Target missing templates list")
    name = rng.choice(names)
    tmpl = templates.get(name)
    if not tmpl:
        raise RuntimeError(f"Template not found: {name}")
    return tmpl


def sample_blocks(pool: List[Dict[str, Any]], n: int, rng: random.Random) -> List[Dict[str, Any]]:
    if n <= 0:
        return []
    if len(pool) < n:
        return []
    return rng.sample(pool, n)


def build_plan(
    ola_level: int,
    template: Dict[str, Any],
    assignment: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], str, List[str], List[List[int]], List[str]]:
    template_name = str(template.get("name", ""))
    nodes = int(template.get("nodes", 0))
    if nodes <= 0:
        raise RuntimeError(f"Invalid template nodes for {template_name}")
    if len(assignment) != nodes:
        raise RuntimeError("Assignment size does not match template nodes")

    assignment_ids = [str(b.get("block_id")) for b in assignment]
    edges = canonicalize_edges(template.get("edges", []))
    edge_weights_mode = template.get("edge_weights_mode", "fixed_template")
    edge_weight_pattern = template.get("edge_weight_pattern")

    canonical_nodes, canonical_edges = canonicalize_plan(assignment_ids, edges)
    canonical_node_order = [str(i) for i in range(len(canonical_nodes))]
    payload = build_plan_payload(
        ola_level,
        template_name,
        canonical_node_order,
        canonical_edges,
        edge_weights_mode,
        edge_weight_pattern,
        canonical_nodes,
    )
    entity_id = entity_id_from_plan(payload)
    return payload, entity_id, canonical_nodes, canonical_edges, canonical_node_order


def choose_engine_params(
    defaults: Dict[str, Any],
    variation_cfg: Dict[str, Any],
    rng: random.Random,
) -> Tuple[Dict[str, float], str]:
    params = {
        "dt": float(defaults.get("dt", 1.0)),
        "T_ticks": int(defaults.get("T_ticks", 200)),
        "W": int(defaults.get("W", 20)),
        "K_local": float(defaults.get("K_local", 0.45)),
        "kappa_global": float(defaults.get("kappa_global", 0.30)),
        "tau_field": float(defaults.get("tau_field", 120.0)),
        "sigma0": float(defaults.get("sigma0", 0.30)),
        "sigma_tc": float(defaults.get("sigma_tc", 60.0)),
        "sigma_theta_init": float(defaults.get("sigma_theta_init", 0.5)),
    }
    if not variation_cfg.get("enabled", False):
        bin_id = engine_params_bin_id(0, 0, 0, 0, 0)
        return params, bin_id
    bins = variation_cfg.get("bins", {})
    edges_map = {
        "K_local": bins.get("K_local_edges", []),
        "kappa_global": bins.get("kappa_edges", []),
        "tau_field": bins.get("tau_field_edges", []),
        "sigma0": bins.get("sigma0_edges", []),
        "sigma_tc": bins.get("sigma_tc_edges", []),
    }
    idxs: Dict[str, int] = {}
    for key, edges in edges_map.items():
        if edges and len(edges) >= 2:
            idx = rng.randrange(0, len(edges) - 1)
            lo, hi = float(edges[idx]), float(edges[idx + 1])
            params[key] = rng.uniform(lo, hi)
            idxs[key] = idx
        else:
            idxs[key] = 0
    bin_id = engine_params_bin_id(
        idxs["K_local"],
        idxs["kappa_global"],
        idxs["tau_field"],
        idxs["sigma0"],
        idxs["sigma_tc"],
    )
    return params, bin_id
