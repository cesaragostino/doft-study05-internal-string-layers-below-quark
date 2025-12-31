"""Explorer V4 CLI (DOF-only, clean-room)."""

from __future__ import annotations

import argparse
import json
import platform
import random
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from core.ids.hashing import hash_file, hash_text, stable_dumps
from core.ids.time import utc_now_iso
from core.io.jsonl import append_jsonl, scan_jsonl_ids, write_resume_index
from core.templates.registry import load_templates
from core.io.schema_validation import validate_attempt, validate_entity_candidate
from olar.explorer_engine import compute_metrics, gate_candidate
from olar.explorer_pool import build_block_pool, load_dna_catalog, load_simple_blocks
from olar.explorer_search import build_plan, choose_engine_params, choose_template, sample_blocks

def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _resolve_path(path_str: str, base_dir: Optional[Path]) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if base_dir is not None:
        return base_dir / path
    return path


def _resolve_inputs(cfg: Dict[str, Any], wiring: Dict[str, Any]) -> Dict[str, Path]:
    inputs = cfg.get("inputs", {})
    wiring_inputs = (wiring or {}).get("inputs", {})
    ola1 = wiring_inputs.get("ola1", {})
    blocks_path = Path(inputs.get("blocks_json", ola1.get("simple_blocks_json", "")))
    dna_path = Path(inputs.get("dof_dna_catalog_csv", ola1.get("dof_dna_catalog_csv", "")))
    templates_path = Path(inputs.get("templates_json", "data/config/ola2/ola2_templates.json"))
    if not blocks_path or not dna_path:
        raise RuntimeError("Explorer inputs require simple_blocks.json and dof_dna_catalog.csv")
    return {
        "blocks_json": blocks_path,
        "dof_dna_catalog_csv": dna_path,
        "templates_json": templates_path,
    }


def _resolve_outputs(cfg: Dict[str, Any], output_root: Optional[Path]) -> Dict[str, Path]:
    outputs = cfg.get("outputs", {})
    return {
        "attempts_jsonl": _resolve_path(outputs.get("attempts_jsonl", "attempts.jsonl"), output_root),
        "entities_candidates_jsonl": _resolve_path(
            outputs.get("entities_candidates_jsonl", "entities_candidates.jsonl"),
            output_root,
        ),
        "report_md": _resolve_path(outputs.get("report_md", "report.md"), output_root),
    }


def _resolve_runtime(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "seed_policy": cfg.get("seed_policy", {}),
        "engine_defaults": cfg.get("engine_defaults", {}),
        "engine_variation": cfg.get("engine_variation", {}),
        "tagging_thresholds": cfg.get("tagging_thresholds", {}),
        "progress": cfg.get("progress", {}),
    }


def _short_id(value: Optional[str], keep: int = 8) -> str:
    if not value:
        return ""
    return value[:keep]


def main() -> None:
    parser = argparse.ArgumentParser(description="Explorer V4 CLI (DOF-only).")
    parser.add_argument("--config", required=True, help="Path to olaX_explorer.json.")
    parser.add_argument("--run-inputs", required=True, help="Path to doft_run_inputs_v4.json.")
    parser.add_argument("--output-root", required=False, help="Override output root.")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    wiring_path = Path(args.run_inputs)
    cfg = _load_json(cfg_path)
    wiring = _load_json(wiring_path)
    output_root = Path(args.output_root) if args.output_root else None

    inputs = _resolve_inputs(cfg, wiring)
    outputs = _resolve_outputs(cfg, output_root)
    runtime = _resolve_runtime(cfg)

    print("[explorer_cli] resolved inputs:")
    for k, v in inputs.items():
        print(f"- {k}: {v}")
    print("[explorer_cli] resolved outputs:")
    for k, v in outputs.items():
        print(f"- {k}: {v}")
    print("[explorer_cli] runtime config:")
    for k, v in runtime.items():
        print(f"- {k}: {v}")

    blocks = load_simple_blocks(inputs["blocks_json"])
    block_selection = cfg.get("block_selection", {})
    block_id_key = str(block_selection.get("block_id_key", "block_id"))
    dna_map = load_dna_catalog(inputs["dof_dna_catalog_csv"], id_key=block_id_key)
    pool = build_block_pool(blocks, dna_map, block_selection)
    print(f"[explorer_cli] blocks_loaded={len(blocks)} pool_filtered={len(pool)}")
    templates = load_templates(inputs["templates_json"])

    seed_policy = runtime.get("seed_policy", {})
    salt = str(seed_policy.get("salt", "explorer_v4"))
    rng = random.Random(int(hash_text(salt)[:8], 16))
    bin_salt = str(runtime.get("engine_variation", {}).get("salt", "bin_sample_v1"))

    attempts_path = outputs["attempts_jsonl"]
    entities_path = outputs["entities_candidates_jsonl"]
    seen_eval_ids, attempts_offset = scan_jsonl_ids(
        attempts_path, lambda r: r.get("eval_id")
    )
    seen_entities, entities_offset = scan_jsonl_ids(
        entities_path, lambda r: (r.get("ids") or {}).get("entity_id") or r.get("entity_id")
    )
    existing_eval_ids = len(seen_eval_ids)
    if existing_eval_ids:
        print(
            f"[explorer_cli] WARNING: dedupe skip [0 / {existing_eval_ids}]"
            " (this_run / total_existing)"
        )

    config_hash = f"sha256:{hash_file(cfg_path)}"
    blocks_hash = f"sha256:{hash_file(inputs['blocks_json'])}"
    dna_hash = f"sha256:{hash_file(inputs['dof_dna_catalog_csv'])}"
    templates_hash = f"sha256:{hash_file(inputs['templates_json'])}"
    inputs_hash = f"sha256:{hash_text('|'.join([hash_file(inputs['blocks_json']), hash_file(inputs['dof_dna_catalog_csv']), hash_file(inputs['templates_json'])]))}"
    code_hash = f"sha256:{hash_file(Path(__file__))}"
    machine = {"python": platform.python_version(), "platform": platform.platform()}

    attempts_rows = []
    entities_rows = []
    attempt_progress: Dict[str, Tuple[int, int]] = {}
    run_id = str(uuid.uuid4())
    output_policy = runtime.get("output_policy", {}) or {}
    emit_non_candidates = bool(output_policy.get("emit_non_candidates", False))
    progress_cfg = runtime.get("progress", {})
    flush_every = int(progress_cfg.get("flush_every_evals", 0) or 0)
    log_every = int(progress_cfg.get("log_every_terms", 0) or 0)
    evals_seen = 0
    evals_deduped = 0
    evals_since_flush = 0
    attempts_written_total = 0
    attempts_candidates_written = 0
    entities_written_total = 0
    entities_candidates_written = 0
    dropped_non_candidate = 0

    def _flush_attempts() -> None:
        nonlocal attempts_written_total
        if not attempts_rows:
            return
        written = append_jsonl(attempts_path, attempts_rows, validate=validate_attempt)
        for row in attempts_rows:
            tags = row.get("tags_raw") or {}
            if not tags.get("candidate"):
                eval_id = row.get("eval_id")
                if eval_id in attempt_progress:
                    attempt_progress.pop(eval_id, None)
                continue
            entity_id = row.get("entity_id")
            eval_id = row.get("eval_id")
            seed = row.get("seed")
            bin_id = row.get("engine_params_bin_id")
            progress = attempt_progress.pop(eval_id, None)
            budget_prefix = ""
            if progress:
                budget_prefix = f"[{progress[0]} / {progress[1]}] "
            print("")
            print(
                "[explorer_cli] wrote attempt"
                f" {budget_prefix}entity={_short_id(entity_id)}"
                f" eval={_short_id(eval_id)}"
                f" seed={seed}"
                f" bin={bin_id}"
                f" candidate={tags.get('candidate')}"
            )
        attempts_rows.clear()
        attempts_written_total += written

    def _flush_entities() -> None:
        nonlocal entities_written_total
        if not entities_rows:
            return
        written = append_jsonl(entities_path, entities_rows, validate=validate_entity_candidate)
        for row in entities_rows:
            tags = row.get("tags_raw") or {}
            print(
                "[explorer_cli] wrote entity"
                f" entity={_short_id(row.get('entity_id'))}"
                f" source_eval={_short_id(row.get('source_eval_id'))}"
                f" seed={row.get('seed')}"
                f" bin={row.get('engine_params_bin_id')}"
                f" candidate={tags.get('candidate')}"
            )
        entities_rows.clear()
        entities_written_total += written

    for target_idx, target in enumerate(cfg.get("targets", [])):
        budget_evals = int(target.get("budget_evals", 0))
        max_draws = int(progress_cfg.get("max_draws_per_target", 0) or 0)
        if max_draws <= 0:
            max_draws = max(budget_evals * 10, budget_evals + 100)
        draws = 0
        new_evals = 0
        while new_evals < budget_evals and draws < max_draws:
            draws += 1
            template = choose_template(target, templates, rng)
            nodes = int(template.get("nodes", 0))
            assignment = sample_blocks(pool, nodes, rng)
            if len(assignment) != nodes:
                continue
            build_payload, entity_id, canonical_nodes, canonical_edges, canonical_node_order = build_plan(
                int(cfg.get("ola", 2)), template, assignment
            )
            bin_rng = random.Random(int(hash_text(f"{entity_id}|{bin_salt}|0")[:8], 16))
            engine_params, param_bin_id = choose_engine_params(
                runtime.get("engine_defaults", {}), runtime.get("engine_variation", {}), bin_rng
            )
            seed = int(hash_text(f"{entity_id}|{salt}|0")[:8], 16)
            eval_payload = {
                "entity_id": entity_id,
                "seed": seed,
                "engine_params_bin_id": param_bin_id,
                "role": "explorer",
                "schema_version": "olar_attempt_v1",
            }
            eval_id = hash_text(stable_dumps(eval_payload))
            evals_seen += 1
            if eval_id in seen_eval_ids:
                evals_deduped += 1
                continue
            seen_eval_ids.add(eval_id)
            new_evals += 1

            block_map = {str(b.get("block_id")): b for b in assignment}
            blocks_in_order = []
            for bid in canonical_nodes:
                block = block_map.get(bid, {})
                blocks_in_order.append({"block_id": block.get("block_id"), "omega_ref": block.get("omega_ref")})
            metrics_raw = compute_metrics(
                {
                    "canonical_node_order": canonical_node_order,
                    "edges": canonical_edges,
                    "assignment": {"block_ids": canonical_nodes, "block_key_used": "block_id"},
                    "blocks": blocks_in_order,
                },
                engine_params,
                seed,
            )
            tags_raw, reasons = gate_candidate(
                metrics_raw,
                runtime.get("tagging_thresholds", {}),
                str(runtime.get("tagging_thresholds", {}).get("viability_mode", "")),
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
                "timestamp_utc": utc_now_iso(),
                "ola": int(cfg.get("ola", 2)),
                "role": "explorer",
                "entity_id": entity_id,
                "eval_id": eval_id,
                "target": {"name": target.get("name", ""), "index": target_idx, "phase": target.get("phase", "phase1")},
                "build_plan": build_payload,
                "template_name": template.get("name", ""),
                "edges": canonical_edges,
                "canonical_node_order": canonical_node_order,
                "assignment": {"block_ids": canonical_nodes, "block_key_used": "block_id"},
                "seed": seed,
                "engine_params_bin_id": param_bin_id,
                "engine_params": engine_params,
                "metrics_raw": metrics_raw,
                "tags_raw": tags_raw,
                "reasons_raw": reasons,
                "provenance": {
                    "config_hash": config_hash,
                    "blocks_hash": blocks_hash,
                    "dna_hash": dna_hash,
                    "templates_hash": templates_hash,
                    "code_hash": code_hash,
                    "inputs_hash": inputs_hash,
                    "block_id_key_used": block_id_key,
                    "machine": machine,
                },
            }
            validate_attempt(attempt)
            attempts_rows.append(attempt)
            attempt_progress[eval_id] = (new_evals, budget_evals)
            evals_since_flush += 1

            if entity_id in seen_entities:
                continue
            if not candidate and not emit_non_candidates:
                dropped_non_candidate += 1
                continue
            seen_entities.add(entity_id)
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
                "timestamp_utc": utc_now_iso(),
                "ola": int(cfg.get("ola", 2)),
                "entity_id": entity_id,
                "source_eval_id": eval_id,
                "build_plan": build_payload,
                "template_name": template.get("name", ""),
                "edges": canonical_edges,
                "canonical_node_order": canonical_node_order,
                "assignment": {"block_ids": canonical_nodes, "block_key_used": "block_id"},
                "parent_ids": canonical_nodes,
                "seed": seed,
                "engine_params_bin_id": param_bin_id,
                "metrics_summary": metrics_summary,
                "tags_raw": entity_tags,
                "reasons_raw": reasons,
                "provenance": {
                    "config_hash": config_hash,
                    "blocks_hash": blocks_hash,
                    "dna_hash": dna_hash,
                    "templates_hash": templates_hash,
                    "code_hash": code_hash,
                    "inputs_hash": inputs_hash,
                    "block_id_key_used": block_id_key,
                    "machine": machine,
                },
            }
            validate_entity_candidate(entity)
            entities_rows.append(entity)
            if candidate:
                entities_candidates_written += 1

            if flush_every and evals_since_flush >= flush_every:
                _flush_attempts()
                _flush_entities()
                evals_since_flush = 0

            if log_every and evals_seen % log_every == 0:
                print(".", end="", flush=True)

        if draws >= max_draws and new_evals < budget_evals:
            print(
                "[explorer_cli] max_draws reached"
                f" target={target.get('name', '')}"
                f" new_evals={new_evals}"
                f" budget_evals={budget_evals}"
            )

    _flush_attempts()
    _flush_entities()
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
        f"[explorer_cli] attempts_written={attempts_written_total}"
        f" entities_written={entities_written_total}"
        f" entities_written_candidate_true={entities_candidates_written}"
        f" dropped_non_candidate={dropped_non_candidate}"
        f" total_attempts={total_attempts}"
        f" total_entities={total_entities}"
        f" total_candidates={total_candidates}"
    )
    # Reports are generated by core.catalog.builder to keep explorer output clean.
    if evals_deduped:
        print(
            "[explorer_cli] WARNING: dedupe skip"
            f" [{evals_deduped} / {len(seen_eval_ids)}]"
            " (this_run / total_existing)"
        )

    # TODO: delegate to explorer_pool/search/engine layers.


if __name__ == "__main__":
    main()
