"""Ola-recursive explorer (V1)."""

from __future__ import annotations

import argparse
import json
import platform
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from core.ids.hashing import hash_file, hash_text, stable_dumps
from core.ids.plan import build_plan_payload, canonicalize_plan, engine_params_bin_id, entity_id_from_plan
from core.io.jsonl import append_jsonl, iter_jsonl, scan_jsonl_ids, write_resume_index
from core.templates.registry import canonicalize_edges, load_templates
from core.io.schema_validation import validate_attempt, validate_entity_candidate
from olar.explorer_engine import compute_metrics, gate_candidate


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _norm_run_id(val: Any) -> str:
    try:
        f = float(val)
        return str(int(f))
    except Exception:
        return str(val)


def _short_id(value: Optional[str], keep: int = 8) -> str:
    if not value:
        return ""
    text = str(value)
    if len(text) <= keep * 2:
        return text
    return f"{text[:keep]}..{text[-keep:]}"


def _extract_blocks(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("blocks", "promoted_blocks"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        results = raw.get("results")
        if isinstance(results, dict) and isinstance(results.get("blocks"), list):
            return results["blocks"]
    return []


def _load_dna_map(path: Path, id_key: str) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        return {}
    import csv

    out: Dict[str, Dict[str, str]] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get(id_key) if id_key in row else row.get("run_id")
            rid = _norm_run_id(rid)
            dof_grade = str(row.get("dof_grade", "") or row.get("dna_grade", "")).upper()
            out[rid] = {
                "dof_grade": dof_grade if dof_grade else "",
                "dof_family_id": str(row.get("dof_family_id", "") or ""),
                "dof_family_friendly": str(row.get("dof_family_friendly", "") or ""),
            }
    return out


def _resolve_output(path_str: str, output_dir: Optional[Path]) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if output_dir is not None:
        return output_dir / path
    return path


def _sample_param_from_edges(edges: List[float], rng: random.Random, fallback: float) -> float:
    if not edges or len(edges) < 2:
        return float(fallback)
    idx = rng.randrange(0, len(edges) - 1)
    lo, hi = float(edges[idx]), float(edges[idx + 1])
    return rng.uniform(lo, hi)


def _sample_engine_params(
    defaults: Dict[str, float],
    variation_cfg: Dict[str, Any],
    rng: random.Random,
) -> Tuple[Dict[str, float], str]:
    if not variation_cfg.get("enabled", False):
        return dict(defaults), "fixed"
    bins = variation_cfg.get("bins", {})
    edges_map = {
        "K_local": bins.get("K_local_edges", []),
        "kappa_global": bins.get("kappa_edges", []),
        "tau_field": bins.get("tau_field_edges", []),
        "sigma0": bins.get("sigma0_edges", []),
        "sigma_tc": bins.get("sigma_tc_edges", []),
    }
    params = dict(defaults)
    bin_ids: Dict[str, int] = {}
    for key, edges in edges_map.items():
        if edges and len(edges) >= 2:
            idx = rng.randrange(0, len(edges) - 1)
            lo, hi = float(edges[idx]), float(edges[idx + 1])
            params[key] = rng.uniform(lo, hi)
            bin_ids[key] = idx
        else:
            params[key] = float(params[key])
            bin_ids[key] = 0
    bin_id = engine_params_bin_id(
        bin_ids["K_local"],
        bin_ids["kappa_global"],
        bin_ids["tau_field"],
        bin_ids["sigma0"],
        bin_ids["sigma_tc"],
    )
    return params, bin_id


def _select_blocks(
    blocks: List[Dict[str, Any]],
    target_families: Optional[Sequence[str]],
    nodes: int,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    if nodes <= 0:
        return []
    if target_families:
        fam_lower = {str(f).lower() for f in target_families}
        pool = [b for b in blocks if str(b.get("family", "")).lower() in fam_lower]
    else:
        pool = list(blocks)
    if len(pool) < nodes:
        return []
    return rng.sample(pool, nodes)


def _entity_id_from_plan(payload: Dict[str, Any]) -> str:
    return entity_id_from_plan(payload)


def _eval_id_from_payload(
    entity_id: str,
    seed: int,
    engine_params_bin_id: str,
    role: str,
    schema_version: str,
) -> str:
    payload = {
        "entity_id": entity_id,
        "seed": int(seed),
        "engine_params_bin_id": engine_params_bin_id,
        "role": role,
        "schema_version": schema_version,
    }
    return hash_text(stable_dumps(payload))


def main() -> None:
    parser = argparse.ArgumentParser(description="olar explorer (V1).")
    parser.add_argument("--config", required=True, help="Path to explorer config JSON.")
    parser.add_argument("--output-dir", required=False, help="Override output dir.")
    parser.add_argument("--stop-file", required=False, help="Stop-file path for graceful shutdown.")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = _load_json(config_path)
    output_dir = Path(args.output_dir) if args.output_dir else None
    stop_file = args.stop_file or cfg.get("stop_file")
    stop_path = Path(stop_file) if stop_file else None

    inputs = cfg.get("inputs", {})
    blocks_path = Path(inputs.get("blocks_json", "data/processed/ola1/simple_blocks.json"))
    dna_path = Path(inputs.get("dof_dna_catalog_csv", "data/processed/ola1/dof_dna_catalog.csv"))
    templates_path = Path(inputs.get("templates_json", "data/config/ola2/ola2_templates.json"))

    outputs = cfg.get("outputs", {})
    attempts_path = _resolve_output(outputs.get("attempts_jsonl", "attempts.jsonl"), output_dir)
    entities_path = _resolve_output(outputs.get("entities_candidates_jsonl", "entities_candidates.jsonl"), output_dir)
    report_path = None
    if outputs.get("report_md"):
        report_path = _resolve_output(outputs.get("report_md", "report.md"), output_dir)

    raw_blocks = _load_json(blocks_path)
    blocks = _extract_blocks(raw_blocks)
    if not blocks:
        raise RuntimeError(f"No blocks found in {blocks_path}")

    block_selection = cfg.get("block_selection", {})
    require_dna = bool(block_selection.get("require_dna", True))
    allowed_grades = {str(g).upper() for g in (block_selection.get("allowed_dof_grades") or [])}
    allowed_family_ids = {str(f) for f in (block_selection.get("allowed_family_ids") or [])}
    denied_family_ids = {str(f) for f in (block_selection.get("denied_family_ids") or [])}
    block_id_key = str(block_selection.get("block_id_key", "block_id"))
    dna_map = _load_dna_map(dna_path, block_id_key)

    dropped_missing_dna = 0
    dropped_not_allowed_grade = 0
    dropped_not_allowed_family = 0
    total_blocks = len(blocks)
    filtered_blocks: List[Dict[str, Any]] = []
    for b in blocks:
        origin = b.get(block_id_key) or b.get("origin_run_id")
        if origin is None or origin == "":
            if require_dna:
                dropped_missing_dna += 1
                continue
            filtered_blocks.append(b)
            continue
        rid = _norm_run_id(origin)
        dna_row = dna_map.get(rid)
        if not dna_row:
            if require_dna:
                dropped_missing_dna += 1
                continue
            filtered_blocks.append(b)
            continue
        dof_grade = str(dna_row.get("dof_grade", "")).upper()
        b["dof_grade"] = dof_grade
        b["dof_family_id"] = dna_row.get("dof_family_id", "")
        b["dof_family_friendly"] = dna_row.get("dof_family_friendly", "")
        if allowed_grades and dof_grade not in allowed_grades:
            dropped_not_allowed_grade += 1
            continue
        fam_id = str(b.get("dof_family_id") or "")
        if allowed_family_ids and fam_id not in allowed_family_ids:
            dropped_not_allowed_family += 1
            continue
        if denied_family_ids and fam_id in denied_family_ids:
            dropped_not_allowed_family += 1
            continue
        filtered_blocks.append(b)
    blocks = filtered_blocks
    print(f"[olar_explorer] blocks_loaded={total_blocks} blocks_selected={len(blocks)}")
    if not blocks:
        raise RuntimeError("No blocks left after DOF filtering.")

    templates = load_templates(templates_path)
    dof_grade_counts: Dict[str, int] = {}
    for b in blocks:
        grade = str(b.get("dof_grade", "")).upper() or "UNKNOWN"
        dof_grade_counts[grade] = dof_grade_counts.get(grade, 0) + 1
    print(f"[olar_explorer] dof_grade_counts={dof_grade_counts}")

    template_nodes = [
        int(t.get("nodes", 0))
        for t in templates.values()
        if isinstance(t, dict) and int(t.get("nodes", 0)) > 0
    ]
    min_nodes = min(template_nodes) if template_nodes else 0
    max_nodes = max(template_nodes) if template_nodes else 0
    print(f"[olar_explorer] template_nodes_min={min_nodes} template_nodes_max={max_nodes}")
    if min_nodes and len(blocks) < min_nodes:
        raise RuntimeError(
            f"Not enough blocks for templates: have={len(blocks)} min_required={min_nodes}"
        )

    engine_defaults = cfg.get("engine_defaults", {})
    defaults = {
        "dt": float(engine_defaults.get("dt", 1.0)),
        "T_ticks": int(engine_defaults.get("T_ticks", 200)),
        "W": int(engine_defaults.get("W", 20)),
        "K_local": float(engine_defaults.get("K_local", 0.45)),
        "kappa_global": float(engine_defaults.get("kappa_global", 0.30)),
        "tau_field": float(engine_defaults.get("tau_field", 120.0)),
        "sigma0": float(engine_defaults.get("sigma0", 0.30)),
        "sigma_tc": float(engine_defaults.get("sigma_tc", 60.0)),
        "sigma_theta_init": float(engine_defaults.get("sigma_theta_init", 0.5)),
    }
    variation_cfg = cfg.get("engine_variation", {})

    seed_policy = cfg.get("seed_policy", {})
    seed_mode = str(seed_policy.get("mode", "deterministic")).lower()
    seed_salt = str(seed_policy.get("salt", "explorer_v1"))
    seeds_per_attempt = int(seed_policy.get("seeds_per_attempt", 1))
    rng_seed = int(hash_text(seed_salt)[:8], 16)
    rng = random.Random(rng_seed)

    config_hash = f"sha256:{hash_file(config_path)}"
    code_hash = f"sha256:{hash_file(Path(__file__))}"
    blocks_hash = f"sha256:{hash_file(blocks_path)}"
    templates_hash = f"sha256:{hash_file(templates_path)}"
    machine = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }

    attempts_rows: List[Dict[str, Any]] = []
    entities_rows: List[Dict[str, Any]] = []
    output_policy = cfg.get("output_policy", {}) or {}
    emit_non_candidates = bool(output_policy.get("emit_non_candidates", False))

    seen_eval_ids, attempts_offset = scan_jsonl_ids(
        attempts_path, lambda r: (r.get("ids") or {}).get("eval_id") or r.get("eval_id")
    )
    seen_entities, entities_offset = scan_jsonl_ids(
        entities_path, lambda r: (r.get("ids") or {}).get("entity_id") or r.get("entity_id")
    )
    existing_eval_ids = len(seen_eval_ids)
    if existing_eval_ids:
        print(
            "[olar_explorer] WARNING: dedupe skip"
            f" [0 / {existing_eval_ids}]"
            " (this_run / total_existing)"
        )

    targets = cfg.get("targets", [])
    eval_idx = 0
    attempt_id = 0
    attempts_candidates_written = 0
    entities_candidates_written = 0
    dropped_non_candidate = 0
    run_id = str(uuid.uuid4())
    progress_cfg = cfg.get("progress", {})
    log_every = int(progress_cfg.get("log_every_terms", 10) or 10)
    if log_every <= 0:
        log_every = 10
    stop_requested = False
    for target_idx, target in enumerate(targets):
        if stop_requested:
            break
        target_name = target.get("name", "unknown")
        template_names = target.get("templates", [])
        budget = int(target.get("budget_evals", 0))
        target_families = target.get("allowed_block_families")
        target_phase = target.get("phase", "phase1")
        target_index = int(target.get("index", target_idx))
        if budget <= 0:
            continue
        new_evals = 0
        for local_idx in range(budget):
            if stop_path and stop_path.exists():
                print("[olar_explorer] stop-file detected; stopping after current batch.", flush=True)
                try:
                    stop_path.unlink()
                except OSError:
                    pass
                stop_requested = True
                break
            if (local_idx + 1) % log_every == 0:
                print(".", end="", flush=True)
            tmpl_name = rng.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            if not tmpl:
                continue
            nodes = int(tmpl.get("nodes", 0))
            assignment_blocks = _select_blocks(blocks, target_families, nodes, rng)
            if len(assignment_blocks) != nodes:
                continue
            assignment_ids = [str(b.get("block_id")) for b in assignment_blocks]
            edges = tmpl.get("edges", [])
            edge_weights_mode = tmpl.get("edge_weights_mode", "fixed_template")
            edge_weight_pattern = tmpl.get("edge_weight_pattern")
            canonical_nodes, canonical_edges = canonicalize_plan(assignment_ids, edges)
            plan_payload = build_plan_payload(
                int(cfg.get("ola", 2)),
                tmpl_name,
                canonical_nodes,
                canonical_edges,
                edge_weights_mode,
                edge_weight_pattern,
                canonical_nodes,
            )
            entity_id = _entity_id_from_plan(plan_payload)
            build_plan = plan_payload
            parent_ids = assignment_ids

            if seed_mode == "deterministic":
                base_seed = int(hash_text(f"{entity_id}|{seed_salt}|{eval_idx}")[:8], 16)
                seeds = [base_seed + i for i in range(seeds_per_attempt)]
            else:
                seeds = [rng.randint(0, 2**32 - 1) for _ in range(seeds_per_attempt)]

            engine_params, engine_params_bin_id = _sample_engine_params(defaults, variation_cfg, rng)
            block_map = {str(b.get("block_id")): b for b in assignment_blocks}
            blocks_in_order = []
            for bid in canonical_nodes:
                block = block_map.get(bid, {})
                blocks_in_order.append({"block_id": block.get("block_id"), "omega_ref": block.get("omega_ref")})
            for seed in seeds:
                eval_id = _eval_id_from_payload(
                    entity_id,
                    seed,
                    engine_params_bin_id,
                    "explorer",
                    "olar_attempt_v1",
                )
                if eval_id in seen_eval_ids:
                    continue
                seen_eval_ids.add(eval_id)
                new_evals += 1
                metrics_raw = compute_metrics(
                    {
                        "canonical_node_order": canonical_nodes,
                        "edges": canonical_edges,
                        "assignment": {"block_ids": canonical_nodes, "block_key_used": "block_id"},
                        "blocks": blocks_in_order,
                    },
                    engine_params,
                    seed,
                )
                tags_raw, reasons = gate_candidate(
                    metrics_raw,
                    cfg.get("tagging_thresholds", {}),
                    str(cfg.get("tagging_thresholds", {}).get("viability_mode", "")),
                )
                tags_raw = dict(tags_raw)
                tags_raw.setdefault("labels", [])
                tags_raw.setdefault("thresholds_version", "")
                tags_raw["emitted"] = True
                candidate = bool(tags_raw.get("candidate"))
                if candidate:
                    attempts_candidates_written += 1
                attempt = {
                    "schema_version": "olar_attempt_v1",
                    "run_session_id": run_id,
                    "timestamp_utc": _utc_now(),
                    "ola": int(cfg.get("ola", 2)),
                    "role": "explorer",
                    "entity_id": entity_id,
                    "eval_id": eval_id,
                    "target": {"name": target_name, "index": target_index, "phase": target_phase},
                    "build_plan": build_plan,
                    "template_name": tmpl_name,
                    "edges": canonical_edges,
                    "canonical_node_order": canonical_nodes,
                    "assignment": {"block_ids": assignment_ids, "block_key_used": "block_id"},
                    "seed": seed,
                    "engine_params_bin_id": engine_params_bin_id,
                    "engine_params": engine_params,
                    "metrics_raw": metrics_raw,
                    "tags_raw": tags_raw,
                    "reasons_raw": reasons,
                    "provenance": {
                        "config_hash": config_hash,
                        "blocks_hash": blocks_hash,
                        "templates_hash": templates_hash,
                        "code_hash": code_hash,
                        "machine": machine,
                    },
                }
                validate_attempt(attempt)
                attempts_rows.append(attempt)
                attempt_id += 1
                if entity_id in seen_entities:
                    continue
                if not candidate and not emit_non_candidates:
                    dropped_non_candidate += 1
                    continue
                seen_entities.add(entity_id)
                source_eval_id = ""
                if attempts_rows:
                    source_eval_id = attempts_rows[-1].get("eval_id") or (attempts_rows[-1].get("ids") or {}).get(
                        "eval_id", ""
                    )
                metrics_summary = {
                    "R_mean_lastW": metrics_raw.get("R_mean_lastW"),
                    "phase_var_lastW": metrics_raw.get("phase_var_lastW"),
                    "QualityLock": metrics_raw.get("QualityLock"),
                    "memory_score_k10": metrics_raw.get("memory_score_k10"),
                    "omega_eff": metrics_raw.get("omega_eff"),
                }
                entity_tags = dict(tags_raw)
                entity_tags["emitted"] = True
                entity = {
                    "schema_version": "olar_entity_candidate_v1",
                    "run_session_id": run_id,
                    "timestamp_utc": _utc_now(),
                    "ola": int(cfg.get("ola", 2)),
                    "entity_id": entity_id,
                    "source_eval_id": source_eval_id,
                    "build_plan": build_plan,
                    "template_name": tmpl_name,
                    "edges": canonical_edges,
                    "canonical_node_order": canonical_nodes,
                    "assignment": {"block_ids": assignment_ids, "block_key_used": "block_id"},
                    "parent_ids": parent_ids,
                    "seed": seed,
                    "engine_params_bin_id": engine_params_bin_id,
                    "metrics_summary": metrics_summary,
                    "tags_raw": entity_tags,
                    "reasons_raw": reasons,
                    "provenance": {
                        "config_hash": config_hash,
                        "blocks_hash": blocks_hash,
                        "templates_hash": templates_hash,
                        "code_hash": code_hash,
                    },
                }
                validate_entity_candidate(entity)
                entities_rows.append(entity)
                if candidate:
                    entities_candidates_written += 1
                print("", flush=True)
                print(
                    "[explorer_cli] wrote attempt"
                    f" [{new_evals} / {budget}]"
                    f" entity={_short_id(entity_id)}"
                    f" eval={_short_id(eval_id)}"
                    f" seed={seed}"
                    f" bin={engine_params_bin_id}"
                    f" candidate={candidate}",
                    flush=True,
                )
                print(
                    "[explorer_cli] wrote entity"
                    f" entity={_short_id(entity_id)}"
                    f" source_eval={_short_id(source_eval_id)}"
                    f" seed={seed}"
                    f" bin={engine_params_bin_id}"
                    f" candidate={candidate}",
                    flush=True,
                )
            eval_idx += 1

    attempts_written = append_jsonl(attempts_path, attempts_rows, validate=validate_attempt)
    entities_written = append_jsonl(entities_path, entities_rows, validate=validate_entity_candidate)
    total_attempts = sum(1 for _ in iter_jsonl(attempts_path)) if attempts_path.exists() else 0
    total_entities = sum(1 for _ in iter_jsonl(entities_path)) if entities_path.exists() else 0
    total_candidates = sum(
        1 for row in iter_jsonl(entities_path) if (row.get("tags_raw") or {}).get("candidate") is True
    )
    attempts_size = attempts_path.stat().st_size if attempts_path.exists() else attempts_offset
    entities_size = entities_path.stat().st_size if entities_path.exists() else entities_offset
    write_resume_index(attempts_path.with_suffix(".resume.json"), attempts_size, {"ids": len(seen_eval_ids)})
    write_resume_index(entities_path.with_suffix(".resume.json"), entities_size, {"ids": len(seen_entities)})
    print(
        "[olar_explorer] "
        f"attempts_written={attempts_written} entities_written={entities_written} "
        f"entities_written_candidate_true={entities_candidates_written} dropped_non_candidate={dropped_non_candidate} "
        f"dropped_missing_dna={dropped_missing_dna} dropped_not_allowed_grade={dropped_not_allowed_grade} "
        f"dropped_not_allowed_family={dropped_not_allowed_family} "
        f"total_attempts={total_attempts} total_entities={total_entities} total_candidates={total_candidates}"
    )
    # Reports are generated by core.catalog.builder to keep explorer output clean.


if __name__ == "__main__":
    main()
