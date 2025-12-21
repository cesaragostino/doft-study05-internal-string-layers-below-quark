"""Structure Explorer v2 (Ola2) - structure discovery with Kuramoto + memory.

Implements the v2 spec: two-phase search, canonicalization, memory store,
and JSONL outputs with progress terms.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
import uuid
import platform
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from study06.run_ola2_compounds import _load_blocks as _load_blocks_wave1

# Import simulator from scripts/ (repo root)
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR.parent) not in __import__("sys").path:
    __import__("sys").path.append(str(SCRIPTS_DIR.parent))
from scripts.ola2_reloaded_sim import simulate_ola2  # type: ignore


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _extract_blocks(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        # Prefer explicit block list keys; ignore legacy compounds unless warm-start.
        for key in ("blocks", "promoted_blocks"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        results = raw.get("results")
        if isinstance(results, dict) and isinstance(results.get("blocks"), list):
            return results["blocks"]
    return []


def _is_finite(val: Any) -> bool:
    try:
        return math.isfinite(float(val))
    except Exception:
        return False


def _pick_omega(block: Dict[str, Any]) -> float:
    for key in ("omega_ref", "M_spec", "f_ref", "mass_sim_gev"):
        val = block.get(key)
        if _is_finite(val):
            return float(val)
    return 1.0


def _pick_mass(block: Dict[str, Any]) -> float:
    for key in ("mass_sim_gev", "omega_ref", "M_spec", "f_ref"):
        val = block.get(key)
        if _is_finite(val):
            return float(val)
    return 1.0


def _lock_entropy(lock_q: Dict[str, Any]) -> float:
    def _to_float(val):
        try:
            return float(val)
        except Exception:
            return 0.0
    q = max(_to_float(lock_q.get("Q", 0.0)), 0.0)
    s1 = max(_to_float(lock_q.get("S1", 0.0)), 0.0)
    s2 = max(_to_float(lock_q.get("S2", 0.0)), 0.0)
    s = q + s1 + s2
    if s <= 1e-12:
        return math.log(3) / math.log(3)
    p = [q / s, s1 / s, s2 / s]
    return float(-sum(pi * math.log(pi + 1e-12) for pi in p) / math.log(3))


def _sample_blocks(
    pool: List[Dict[str, Any]],
    families: Sequence[str],
    allowed_particle_names: Optional[Sequence[str]],
    k: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    fam_lower = {f.lower() for f in families} if families else set()
    allowed_names = {n.lower() for n in allowed_particle_names} if allowed_particle_names else None
    if "match_any" in fam_lower:
        filtered = list(pool)
    else:
        filtered = [b for b in pool if (not fam_lower or str(b.get("family", "")).lower() in fam_lower)]
    if allowed_names is not None:
        filtered = [b for b in filtered if str(b.get("particle_name", "")).lower() in allowed_names]
    if len(filtered) < k:
        return []
    weights = []
    for b in filtered:
        d = b.get("match_score", {}).get("d_total")
        try:
            d = float(d)
        except Exception:
            d = math.inf
        w = 1.0 / (1.0 + d) if math.isfinite(d) else 0.1
        weights.append(max(w, 1e-3))
    return rng.choices(filtered, weights=weights, k=k)


def _edge_set(edges: Sequence[Sequence[int]]) -> set[Tuple[int, int]]:
    out = set()
    for e in edges:
        if len(e) < 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i == j:
            continue
        out.add((min(i, j), max(i, j)))
    return out


def _automorphisms(nodes: int, edges: Sequence[Sequence[int]]) -> List[Tuple[int, ...]]:
    edges_set = _edge_set(edges)
    perms: List[Tuple[int, ...]] = []
    for perm in permutations(range(nodes)):
        ok = True
        for i in range(nodes):
            for j in range(i + 1, nodes):
                has_edge = (min(i, j), max(i, j)) in edges_set
                mapped = (min(perm[i], perm[j]), max(perm[i], perm[j])) in edges_set
                if has_edge != mapped:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            perms.append(perm)
    return perms


def _fmt_weight(val: float) -> str:
    return f"{float(val):.6g}"


def _canonicalize_assignment(
    template_name: str,
    edges: Sequence[Sequence[int]],
    assignment_keys: List[str],
    edge_weight_pattern: Optional[List[float]],
    perms: List[Tuple[int, ...]],
) -> Tuple[str, List[str], Optional[List[float]]]:
    edge_weight_map = {}
    if edge_weight_pattern is not None:
        for e, w in zip(edges, edge_weight_pattern):
            if len(e) < 2:
                continue
            i, j = int(e[0]), int(e[1])
            edge_weight_map[(min(i, j), max(i, j))] = float(w)
    best_serial = None
    best_assign: List[str] = assignment_keys
    best_weights: Optional[List[float]] = edge_weight_pattern
    for perm in perms:
        perm_assign = [assignment_keys[perm[i]] for i in range(len(assignment_keys))]
        perm_weights = None
        if edge_weight_pattern is not None:
            perm_weights = []
            for e in edges:
                i, j = int(e[0]), int(e[1])
                key = (min(perm[i], perm[j]), max(perm[i], perm[j]))
                perm_weights.append(edge_weight_map.get(key, 1.0))
        parts = [template_name, ",".join(perm_assign)]
        if perm_weights is not None:
            parts.append(",".join(_fmt_weight(w) for w in perm_weights))
        serial = "|".join(parts)
        if best_serial is None or serial < best_serial:
            best_serial = serial
            best_assign = perm_assign
            best_weights = perm_weights
    if best_serial is None:
        best_serial = f"{template_name}|{','.join(assignment_keys)}"
    return best_serial, best_assign, best_weights


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bin_index(val: float, edges: List[float]) -> int:
    if not edges or len(edges) < 2 or not _is_finite(val):
        return 0
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if i == len(edges) - 2:
            if lo <= val <= hi:
                return i
        if lo <= val < hi:
            return i
    return max(len(edges) - 2, 0)


def _param_bin_id(params: Dict[str, float], bins: Dict[str, List[float]]) -> str:
    idx_k = _bin_index(params["K_local"], bins.get("K_local_edges", []))
    idx_kappa = _bin_index(params["kappa_global"], bins.get("kappa_edges", []))
    idx_tau = _bin_index(params["tau_field"], bins.get("tau_field_edges", []))
    idx_s0 = _bin_index(params["sigma0"], bins.get("sigma0_edges", []))
    idx_stc = _bin_index(params["sigma_tc"], bins.get("sigma_tc_edges", []))
    return f"K{idx_k}_k{idx_kappa}_tau{idx_tau}_s0{idx_s0}_stc{idx_stc}"


def _sample_param_from_edges(edges: List[float], rng: random.Random, fallback: float) -> float:
    if not edges or len(edges) < 2:
        return float(fallback)
    idx = rng.randrange(0, len(edges) - 1)
    lo, hi = float(edges[idx]), float(edges[idx + 1])
    return rng.uniform(lo, hi)


def _sample_params(
    defaults: Dict[str, float],
    variation_cfg: Dict[str, Any],
    rng: random.Random,
    neighbor_bins: Optional[Dict[str, int]] = None,
    base_bins: Optional[Dict[str, int]] = None,
) -> Tuple[Dict[str, float], str]:
    params = dict(defaults)
    if not variation_cfg.get("enabled", False):
        return params, "fixed"
    bins = variation_cfg.get("bins", {})
    edges_map = {
        "K_local": bins.get("K_local_edges", []),
        "kappa_global": bins.get("kappa_edges", []),
        "tau_field": bins.get("tau_field_edges", []),
        "sigma0": bins.get("sigma0_edges", []),
        "sigma_tc": bins.get("sigma_tc_edges", []),
    }
    for key, edges in edges_map.items():
        if neighbor_bins and base_bins and key in base_bins and edges and len(edges) >= 2:
            max_idx = len(edges) - 2
            base_idx = base_bins[key]
            span = neighbor_bins.get(key, 0)
            lo_idx = max(0, base_idx - span)
            hi_idx = min(max_idx, base_idx + span)
            idx = rng.randint(lo_idx, hi_idx)
            lo, hi = float(edges[idx]), float(edges[idx + 1])
            params[key] = rng.uniform(lo, hi)
        else:
            params[key] = _sample_param_from_edges(edges, rng, params[key])
    bin_id = _param_bin_id(params, bins)
    return params, bin_id


def _best_score(metrics: Dict[str, Any]) -> float:
    r = metrics.get("R_mean_lastW")
    pv = metrics.get("phase_var_lastW")
    mem = metrics.get("memory_score_k10")
    if not _is_finite(r) or not _is_finite(pv):
        return -1e9
    mem_val = float(mem) if _is_finite(mem) else 0.0
    return float(r) - 3.0 * float(pv) + 0.2 * mem_val


def run_structure_explorer(config_path: Path, output_dir: Path, seed: Optional[int]) -> None:
    started_utc = _utc_now()
    cfg = _load_json(config_path)
    rng = random.Random(seed)
    run_id = cfg.get("run_id") or str(uuid.uuid4())

    inputs = cfg.get("inputs", {})
    blocks_path = Path(inputs.get("blocks_json", "data/processed/ola1/simple_blocks.json"))
    templates_path = Path(inputs.get("templates_json", "data/raw/compound_templates.json"))
    config_hash = f"sha256:{hashlib.sha256(config_path.read_bytes()).hexdigest()}"
    wave1_input_file_hash = f"sha256:{hashlib.sha256(blocks_path.read_bytes()).hexdigest()}"

    raw_blocks = _load_blocks_wave1(blocks_path)
    blocks = _extract_blocks(raw_blocks)
    if not blocks:
        raise RuntimeError(f"No blocks found in {blocks_path}")
    block_map = {b.get("block_id"): b for b in blocks if b.get("block_id")}

    templates_list = _load_json(templates_path)
    templates = {t["name"]: t for t in templates_list}

    engine_defaults = cfg.get("engine_defaults", {})
    defaults = {
        "dt": float(engine_defaults.get("dt", 1.0)),
        "T_ticks": int(engine_defaults.get("T_ticks", 120)),
        "W": int(engine_defaults.get("W", 20)),
        "K_local": float(engine_defaults.get("K_local", 0.15)),
        "kappa_global": float(engine_defaults.get("kappa_global", 0.25)),
        "tau_field": float(engine_defaults.get("tau_field", 20)),
        "sigma0": float(engine_defaults.get("sigma0", 0.30)),
        "sigma_tc": float(engine_defaults.get("sigma_tc", 60)),
        "sigma_theta_init": float(engine_defaults.get("sigma_theta_init", 0.5)),
    }
    variation_cfg = cfg.get("engine_variation", {})

    templates_cfg = cfg.get("templates", {})
    edge_weight_policy = templates_cfg.get("edge_weight_policy", "fixed_template")
    edge_weight_levels = templates_cfg.get("edge_weight_levels", [1.0])

    tagging = cfg.get("tagging", {})
    r_min = float(tagging.get("R_mean_lastW_min", 0.85))
    pv_max = float(tagging.get("phase_var_lastW_max", 0.02))
    mem_min = float(tagging.get("memory_score_k10_min", 0.0))

    search_policy = cfg.get("search_policy", {})
    phase1_fraction = float(search_policy.get("phase1_fraction", 0.7))
    phase2_fraction = float(search_policy.get("phase2_fraction", 0.3))
    phase1_cfg = search_policy.get("phase1", {})
    phase2_cfg = search_policy.get("phase2", {})
    template_balance = phase1_cfg.get("template_balance", "round_robin")
    max_repeats_per_structure = int(phase1_cfg.get("max_repeats_per_structure", 1))

    export_cfg = cfg.get("export", {})
    min_seed_stability = float(export_cfg.get("min_seed_stability_for_export", 0.5))
    min_viable_hits = int(export_cfg.get("min_viable_hits_for_export", 1))
    export_promising_nonviable = bool(export_cfg.get("export_promising_nonviable", False))
    r_promising_min = float(export_cfg.get("R_promising_min", 0.80))
    pv_promising_max = float(export_cfg.get("phase_var_promising_max", 0.03))

    outputs = cfg.get("outputs", {})
    accepted_path = output_dir / outputs.get("accepted_jsonl", "accepted.jsonl")
    rejected_path = output_dir / outputs.get("rejected_jsonl", "rejected.jsonl")
    structures_config_path = output_dir / outputs.get("structures_config_json", "structures_config.json")
    structures_cards_path = output_dir / outputs.get("structures_cards_json", "explorer/structures_cards.json")
    report_path = output_dir / outputs.get("report_md", "report.md")
    progress_path = output_dir / outputs.get("progress_terms_jsonl", "progress_terms.jsonl")

    progress_cfg = cfg.get("progress", {})
    term_attempts = int(progress_cfg.get("term_attempts", 500))
    term_seconds = int(progress_cfg.get("term_seconds", 10))

    memory_cfg = cfg.get("memory_store", {})
    memory_enabled = bool(memory_cfg.get("enabled", True))
    memory_path = output_dir / memory_cfg.get("path", "explorer_memory/memory_store.jsonl")

    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    automorphisms_cache: Dict[str, List[Tuple[int, ...]]] = {}

    attempt_id = 0
    term_index = 0
    term_start = time.time()
    term_attempts_count = 0
    term_template_counts: Dict[str, int] = {}
    term_viable = 0
    total_viable = 0
    total_attempts = 0
    unique_structures: set[str] = set()

    per_template_counts: Dict[str, int] = {}
    per_template_viable: Dict[str, int] = {}
    per_target_counts: Dict[str, int] = {}
    per_target_viable: Dict[str, int] = {}
    per_phase_counts: Dict[str, int] = {"phase1": 0, "phase2": 0}
    per_phase_viable: Dict[str, int] = {"phase1": 0, "phase2": 0}

    structure_stats: Dict[str, Dict[str, Any]] = {}
    memory_store: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def write_term_progress(best_struct: Optional[Dict[str, Any]]) -> None:
        nonlocal term_index, term_start, term_attempts_count, term_template_counts, term_viable
        if term_attempts_count == 0:
            return
        term_index += 1
        elapsed = time.time() - term_start
        viable_rate = (total_viable / total_attempts) if total_attempts else 0.0
        best_summary = None
        if best_struct:
            best_summary = {
                "structure_id": best_struct.get("structure_id"),
                "R_mean_lastW": best_struct.get("best_metrics", {}).get("R_mean_lastW"),
                "phase_var_lastW": best_struct.get("best_metrics", {}).get("phase_var_lastW"),
                "memory_score_k10": best_struct.get("best_metrics", {}).get("memory_score_k10"),
            }
        line = (
            f"term={term_index} evals={term_attempts_count} total={total_attempts} "
            f"viable={viable_rate:.2%} unique={len(unique_structures)} best={best_summary}"
        )
        print(line)
        entry = {
            "run_id": run_id,
            "term": term_index,
            "term_attempts": term_attempts_count,
            "term_viable": term_viable,
            "cumulative_attempts": total_attempts,
            "cumulative_viable": total_viable,
            "cumulative_viable_rate": viable_rate,
            "unique_structures": len(unique_structures),
            "template_breakdown": term_template_counts,
            "best_structure": best_summary,
            "elapsed_seconds": elapsed,
            "timestamp_utc": _utc_now(),
        }
        with progress_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        cards = _build_structure_cards(structure_stats, export_cfg, mem_min)
        structures_cards_path.parent.mkdir(parents=True, exist_ok=True)
        structures_cards_path.write_text(json.dumps(cards, indent=2))
        report_path.write_text(
            _render_report(
                "Progress",
                structure_stats,
                per_template_counts,
                per_template_viable,
                per_target_counts,
                per_target_viable,
                per_phase_counts,
                per_phase_viable,
                cards,
            )
        )
        term_start = time.time()
        term_attempts_count = 0
        term_template_counts = {}
        term_viable = 0

    def update_memory_store(
        structure_id: str,
        param_bin_id: str,
        target: str,
        template_name: str,
        attempt_seed: int,
        metrics: Dict[str, Any],
        engine_params: Dict[str, Any],
        viable: bool,
    ) -> None:
        if not memory_enabled:
            return
        key = (structure_id, param_bin_id)
        entry = memory_store.get(
            key,
            {
                "structure_id": structure_id,
                "parameter_bin_id": param_bin_id,
                "target": target,
                "template": template_name,
                "n_trials": 0,
                "n_viable": 0,
                "seed_stability": 0.0,
                "best": None,
            },
        )
        entry["n_trials"] += 1
        if viable:
            entry["n_viable"] += 1
        entry["seed_stability"] = entry["n_viable"] / max(entry["n_trials"], 1)
        best = entry.get("best")
        if best is None or _best_score(metrics) > _best_score(best):
            entry["best"] = {
                "R_mean_lastW": metrics.get("R_mean_lastW"),
                "phase_var_lastW": metrics.get("phase_var_lastW"),
                "memory_score_k10": metrics.get("memory_score_k10"),
                "seed": attempt_seed,
                "engine_params": engine_params,
            }
        entry["updated_utc"] = _utc_now()
        memory_store[key] = entry
        with memory_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def update_structure_stats(
        structure_id: str,
        template_name: str,
        target: str,
        assignment_keys: List[str],
        edge_weights: Optional[List[float]],
        metrics: Dict[str, Any],
        engine_params: Dict[str, Any],
        param_bin_id: str,
        viable: bool,
        block_key_used: str,
        block_key_used_per_node: List[str],
        blocks_used: List[Dict[str, Any]],
    ) -> None:
        entry = structure_stats.get(
            structure_id,
            {
                "structure_id": structure_id,
                "template_name": template_name,
                "target": target,
                "assignment": assignment_keys,
                "edge_weights": edge_weights,
                "block_key_used": block_key_used,
                "block_key_used_per_node": block_key_used_per_node,
                "n_trials": 0,
                "n_viable": 0,
                "best_metrics": None,
                "best_params": None,
                "best_param_bin_id": None,
                "assignment_block_ids": [b.get("block_id") for b in blocks_used],
                "assignment_particle_names": [b.get("particle_name") for b in blocks_used],
                "assignment_families": [b.get("family") for b in blocks_used],
                "_blocks": blocks_used,
            },
        )
        entry["n_trials"] += 1
        if viable:
            entry["n_viable"] += 1
        if entry.get("best_metrics") is None or _best_score(metrics) > _best_score(entry["best_metrics"]):
            entry["best_metrics"] = metrics
            entry["best_params"] = engine_params
            entry["best_param_bin_id"] = param_bin_id
        structure_stats[structure_id] = entry

    def build_record(
        target_name: str,
        template_name: str,
        attempt_seed: int,
        attempt_index: int,
        target_index: int,
        target_attempt_index: int,
        assignment: List[Dict[str, Any]],
        assignment_keys: List[str],
        block_key_used: str,
        block_key_used_per_node: List[str],
        structure_id: str,
        canonical_assignment: List[str],
        canonical_edge_weights: Optional[List[float]],
        param_bin_id: str,
        engine_params: Dict[str, Any],
        metrics: Dict[str, Any],
        tags: Dict[str, Any],
        reasons: List[str],
        edge_weights: Optional[List[float]],
        template_edges: List[List[int]],
        phase: str,
    ) -> Dict[str, Any]:
        edge_weights_mode = "fixed_template" if edge_weight_policy == "fixed_template" else "sampled"
        return {
            "run_id": run_id,
            "attempt_id": attempt_index,
            "timestamp_utc": _utc_now(),
            "seed": attempt_seed,
            "target": target_name,
            "target_index": target_index,
            "target_attempt_index": target_attempt_index,
            "template": {
                "name": template_name,
                "edges": template_edges,
                "edge_weights_mode": edge_weights_mode,
            },
            "assignment": {
                "block_ids": [b.get("block_id") for b in assignment],
                "particle_names": [b.get("particle_name") for b in assignment],
                "families": [b.get("family") for b in assignment],
                "block_keys": assignment_keys,
            },
            "canonicalization": {
                "structure_id": structure_id,
                "canonical_assignment": canonical_assignment,
                "canonical_edge_weights": canonical_edge_weights,
                "block_key_used": block_key_used,
                "block_key_used_per_node": block_key_used_per_node,
            },
            "parameter_bin_id": param_bin_id,
            "engine_params": engine_params,
            "metrics": metrics,
            "tags": tags,
            "reasons": reasons,
            "edge_weight_pattern": edge_weights,
            "phase": phase,
        }

    def evaluate_candidate(
        target_name: str,
        template: Dict[str, Any],
        assignment: List[Dict[str, Any]],
        phase: str,
        target_index: int,
        target_attempt_index: int,
        param_neighbor_bins: Optional[Dict[str, int]] = None,
        base_bins: Optional[Dict[str, int]] = None,
        fixed_edge_weights: Optional[List[float]] = None,
    ) -> None:
        nonlocal attempt_id, term_attempts_count, total_attempts, total_viable, term_viable

        nodes = int(template.get("nodes", 0))
        if nodes <= 0:
            return

        assignment_keys = []
        block_key_used_per_node = []
        invalid_identity = False
        for b in assignment:
            if b.get("block_id"):
                assignment_keys.append(str(b.get("block_id")))
                block_key_used_per_node.append("block_id")
            elif b.get("particle_name"):
                assignment_keys.append(str(b.get("particle_name")))
                block_key_used_per_node.append("particle_name")
            elif b.get("block_fingerprint"):
                assignment_keys.append(str(b.get("block_fingerprint")))
                block_key_used_per_node.append("fingerprint")
            else:
                assignment_keys.append("missing_identity")
                block_key_used_per_node.append("missing")
                invalid_identity = True
        block_key_used = "mixed"
        if all(k == "block_id" for k in block_key_used_per_node):
            block_key_used = "block_id"
        elif all(k == "particle_name" for k in block_key_used_per_node):
            block_key_used = "particle_name"
        elif all(k == "fingerprint" for k in block_key_used_per_node):
            block_key_used = "fingerprint"

        template_name = template.get("name", "unknown")
        edges = [list(e[:2]) for e in template.get("edges", [])]

        if template_name not in automorphisms_cache:
            automorphisms_cache[template_name] = _automorphisms(nodes, edges)
        perms = automorphisms_cache[template_name]

        edge_weights = None
        if edge_weight_policy == "sample_discrete":
            if fixed_edge_weights is not None:
                edge_weights = list(fixed_edge_weights)
            else:
                edge_weights = [float(rng.choice(edge_weight_levels)) for _ in edges]
        elif edge_weight_policy == "fixed_template":
            if fixed_edge_weights is not None:
                edge_weights = list(fixed_edge_weights)
            else:
                if edges and len(template.get("edges", [])[0]) >= 3:
                    edge_weights = [float(e[2]) for e in template.get("edges", [])]
                elif template.get("weights"):
                    edge_weights = [float(template["weights"].get(f"{e[0]}-{e[1]}", 1.0)) for e in edges]

        serial, canonical_assignment, canonical_weights = _canonicalize_assignment(
            template_name, edges, assignment_keys, edge_weights, perms
        )
        structure_id = _hash_text(serial)

        if invalid_identity:
            reasons = ["invalid_candidate_missing_identity"]
            tags = {
                "viable": False,
                "memory_good": False,
                "viability_mode": tagging.get("viability_mode", "hard_viable_soft_memory"),
                "thresholds": {"R_mean_lastW_min": r_min, "phase_var_lastW_max": pv_max, "memory_score_k10_min": mem_min},
            }
            record = build_record(
                target_name,
                template_name,
                attempt_seed=-1,
                attempt_index=attempt_id,
                target_index=target_index,
                target_attempt_index=target_attempt_index,
                assignment=assignment,
                assignment_keys=assignment_keys,
                block_key_used=block_key_used,
                block_key_used_per_node=block_key_used_per_node,
                structure_id=structure_id,
                canonical_assignment=canonical_assignment,
                canonical_edge_weights=canonical_weights,
                param_bin_id="invalid",
                engine_params=defaults,
                metrics={},
                tags=tags,
                reasons=reasons,
                edge_weights=edge_weights,
                template_edges=edges,
                phase=phase,
            )
            with rejected_path.open("a") as f:
                f.write(json.dumps(record) + "\n")
            per_template_counts[template_name] = per_template_counts.get(template_name, 0) + 1
            per_target_counts[target_name] = per_target_counts.get(target_name, 0) + 1
            per_phase_counts[phase] = per_phase_counts.get(phase, 0) + 1
            term_template_counts[template_name] = term_template_counts.get(template_name, 0) + 1
            attempt_id += 1
            term_attempts_count += 1
            total_attempts += 1
            return

        params, param_bin_id = _sample_params(defaults, variation_cfg, rng, param_neighbor_bins, base_bins)
        attempt_seed = rng.randint(0, 2**32 - 1)
        np.random.seed(attempt_seed)

        masses = np.array([_pick_mass(b) for b in assignment], dtype=float)
        omegas = np.array([_pick_omega(b) for b in assignment], dtype=float)
        lock_quality = [b.get("lock_quality") or {} for b in assignment]
        sim_template = dict(template)
        if edge_weights is not None:
            sim_edges = []
            for e, w in zip(edges, edge_weights):
                sim_edges.append([int(e[0]), int(e[1]), float(w)])
            sim_template["edges"] = sim_edges

        sim_res = simulate_ola2(
            masses=masses,
            omegas=omegas,
            theta0=None,
            template=sim_template,
            lock_quality=lock_quality,
            dt=params["dt"],
            T_ticks=int(params["T_ticks"]),
            sigma0=params["sigma0"],
            sigma_tc=params["sigma_tc"],
            sigma_theta_init=params["sigma_theta_init"],
            K_local=params["K_local"],
            kappa_global=params["kappa_global"],
            tau_field=params["tau_field"],
            window_W=int(params["W"]),
        )

        metrics = sim_res.get("metrics", {})
        h_block_mean = float(np.mean([_lock_entropy(q) for q in lock_quality])) if lock_quality else None
        metrics = dict(metrics)
        metrics["H_block_mean"] = h_block_mean

        r_mean = metrics.get("R_mean_lastW")
        pv_last = metrics.get("phase_var_lastW")
        memory_score = metrics.get("memory_score_k10")
        viable = bool(_is_finite(r_mean) and _is_finite(pv_last) and r_mean > r_min and pv_last < pv_max)
        memory_good = bool(_is_finite(memory_score) and float(memory_score) >= mem_min)
        reasons: List[str] = []
        if not _is_finite(r_mean):
            reasons.append("missing_R_mean")
        elif r_mean <= r_min:
            reasons.append("low_coherence")
        if not _is_finite(pv_last):
            reasons.append("missing_phase_var")
        elif pv_last >= pv_max:
            reasons.append("high_phase_variance")
        if not memory_good:
            reasons.append("memory_low")

        tags = {
            "viable": viable,
            "memory_good": memory_good,
            "viability_mode": tagging.get("viability_mode", "hard_viable_soft_memory"),
            "thresholds": {"R_mean_lastW_min": r_min, "phase_var_lastW_max": pv_max, "memory_score_k10_min": mem_min},
        }

        record = build_record(
            target_name,
            template_name,
            attempt_seed=attempt_seed,
            attempt_index=attempt_id,
            target_index=target_index,
            target_attempt_index=target_attempt_index,
            assignment=assignment,
            assignment_keys=assignment_keys,
            block_key_used=block_key_used,
            block_key_used_per_node=block_key_used_per_node,
            structure_id=structure_id,
            canonical_assignment=canonical_assignment,
            canonical_edge_weights=canonical_weights,
            param_bin_id=param_bin_id,
            engine_params=params,
            metrics=metrics,
            tags=tags,
            reasons=reasons,
            edge_weights=edge_weights,
            template_edges=edges,
            phase=phase,
        )
        if viable:
            with accepted_path.open("a") as f:
                f.write(json.dumps(record) + "\n")
        else:
            with rejected_path.open("a") as f:
                f.write(json.dumps(record) + "\n")

        update_structure_stats(
            structure_id,
            template_name,
            target_name,
            canonical_assignment,
            canonical_weights,
            metrics,
            params,
            param_bin_id,
            viable,
            block_key_used,
            block_key_used_per_node,
            assignment,
        )
        update_memory_store(
            structure_id,
            param_bin_id,
            target_name,
            template_name,
            attempt_seed,
            metrics,
            params,
            viable,
        )

        unique_structures.add(structure_id)
        per_template_counts[template_name] = per_template_counts.get(template_name, 0) + 1
        per_target_counts[target_name] = per_target_counts.get(target_name, 0) + 1
        per_phase_counts[phase] = per_phase_counts.get(phase, 0) + 1
        term_template_counts[template_name] = term_template_counts.get(template_name, 0) + 1
        term_attempts_count += 1
        total_attempts += 1
        if viable:
            total_viable += 1
            term_viable += 1
            per_template_viable[template_name] = per_template_viable.get(template_name, 0) + 1
            per_target_viable[target_name] = per_target_viable.get(target_name, 0) + 1
            per_phase_viable[phase] = per_phase_viable.get(phase, 0) + 1
        attempt_id += 1

    targets = cfg.get("targets", [])
    for target_index, target in enumerate(targets):
        target_name = target.get("name", f"target_{target_index}")
        template_names = target.get("templates", [])
        families = target.get("allowed_block_families", [])
        allowed_particle_names = target.get("allowed_particle_names")
        budget_evals = int(target.get("budget_evals", 0))
        if budget_evals <= 0:
            continue

        phase1_budget = int(budget_evals * phase1_fraction)
        phase2_budget = budget_evals - phase1_budget

        target_attempt_index = 0
        template_cycle = list(template_names)
        template_cursor = 0
        seen_structures: Dict[str, int] = {}

        # Phase 1
        for _ in range(phase1_budget):
            if template_balance == "round_robin" and template_cycle:
                tmpl_name = template_cycle[template_cursor % len(template_cycle)]
                template_cursor += 1
            else:
                tmpl_name = rng.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            if tmpl is None:
                continue
            nodes = int(tmpl.get("nodes", 0))
            assignment = _sample_blocks(blocks, families, allowed_particle_names, nodes, rng)
            if len(assignment) != nodes:
                reasons = ["not_enough_blocks"]
                tags = {
                    "viable": False,
                    "memory_good": False,
                    "viability_mode": tagging.get("viability_mode", "hard_viable_soft_memory"),
                    "thresholds": {"R_mean_lastW_min": r_min, "phase_var_lastW_max": pv_max, "memory_score_k10_min": mem_min},
                }
                record = build_record(
                    target_name,
                    tmpl_name,
                    attempt_seed=-1,
                    attempt_index=attempt_id,
                    target_index=target_index,
                    target_attempt_index=target_attempt_index,
                    assignment=[],
                    assignment_keys=[],
                    block_key_used="missing",
                    block_key_used_per_node=[],
                    structure_id=f"skip_{attempt_id}",
                    canonical_assignment=[],
                    canonical_edge_weights=None,
                    param_bin_id="invalid",
                    engine_params=defaults,
                    metrics={},
                    tags=tags,
                    reasons=reasons,
                    edge_weights=None,
                    template_edges=[list(e[:2]) for e in tmpl.get("edges", [])],
                    phase="phase1",
                )
                with rejected_path.open("a") as f:
                    f.write(json.dumps(record) + "\n")
                per_template_counts[tmpl_name] = per_template_counts.get(tmpl_name, 0) + 1
                per_target_counts[target_name] = per_target_counts.get(target_name, 0) + 1
                per_phase_counts["phase1"] = per_phase_counts.get("phase1", 0) + 1
                term_template_counts[tmpl_name] = term_template_counts.get(tmpl_name, 0) + 1
                term_attempts_count += 1
                total_attempts += 1
                attempt_id += 1
                target_attempt_index += 1
                continue
            # avoid repeats if possible
            edge_weights_candidate = None
            if edge_weight_policy == "sample_discrete":
                edge_weights_candidate = [float(rng.choice(edge_weight_levels)) for _ in tmpl.get("edges", [])]
            if phase1_cfg.get("prefer_novel_structures", True):
                tries = 0
                while tries < 30:
                    assignment_keys = []
                    for b in assignment:
                        assignment_keys.append(str(b.get("block_id") or b.get("particle_name") or b.get("block_fingerprint") or "missing"))
                    edges = [list(e[:2]) for e in tmpl.get("edges", [])]
                    if tmpl_name not in automorphisms_cache:
                        automorphisms_cache[tmpl_name] = _automorphisms(nodes, edges)
                    serial, _, _ = _canonicalize_assignment(
                        tmpl_name, edges, assignment_keys, edge_weights_candidate, automorphisms_cache[tmpl_name]
                    )
                    structure_id = _hash_text(serial)
                    if seen_structures.get(structure_id, 0) < max_repeats_per_structure:
                        break
                    assignment = _sample_blocks(blocks, families, allowed_particle_names, nodes, rng)
                    if len(assignment) != nodes:
                        break
                    tries += 1
            evaluate_candidate(
                target_name,
                tmpl,
                assignment,
                phase="phase1",
                target_index=target_index,
                target_attempt_index=target_attempt_index,
                fixed_edge_weights=edge_weights_candidate,
            )
            target_attempt_index += 1
            # update repeat tracking
            assignment_keys = []
            for b in assignment:
                assignment_keys.append(str(b.get("block_id") or b.get("particle_name") or b.get("block_fingerprint") or "missing"))
            edges = [list(e[:2]) for e in tmpl.get("edges", [])]
            serial, _, _ = _canonicalize_assignment(tmpl_name, edges, assignment_keys, edge_weights_candidate, automorphisms_cache[tmpl_name])
            structure_id = _hash_text(serial)
            seen_structures[structure_id] = seen_structures.get(structure_id, 0) + 1

            best_struct = None
            if structure_stats:
                best_struct = max(structure_stats.values(), key=lambda s: _best_score(s.get("best_metrics") or {}))
            if term_attempts_count >= term_attempts or (time.time() - term_start) >= term_seconds:
                write_term_progress(best_struct)

        # Phase 2 - refine promising structures
        if phase2_budget > 0:
            promising_rule = phase2_cfg.get("promising_rule", {})
            min_r = float(promising_rule.get("min_R_mean_lastW", 0.80))
            max_pv = float(promising_rule.get("max_phase_var_lastW", 0.03))
            min_mem = float(promising_rule.get("min_memory_score_k10", 0.0))
            seed_repeats = int(phase2_cfg.get("seed_repeats_per_structure", 5))
            neighbor_bins_count = int(phase2_cfg.get("param_neighbor_bins", 0))

            promising = []
            for sid, stats in structure_stats.items():
                if stats.get("target") != target_name:
                    continue
                bm = stats.get("best_metrics") or {}
                if _is_finite(bm.get("R_mean_lastW")) and _is_finite(bm.get("phase_var_lastW")):
                    if bm.get("R_mean_lastW") >= min_r and bm.get("phase_var_lastW") <= max_pv:
                        if not _is_finite(bm.get("memory_score_k10")) or bm.get("memory_score_k10") < min_mem:
                            continue
                        promising.append(stats)
            promising = sorted(promising, key=lambda s: _best_score(s.get("best_metrics") or {}), reverse=True)

            phase2_attempts = 0
            for stats in promising:
                if phase2_attempts >= phase2_budget:
                    break
                blocks_used = []
                if stats.get("block_key_used") == "block_id":
                    blocks_used = [block_map.get(k) for k in stats.get("assignment", [])]
                    blocks_used = [b for b in blocks_used if b]
                if not blocks_used:
                    blocks_used = stats.get("_blocks", [])
                if not blocks_used:
                    continue
                tmpl = templates.get(stats.get("template_name"))
                if not tmpl:
                    continue
                base_bins = None
                if stats.get("best_param_bin_id") and variation_cfg.get("enabled", False):
                    bin_id = stats["best_param_bin_id"]
                    try:
                        parts = bin_id.replace("K", "").split("_")
                        base_bins = {
                            "K_local": int(parts[0]),
                            "kappa_global": int(parts[1].replace("k", "")),
                            "tau_field": int(parts[2].replace("tau", "")),
                            "sigma0": int(parts[3].replace("s0", "")),
                            "sigma_tc": int(parts[4].replace("stc", "")),
                        }
                    except Exception:
                        base_bins = None
                neighbor_bins = None
                if neighbor_bins_count > 0 and base_bins:
                    neighbor_bins = {k: neighbor_bins_count for k in base_bins}
                for _ in range(seed_repeats):
                    if phase2_attempts >= phase2_budget:
                        break
                    evaluate_candidate(
                        target_name,
                        tmpl,
                        blocks_used,
                        phase="phase2",
                        target_index=target_index,
                        target_attempt_index=target_attempt_index,
                        param_neighbor_bins=neighbor_bins,
                        base_bins=base_bins,
                        fixed_edge_weights=stats.get("edge_weights"),
                    )
                    target_attempt_index += 1
                    phase2_attempts += 1
                    best_struct = None
                    if structure_stats:
                        best_struct = max(structure_stats.values(), key=lambda s: _best_score(s.get("best_metrics") or {}))
                    if term_attempts_count >= term_attempts or (time.time() - term_start) >= term_seconds:
                        write_term_progress(best_struct)

    # Final term flush
    best_struct = None
    if structure_stats:
        best_struct = max(structure_stats.values(), key=lambda s: _best_score(s.get("best_metrics") or {}))
    write_term_progress(best_struct)

    # Build structures_config.json
    structures_out = []
    for sid, stats in structure_stats.items():
        trials = stats.get("n_trials", 0)
        n_viable = stats.get("n_viable", 0)
        seed_stability = n_viable / max(trials, 1)
        best_metrics = stats.get("best_metrics") or {}
        export_class = None
        if seed_stability >= min_seed_stability or n_viable >= min_viable_hits:
            export_class = "CONFIRMED_VIABLE"
        elif export_promising_nonviable:
            if (
                best_metrics.get("R_mean_lastW") is not None
                and best_metrics.get("phase_var_lastW") is not None
                and best_metrics.get("R_mean_lastW") >= r_promising_min
                and best_metrics.get("phase_var_lastW") <= pv_promising_max
                and best_metrics.get("memory_score_k10") is not None
                and best_metrics.get("memory_score_k10") >= mem_min
            ):
                export_class = "PROMISING_MEMORY_GOOD"
        if not export_class:
            continue
        structures_out.append(
            {
                "structure_id": sid,
                "template_name": stats.get("template_name"),
                "target": stats.get("target"),
                "assignment": stats.get("assignment"),
                "edge_weights": stats.get("edge_weights"),
                "engine_params": stats.get("best_params"),
                "seed_stability": seed_stability,
                "n_trials": trials,
                "n_viable": n_viable,
                "best_metrics": best_metrics,
                "export_class": export_class,
                "block_key_used": stats.get("block_key_used"),
                "block_key_used_per_node": stats.get("block_key_used_per_node"),
            }
        )
    structures_config_path.write_text(json.dumps(structures_out, indent=2))

    # Write structures cards JSON
    cards = _build_structure_cards(structure_stats, export_cfg, mem_min)
    structures_cards_path.parent.mkdir(parents=True, exist_ok=True)
    structures_cards_path.write_text(json.dumps(cards, indent=2))

    # Write final report
    report_path.write_text(
        _render_report(
            "Final",
            structure_stats,
            per_template_counts,
            per_template_viable,
            per_target_counts,
            per_target_viable,
            per_phase_counts,
            per_phase_viable,
            cards,
        )
    )

    # Write meta.json for traceability
    meta = {
        "schema_version": "ola2_structure_explorer_v2_meta",
        "run_id": run_id,
        "started_utc": started_utc,
        "ended_utc": _utc_now(),
        "inputs": {
            "wave1_blocks_file": str(blocks_path),
            "wave1_input_file_hash": wave1_input_file_hash,
            "templates_file": str(templates_path),
            "config_file": str(config_path),
            "config_hash": config_hash,
        },
        "engine": {
            "simulate_ola2_source": "ola2_reloaded_sim.py",
            "uses_simulate_ola2_unmodified": True,
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    (output_dir / "meta.json").write_text(json.dumps(meta, indent=2))


def _render_report(
    title: str,
    structure_stats: Dict[str, Dict[str, Any]],
    per_template_counts: Optional[Dict[str, int]] = None,
    per_template_viable: Optional[Dict[str, int]] = None,
    per_target_counts: Optional[Dict[str, int]] = None,
    per_target_viable: Optional[Dict[str, int]] = None,
    per_phase_counts: Optional[Dict[str, int]] = None,
    per_phase_viable: Optional[Dict[str, int]] = None,
    cards: Optional[List[Dict[str, Any]]] = None,
) -> str:
    lines = [f"# Structure Explorer Report ({title})", ""]
    total_attempts = sum(per_template_counts.values()) if per_template_counts else 0
    total_viable = sum(per_template_viable.values()) if per_template_viable else 0
    viable_rate = (total_viable / total_attempts) if total_attempts else 0.0
    unique_structures = len(structure_stats)
    repeat_rate = (1.0 - (unique_structures / total_attempts)) if total_attempts else 0.0
    lines.append("## Overview")
    lines.append(f"- total_attempts: {total_attempts}")
    lines.append(f"- total_viable: {total_viable}")
    lines.append(f"- viable_rate: {viable_rate:.2%}")
    lines.append(f"- unique_structures: {unique_structures}")
    lines.append(f"- repeat_rate: {repeat_rate:.2%}")
    lines.append("")

    if per_template_counts:
        lines.append("## By Template")
        lines.append("| template | attempts | viable | rate |")
        lines.append("| --- | --- | --- | --- |")
        for name, cnt in sorted(per_template_counts.items(), key=lambda x: x[0]):
            v = per_template_viable.get(name, 0) if per_template_viable else 0
            rate = (v / cnt) if cnt else 0.0
            lines.append(f"| {name} | {cnt} | {v} | {rate:.2%} |")
        lines.append("")

    if per_target_counts:
        lines.append("## By Target")
        lines.append("| target | attempts | viable | rate |")
        lines.append("| --- | --- | --- | --- |")
        for name, cnt in sorted(per_target_counts.items(), key=lambda x: x[0]):
            v = per_target_viable.get(name, 0) if per_target_viable else 0
            rate = (v / cnt) if cnt else 0.0
            lines.append(f"| {name} | {cnt} | {v} | {rate:.2%} |")
        lines.append("")

    if per_phase_counts:
        lines.append("## Phase Comparison")
        lines.append("| phase | attempts | viable | rate |")
        lines.append("| --- | --- | --- | --- |")
        for name, cnt in per_phase_counts.items():
            v = per_phase_viable.get(name, 0) if per_phase_viable else 0
            rate = (v / cnt) if cnt else 0.0
            lines.append(f"| {name} | {cnt} | {v} | {rate:.2%} |")
        lines.append("")

    # Top structures by coherence
    best_by_r = sorted(
        structure_stats.values(),
        key=lambda s: (s.get("best_metrics") or {}).get("R_mean_lastW") or -1,
        reverse=True,
    )[:20]
    lines.append("## Top Structures by R_mean_lastW")
    lines.append("| structure_id | R_mean_lastW | phase_var_lastW | memory_score_k10 | trials | viable |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for s in best_by_r:
        bm = s.get("best_metrics") or {}
        lines.append(
            f"| {s.get('structure_id')} | {bm.get('R_mean_lastW')} | {bm.get('phase_var_lastW')} | {bm.get('memory_score_k10')} | {s.get('n_trials')} | {s.get('n_viable')} |"
        )
    lines.append("")

    # Top structures by stability
    best_by_stability = sorted(
        structure_stats.values(),
        key=lambda s: (s.get("n_viable", 0) / max(s.get("n_trials", 1), 1)),
        reverse=True,
    )[:20]
    lines.append("## Top Structures by Seed Stability")
    lines.append("| structure_id | seed_stability | trials | viable |")
    lines.append("| --- | --- | --- | --- |")
    for s in best_by_stability:
        trials = s.get("n_trials", 0)
        viable = s.get("n_viable", 0)
        stability = viable / max(trials, 1)
        lines.append(f"| {s.get('structure_id')} | {stability:.3f} | {trials} | {viable} |")
    lines.append("")

    # Top structures by memory score
    best_by_memory = sorted(
        structure_stats.values(),
        key=lambda s: (s.get("best_metrics") or {}).get("memory_score_k10") or -1,
        reverse=True,
    )[:20]
    lines.append("## Top Structures by memory_score_k10")
    lines.append("| structure_id | memory_score_k10 | R_mean_lastW | phase_var_lastW |")
    lines.append("| --- | --- | --- | --- |")
    for s in best_by_memory:
        bm = s.get("best_metrics") or {}
        lines.append(
            f"| {s.get('structure_id')} | {bm.get('memory_score_k10')} | {bm.get('R_mean_lastW')} | {bm.get('phase_var_lastW')} |"
        )
    lines.append("")

    # Energies list
    energy_vals = []
    for s in structure_stats.values():
        bm = s.get("best_metrics") or {}
        if _is_finite(bm.get("E_local_mean_lastW")):
            energy_vals.append(float(bm.get("E_local_mean_lastW")))
    if energy_vals:
        lines.append("## Energies (E_local_mean_lastW)")
        lines.append(f"- count: {len(energy_vals)}")
        lines.append(f"- min: {min(energy_vals):.6g}")
        lines.append(f"- max: {max(energy_vals):.6g}")
        lines.append(f"- mean: {float(np.mean(energy_vals)):.6g}")
        lines.append("")
        top_by_energy = sorted(
            structure_stats.values(),
            key=lambda s: (s.get("best_metrics") or {}).get("E_local_mean_lastW") or -1,
            reverse=True,
        )[:20]
        lines.append("| structure_id | E_local_mean_lastW | R_mean_lastW | phase_var_lastW |")
        lines.append("| --- | --- | --- | --- |")
        for s in top_by_energy:
            bm = s.get("best_metrics") or {}
            lines.append(
                f"| {s.get('structure_id')} | {bm.get('E_local_mean_lastW')} | {bm.get('R_mean_lastW')} | {bm.get('phase_var_lastW')} |"
            )
        lines.append("")
        top_by_energy_min = sorted(
            structure_stats.values(),
            key=lambda s: (s.get("best_metrics") or {}).get("E_local_min_lastW") or 1e18,
        )[:20]
        lines.append("## Energies (E_local_min_lastW)")
        lines.append("| structure_id | E_local_min_lastW | R_mean_lastW | phase_var_lastW |")
        lines.append("| --- | --- | --- | --- |")
        for s in top_by_energy_min:
            bm = s.get("best_metrics") or {}
            lines.append(
                f"| {s.get('structure_id')} | {bm.get('E_local_min_lastW')} | {bm.get('R_mean_lastW')} | {bm.get('phase_var_lastW')} |"
            )
        lines.append("")

    # Pareto frontier
    frontier = []
    for s in structure_stats.values():
        bm = s.get("best_metrics") or {}
        r = bm.get("R_mean_lastW")
        pv = bm.get("phase_var_lastW")
        if not _is_finite(r) or not _is_finite(pv):
            continue
        dominated = False
        for t in structure_stats.values():
            if t is s:
                continue
            tm = t.get("best_metrics") or {}
            r2 = tm.get("R_mean_lastW")
            pv2 = tm.get("phase_var_lastW")
            if not _is_finite(r2) or not _is_finite(pv2):
                continue
            if r2 >= r and pv2 <= pv and (r2 > r or pv2 < pv):
                dominated = True
                break
        if not dominated:
            frontier.append(s)
    lines.append("## Pareto Frontier")
    lines.append("| structure_id | R_mean_lastW | phase_var_lastW | memory_score_k10 |")
    lines.append("| --- | --- | --- | --- |")
    for s in frontier:
        bm = s.get("best_metrics") or {}
        lines.append(
            f"| {s.get('structure_id')} | {bm.get('R_mean_lastW')} | {bm.get('phase_var_lastW')} | {bm.get('memory_score_k10')} |"
        )
    lines.append("")

    if cards:
        lines.append("## Structure Cards (Top-K + Exported)")
        for card in cards:
            lines.append("")
            lines.append(f"### {card.get('structure_id')}")
            lines.append(f"- template: {card.get('template_name')}")
            lines.append(f"- assignment_block_ids: {card.get('assignment_block_ids')}")
            lines.append(f"- assignment_particle_names: {card.get('assignment_particle_names')}")
            lines.append(f"- edge_weights: {card.get('edge_weights')}")
            lines.append(f"- seed_stability: {card.get('seed_stability')}")
            lines.append(f"- n_trials: {card.get('n_trials')}")
            lines.append(f"- n_viable: {card.get('n_viable')}")
            lines.append(f"- engine_params: {card.get('engine_params')}")
            lines.append(f"- best_metrics: {card.get('best_metrics')}")
            lines.append(f"- export_class: {card.get('export_class')}")
            lines.append(f"- lock_snapshot: {card.get('lock_snapshot')}")
        lines.append("")
        exported = [c for c in cards if c.get("export_class")]
        if exported:
            exported_sorted = sorted(exported, key=lambda c: c.get("seed_stability") or 0.0, reverse=True)[:20]
            lines.append("## Lock Recipes (Top Exported)")
            for card in exported_sorted:
                lines.append("")
                lines.append(f"### {card.get('structure_id')}")
                lines.append(f"- export_class: {card.get('export_class')}")
                lines.append(f"- template: {card.get('template_name')}")
                lines.append(f"- blocks: {card.get('assignment_block_ids')}")
                lines.append(f"- particles: {card.get('assignment_particle_names')}")
                lines.append(f"- edge_weights: {card.get('edge_weights')}")
                lines.append(f"- engine_params: {card.get('engine_params')}")
                bm = card.get("best_metrics") or {}
                lines.append(
                    "- best_metrics: "
                    f"R_mean_lastW={bm.get('R_mean_lastW')}, "
                    f"phase_var_lastW={bm.get('phase_var_lastW')}, "
                    f"memory_score_k10={bm.get('memory_score_k10')}, "
                    f"E_local_mean_lastW={bm.get('E_local_mean_lastW')}, "
                    f"E_local_min_lastW={bm.get('E_local_min_lastW')}"
                )
                lines.append(f"- seed_stability: {card.get('seed_stability')}")
                lines.append(f"- n_trials: {card.get('n_trials')}")
                lines.append(f"- n_viable: {card.get('n_viable')}")
            lines.append("")
    return "\n".join(lines)


def _build_structure_cards(
    structure_stats: Dict[str, Dict[str, Any]],
    export_cfg: Dict[str, Any],
    mem_min: float,
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    min_seed_stability = float(export_cfg.get("min_seed_stability_for_export", 0.5))
    min_viable_hits = int(export_cfg.get("min_viable_hits_for_export", 1))
    export_promising_nonviable = bool(export_cfg.get("export_promising_nonviable", False))
    r_promising_min = float(export_cfg.get("R_promising_min", 0.80))
    pv_promising_max = float(export_cfg.get("phase_var_promising_max", 0.03))

    def export_class_for(stats: Dict[str, Any]) -> Optional[str]:
        trials = stats.get("n_trials", 0)
        n_viable = stats.get("n_viable", 0)
        seed_stability = n_viable / max(trials, 1)
        best_metrics = stats.get("best_metrics") or {}
        if seed_stability >= min_seed_stability or n_viable >= min_viable_hits:
            return "CONFIRMED_VIABLE"
        if export_promising_nonviable:
            if (
                best_metrics.get("R_mean_lastW") is not None
                and best_metrics.get("phase_var_lastW") is not None
                and best_metrics.get("R_mean_lastW") >= r_promising_min
                and best_metrics.get("phase_var_lastW") <= pv_promising_max
                and best_metrics.get("memory_score_k10") is not None
                and best_metrics.get("memory_score_k10") >= mem_min
            ):
                return "PROMISING_MEMORY_GOOD"
        return None

    top_structs = sorted(
        structure_stats.values(),
        key=lambda s: _best_score(s.get("best_metrics") or {}),
        reverse=True,
    )[:top_k]
    exported = [s for s in structure_stats.values() if export_class_for(s)]
    merged = {s.get("structure_id"): s for s in top_structs}
    for s in exported:
        merged[s.get("structure_id")] = s

    cards = []
    for s in merged.values():
        trials = s.get("n_trials", 0)
        n_viable = s.get("n_viable", 0)
        seed_stability = n_viable / max(trials, 1)
        bm = s.get("best_metrics") or {}
        cards.append(
            {
                "structure_id": s.get("structure_id"),
                "template_name": s.get("template_name"),
                "target": s.get("target"),
                "assignment_block_ids": s.get("assignment_block_ids"),
                "assignment_particle_names": s.get("assignment_particle_names"),
                "assignment_families": s.get("assignment_families"),
                "edge_weights": s.get("edge_weights"),
                "engine_params": s.get("best_params"),
                "best_metrics": bm,
                "seed_stability": seed_stability,
                "n_trials": trials,
                "n_viable": n_viable,
                "export_class": export_class_for(s),
                "lock_snapshot": {
                    "R_final": bm.get("R_final"),
                    "Z_final_abs": bm.get("Z_final_abs"),
                    "edge_phase_diff_mean_lastW": bm.get("edge_phase_diff_mean_lastW"),
                    "edge_phase_diff_std_lastW": bm.get("edge_phase_diff_std_lastW"),
                },
            }
        )
    return cards


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Structure Explorer v2 (Ola2).")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/ola2_structure_explorer_v2"))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    run_structure_explorer(args.config, args.output, args.seed)


if __name__ == "__main__":
    main()
