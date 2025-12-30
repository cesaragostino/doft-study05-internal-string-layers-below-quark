"""Deterministic catalog builder (V1)."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from core.io.jsonl import iter_jsonl


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _resolve_output(path_str: str, output_dir: Optional[Path]) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if output_dir is not None:
        return output_dir / path
    return path


def _resolve_input(path_str: str, base_dir: Path) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return base_dir / path


def _load_entities_candidates(path: Path) -> Dict[str, Dict[str, Any]]:
    entities: Dict[str, Dict[str, Any]] = {}
    for row in iter_jsonl(path):
        ids = row.get("ids") or {}
        eid = ids.get("entity_id") or row.get("entity_id")
        if not eid:
            continue
        eid = str(eid)
        if eid in entities:
            continue
        entities[eid] = row
    return entities


def _build_min_entity(entity_id: str, ola: int, provenance: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": "olar_entity_v1",
        "entity_id": entity_id,
        "ola": ola,
        "build_plan": "",
        "template_name": "",
        "canonical_node_order": [],
        "edges": [],
        "assignment": {},
        "parent_ids": [],
        "provenance": {
            "config_hash": provenance.get("config_hash"),
            "blocks_hash": provenance.get("blocks_hash"),
            "templates_hash": provenance.get("templates_hash"),
            "code_hash": provenance.get("code_hash"),
            "block_id_key_used": "",
        },
        "source": {
            "explorer_source_eval_id": "",
            "explorer_seed": 0,
            "explorer_engine_params_bin_id": "",
        },
    }


def _build_entity_record(candidate: Dict[str, Any], default_ola: int) -> Dict[str, Any]:
    assignment = candidate.get("assignment") if isinstance(candidate.get("assignment"), dict) else {}
    provenance = candidate.get("provenance") if isinstance(candidate.get("provenance"), dict) else {}
    block_key_used = assignment.get("block_key_used") or ""
    source_eval_id = candidate.get("source_eval_id") or ""
    seed = candidate.get("seed")
    engine_params_bin_id = candidate.get("engine_params_bin_id") or ""
    return {
        "schema_version": "olar_entity_v1",
        "ola": int(candidate.get("ola", default_ola)),
        "entity_id": str(candidate.get("entity_id", "")),
        "template_name": candidate.get("template_name"),
        "edges": candidate.get("edges"),
        "canonical_node_order": candidate.get("canonical_node_order"),
        "assignment": assignment,
        "build_plan": candidate.get("build_plan"),
        "parent_ids": candidate.get("parent_ids"),
        "provenance": {
            "config_hash": provenance.get("config_hash"),
            "blocks_hash": provenance.get("blocks_hash"),
            "templates_hash": provenance.get("templates_hash"),
            "code_hash": provenance.get("code_hash"),
            "block_id_key_used": block_key_used,
        },
        "source": {
            "explorer_source_eval_id": source_eval_id,
            "explorer_seed": int(seed) if isinstance(seed, (int, float)) else seed or 0,
            "explorer_engine_params_bin_id": engine_params_bin_id,
        },
    }


def _mean_std(values: List[float]) -> Tuple[Optional[float], Optional[float]]:
    if not values:
        return None, None
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, 0.0
    var = sum((val - mean) ** 2 for val in values) / (len(values) - 1)
    return mean, var**0.5


def _format_mean_std(mean: Optional[float], std: Optional[float]) -> str:
    if mean is None:
        return "n/a"
    if std is None:
        return f"{mean:.3f}"
    return f"{mean:.3f} ± {std:.3f}"


def _format_scalar(val: Optional[float]) -> str:
    if val is None:
        return "n/a"
    return f"{val:.3f}"


def _collect_metric(evals: List[Dict[str, Any]], key: str) -> List[float]:
    values: List[float] = []
    for row in evals:
        metrics = row.get("metrics_raw") or {}
        val = metrics.get(key)
        if isinstance(val, (int, float)):
            values.append(float(val))
    return values


def _best_eval_id_by_metric(evals: List[Dict[str, Any]], key: str) -> str:
    best_id = ""
    best_val = None
    for row in evals:
        metrics = row.get("metrics_raw") or {}
        val = metrics.get(key)
        if not isinstance(val, (int, float)):
            continue
        if best_val is None or float(val) > best_val:
            best_val = float(val)
            best_id = str(row.get("eval_id", "") or "")
    return best_id


def _node_count(row: Dict[str, Any]) -> int:
    canonical = row.get("canonical_node_order")
    if isinstance(canonical, list) and canonical:
        return len(canonical)
    assignment = row.get("assignment") if isinstance(row.get("assignment"), dict) else {}
    block_ids = assignment.get("block_ids")
    if isinstance(block_ids, list):
        return len(block_ids)
    return 0


def _edge_count(row: Dict[str, Any]) -> int:
    edges = row.get("edges")
    if isinstance(edges, list):
        return len(edges)
    return 0


def _density(edges: int, nodes: int) -> Optional[float]:
    if nodes < 2:
        return None
    max_edges = nodes * (nodes - 1) / 2
    if max_edges <= 0:
        return None
    return edges / max_edges


def _load_family_ids(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    family_by_id: Dict[str, str] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            eid = row.get("entity_id")
            if not eid:
                continue
            family = row.get("confirmed_family_id") or row.get("taxonomy_family_id") or ""
            family_by_id[str(eid)] = family
    return family_by_id


def _load_promoted_ids_from_csv(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    promoted: Set[str] = set()
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            block_id = row.get("block_id")
            if block_id:
                promoted.add(str(block_id))
    return promoted


def _load_promoted_ids_from_blocks(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        blocks = data.get("blocks")
    else:
        blocks = data
    if not isinstance(blocks, list):
        return set()
    promoted = set()
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_id = block.get("block_id")
        if block_id:
            promoted.add(str(block_id))
    return promoted


def _load_promoted_ids(promote_cfg_path: Path) -> Set[str]:
    if not promote_cfg_path.exists():
        return set()
    cfg = json.loads(promote_cfg_path.read_text())
    dna_csv = cfg.get("dna_output_csv")
    blocks_json = cfg.get("output_blocks_json")
    if dna_csv:
        promoted = _load_promoted_ids_from_csv(Path(dna_csv))
        if promoted:
            return promoted
    if blocks_json:
        return _load_promoted_ids_from_blocks(Path(blocks_json))
    return set()


def _summary_lines(
    title: str,
    rows: List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]],
    entities_candidates: Dict[str, Dict[str, Any]],
) -> List[str]:
    ids = {row[0] for row in rows}
    template_stats: Dict[str, Dict[str, int]] = {}
    for eid, candidate in entities_candidates.items():
        template_name = candidate.get("template_name") or "unknown"
        stats = template_stats.setdefault(template_name, {"total": 0, "count": 0})
        stats["total"] += 1
        if eid in ids:
            stats["count"] += 1
    lines = [
        f"Resumen por template ({title}):",
        "",
        f"| Template | Total | {title} | Rate |",
        "|---|---:|---:|---:|",
    ]
    for template_name in sorted(template_stats):
        stats = template_stats[template_name]
        total = stats["total"]
        count = stats["count"]
        rate = (count / total * 100.0) if total else 0.0
        lines.append(f"| {template_name} | {total} | {count} | {rate:.1f}% |")
    lines.append("")
    return lines


def _candidate_section(
    title: str,
    rows: List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]],
    entities_candidates: Dict[str, Dict[str, Any]],
    family_by_id: Dict[str, str],
) -> List[str]:
    if not rows:
        return []
    lines: List[str] = [f"## {title} Candidates", "", *_summary_lines(title, rows, entities_candidates)]
    for idx, (eid, candidate, evals) in enumerate(rows, start=1):
        template_name = candidate.get("template_name") or "unknown"
        nodes = _node_count(candidate)
        edges = _edge_count(candidate)
        density = _density(edges, nodes)
        block_ids = []
        assignment = candidate.get("assignment") if isinstance(candidate.get("assignment"), dict) else {}
        raw_block_ids = assignment.get("block_ids")
        if isinstance(raw_block_ids, list):
            block_ids = [str(bid) for bid in raw_block_ids]
        h_mean, h_std = _mean_std(_collect_metric(evals, "H_part_norm_mean_lastW"))
        pe_mean, pe_std = _mean_std(_collect_metric(evals, "PE_lockS1_norm"))
        r_mean, r_std = _mean_std(_collect_metric(evals, "R_network_S1_mean_lastW"))
        robustness = None
        metrics_summary = candidate.get("metrics_summary")
        if isinstance(metrics_summary, dict):
            val = metrics_summary.get("memory_score_k10")
            if isinstance(val, (int, float)):
                robustness = float(val)
        seeds_total = len(
            {
                int(row.get("seed"))
                for row in evals
                if isinstance(row.get("seed"), (int, float))
            }
        )
        if not seeds_total:
            seeds_total = len(evals)

        lines.extend(
            [
                f"### {title} #{idx}: {template_name} (N={nodes})",
                "",
                f"Entity ID: {eid}",
                f"Family ID: {family_by_id.get(eid) or 'n/a'}",
                "",
                "Metrics:",
                f"- R_network: {_format_mean_std(r_mean, r_std)}",
                f"- PE_lock: {_format_mean_std(pe_mean, pe_std)}",
                f"- H_part: {_format_mean_std(h_mean, h_std)}",
                f"- Robustness: {_format_scalar(robustness)}",
                "",
                "Topologia:",
                f"- Nodos: {nodes}",
                f"- Edges: {edges}",
                f"- Density: {_format_scalar(density)}" if density is not None else "- Density: n/a",
                "",
                "Composicion (blocks Ola1):",
                f"{', '.join(block_ids) if block_ids else 'n/a'}",
                "",
                "Sweep:",
                f"- Evals: {len(evals)}",
                f"- Seeds: {seeds_total}",
                "",
            ]
        )
    return lines


def _write_sections(report_path: Path, sections: List[str], markers: List[str]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_path.exists():
        existing = report_path.read_text()
        for marker in markers:
            if marker in existing:
                existing = existing.split(marker)[0].rstrip() + "\n\n"
        report_path.write_text(existing + "\n".join(sections).rstrip() + "\n")
    else:
        report_path.write_text("\n".join(sections).rstrip() + "\n")


def _write_report(report_path: Path, sections: List[str]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(sections).rstrip() + "\n")


def _rollup_key(row: Dict[str, Any]) -> Tuple[str, int]:
    template_name = row.get("template_name") or "unknown"
    return str(template_name), _node_count(row)


def _wilson_ci(successes: int, total: int, z: float = 1.96) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if total <= 0:
        return None, None, None
    p = successes / total
    denom = 1.0 + (z**2) / total
    center = (p + (z**2) / (2 * total)) / denom
    margin = z * ((p * (1 - p) / total + (z**2) / (4 * total * total)) ** 0.5) / denom
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return center, lo, hi


def build_catalog(config_path: Path, output_dir: Optional[Path] = None) -> None:
    cfg = _load_json(config_path)
    base_dir = config_path.parent
    inputs = cfg.get("inputs", {})
    attempts_path = _resolve_input(
        inputs.get("attempts_jsonl", "data/processed/ola2/raw/attempts.jsonl"),
        base_dir,
    )
    evaluations_path = _resolve_input(
        inputs.get("evaluations_jsonl", "data/processed/ola2/raw/evaluations.jsonl"),
        base_dir,
    )
    templates_path = _resolve_input(
        inputs.get("templates_json", "data/config/ola2/ola2_templates.json"),
        base_dir,
    )
    entities_candidates_input = inputs.get("entities_candidates_jsonl")
    if entities_candidates_input:
        entities_candidates_path = _resolve_input(str(entities_candidates_input), base_dir)
    else:
        entities_candidates_path = attempts_path.parent / "entities_candidates.jsonl"

    print("[core_catalog] Wiring Check:")
    print(f"- attempts_jsonl={attempts_path.resolve()}")
    print(f"- entities_candidates_jsonl={entities_candidates_path.resolve()}")
    print(f"- evaluations_jsonl={evaluations_path.resolve()}")
    print(f"- templates_json={templates_path.resolve()}")

    outputs = cfg.get("outputs", {})
    catalog_dir = _resolve_output(outputs.get("catalog_dir", "catalog"), output_dir)
    entities_out = _resolve_output(outputs.get("entities_jsonl", "entities.jsonl"), output_dir)
    genome_out = _resolve_output(outputs.get("genome_layer_csv", "genome_layers.csv"), output_dir)
    rollups_out = _resolve_output(outputs.get("rollups_json", "rollups.json"), output_dir)
    sweep_report_path = outputs.get("sweep_report_md") or outputs.get("report_md")
    sweep_report_out = _resolve_output(sweep_report_path, output_dir) if sweep_report_path else None
    explorer_report_path = outputs.get("explorer_report_md")
    explorer_report_out = _resolve_output(explorer_report_path, output_dir) if explorer_report_path else None
    promote_cfg_input = inputs.get("promote_config", "ola2_promote_blocks.json")
    promote_cfg_path = _resolve_input(str(promote_cfg_input), base_dir)
    taxonomy_out = genome_out.with_name(f"{genome_out.stem}_taxonomy.csv")

    catalog_dir.mkdir(parents=True, exist_ok=True)
    entities_out.parent.mkdir(parents=True, exist_ok=True)
    genome_out.parent.mkdir(parents=True, exist_ok=True)

    entities_candidates: Dict[str, Dict[str, Any]] = {}
    if entities_candidates_path.exists():
        entities_candidates = _load_entities_candidates(entities_candidates_path)

    seen_attempt_eval_ids: Set[str] = set()
    attempts_rollup: Dict[Tuple[str, int], int] = {}
    for row in iter_jsonl(attempts_path):
        eval_id = row.get("eval_id")
        if not eval_id:
            ids = row.get("ids") or {}
            eval_id = ids.get("eval_id")
        if not eval_id:
            continue
        eval_id = str(eval_id)
        if eval_id in seen_attempt_eval_ids:
            continue
        seen_attempt_eval_ids.add(eval_id)
        key = _rollup_key(row)
        attempts_rollup[key] = attempts_rollup.get(key, 0) + 1

    sweep_eval_ids: Set[str] = set()
    sweep_evals_by_entity_id: Dict[str, List[Dict[str, Any]]] = {}
    for row in iter_jsonl(evaluations_path):
        eval_id = row.get("eval_id")
        if not eval_id:
            continue
        eval_id = str(eval_id)
        if eval_id in sweep_eval_ids:
            continue
        sweep_eval_ids.add(eval_id)
        eid = row.get("entity_id")
        if not eid:
            continue
        sweep_evals_by_entity_id.setdefault(str(eid), []).append(row)

    entities: Dict[str, Dict[str, Any]] = {}
    if entities_candidates:
        for eid, candidate in entities_candidates.items():
            if not eid:
                continue
            entities[eid] = _build_entity_record(candidate, int(cfg.get("ola", 2)))
    else:
        for row in iter_jsonl(attempts_path):
            ids = row.get("ids") or {}
            eid = ids.get("entity_id") or row.get("entity_id")
            if not eid:
                continue
            eid = str(eid)
            if eid in entities:
                continue
            entities[eid] = _build_min_entity(eid, int(cfg.get("ola", 2)), row.get("provenance", {}))

    # Write entities.jsonl
    with entities_out.open("w") as f:
        for row in entities.values():
            f.write(json.dumps(row) + "\n")

    # Build genome layer CSV (left join from entities_candidates.jsonl).
    genome_fieldnames = [
        "entity_id",
        "template_name",
        "ola",
        "lineage",
        "genes_inherited",
        "genes_olaX",
        "robustness_score",
        "taxonomy_version",
        "taxonomy_kingdom",
        "taxonomy_family_id",
        "sweep_evals_total",
        "sweep_seeds_total",
        "sweep_attempted",
        "H_part_norm_mean",
        "H_part_norm_std",
        "PE_lockS1_norm_mean",
        "PE_lockS1_norm_std",
        "R_network_S1_mean",
        "R_network_S1_std",
        "pQ_mean",
        "pS1_mean",
        "pS2_mean",
        "best_eval_id",
    ]
    with genome_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=genome_fieldnames)
        writer.writeheader()
        for eid, candidate in entities_candidates.items():
            evals = sweep_evals_by_entity_id.get(eid, [])
            eval_count = len(evals)
            seed_vals = {
                int(row.get("seed"))
                for row in evals
                if isinstance(row.get("seed"), (int, float))
            }
            seeds_total = len(seed_vals) if seed_vals else eval_count
            h_vals = _collect_metric(evals, "H_part_norm_mean_lastW")
            pe_vals = _collect_metric(evals, "PE_lockS1_norm")
            r_vals = _collect_metric(evals, "R_network_S1_mean_lastW")
            pq_vals = _collect_metric(evals, "pQ_mean_lastW")
            ps1_vals = _collect_metric(evals, "pS1_mean_lastW")
            ps2_vals = _collect_metric(evals, "pS2_mean_lastW")
            h_mean, h_std = _mean_std(h_vals)
            pe_mean, pe_std = _mean_std(pe_vals)
            r_mean, r_std = _mean_std(r_vals)
            pq_mean, _ = _mean_std(pq_vals)
            ps1_mean, _ = _mean_std(ps1_vals)
            ps2_mean, _ = _mean_std(ps2_vals)
            row = {
                "entity_id": eid,
                "template_name": candidate.get("template_name"),
                "ola": int(candidate.get("ola", cfg.get("ola", 2))),
                "lineage": "{}",
                "genes_inherited": "{}",
                "genes_olaX": "{}",
                "robustness_score": "",
                "taxonomy_version": "",
                "taxonomy_kingdom": "",
                "taxonomy_family_id": "",
                "sweep_evals_total": eval_count,
                "sweep_seeds_total": seeds_total,
                "sweep_attempted": bool(eval_count),
                "H_part_norm_mean": h_mean,
                "H_part_norm_std": h_std,
                "PE_lockS1_norm_mean": pe_mean,
                "PE_lockS1_norm_std": pe_std,
                "R_network_S1_mean": r_mean,
                "R_network_S1_std": r_std,
                "pQ_mean": pq_mean,
                "pS1_mean": ps1_mean,
                "pS2_mean": ps2_mean,
                "best_eval_id": _best_eval_id_by_metric(evals, "R_network_S1_mean_lastW") if evals else "",
            }
            writer.writerow({k: ("" if v is None else v) for k, v in row.items()})

    candidates_rollup: Dict[Tuple[str, int], int] = {}
    sweep_attempted_rollup: Dict[Tuple[str, int], int] = {}
    sweep_evals_rollup: Dict[Tuple[str, int], int] = {}
    for eid, candidate in entities_candidates.items():
        key = _rollup_key(candidate)
        candidates_rollup[key] = candidates_rollup.get(key, 0) + 1
        evals_for_entity = sweep_evals_by_entity_id.get(eid, [])
        if evals_for_entity:
            sweep_attempted_rollup[key] = sweep_attempted_rollup.get(key, 0) + 1
            sweep_evals_rollup[key] = sweep_evals_rollup.get(key, 0) + len(evals_for_entity)

    rollups_by_template = []
    keys = set(attempts_rollup) | set(candidates_rollup) | set(sweep_attempted_rollup)
    for (template_name, n_nodes) in sorted(keys, key=lambda k: (k[0], k[1])):
        attempts_total = attempts_rollup.get((template_name, n_nodes), 0)
        candidates_total = candidates_rollup.get((template_name, n_nodes), 0)
        sweep_attempted_total = sweep_attempted_rollup.get((template_name, n_nodes), 0)
        sweep_evals_total = sweep_evals_rollup.get((template_name, n_nodes), 0)
        viables_total = sweep_attempted_total
        candidate_rate = (candidates_total / attempts_total) if attempts_total else None
        sweep_attempt_rate = (sweep_attempted_total / candidates_total) if candidates_total else None
        viable_rate_technical = (viables_total / attempts_total) if attempts_total else None
        viable_rate = (sweep_attempted_total / candidates_total) if candidates_total else None
        center, lo, hi = _wilson_ci(viables_total, attempts_total)
        v_center, v_lo, v_hi = _wilson_ci(sweep_attempted_total, candidates_total)
        rollups_by_template.append(
            {
                "template_name": template_name,
                "N": n_nodes,
                "attempts_total": attempts_total,
                "candidates_total": candidates_total,
                "sweep_evals_total": sweep_evals_total,
                "sweep_attempted_total": sweep_attempted_total,
                "viables_total": viables_total,
                "candidate_rate": candidate_rate,
                "sweep_attempt_rate": sweep_attempt_rate,
                "viable_rate_technical": viable_rate_technical,
                "viable_rate": viable_rate,
                "viable_rate_technical_ci_wilson": {
                    "center": center,
                    "low": lo,
                    "high": hi,
                },
                "viable_rate_ci_wilson": {
                    "center": v_center,
                    "low": v_lo,
                    "high": v_hi,
                },
            }
        )

    rollups = {
        "attempts_total": len(seen_attempt_eval_ids),
        "candidates_total": len(entities_candidates),
        "sweep_attempted_total": sum(1 for eid in entities_candidates if sweep_evals_by_entity_id.get(eid)),
        "viables_total": sum(1 for eid in entities_candidates if sweep_evals_by_entity_id.get(eid)),
        "sweep_evals_total": len(sweep_eval_ids),
        "attempts_total_by_template": [
            {"template_name": r["template_name"], "N": r["N"], "attempts_total": r["attempts_total"]}
            for r in rollups_by_template
        ],
        "candidates_total_by_template": [
            {"template_name": r["template_name"], "N": r["N"], "candidates_total": r["candidates_total"]}
            for r in rollups_by_template
        ],
        "sweep_evals_total_by_template": [
            {"template_name": r["template_name"], "N": r["N"], "sweep_evals_total": r["sweep_evals_total"]}
            for r in rollups_by_template
        ],
        "sweep_passed_total_by_template": [
            {"template_name": r["template_name"], "N": r["N"], "sweep_passed_total": r["sweep_attempted_total"]}
            for r in rollups_by_template
        ],
        "by_template": rollups_by_template,
        "templates_hash": str(templates_path),
    }
    rollups_out.write_text(json.dumps(rollups, indent=2))
    family_by_id = _load_family_ids(taxonomy_out)
    promoted_ids = _load_promoted_ids(promote_cfg_path)
    promoted_rows: List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]] = []
    viable_rows: List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]] = []
    for eid, candidate in entities_candidates.items():
        evals = sweep_evals_by_entity_id.get(eid, [])
        if eid in promoted_ids:
            promoted_rows.append((eid, candidate, evals))
        if evals:
            viable_rows.append((eid, candidate, evals))

    if sweep_report_out is not None:
        sweep_sections = ["# Sweep Report", ""]
        sweep_sections.extend(_candidate_section("Promoted", promoted_rows, entities_candidates, family_by_id))
        _write_report(sweep_report_out, sweep_sections)

    if explorer_report_out is not None:
        attempts_total = sum(1 for _ in iter_jsonl(attempts_path)) if attempts_path.exists() else 0
        attempts_candidate_true = sum(
            1 for row in iter_jsonl(attempts_path) if (row.get("tags_raw") or {}).get("candidate") is True
        )
        entities_total = len(entities_candidates)
        entities_candidate_true = sum(
            1 for row in entities_candidates.values() if (row.get("tags_raw") or {}).get("candidate") is True
        )
        candidate_rate = (attempts_candidate_true / attempts_total) if attempts_total else 0.0

        explorer_sections = [
            "# Explorer Report",
            "",
            "## Counts (on disk)",
            f"- attempts_total: {attempts_total}",
            f"- attempts_candidate_true: {attempts_candidate_true}",
            f"- candidate_rate: {candidate_rate:.6g}",
            f"- entities_total: {entities_total}",
            f"- entities_candidate_true: {entities_candidate_true}",
            "",
        ]
        explorer_sections.extend(_candidate_section("Viable", viable_rows, entities_candidates, family_by_id))
        _write_report(explorer_report_out, explorer_sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="core catalog builder (V1).")
    parser.add_argument("--config", required=True, help="Path to catalog build config JSON.")
    parser.add_argument("--output-dir", required=False, help="Override output dir.")
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else None
    build_catalog(Path(args.config), output_dir=output_dir)


if __name__ == "__main__":
    main()
