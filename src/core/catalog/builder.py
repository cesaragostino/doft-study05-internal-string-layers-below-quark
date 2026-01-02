"""Deterministic catalog builder (V1)."""

from __future__ import annotations

import argparse
import csv
import json
import math
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


def _has_jsonl_rows(path: Path) -> bool:
    if not path.exists():
        return False
    for _ in iter_jsonl(path):
        return True
    return False


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


def _collect_metric_with_fallback(
    evals: List[Dict[str, Any]],
    primary_key: str,
    fallback_key: str,
) -> List[float]:
    values: List[float] = []
    for row in evals:
        metrics = row.get("metrics_raw") or {}
        val = metrics.get(primary_key)
        if val is None:
            val = metrics.get(fallback_key)
        if isinstance(val, (int, float)):
            values.append(float(val))
    return values


def _candidate_metric(candidate: Dict[str, Any], key: str) -> Optional[float]:
    metrics = candidate.get("metrics_summary") or {}
    val = metrics.get(key)
    if isinstance(val, (int, float)) and math.isfinite(val):
        return float(val)
    return None


def _primary_metric_keys() -> Tuple[str, str, str]:
    return (
        "R_network_S1_mean",
        "PE_lockS1_norm_mean",
        "H_part_norm_mean",
    )


def _eval_primary_values(row: Dict[str, Any]) -> Dict[str, Optional[float]]:
    metrics = row.get("metrics_raw") or {}
    fallback = {
        "R_network_S1_mean": "R_network_S1_mean_lastW",
        "PE_lockS1_norm_mean": "PE_lockS1_norm",
        "H_part_norm_mean": "H_part_norm_mean_lastW",
    }
    primaries: Dict[str, Optional[float]] = {}
    for key in _primary_metric_keys():
        val = metrics.get(key)
        if val is None:
            val = metrics.get(fallback.get(key, ""))
        if isinstance(val, (int, float)) and math.isfinite(val):
            primaries[key] = float(val)
        else:
            primaries[key] = None
    return primaries


def _eval_is_finite_primary(row: Dict[str, Any], primaries: Dict[str, Optional[float]]) -> bool:
    if isinstance(row.get("is_finite_primary"), bool):
        return bool(row.get("is_finite_primary"))
    return all(val is not None for val in primaries.values())


def _eval_nan_primary_count(row: Dict[str, Any], primaries: Dict[str, Optional[float]]) -> int:
    val = row.get("nan_primary_count")
    if isinstance(val, (int, float)):
        return int(val)
    return sum(1 for item in primaries.values() if item is None)


def _eval_sweep_passed(row: Dict[str, Any], is_finite_primary: bool) -> bool:
    if isinstance(row.get("sweep_passed"), bool):
        return bool(row.get("sweep_passed"))
    return is_finite_primary


def _percentile(values: List[float], pct: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    k = (len(ordered) - 1) * pct
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def _robust_score(mean: Optional[float], std: Optional[float], eps: float = 1e-9) -> Optional[float]:
    if mean is None or std is None:
        return None
    denom = max(eps, abs(mean))
    score = 1.0 - (std / denom)
    return max(0.0, min(1.0, score))


def _best_eval_id_by_metric(evals: List[Dict[str, Any]], key: str, fallback: Optional[str] = None) -> str:
    best_id = ""
    best_val = None
    for row in evals:
        metrics = row.get("metrics_raw") or {}
        val = metrics.get(key)
        if val is None and fallback:
            val = metrics.get(fallback)
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


def _degree_stats(row: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    nodes = _node_count(row)
    if nodes <= 0:
        return None, None
    edges = row.get("edges")
    if not isinstance(edges, list):
        return None, None
    degrees = [0] * nodes
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) < 2:
            continue
        try:
            a = int(edge[0])
            b = int(edge[1])
        except (TypeError, ValueError):
            continue
        if 0 <= a < nodes:
            degrees[a] += 1
        if 0 <= b < nodes:
            degrees[b] += 1
    return _mean_std([float(val) for val in degrees])


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

    has_attempts = _has_jsonl_rows(attempts_path)
    has_entities = _has_jsonl_rows(entities_candidates_path)
    has_evals = _has_jsonl_rows(evaluations_path)
    if not (has_attempts or has_entities or has_evals):
        print(
            "WARNING - STOPPED: no input data found; no processing performed. "
            f"attempts_jsonl={attempts_path} entities_candidates_jsonl={entities_candidates_path} "
            f"evaluations_jsonl={evaluations_path}"
        )
        return

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
    sweep_runtime_vals: List[float] = []
    sweep_nan_primary_total = 0
    sweep_passed_eval_total = 0
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
        primaries = _eval_primary_values(row)
        is_finite_primary = _eval_is_finite_primary(row, primaries)
        sweep_nan_primary_total += _eval_nan_primary_count(row, primaries)
        if _eval_sweep_passed(row, is_finite_primary):
            sweep_passed_eval_total += 1
        runtime_sec = row.get("runtime_sec")
        if isinstance(runtime_sec, (int, float)) and math.isfinite(runtime_sec):
            sweep_runtime_vals.append(float(runtime_sec))

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
        "node_count",
        "edge_count",
        "density",
        "degree_mean",
        "degree_std",
        "ola",
        "lineage",
        "genes_inherited",
        "genes_olaX",
        "robustness_score",
        "taxonomy_version",
        "taxonomy_kingdom",
        "taxonomy_family_id",
        "is_candidate",
        "was_swept",
        "sweep_evals_planned",
        "sweep_evals_total",
        "seed_evals_total",
        "seed_success_count",
        "sweep_passed_total",
        "sweep_passed_any",
        "sweep_passed",
        "sweep_seeds_total",
        "sweep_attempted",
        "nan_primary_total",
        "nan_primary_count",
        "nan_primary_rate",
        "seed_success_rate",
        "H_part_norm_mean",
        "H_part_norm_std",
        "PE_lockS1_norm_mean",
        "PE_lockS1_norm_std",
        "R_network_S1_mean",
        "R_network_S1_std",
        "R_mean_lastW_mean",
        "phase_var_lastW_mean",
        "QualityLock_mean",
        "H_part_norm_mean_mean",
        "H_part_norm_mean_std",
        "PE_lockS1_norm_mean_mean",
        "PE_lockS1_norm_mean_std",
        "R_network_S1_mean_mean",
        "R_network_S1_mean_std",
        "robust_score_v1",
        "bins_used_count",
        "H_part_over_bins_std",
        "PE_lock_over_bins_std",
        "R_network_over_bins_std",
        "robust_score_v2",
        "runtime_sec_mean",
        "runtime_sec_p95",
        "pQ_mean",
        "pS1_mean",
        "pS2_mean",
        "best_eval_id",
    ]
    entity_stats: Dict[str, Dict[str, Any]] = {}
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
            bin_ids = {
                str(row.get("engine_params_bin_id"))
                for row in evals
                if row.get("engine_params_bin_id")
            }
            seed_indices = [
                int(row.get("seed_index"))
                for row in evals
                if isinstance(row.get("seed_index"), (int, float))
            ]
            seeds_planned = (max(seed_indices) + 1) if seed_indices else (len(seed_vals) if seed_vals else 0)
            bins_used_count = len(bin_ids) if bin_ids else (1 if evals else 0)
            sweep_evals_planned = seeds_planned * bins_used_count if seeds_planned and bins_used_count else eval_count
            nan_primary_total = 0
            sweep_passed_total = 0
            passed_evals: List[Dict[str, Any]] = []
            runtime_vals = []
            for row in evals:
                primaries = _eval_primary_values(row)
                is_finite_primary = _eval_is_finite_primary(row, primaries)
                nan_primary_total += _eval_nan_primary_count(row, primaries)
                if _eval_sweep_passed(row, is_finite_primary):
                    sweep_passed_total += 1
                    passed_evals.append(row)
                runtime_sec = row.get("runtime_sec")
                if isinstance(runtime_sec, (int, float)) and math.isfinite(runtime_sec):
                    runtime_vals.append(float(runtime_sec))
            sweep_passed_any = sweep_passed_total > 0
            num_primary = len(_primary_metric_keys())
            nan_primary_rate = (
                nan_primary_total / (eval_count * num_primary) if eval_count and num_primary else None
            )
            seed_success_rate = (
                sweep_passed_total / sweep_evals_planned if sweep_evals_planned else None
            )
            h_vals = _collect_metric_with_fallback(evals, "H_part_norm_mean", "H_part_norm_mean_lastW")
            pe_vals = _collect_metric_with_fallback(evals, "PE_lockS1_norm_mean", "PE_lockS1_norm")
            r_vals = _collect_metric_with_fallback(evals, "R_network_S1_mean", "R_network_S1_mean_lastW")
            r_lastw_vals = _collect_metric(evals, "R_mean_lastW")
            pv_vals = _collect_metric(evals, "phase_var_lastW")
            q_vals = _collect_metric(evals, "QualityLock")
            if not r_lastw_vals:
                r_lastw = _candidate_metric(candidate, "R_mean_lastW")
                if r_lastw is not None:
                    r_lastw_vals = [r_lastw]
            if not pv_vals:
                pv = _candidate_metric(candidate, "phase_var_lastW")
                if pv is not None:
                    pv_vals = [pv]
            if not q_vals:
                ql = _candidate_metric(candidate, "QualityLock")
                if ql is not None:
                    q_vals = [ql]
            pq_vals = _collect_metric(evals, "pQ_mean_lastW")
            ps1_vals = _collect_metric(evals, "pS1_mean_lastW")
            ps2_vals = _collect_metric(evals, "pS2_mean_lastW")
            h_mean, h_std = _mean_std(h_vals)
            pe_mean, pe_std = _mean_std(pe_vals)
            r_mean, r_std = _mean_std(r_vals)
            r_lastw_mean, _ = _mean_std(r_lastw_vals)
            pv_mean, _ = _mean_std(pv_vals)
            q_mean, _ = _mean_std(q_vals)
            pq_mean, _ = _mean_std(pq_vals)
            ps1_mean, _ = _mean_std(ps1_vals)
            ps2_mean, _ = _mean_std(ps2_vals)
            h_pass_vals = _collect_metric_with_fallback(passed_evals, "H_part_norm_mean", "H_part_norm_mean_lastW")
            pe_pass_vals = _collect_metric_with_fallback(passed_evals, "PE_lockS1_norm_mean", "PE_lockS1_norm")
            r_pass_vals = _collect_metric_with_fallback(passed_evals, "R_network_S1_mean", "R_network_S1_mean_lastW")
            h_pass_mean, h_pass_std = _mean_std(h_pass_vals)
            pe_pass_mean, pe_pass_std = _mean_std(pe_pass_vals)
            r_pass_mean, r_pass_std = _mean_std(r_pass_vals)
            robust_r = _robust_score(r_pass_mean, r_pass_std)
            robust_pe = _robust_score(pe_pass_mean, pe_pass_std)
            robust_score_v1 = None
            if robust_r is not None and robust_pe is not None:
                robust_score_v1 = min(robust_r, robust_pe)
            r_bins: Dict[str, List[float]] = {}
            pe_bins: Dict[str, List[float]] = {}
            h_bins: Dict[str, List[float]] = {}
            for row in passed_evals:
                bin_id = row.get("engine_params_bin_id")
                if not bin_id:
                    continue
                bin_id = str(bin_id)
                for target, metric_key in (
                    (r_bins, "R_network_S1_mean"),
                    (pe_bins, "PE_lockS1_norm_mean"),
                    (h_bins, "H_part_norm_mean"),
                ):
                    metrics = row.get("metrics_raw") or {}
                    val = metrics.get(metric_key)
                    if val is None:
                        fallback = {
                            "R_network_S1_mean": "R_network_S1_mean_lastW",
                            "PE_lockS1_norm_mean": "PE_lockS1_norm",
                            "H_part_norm_mean": "H_part_norm_mean_lastW",
                        }
                        val = metrics.get(fallback.get(metric_key, ""))
                    if isinstance(val, (int, float)) and math.isfinite(val):
                        target.setdefault(bin_id, []).append(float(val))
            r_bin_means = [sum(vals) / len(vals) for vals in r_bins.values() if vals]
            pe_bin_means = [sum(vals) / len(vals) for vals in pe_bins.values() if vals]
            h_bin_means = [sum(vals) / len(vals) for vals in h_bins.values() if vals]
            r_bin_std = _mean_std(r_bin_means)[1]
            pe_bin_std = _mean_std(pe_bin_means)[1]
            h_bin_std = _mean_std(h_bin_means)[1]
            robust_r_v2 = _robust_score(_mean_std(r_bin_means)[0], r_bin_std)
            robust_pe_v2 = _robust_score(_mean_std(pe_bin_means)[0], pe_bin_std)
            robust_score_v2 = None
            if robust_r_v2 is not None and robust_pe_v2 is not None:
                robust_score_v2 = min(robust_r_v2, robust_pe_v2)
            runtime_sec_mean, _runtime_sec_std = _mean_std(runtime_vals)
            runtime_sec_p95 = _percentile(runtime_vals, 0.95)
            node_count = _node_count(candidate)
            edge_count = _edge_count(candidate)
            density = _density(edge_count, node_count)
            degree_mean, degree_std = _degree_stats(candidate)
            row = {
                "entity_id": eid,
                "template_name": candidate.get("template_name"),
                "node_count": node_count,
                "edge_count": edge_count,
                "density": density,
                "degree_mean": degree_mean,
                "degree_std": degree_std,
                "ola": int(candidate.get("ola", cfg.get("ola", 2))),
                "lineage": "{}",
                "genes_inherited": "{}",
                "genes_olaX": "{}",
                "robustness_score": "",
                "taxonomy_version": "",
                "taxonomy_kingdom": "",
                "taxonomy_family_id": "",
                "is_candidate": bool(candidate.get("is_candidate", True)),
                "was_swept": bool(eval_count),
                "sweep_evals_planned": sweep_evals_planned,
                "sweep_evals_total": eval_count,
                "seed_evals_total": eval_count,
                "seed_success_count": sweep_passed_total,
                "sweep_passed_total": sweep_passed_total,
                "sweep_passed_any": sweep_passed_any,
                "sweep_passed": sweep_passed_any,
                "sweep_seeds_total": seeds_total,
                "sweep_attempted": bool(eval_count),
                "nan_primary_total": nan_primary_total,
                "nan_primary_count": nan_primary_total,
                "nan_primary_rate": nan_primary_rate,
                "seed_success_rate": seed_success_rate,
                "H_part_norm_mean": h_mean,
                "H_part_norm_std": h_std,
                "PE_lockS1_norm_mean": pe_mean,
                "PE_lockS1_norm_std": pe_std,
                "R_network_S1_mean": r_mean,
                "R_network_S1_std": r_std,
                "R_mean_lastW_mean": r_lastw_mean,
                "phase_var_lastW_mean": pv_mean,
                "QualityLock_mean": q_mean,
                "H_part_norm_mean_mean": h_pass_mean,
                "H_part_norm_mean_std": h_pass_std,
                "PE_lockS1_norm_mean_mean": pe_pass_mean,
                "PE_lockS1_norm_mean_std": pe_pass_std,
                "R_network_S1_mean_mean": r_pass_mean,
                "R_network_S1_mean_std": r_pass_std,
                "robust_score_v1": robust_score_v1,
                "bins_used_count": bins_used_count,
                "H_part_over_bins_std": h_bin_std,
                "PE_lock_over_bins_std": pe_bin_std,
                "R_network_over_bins_std": r_bin_std,
                "robust_score_v2": robust_score_v2,
                "runtime_sec_mean": runtime_sec_mean,
                "runtime_sec_p95": runtime_sec_p95,
                "pQ_mean": pq_mean,
                "pS1_mean": ps1_mean,
                "pS2_mean": ps2_mean,
                "best_eval_id": _best_eval_id_by_metric(
                    evals, "R_network_S1_mean", "R_network_S1_mean_lastW"
                )
                if evals
                else "",
            }
            writer.writerow({k: ("" if v is None else v) for k, v in row.items()})
            entity_stats[eid] = {
                "node_count": row["node_count"],
                "sweep_evals_total": eval_count,
                "sweep_passed_total": sweep_passed_total,
                "sweep_passed_any": sweep_passed_any,
                "nan_primary_total": nan_primary_total,
                "runtime_sec_mean": runtime_sec_mean,
            }

    candidates_rollup: Dict[Tuple[str, int], int] = {}
    sweep_attempted_rollup: Dict[Tuple[str, int], int] = {}
    sweep_passed_rollup: Dict[Tuple[str, int], int] = {}
    sweep_evals_rollup: Dict[Tuple[str, int], int] = {}
    for eid, candidate in entities_candidates.items():
        key = _rollup_key(candidate)
        candidates_rollup[key] = candidates_rollup.get(key, 0) + 1
        evals_for_entity = sweep_evals_by_entity_id.get(eid, [])
        stats = entity_stats.get(eid, {})
        if evals_for_entity:
            sweep_attempted_rollup[key] = sweep_attempted_rollup.get(key, 0) + 1
            sweep_evals_rollup[key] = sweep_evals_rollup.get(key, 0) + len(evals_for_entity)
        if stats.get("sweep_passed_any"):
            sweep_passed_rollup[key] = sweep_passed_rollup.get(key, 0) + 1

    rollups_by_template = []
    keys = set(attempts_rollup) | set(candidates_rollup) | set(sweep_attempted_rollup)
    for (template_name, n_nodes) in sorted(keys, key=lambda k: (k[0], k[1])):
        attempts_total = attempts_rollup.get((template_name, n_nodes), 0)
        candidates_total = candidates_rollup.get((template_name, n_nodes), 0)
        sweep_attempted_total = sweep_attempted_rollup.get((template_name, n_nodes), 0)
        sweep_passed_total = sweep_passed_rollup.get((template_name, n_nodes), 0)
        sweep_evals_total = sweep_evals_rollup.get((template_name, n_nodes), 0)
        viables_total = sweep_passed_total
        candidate_rate = (candidates_total / attempts_total) if attempts_total else None
        sweep_attempt_rate = (sweep_attempted_total / candidates_total) if candidates_total else None
        viable_rate_technical = (viables_total / attempts_total) if attempts_total else None
        viable_rate = (viables_total / candidates_total) if candidates_total else None
        center, lo, hi = _wilson_ci(viables_total, attempts_total)
        v_center, v_lo, v_hi = _wilson_ci(viables_total, candidates_total)
        rollups_by_template.append(
            {
                "template_name": template_name,
                "N": n_nodes,
                "attempts_total": attempts_total,
                "candidates_total": candidates_total,
                "sweep_evals_total": sweep_evals_total,
                "sweep_attempted_total": sweep_attempted_total,
                "sweep_passed_total": sweep_passed_total,
                "viables_total": viables_total,
                "candidate_rate": candidate_rate,
                "sweep_attempt_rate": sweep_attempt_rate,
                "technical_viable_rate": viable_rate,
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

    sweep_passed_total = sum(
        1 for eid, stats in entity_stats.items() if stats.get("sweep_passed_any")
    )
    runtime_sec_mean_global, _runtime_std_global = _mean_std(sweep_runtime_vals)
    runtime_sec_p95_global = _percentile(sweep_runtime_vals, 0.95)
    num_primary = len(_primary_metric_keys())
    nan_primary_rate_global = (
        sweep_nan_primary_total / (len(sweep_eval_ids) * num_primary)
        if sweep_eval_ids and num_primary
        else None
    )
    technical_viable_rate = (
        sweep_passed_total / len(entities_candidates) if entities_candidates else None
    )
    rollups = {
        "attempts_total": len(seen_attempt_eval_ids),
        "candidates_total": len(entities_candidates),
        "sweep_attempted_total": sum(1 for eid in entities_candidates if sweep_evals_by_entity_id.get(eid)),
        "sweep_passed_total": sweep_passed_total,
        "technical_viable_rate": technical_viable_rate,
        "nan_primary_rate_global": nan_primary_rate_global,
        "runtime_sec_mean_global": runtime_sec_mean_global,
        "runtime_sec_p95_global": runtime_sec_p95_global,
        "viables_total": sweep_passed_total,
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
            {"template_name": r["template_name"], "N": r["N"], "sweep_passed_total": r["sweep_passed_total"]}
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
