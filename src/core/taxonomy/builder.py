"""DOFT taxonomy builder (V1)."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.ids.hashing import hash_text, stable_dumps
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


def _to_float(val: Any) -> Optional[float]:
    try:
        f = float(val)
        if f == f:
            return f
    except Exception:
        return None
    return None


def _bin_id(val: Optional[float], edges: List[float]) -> str:
    if val is None or not edges or len(edges) < 2:
        return "na"
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if i == len(edges) - 2:
            if lo <= val <= hi:
                return str(i)
        if lo <= val < hi:
            return str(i)
    return "oob"


def _family_id_from_bins(bins: Dict[str, str]) -> str:
    parts = [f"{k}={v}" for k, v in sorted(bins.items())]
    return "|".join(parts)


def _classify(
    row: Dict[str, Any],
    thresholds: Dict[str, Any],
) -> str:
    quality_lock = _to_float(row.get("quality_lock") or row.get("QualityLock"))
    r_mean = _to_float(row.get("R_mean_lastW"))
    pv = _to_float(row.get("phase_var_lastW"))
    seeds = _to_float(row.get("seeds_viable"))

    locked_min_q = _to_float(thresholds.get("locked_min_quality_lock"))
    locked_min_r = _to_float(thresholds.get("locked_min_R_mean_lastW"))
    locked_max_pv = _to_float(thresholds.get("locked_max_phase_var_lastW"))
    locked_min_seeds = thresholds.get("locked_requires_min_seeds")

    if (
        quality_lock is not None
        and r_mean is not None
        and pv is not None
        and locked_min_q is not None
        and locked_min_r is not None
        and locked_max_pv is not None
    ):
        if (
            quality_lock >= locked_min_q
            and r_mean >= locked_min_r
            and pv <= locked_max_pv
            and (locked_min_seeds is None or (seeds is not None and seeds >= float(locked_min_seeds)))
        ):
            return "LOCKED"
    return "UNKNOWN"


def _stable_family_id(
    taxonomy_version: str, template_name: str, attractor_class: str, bin_label: str
) -> str:
    serial = "|".join([taxonomy_version, template_name, attractor_class, bin_label])
    return hash_text(serial)[:16]


def _to_float_safe(val: Any) -> Optional[float]:
    try:
        f = float(val)
        if math.isfinite(f):
            return f
    except Exception:
        return None
    return None


def classify_attractor(r_mean: Optional[float], pe_mean: Optional[float], thr: Dict[str, Any]) -> str:
    # Deterministic: uses only R_network_S1_mean and PE_lockS1_norm_mean aggregates.
    if r_mean is None or pe_mean is None:
        return "INCOHERENT"
    if r_mean < float(thr.get("min_coherence", 0.0)):
        return "INCOHERENT"
    if r_mean >= float(thr.get("hypersync_r", 1.0)) and pe_mean < float(thr.get("min_complexity", 0.0)):
        return "HYPER_SYNC"
    return "FUNCTIONAL_LOCK"


def _node_count(entity: Dict[str, Any]) -> int:
    canonical = entity.get("canonical_node_order")
    if isinstance(canonical, list) and canonical:
        return len(canonical)
    assignment = entity.get("assignment") if isinstance(entity.get("assignment"), dict) else {}
    block_ids = assignment.get("block_ids")
    if isinstance(block_ids, list):
        return len(block_ids)
    return 0


def _format_metric(val: Optional[float]) -> str:
    if val is None:
        return "NA"
    return f"{val:.3f}"


def _is_scalar(val: Any) -> bool:
    return val is None or isinstance(val, (str, int, float, bool))


def _assert_scalar_payload(payload: Any, path: str = "root") -> None:
    if _is_scalar(payload):
        return
    if isinstance(payload, list):
        for idx, item in enumerate(payload):
            _assert_scalar_payload(item, f"{path}[{idx}]")
        return
    if isinstance(payload, dict):
        for key, val in payload.items():
            _assert_scalar_payload(val, f"{path}.{key}")
        return
    raise ValueError(f"non-scalar payload at {path}")


def _assert_scalar_row(row: Dict[str, Any]) -> None:
    for key, val in row.items():
        if not _is_scalar(val):
            raise ValueError(f"taxonomy row field not scalar: {key}")


def _require_row_fields(row: Dict[str, Any], fields: List[str]) -> None:
    missing = [f for f in fields if row.get(f) in (None, "")]
    if missing:
        raise ValueError(f"taxonomy row missing fields: {missing}")


def apply_taxonomy(config_path: Path, output_dir: Optional[Path] = None) -> None:
    cfg = _load_json(config_path)
    inputs = cfg.get("inputs", {})
    genome_path = Path(inputs.get("genome_layer_csv", "data/processed/ola2/catalog/genome_layers_ola2.csv"))
    entities_path = Path(inputs.get("entities_jsonl", "data/processed/ola2/catalog/entities.jsonl"))

    outputs = cfg.get("outputs", {})
    out_genome = _resolve_output(outputs.get("genome_layer_out_csv", "genome_layers_taxonomy.csv"), output_dir)
    rollups_out = _resolve_output(outputs.get("taxonomy_rollups_json", "taxonomy_rollups.json"), output_dir)

    thresholds = cfg.get("thresholds", {})
    attractor_thresholds = cfg.get("attractor_thresholds", {})
    thresholds_version = str(cfg.get("thresholds_version") or cfg.get("taxonomy_version") or "")
    family_bins_cfg = (cfg.get("family_bins") or {}).get("bins", {})
    taxonomy_bins_cfg = cfg.get("taxonomy_bins") or {}
    use_bins_for_id = bool((cfg.get("family_bins") or {}).get("use_bins_for_id", False))
    taxonomy_version = cfg.get("taxonomy_version", "")

    if not genome_path.exists():
        raise RuntimeError(f"genome_layer_csv missing: {genome_path}")
    if not entities_path.exists():
        raise RuntimeError(f"entities_jsonl missing: {entities_path}")

    out_genome.parent.mkdir(parents=True, exist_ok=True)
    rollups_out.parent.mkdir(parents=True, exist_ok=True)

    entity_by_id: Dict[str, Dict[str, Any]] = {}
    for row in iter_jsonl(entities_path):
        eid = row.get("entity_id")
        if not eid:
            continue
        entity_by_id[str(eid)] = row

    rows: List[Dict[str, Any]] = []
    with genome_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    rollup_counts: Dict[str, int] = {}
    rollups_by_template: Dict[Tuple[str, int], Dict[str, Any]] = {}
    counts_by_template_name: Dict[str, Dict[str, int]] = {}
    counts_by_attractor_class: Dict[str, int] = {}
    counts_by_confirmed_family_id: Dict[str, int] = {}
    entities_total = 0
    entities_unmeasured = 0
    entities_measured = 0
    entities_viable_tax = 0
    entities_nonviable = 0
    for row in rows:
        _require_row_fields(row, ["entity_id", "template_name", "sweep_evals_total"])
        evals_total = int(_to_float_safe(row.get("sweep_evals_total")) or 0)
        if evals_total > 0:
            _require_row_fields(
                row,
                ["R_network_S1_mean", "PE_lockS1_norm_mean", "H_part_norm_mean"],
            )
        entities_total += 1
        kingdom = _classify(row, thresholds)
        rollup_counts[kingdom] = rollup_counts.get(kingdom, 0) + 1

        family_id = ""
        if use_bins_for_id:
            bins = {
                "R_mean_lastW": _bin_id(_to_float(row.get("R_mean_lastW")), family_bins_cfg.get("R_mean_lastW_edges", [])),
                "entropy_quality": _bin_id(
                    _to_float(row.get("entropy_quality")), family_bins_cfg.get("entropy_quality_edges", [])
                ),
                "memory_score_k10": _bin_id(
                    _to_float(row.get("memory_score_k10")), family_bins_cfg.get("memory_score_k10_edges", [])
                ),
                "phase_var_lastW": _bin_id(
                    _to_float(row.get("phase_var_lastW")), family_bins_cfg.get("phase_var_lastW_edges", [])
                ),
            }
            family_id = _family_id_from_bins(bins)
        row["taxonomy_version"] = taxonomy_version
        row["thresholds_version"] = thresholds_version
        row["taxonomy_kingdom"] = kingdom
        row["taxonomy_family_id"] = family_id
        r_mean = _to_float_safe(row.get("R_network_S1_mean"))
        pe_mean = _to_float_safe(row.get("PE_lockS1_norm_mean"))
        if evals_total == 0 or r_mean is None or pe_mean is None:
            attractor_class = "UNMEASURED"
            row["attractor_class"] = attractor_class
            row["viability_state"] = "UNMEASURED"
        else:
            attractor_class = classify_attractor(r_mean, pe_mean, attractor_thresholds)
            row["attractor_class"] = attractor_class
            if attractor_class in ("FUNCTIONAL_LOCK", "HYPER_SYNC"):
                row["viability_state"] = "VIABLE"
            elif attractor_class == "INCOHERENT":
                row["viability_state"] = "NONVIABLE"
            else:
                row["viability_state"] = "UNMEASURED"
        dof_grade = row.get("dof_grade") or ""
        row["dof_grade"] = dof_grade

        eid = row.get("entity_id") or ""
        entity = entity_by_id.get(str(eid)) if eid else None
        template_name = entity.get("template_name") if isinstance(entity, dict) else "unknown"
        template_name = template_name or "unknown"
        n_nodes = _node_count(entity) if isinstance(entity, dict) else 0
        key = (str(template_name), n_nodes)
        h_mean = _to_float_safe(row.get("H_part_norm_mean"))
        r_bin = _bin_id(r_mean, family_bins_cfg.get("R_mean_lastW_edges", []))
        pe_bin = _bin_id(pe_mean, taxonomy_bins_cfg.get("pe_edges", []))
        h_bin = _bin_id(h_mean, taxonomy_bins_cfg.get("h_part_edges", []))
        if attractor_class == "UNMEASURED":
            row["confirmed_family_id"] = ""
            row["confirmed_family_friendly"] = "UNMEASURED"
        else:
            bin_label = f"R{r_bin}_PE{pe_bin}_H{h_bin}"
            row["confirmed_family_id"] = _stable_family_id(
                taxonomy_version,
                str(template_name),
                attractor_class,
                bin_label,
            )
            row["confirmed_family_friendly"] = f"{template_name}:{attractor_class}:{bin_label}"
        row["taxonomy_inputs"] = (
            f"R={_format_metric(r_mean)} "
            f"PE={_format_metric(pe_mean)} "
            f"H={_format_metric(h_mean)} "
            f"evals={evals_total}"
        )
        if row["attractor_class"] not in (
            "UNMEASURED",
            "INCOHERENT",
            "HYPER_SYNC",
            "FUNCTIONAL_LOCK",
        ):
            raise ValueError(f"invalid attractor_class: {row['attractor_class']}")
        _assert_scalar_row(row)

        counts_by_attractor_class[attractor_class] = counts_by_attractor_class.get(attractor_class, 0) + 1
        if row["confirmed_family_id"]:
            fid = row["confirmed_family_id"]
            counts_by_confirmed_family_id[fid] = counts_by_confirmed_family_id.get(fid, 0) + 1

        t_counts = counts_by_template_name.setdefault(
            str(template_name),
            {"total": 0, "measured": 0, "unmeasured": 0, "viable_taxonomic": 0, "nonviable": 0},
        )
        t_counts["total"] += 1
        if row["viability_state"] == "UNMEASURED":
            t_counts["unmeasured"] += 1
            entities_unmeasured += 1
        else:
            t_counts["measured"] += 1
            entities_measured += 1
            if row["viability_state"] == "VIABLE":
                t_counts["viable_taxonomic"] += 1
                entities_viable_tax += 1
            elif row["viability_state"] == "NONVIABLE":
                t_counts["nonviable"] += 1
                entities_nonviable += 1
        rollup = rollups_by_template.setdefault(
            key,
            {
                "template_name": str(template_name),
                "N": n_nodes,
                "total": 0,
                "counts_by_dof_grade": {},
                "counts_by_attractor_class": {},
                "attempted_sweep_total": 0,
                "useful_total": 0,
                "trivial_total": 0,
            },
        )
        rollup["total"] += 1
        grade_counts = rollup["counts_by_dof_grade"]
        grade_counts[dof_grade] = grade_counts.get(dof_grade, 0) + 1
        attractor = attractor_class or ""
        attr_counts = rollup["counts_by_attractor_class"]
        attr_counts[attractor] = attr_counts.get(attractor, 0) + 1
        attempted = row.get("sweep_attempted")
        if attempted in (True, "true", "True", "1", 1):
            rollup["attempted_sweep_total"] += 1
        if attractor_class == "FUNCTIONAL_LOCK":
            rollup["useful_total"] += 1
        if attractor_class == "HYPER_SYNC":
            rollup["trivial_total"] += 1

    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = [
            "entity_id",
            "ola",
            "genes_inherited",
            "genes_olaX",
            "taxonomy_version",
            "thresholds_version",
            "taxonomy_kingdom",
            "taxonomy_family_id",
            "dof_grade",
            "confirmed_family_id",
            "confirmed_family_friendly",
            "viability_state",
            "attractor_class",
            "taxonomy_inputs",
        ]

    with out_genome.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    top_family_limit = int((cfg.get("rollups") or {}).get("top_confirmed_families", 25))
    top_families = sorted(
        counts_by_confirmed_family_id.items(), key=lambda item: (-item[1], item[0])
    )[:top_family_limit]
    rollups_payload = {
        "entities_total": entities_total,
        "entities_unmeasured": entities_unmeasured,
        "entities_measured": entities_measured,
        "entities_viable_taxonomic": entities_viable_tax,
        "entities_nonviable": entities_nonviable,
        "counts_by_template_name": counts_by_template_name,
        "counts_by_attractor_class": counts_by_attractor_class,
        "top_confirmed_families": [
            {"confirmed_family_id": fid, "count": count} for fid, count in top_families
        ],
        "viable_rate_taxonomic": (
            entities_viable_tax / entities_measured if entities_measured else None
        ),
        "measured_rate": (entities_measured / entities_total if entities_total else None),
        "counts_by_kingdom": rollup_counts,
        "by_template": [
            {
                **rollup,
                "useful_rate": (
                    rollup["useful_total"] / rollup["attempted_sweep_total"]
                    if rollup["attempted_sweep_total"]
                    else None
                ),
                "trivial_rate": (
                    rollup["trivial_total"] / rollup["attempted_sweep_total"]
                    if rollup["attempted_sweep_total"]
                    else None
                ),
            }
            for rollup in sorted(
                rollups_by_template.values(), key=lambda r: (r["template_name"], r["N"])
            )
        ],
    }
    _assert_scalar_payload(rollups_payload)
    rollups_out.write_text(json.dumps(rollups_payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="core taxonomy builder (V1).")
    parser.add_argument("--config", required=True, help="Path to taxonomy config JSON.")
    parser.add_argument("--output-dir", required=False, help="Override output dir.")
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else None
    apply_taxonomy(Path(args.config), output_dir=output_dir)


if __name__ == "__main__":
    main()
