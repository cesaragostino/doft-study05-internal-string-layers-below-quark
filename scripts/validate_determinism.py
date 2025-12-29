"""Determinism validator for Ola2 end-to-end artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from core.ids.hashing import hash_file, hash_text, stable_dumps
from core.io.jsonl import iter_jsonl


def _as_str(val: Any) -> str:
    return str(val) if val is not None else ""


def _round_float(val: Any, decimals: int) -> Any:
    if isinstance(val, float):
        return round(val, decimals)
    if isinstance(val, dict):
        return {k: _round_float(v, decimals) for k, v in val.items()}
    if isinstance(val, list):
        return [_round_float(v, decimals) for v in val]
    return val


def _hash_list(rows: Iterable[Tuple[Any, ...]]) -> str:
    serial = stable_dumps(sorted(rows))
    return f"sha256:{hash_text(serial)}"


def _hash_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return f"sha256:{hash_file(path)}"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _report_explorer(
    attempts_path: Path, entities_candidates_path: Path, decimals: int
) -> Dict[str, Any]:
    attempts_rows: List[Tuple[str, str, str, str]] = []
    for row in iter_jsonl(attempts_path):
        eval_id = row.get("eval_id") or (row.get("ids") or {}).get("eval_id")
        attempts_rows.append(
            (
                _as_str(row.get("entity_id") or (row.get("ids") or {}).get("entity_id")),
                _as_str(eval_id),
                _as_str(row.get("engine_params_bin_id")),
                _as_str(row.get("seed")),
            )
        )
    candidates_rows: List[Tuple[str, str, str, str]] = []
    for row in iter_jsonl(entities_candidates_path):
        candidates_rows.append(
            (
                _as_str(row.get("entity_id")),
                _as_str(row.get("source_eval_id")),
                _as_str(row.get("engine_params_bin_id")),
                _as_str(row.get("seed")),
            )
        )
    return {
        "attempts_total": len(attempts_rows),
        "candidates_total": len(candidates_rows),
        "attempts_hash": _hash_list(attempts_rows),
        "candidates_hash": _hash_list(candidates_rows),
        "rounding_decimals": decimals,
    }


def _report_sweep(evaluations_path: Path, decimals: int) -> Dict[str, Any]:
    eval_rows: List[Tuple[str, str]] = []
    for row in iter_jsonl(evaluations_path):
        eval_id = row.get("eval_id")
        metrics = row.get("metrics_raw") or {}
        metrics = _round_float(metrics, decimals)
        eval_rows.append((_as_str(eval_id), stable_dumps(metrics)))
    return {
        "evaluations_total": len(eval_rows),
        "evaluations_hash": _hash_list(eval_rows),
        "rounding_decimals": decimals,
    }


def _report_catalog(rollups_path: Path, genome_path: Path, entities_path: Path) -> Dict[str, Any]:
    return {
        "rollups_hash": _hash_file(rollups_path),
        "genome_hash": _hash_file(genome_path),
        "entities_hash": _hash_file(entities_path),
    }


def _report_promotion(blocks_path: Path, dna_path: Path) -> Dict[str, Any]:
    return {
        "blocks_hash": _hash_file(blocks_path),
        "dna_hash": _hash_file(dna_path),
    }


def _diff_reports(base: Dict[str, Any], current: Dict[str, Any]) -> List[str]:
    diffs: List[str] = []
    keys = sorted(set(base) | set(current))
    for key in keys:
        if base.get(key) != current.get(key):
            diffs.append(key)
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser(description="Determinism validator for Ola2 artifacts.")
    parser.add_argument("--attempts", type=Path, default=Path("data/processed/ola2/raw/attempts.jsonl"))
    parser.add_argument(
        "--entities-candidates",
        type=Path,
        default=Path("data/processed/ola2/raw/entities_candidates.jsonl"),
    )
    parser.add_argument(
        "--evaluations", type=Path, default=Path("data/processed/ola2/raw/evaluations.jsonl")
    )
    parser.add_argument(
        "--catalog-rollups", type=Path, default=Path("data/processed/ola2/catalog/rollups.json")
    )
    parser.add_argument(
        "--genome-layer", type=Path, default=Path("data/processed/ola2/catalog/genome_layers_ola2.csv")
    )
    parser.add_argument(
        "--entities", type=Path, default=Path("data/processed/ola2/catalog/entities.jsonl")
    )
    parser.add_argument(
        "--taxonomy-rollups",
        type=Path,
        default=Path("data/processed/ola2/catalog/taxonomy_rollups.json"),
    )
    parser.add_argument(
        "--promoted-blocks",
        type=Path,
        default=Path("data/processed/ola3/inputs/blocks_from_ola2.json"),
    )
    parser.add_argument(
        "--promoted-dna",
        type=Path,
        default=Path("data/processed/ola3/inputs/dof_dna_catalog_from_ola2.csv"),
    )
    parser.add_argument("--float-decimals", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola2/determinism_report.json"))
    parser.add_argument("--compare", type=Path, help="Compare against an existing report JSON.")
    args = parser.parse_args()

    report = {
        "explorer": _report_explorer(args.attempts, args.entities_candidates, args.float_decimals),
        "sweep": _report_sweep(args.evaluations, args.float_decimals),
        "catalog": _report_catalog(args.catalog_rollups, args.genome_layer, args.entities),
        "taxonomy": {"rollups_hash": _hash_file(args.taxonomy_rollups)},
        "promotion": _report_promotion(args.promoted_blocks, args.promoted_dna),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=True))
    print(f"[determinism] report_written={args.output}")

    if args.compare:
        base = _load_json(args.compare)
        diffs = _diff_reports(base, report)
        if diffs:
            print(f"[determinism] mismatched_keys={diffs}")
            raise SystemExit(2)
        print("[determinism] compare=ok")


if __name__ == "__main__":
    main()
