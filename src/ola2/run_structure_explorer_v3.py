"""Structure Explorer v2 (Ola2) - attempts-first explorer (v3 config).

Writes a single attempts.jsonl stream and derives species_catalog.jsonl + report.md.
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
import csv
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from ola2.ola2_reloaded_sim import simulate_ola2


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _load_blocks_wave1(path: Path) -> Any:
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


def _norm_run_id(val: Any) -> str:
    try:
        f = float(val)
        return str(int(f))
    except Exception:
        return str(val)


def _load_dof_grade_a(path: Path) -> set[str]:
    if not path.exists():
        return set()
    grade_a: set[str] = set()
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = _norm_run_id(row.get("run_id"))
            dna_grade = str(row.get("dna_grade", "")).upper()
            if dna_grade:
                if dna_grade == "A":
                    grade_a.add(rid)
                continue
            try:
                d_total = float(row.get("d_total"))
            except Exception:
                d_total = None
            if d_total is not None and d_total < 0.5:
                grade_a.add(rid)
    return grade_a


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
    mem_val = float(mem) if _is_finite(mem) and float(mem) > 0 else 0.0
    return float(r) - 3.0 * float(pv) + 0.2 * mem_val


def run_structure_explorer(config_path: Path, output_dir: Path, seed: Optional[int]) -> None:
    started_utc = _utc_now()
    cfg = _load_json(config_path)
    rng = random.Random(seed)
    run_id = cfg.get("run_id") or str(uuid.uuid4())

    inputs = cfg.get("inputs", {})
    blocks_path = Path(inputs.get("blocks_json", "data/processed/ola1/simple_blocks.json"))
    templates_path = Path(inputs.get("templates_json", "data/raw/compound_templates.json"))
    dna_path = Path(inputs.get("dof_dna_catalog_csv", "data/processed/ola1/dof_dna_catalog.csv"))
    config_hash = f"sha256:{hashlib.sha256(config_path.read_bytes()).hexdigest()}"
    wave1_input_file_hash = f"sha256:{hashlib.sha256(blocks_path.read_bytes()).hexdigest()}"
    templates_hash = f"sha256:{hashlib.sha256(templates_path.read_bytes()).hexdigest()}"
    code_hash = f"sha256:{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}"

    raw_blocks = _load_blocks_wave1(blocks_path)
    blocks = _extract_blocks(raw_blocks)
    if not blocks:
        raise RuntimeError(f"No blocks found in {blocks_path}")
    grade_a_ids = _load_dof_grade_a(dna_path)
    if grade_a_ids:
        blocks = [b for b in blocks if _norm_run_id(b.get("origin_run_id")) in grade_a_ids]
    if not blocks:
        raise RuntimeError("No Grade A DOF blocks found for Structure Explorer.")
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
    r_final_min = tagging.get("R_final_min")
    quality_lock_min = tagging.get("quality_lock_min")

    search_policy = cfg.get("search_policy", {})
    phase1_fraction = float(search_policy.get("phase1_fraction", 0.7))
    phase2_fraction = float(search_policy.get("phase2_fraction", 0.3))
    phase1_cfg = search_policy.get("phase1", {})
    phase2_cfg = search_policy.get("phase2", {})
    template_balance = phase1_cfg.get("template_balance", "round_robin")
    max_repeats_per_structure = int(phase1_cfg.get("max_repeats_per_structure", 1))

    outputs = cfg.get("outputs", {})
    attempts_path = output_dir / outputs.get("attempts_jsonl", "attempts.jsonl")
    species_catalog_path = output_dir / outputs.get("species_catalog_jsonl", "species_catalog.jsonl")
    report_path = output_dir / outputs.get("report_md", "report.md")

    progress_cfg = cfg.get("progress", {})
    term_attempts = int(progress_cfg.get("term_attempts", 500))
    term_seconds = int(progress_cfg.get("term_seconds", 10))

    output_dir.mkdir(parents=True, exist_ok=True)
    attempts_path.parent.mkdir(parents=True, exist_ok=True)
    species_catalog_path.parent.mkdir(parents=True, exist_ok=True)

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
        term_start = time.time()
        term_attempts_count = 0
        term_template_counts = {}
        term_viable = 0

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
        assignment_block_ids = [b.get("block_id") for b in assignment]
        assignment_particle_names = [b.get("particle_name") for b in assignment]
        structure = {
            "template_name": template_name,
            "structure_id": structure_id,
            "canonical_node_order": canonical_assignment,
            "edges": template_edges,
            "edge_weights_mode": edge_weights_mode,
            "edge_weight_pattern": edge_weights,
            "assignment": {
                "block_ids": assignment_block_ids,
                "particle_names": assignment_particle_names,
                "block_keys": assignment_keys,
            },
            "block_key_used": block_key_used,
            "block_key_used_per_node": block_key_used_per_node,
        }
        viability_state = "INVALID" if "invalid_candidate_missing_identity" in reasons else "BOUNDED"
        attractor_class = "COHERENT_LOCKED" if tags.get("viable") else "DRIFT_BOUNDED"
        grade = "A" if tags.get("viable") else "C"
        return {
            "schema_version": "ola2_attempt_v1",
            "run_id": run_id,
            "attempt_id": attempt_index,
            "timestamp_utc": _utc_now(),
            "seed": attempt_seed,
            "provenance": {
                "config_hash": config_hash,
                "blocks_hash": wave1_input_file_hash,
                "templates_hash": templates_hash,
                "code_hash": code_hash,
                "machine": {
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                },
            },
            "target": {
                "name": target_name,
                "index": target_index,
                "attempt_index": target_attempt_index,
                "phase": phase,
            },
            "structure": structure,
            "parameter_bin_id": param_bin_id,
            "engine_params": engine_params,
            "metrics": metrics,
            "taxonomy": {
                "viability_state": viability_state,
                "attractor_class": attractor_class,
                "grade": grade,
            },
            "tags": tags,
            "reasons": reasons,
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
                "thresholds": {
                    "R_mean_lastW_min": r_min,
                    "phase_var_lastW_max": pv_max,
                    "memory_score_k10_min": mem_min,
                    "R_final_min": r_final_min,
                    "quality_lock_min": quality_lock_min,
                },
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
            with attempts_path.open("a") as f:
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
        r_final = metrics.get("R_final")
        quality_lock = metrics.get("QualityLock")
        memory_score = metrics.get("memory_score_k10")
        memory_score_pos = float(memory_score) if _is_finite(memory_score) and float(memory_score) > 0 else None
        viable = bool(_is_finite(r_mean) and _is_finite(pv_last) and r_mean > r_min and pv_last < pv_max)
        r_final_ok = None
        quality_lock_ok = None
        if r_final_min is not None:
            try:
                r_final_min_val = float(r_final_min)
            except Exception:
                r_final_min_val = None
            if r_final_min_val is not None:
                r_final_ok = bool(_is_finite(r_final) and float(r_final) > r_final_min_val)
        if quality_lock_min is not None:
            try:
                quality_lock_min_val = float(quality_lock_min)
            except Exception:
                quality_lock_min_val = None
            if quality_lock_min_val is not None:
                quality_lock_ok = bool(_is_finite(quality_lock) and float(quality_lock) > quality_lock_min_val)
        memory_good = bool(memory_score_pos is not None and memory_score_pos >= mem_min)
        reasons: List[str] = []
        if not _is_finite(r_mean):
            reasons.append("missing_R_mean")
        elif r_mean <= r_min:
            reasons.append("low_coherence")
        if not _is_finite(pv_last):
            reasons.append("missing_phase_var")
        elif pv_last >= pv_max:
            reasons.append("high_phase_variance")
        if r_final_min is not None:
            if not _is_finite(r_final):
                reasons.append("missing_R_final")
            elif r_final_ok is False:
                reasons.append("low_R_final")
        if quality_lock_min is not None:
            if not _is_finite(quality_lock):
                reasons.append("missing_quality_lock")
            elif quality_lock_ok is False:
                reasons.append("low_quality_lock")
        if not _is_finite(memory_score):
            reasons.append("memory_missing")
        elif float(memory_score) <= 0:
            reasons.append("memory_non_positive")
        elif not memory_good:
            reasons.append("memory_low")

        tags = {
            "viable": viable,
            "memory_good": memory_good,
            "R_final_ok": r_final_ok,
            "quality_lock_ok": quality_lock_ok,
            "viability_mode": tagging.get("viability_mode", "hard_viable_soft_memory"),
            "thresholds": {
                "R_mean_lastW_min": r_min,
                "phase_var_lastW_max": pv_max,
                "memory_score_k10_min": mem_min,
                "R_final_min": r_final_min,
                "quality_lock_min": quality_lock_min,
            },
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
        with attempts_path.open("a") as f:
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
                    "thresholds": {
                        "R_mean_lastW_min": r_min,
                        "phase_var_lastW_max": pv_max,
                        "memory_score_k10_min": mem_min,
                        "R_final_min": r_final_min,
                        "quality_lock_min": quality_lock_min,
                    },
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
                with attempts_path.open("a") as f:
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

    species_catalog = _build_species_catalog(structure_stats)
    with species_catalog_path.open("w") as f:
        for row in species_catalog:
            f.write(json.dumps(row) + "\n")

    report_path.write_text(
        _render_report(
            structure_stats,
            species_catalog,
            per_template_counts,
            per_template_viable,
            per_target_counts,
            per_target_viable,
        )
    )


def _build_species_catalog(structure_stats: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    species: List[Dict[str, Any]] = []
    for sid, stats in structure_stats.items():
        trials = stats.get("n_trials", 0)
        n_viable = stats.get("n_viable", 0)
        stability = n_viable / max(trials, 1)
        species.append(
            {
                "species_id": sid,
                "structure_id": sid,
                "template_name": stats.get("template_name"),
                "assignment": stats.get("assignment"),
                "edge_weights": stats.get("edge_weights"),
                "n_trials": trials,
                "n_viable": n_viable,
                "seed_stability": stability,
                "best_metrics": stats.get("best_metrics"),
                "best_params": stats.get("best_params"),
            }
        )
    species.sort(key=lambda s: (s.get("seed_stability", 0.0), s.get("n_viable", 0)), reverse=True)
    return species


def _render_report(
    structure_stats: Dict[str, Dict[str, Any]],
    species_catalog: List[Dict[str, Any]],
    per_template_counts: Optional[Dict[str, int]] = None,
    per_template_viable: Optional[Dict[str, int]] = None,
    per_target_counts: Optional[Dict[str, int]] = None,
    per_target_viable: Optional[Dict[str, int]] = None,
) -> str:
    lines = ["# Ola2 Structure Explorer Report", ""]
    total_attempts = sum(per_template_counts.values()) if per_template_counts else 0
    total_viable = sum(per_template_viable.values()) if per_template_viable else 0
    viable_rate = (total_viable / total_attempts) if total_attempts else 0.0
    unique_structures = len(structure_stats)
    lines.append("## Overview")
    lines.append(f"- total_attempts: {total_attempts}")
    lines.append(f"- total_viable: {total_viable}")
    lines.append(f"- viable_rate: {viable_rate:.2%}")
    lines.append(f"- unique_structures: {unique_structures}")
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

    lines.append("## Species Catalog (Top 20 by seed_stability)")
    lines.append("| species_id | seed_stability | trials | viable | R_mean_lastW | phase_var_lastW | memory_score_k10 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for row in species_catalog[:20]:
        bm = row.get("best_metrics") or {}
        lines.append(
            f"| {row.get('species_id')} | {row.get('seed_stability'):.3f} | {row.get('n_trials')} | {row.get('n_viable')} | "
            f"{bm.get('R_mean_lastW')} | {bm.get('phase_var_lastW')} | {bm.get('memory_score_k10')} |"
        )
    lines.append("")
    return "\n".join(lines)
def main() -> None:
    parser = argparse.ArgumentParser(description="Run Structure Explorer v2 (Ola2).")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/ola2_structure_explorer_v2"))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    run_structure_explorer(args.config, args.output, args.seed)


if __name__ == "__main__":
    main()
