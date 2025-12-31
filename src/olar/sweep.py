"""Ola-recursive sweep (V1)."""

from __future__ import annotations

import argparse
import heapq
import json
import math
import platform
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from core.ids.engine_bins import is_engine_params_bin_id, neighbor_engine_params_bin_ids, resolve_engine_params
from core.ids.hashing import hash_file, hash_text, stable_dumps
from core.ids.time import utc_now_iso
from core.io.jsonl import append_jsonl, iter_jsonl, scan_jsonl_ids, write_resume_index
from core.io.schema_validation import validate_evaluation
from olar.explorer_pool import load_dna_catalog, load_simple_blocks
from olar.differential_engine import DifferentialNetwork
from olar.hydration import BlockHydrationError, build_hydrated_entity


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _resolve_output(path_str: str, output_dir: Optional[Path]) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if output_dir is not None:
        return output_dir / path
    return path


def _resolve_input_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return path


def _reset_outputs_if_needed(cfg: Dict[str, Any], evaluations_path: Path) -> None:
    policy = cfg.get("output_policy", {}) or {}
    if not policy.get("reset_outputs", False):
        return
    resume_path = evaluations_path.with_suffix(".resume.json")
    removed = []
    for path in (evaluations_path, resume_path):
        if path.exists():
            path.unlink()
            removed.append(str(path))
    if removed:
        print(f"[olar_sweep] reset_outputs removed={removed}")


def _seed_from_entity(entity_id: str, idx: int, salt: str, bin_id: Optional[str] = None) -> int:
    payload = f"{entity_id}|{idx}|{salt}"
    if bin_id:
        payload = f"{payload}|{bin_id}"
    return int(hash_text(payload)[:8], 16) & 0xFFFFFFFF


def _sanitize_numbers(obj: Any) -> Tuple[Any, bool]:
    if isinstance(obj, float):
        if math.isfinite(obj):
            return obj, False
        return None, True
    if isinstance(obj, list):
        sanitized = []
        invalid = False
        for item in obj:
            val, bad = _sanitize_numbers(item)
            sanitized.append(val)
            invalid = invalid or bad
        return sanitized, invalid
    if isinstance(obj, dict):
        sanitized: Dict[str, Any] = {}
        invalid = False
        for key, value in obj.items():
            val, bad = _sanitize_numbers(value)
            sanitized[key] = val
            invalid = invalid or bad
        return sanitized, invalid
    return obj, False



def _select_candidates(
    cfg: Dict[str, Any],
    entities_path: Path,
) -> Tuple[List[Dict[str, Any]], int, int]:
    mode = (cfg.get("candidate_source") or {}).get("mode", "attempts")
    override_ids = cfg.get("_override_entity_ids")
    if override_ids:
        override_ids = {str(eid) for eid in override_ids}
    if mode != "attempts":
        candidates = [row for row in iter_jsonl(entities_path) if row.get("entity_id")]
        return candidates, 0, 0
    filter_cfg = (cfg.get("candidate_source") or {}).get("filter", {})
    shard_cfg = cfg.get("candidate_shard", {}) or {}
    shard_enabled = bool(shard_cfg.get("enabled", False))
    shard_count = int(shard_cfg.get("shard_count", 0) or 0)
    shard_id = int(shard_cfg.get("shard_id", 0) or 0)
    shard_hash = str(shard_cfg.get("hash", "sha256_hex8"))
    if shard_enabled and not override_ids:
        if shard_count <= 0:
            raise RuntimeError("candidate_shard enabled but shard_count <= 0")
        if shard_id < 0 or shard_id >= shard_count:
            raise RuntimeError("candidate_shard shard_id out of range")
        if shard_hash != "sha256_hex8":
            raise RuntimeError(f"candidate_shard unsupported hash: {shard_hash}")
    require_candidate = bool(filter_cfg.get("require_candidate", True))
    require_quality_lock_ok = bool(filter_cfg.get("require_quality_lock_ok", False))
    require_memory_non_negative = bool(filter_cfg.get("require_memory_non_negative", False))
    min_quality_lock = filter_cfg.get("min_quality_lock")
    min_r_mean = filter_cfg.get("min_R_mean_lastW")
    max_phase_var = filter_cfg.get("max_phase_var_lastW")
    top_k_by = str(filter_cfg.get("top_k_by", "priority_score"))
    top_k = int(filter_cfg.get("top_k", 0))

    skipped_by_filter = 0
    skipped_by_shard = 0
    filtered: List[Tuple[float, str, Dict[str, Any]]] = []
    heap: List[Tuple[Tuple[float, str], Dict[str, Any]]] = []

    for row in iter_jsonl(entities_path):
        eid = row.get("entity_id")
        if not eid:
            continue
        eid = str(eid)
        if override_ids and eid not in override_ids:
            continue
        if shard_enabled:
            shard_val = int(hash_text(eid)[:8], 16) % shard_count
            if shard_val != shard_id:
                skipped_by_shard += 1
                continue
        tags = row.get("tags_raw") or {}
        metrics = row.get("metrics_summary") or {}
        if require_candidate and not tags.get("candidate"):
            skipped_by_filter += 1
            continue
        if require_quality_lock_ok and not tags.get("quality_lock_ok"):
            skipped_by_filter += 1
            continue
        if require_memory_non_negative:
            mem_val = metrics.get("memory_score_k10")
            if mem_val is None or float(mem_val) < 0.0:
                skipped_by_filter += 1
                continue
        if min_quality_lock is not None:
            q_val = metrics.get("QualityLock")
            if q_val is None or float(q_val) < float(min_quality_lock):
                skipped_by_filter += 1
                continue
        if min_r_mean is not None:
            r_val = metrics.get("R_mean_lastW")
            if r_val is None or float(r_val) < float(min_r_mean):
                skipped_by_filter += 1
                continue
        if max_phase_var is not None:
            pv_val = metrics.get("phase_var_lastW")
            if pv_val is None or float(pv_val) > float(max_phase_var):
                skipped_by_filter += 1
                continue
        if top_k_by not in metrics:
            if top_k_by == "priority_score":
                score = metrics.get("R_mean_lastW")
                if score is None:
                    score = 0.0
            else:
                raise RuntimeError(f"candidate_source.filter.top_k_by missing in metrics_summary: {top_k_by}")
        score_val = metrics.get(top_k_by)
        if score_val is None and top_k_by == "priority_score":
            score_val = metrics.get("R_mean_lastW")
            if score_val is None:
                score_val = 0.0
        if score_val is None:
            raise RuntimeError(f"candidate_source.filter.top_k_by missing in metrics_summary: {top_k_by}")
        score = float(score_val)
        if top_k:
            key = (score, eid)
            if len(heap) < top_k:
                heapq.heappush(heap, (key, row))
            else:
                if key > heap[0][0]:
                    heapq.heapreplace(heap, (key, row))
        else:
            filtered.append((score, eid, row))

    if top_k:
        selected = sorted(heap, key=lambda it: (-it[0][0], it[0][1]))
        return [row for _, row in selected], skipped_by_filter, skipped_by_shard

    filtered.sort(key=lambda it: (-it[0], it[1]))
    return [row for _, _, row in filtered], skipped_by_filter, skipped_by_shard


def main() -> None:
    parser = argparse.ArgumentParser(description="olar sweep (V1).")
    parser.add_argument("--config", required=True, help="Path to sweep config JSON.")
    parser.add_argument("--output-dir", required=False, help="Override output dir.")
    parser.add_argument(
        "--stop-file",
        required=False,
        help="Optional stop file path for graceful shutdown (checked between evals).",
    )
    parser.add_argument(
        "--entity-id",
        action="append",
        help="Restrict sweep to a specific entity_id (repeatable).",
    )
    parser.add_argument(
        "--entity-ids",
        help="Comma-separated list of entity_ids to process.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = _load_json(config_path)
    override_ids: List[str] = []
    if args.entity_ids:
        override_ids.extend([part.strip() for part in args.entity_ids.split(",") if part.strip()])
    if args.entity_id:
        override_ids.extend([str(val) for val in args.entity_id if str(val).strip()])
    if override_ids:
        cfg["_override_entity_ids"] = override_ids
    output_dir = Path(args.output_dir) if args.output_dir else None
    stop_file = args.stop_file or cfg.get("stop_file")
    stop_path = Path(stop_file) if stop_file else None

    inputs = cfg.get("inputs", {})
    entities_path = Path(inputs.get("entities_candidates_jsonl", "data/processed/ola2/raw/entities_candidates.jsonl"))
    blocks_path = _resolve_input_path(inputs.get("blocks_json", "data/processed/ola1/simple_blocks.json"))
    dna_path = _resolve_input_path(inputs.get("dof_dna_catalog_csv", "data/processed/ola1/dof_dna_catalog.csv"))
    print(
        "[olar_sweep] Wiring Check: "
        f"blocks_json={blocks_path}, dna_catalog={dna_path}, theta_internal_required=true"
    )

    outputs = cfg.get("outputs", {})
    evaluations_path = _resolve_output(outputs.get("evaluations_jsonl", "evaluations.jsonl"), output_dir)

    if not entities_path.exists():
        raise RuntimeError(f"No entities found in {entities_path}")

    _reset_outputs_if_needed(cfg, evaluations_path)
    entities, entities_skipped_by_filter, entities_skipped_by_shard = _select_candidates(cfg, entities_path)
    blocks = load_simple_blocks(blocks_path)
    block_id_key = "block_id"
    dna_map = load_dna_catalog(dna_path, id_key=block_id_key)
    blocks_by_id = {str(b.get(block_id_key)): b for b in blocks if b.get(block_id_key)}

    if not entities:
        raise RuntimeError("No candidates found for sweep.")

    seed_policy = cfg.get("seed_policy", {})
    seed_mode = str(seed_policy.get("mode", "deterministic")).lower()
    seed_salt = str(seed_policy.get("salt", "sweep_v1"))
    seeds = int(seed_policy.get("seeds", 1))
    min_seeds_required = int(seed_policy.get("min_seeds_required", seeds))
    engine_defaults = cfg.get("engine_defaults")
    engine_variation = cfg.get("engine_variation")
    if not isinstance(engine_defaults, dict):
        raise RuntimeError("Sweep config missing engine_defaults for engine reconstruction.")
    if not isinstance(engine_variation, dict):
        raise RuntimeError("Sweep config missing engine_variation for engine reconstruction.")
    bin_map = {
        "K_local_edges": "K_local",
        "kappa_edges": "kappa_global",
        "tau_field_edges": "tau_field",
        "sigma0_edges": "sigma0",
        "sigma_tc_edges": "sigma_tc",
    }
    bins_cfg = engine_variation.get("bins") or {}
    varied = []
    fixed = []
    for edges_key, param_key in bin_map.items():
        edges = bins_cfg.get(edges_key)
        if isinstance(edges, list) and len(edges) >= 2:
            varied.append(param_key)
        else:
            fixed.append(param_key)
    fixed.extend(["dt", "T_ticks", "W", "sigma_theta_init"])
    varied_str = ", ".join(sorted(set(varied)))
    fixed_str = ", ".join(sorted(set(fixed)))
    print(f"[olar_sweep] Parameter Strategy: Varied={{{varied_str}}}, Fixed/Defaults={{{fixed_str}}}")

    config_hash = f"sha256:{hash_file(config_path)}"
    code_hash = f"sha256:{hash_file(Path(__file__))}"
    inputs_hash = f"sha256:{hash_text('|'.join([hash_file(entities_path)]))}"
    machine = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }

    progress_cfg = cfg.get("progress", {})
    flush_every = int(progress_cfg.get("flush_every_evals", 0) or 0)
    log_every_evals = int(progress_cfg.get("log_every_evals", 0) or 0)
    if flush_every <= 0:
        flush_every = 500
    budgets = cfg.get("budgets", {}) or {}
    early_stop = budgets.get("early_stop") or {}
    early_after = int(early_stop.get("after_seeds", 0) or 0)
    early_threshold = early_stop.get("fail_threshold")
    early_enabled = early_after > 0 and early_threshold is not None
    max_evals_per_entity = int(budgets.get("max_evals_per_entity", 0) or 0)

    eval_rows: List[Dict[str, Any]] = []
    seen_eval_ids, eval_offset = scan_jsonl_ids(evaluations_path, lambda r: r.get("eval_id"))
    existing_eval_ids = len(seen_eval_ids)
    print(f"[olar_sweep] WARNING: dedupe skip [0 / {existing_eval_ids}] (this_run / total_existing)")
    if entities_skipped_by_shard:
        print(f"[olar_sweep] skipped_by_shard={entities_skipped_by_shard}")
    evals_deduped = 0
    evals_written_total = 0
    evals_seen_total = 0
    entities_processed = 0
    sweep_run_id = str(uuid.uuid4())
    stop_requested = False
    neighborhood = cfg.get("neighborhood", {}) or {}
    neighborhood_mode = str(neighborhood.get("mode", "param_bin_neighbors"))
    max_neighbor_bins = int(neighborhood.get("max_neighbor_bins", 0))

    total_entities = len(entities)
    for cand_idx, entity in enumerate(entities):
        if stop_requested:
            break
        eid = str(entity.get("entity_id", ""))
        if not eid:
            continue
        print(f"[olar_sweep] start_entity={eid} index={cand_idx + 1}/{total_entities}", flush=True)
        entities_processed += 1
        base_bin_id = entity.get("engine_params_bin_id")
        if not base_bin_id:
            raise RuntimeError(f"Entity {eid} missing top-level engine_params_bin_id for sweep.")
        if not is_engine_params_bin_id(base_bin_id):
            raise RuntimeError(f"Entity {eid} has invalid engine_params_bin_id={base_bin_id!r}.")
        build_plan = entity.get("build_plan")
        if not isinstance(build_plan, dict):
            raise RuntimeError(f"Entity {eid} missing build_plan object for sweep.")
        assignment = entity.get("assignment")
        if not isinstance(assignment, dict):
            raise RuntimeError(f"Entity {eid} missing assignment for sweep.")
        template_name = entity.get("template_name")
        edges = entity.get("edges")
        canonical_node_order = entity.get("canonical_node_order")
        parent_ids = entity.get("parent_ids")
        if not isinstance(edges, list):
            raise RuntimeError(f"Entity {eid} missing edges for sweep.")
        if not isinstance(canonical_node_order, list):
            raise RuntimeError(f"Entity {eid} missing canonical_node_order for sweep.")
        if not isinstance(parent_ids, list):
            raise RuntimeError(f"Entity {eid} missing parent_ids for sweep.")
        if len(range(seeds)) < min_seeds_required:
            continue
        if min_seeds_required:
            print(
                "[olar_sweep] min_seeds_required"
                f" entity_id={eid}"
                f" required={min_seeds_required}"
                f" planned={seeds}"
            )
        try:
            hydrated_entity = build_hydrated_entity(entity, blocks_by_id, dna_map, block_id_key=block_id_key)
        except BlockHydrationError:
            raise
        if neighborhood_mode == "param_bin_neighbors":
            bin_ids = neighbor_engine_params_bin_ids(base_bin_id, engine_variation.get("bins") or {}, max_neighbor_bins)
        else:
            bin_ids = [base_bin_id]
        evals_for_entity = 0
        stop_entity = False
        early_cut = False
        for param_bin_id in bin_ids:
            if seed_mode == "deterministic":
                seed_list = [_seed_from_entity(eid, i, seed_salt, param_bin_id) for i in range(seeds)]
            else:
                seed_list = [
                    int(hash_text(f"{eid}|{i}|{seed_salt}|{param_bin_id}")[:8], 16)
                    for i in range(seeds)
                ]
            engine_params = resolve_engine_params(
                engine_defaults,
                engine_variation.get("bins") or {},
                param_bin_id,
            )
            for idx, seed in enumerate(seed_list):
                if stop_path and stop_path.exists():
                    print("[olar_sweep] stop-file detected; stopping after current evals.")
                    try:
                        stop_path.unlink()
                    except OSError:
                        pass
                    stop_requested = True
                    break
                payload = {
                    "entity_id": eid,
                    "seed": int(seed),
                    "engine_params_bin_id": param_bin_id,
                    "role": "sweep",
                    "schema_version": "olar_evaluation_v1",
                }
                eval_id = hash_text(stable_dumps(payload))
                if eval_id in seen_eval_ids:
                    evals_deduped += 1
                    continue
                seen_eval_ids.add(eval_id)
                nodes = hydrated_entity.get("nodes") or []
                node_theta = [node.get("theta_internal") for node in nodes]
                node_omega = [node.get("omega_ref") for node in nodes]
                diff = DifferentialNetwork(
                    node_theta,
                    node_omega,
                    edges,
                    engine_params,
                    int(seed),
                )
                metrics_raw_full = diff.run()
                metrics_raw = {
                    k: v
                    for k, v in metrics_raw_full.items()
                    if v is None or isinstance(v, (str, int, float, bool))
                }
                metrics_raw, numeric_invalid = _sanitize_numbers(metrics_raw)
                early_cut = False
                if early_enabled and idx + 1 >= early_after:
                    r_mean = metrics_raw.get("R_network_S1_mean_lastW")
                    if r_mean is not None and float(r_mean) < float(early_threshold):
                        metrics_raw["early_stop_triggered"] = True
                        metrics_raw["early_stop_threshold"] = float(early_threshold)
                        metrics_raw["early_stop_after_seeds"] = early_after
                        early_cut = True
                tags_raw = {"seed_index": idx}
                reasons_raw: List[str] = []
                if numeric_invalid:
                    tags_raw["numeric_valid"] = False
                    tags_raw["candidate"] = False
                    reasons_raw.append("numeric_invalid_nan_or_inf")
                evaluation = {
                    "schema_version": "olar_evaluation_v1",
                    "run_session_id": sweep_run_id,
                    "timestamp_utc": utc_now_iso(),
                    "ola": int(cfg.get("ola", 2)),
                    "role": "sweep",
                    "entity_id": eid,
                    "eval_id": eval_id,
                    "seed": int(seed),
                    "engine_params_bin_id": param_bin_id,
                    "engine_params": engine_params,
                    "metrics_raw": metrics_raw,
                    "tags_raw": tags_raw,
                    "reasons_raw": reasons_raw,
                    "provenance": {
                        "config_hash": config_hash,
                        "code_hash": code_hash,
                        "inputs_hash": inputs_hash,
                        "machine": machine,
                    },
                }
                validate_evaluation(evaluation)
                eval_rows.append(evaluation)
                evals_for_entity += 1
                evals_seen_total += 1
                if log_every_evals and evals_seen_total % log_every_evals == 0:
                    print(
                        "[olar_sweep] progress"
                        f" evals_seen={evals_seen_total}"
                        f" evals_written={evals_written_total}"
                        f" entities_processed={entities_processed}"
                        f" entity_index={cand_idx + 1}/{total_entities}",
                        flush=True,
                    )
                if flush_every and len(eval_rows) >= flush_every:
                    evals_written_total += append_jsonl(
                        evaluations_path,
                        eval_rows,
                        validate=validate_evaluation,
                        allow_nan=False,
                    )
                    eval_rows.clear()
                if early_cut:
                    break
                if max_evals_per_entity and evals_for_entity >= max_evals_per_entity:
                    stop_entity = True
                    break
            if stop_requested or stop_entity or early_cut:
                break
        if stop_requested:
            break
        print(
            "[olar_sweep] entity_done"
            f" entity_id={eid}"
            f" evals_for_entity={evals_for_entity}",
            flush=True,
        )

    written = append_jsonl(
        evaluations_path,
        eval_rows,
        validate=validate_evaluation,
        allow_nan=False,
    )
    evals_written_total += written
    eval_size = evaluations_path.stat().st_size if evaluations_path.exists() else eval_offset
    write_resume_index(evaluations_path.with_suffix(".resume.json"), eval_size, {"ids": len(seen_eval_ids)})
    print(
        "[olar_sweep] evaluations_written="
        f"{evals_written_total}"
        f" entities_processed={entities_processed}"
        f" entities_skipped_by_filter={entities_skipped_by_filter}"
        f" dedupe_skips={evals_deduped}"
    )
    print(
        "[olar_sweep] WARNING: dedupe skip"
        f" [{evals_deduped} / {len(seen_eval_ids)}]"
        " (this_run / total_existing)"
    )


if __name__ == "__main__":
    main()
