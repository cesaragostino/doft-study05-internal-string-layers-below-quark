"""Export DOF DNA catalog keyed by block_id (Ola1 -> Ola2 adapter)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from olar.explorer_pool import load_simple_blocks
from core.io.schema_validation import validate_theta_internal


def _norm_id(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        if isinstance(val, float) and (not math.isfinite(val)):
            return ""
        if float(val).is_integer():
            return str(int(val))
        return str(val)
    text = str(val).strip()
    if text == "":
        return ""
    try:
        as_float = float(text)
    except Exception:
        return text
    if not math.isfinite(as_float):
        return ""
    if as_float.is_integer():
        return str(int(as_float))
    return text


def _load_dna_rows(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    if not path.exists():
        raise RuntimeError(f"DNA catalog missing: {path}")
    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    if not rows:
        raise RuntimeError(f"DNA catalog empty: {path}")
    if "run_id" not in (fieldnames or []):
        raise RuntimeError("DNA catalog missing run_id column (required for export)")
    return rows, fieldnames


def _hash_file(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def _short_hash(text: str, keep: int = 16) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:keep]


def _load_runs_full(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"runs_full.jsonl missing: {path}")
    runs: Dict[str, Dict[str, Any]] = {}
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            rid = _norm_id(rec.get("run_id"))
            if not rid:
                continue
            runs[rid] = rec
    if not runs:
        raise RuntimeError(f"runs_full.jsonl empty: {path}")
    return runs


def _pick_dna_row(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Deterministic policy: first row in file order.
    return rows[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export DOF DNA catalog keyed by block_id.")
    parser.add_argument("--blocks-json", type=Path, default=Path("data/processed/ola1/simple_blocks.json"))
    parser.add_argument("--dna-csv", type=Path, default=Path("data/processed/ola1/dof_dna_catalog.csv"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ola1/dof_dna_catalog_by_block_id.csv"),
    )
    parser.add_argument(
        "--runs-full-jsonl",
        type=Path,
        default=None,
        help="runs_full.jsonl with canonical theta_internal by run_id",
    )
    parser.add_argument(
        "--blocks-output",
        type=Path,
        default=None,
        help="Write simple_blocks_canonical.json with theta_internal by run_id",
    )
    parser.add_argument(
        "--allow-missing-dna",
        action="store_true",
        help="Skip blocks without DNA instead of erroring.",
    )
    args = parser.parse_args()

    blocks = load_simple_blocks(args.blocks_json)
    dna_rows, dna_fields = _load_dna_rows(args.dna_csv)
    required_cols = {
        "dof_grade",
        "dof_family_id",
        "dof_family_friendly",
        "omega_ref_proxy",
        "genes_min",
        "dna_cluster_id",
    }
    missing_cols = sorted(col for col in required_cols if col not in dna_fields)
    if missing_cols:
        raise RuntimeError(f"DNA catalog missing required columns: {missing_cols}")
    runs_full = None
    if args.blocks_output:
        if not args.runs_full_jsonl:
            raise RuntimeError("--runs-full-jsonl is required when --blocks-output is set.")
        runs_full = _load_runs_full(args.runs_full_jsonl)

    run_to_rows: Dict[str, List[Dict[str, Any]]] = {}
    for row in dna_rows:
        rid = _norm_id(row.get("run_id"))
        if not rid:
            continue
        run_to_rows.setdefault(rid, []).append(row)

    run_to_pick: Dict[str, Dict[str, Any]] = {}
    multi_runs = 0
    for rid, rows in run_to_rows.items():
        if len(rows) > 1:
            multi_runs += 1
        run_to_pick[rid] = _pick_dna_row(rows)

    block_to_run: Dict[str, str] = {}
    run_to_blocks: Dict[str, List[str]] = {}
    missing_origin = []
    for block in blocks:
        block_id = _norm_id(block.get("block_id"))
        origin_run_id = _norm_id(block.get("origin_run_id"))
        if not block_id:
            continue
        if not origin_run_id:
            missing_origin.append(block_id)
            continue
        block_to_run[block_id] = origin_run_id
        run_to_blocks.setdefault(origin_run_id, []).append(block_id)

    if missing_origin and not args.allow_missing_dna:
        sample = ", ".join(missing_origin[:5])
        raise RuntimeError(f"Missing origin_run_id for {len(missing_origin)} blocks (e.g. {sample})")

    canonical_blocks: List[Dict[str, Any]] = []
    seen_run_ids: set[str] = set()

    out_rows: List[Dict[str, Any]] = []
    missing_dna = []
    for block in blocks:
        block_id = _norm_id(block.get("block_id"))
        if not block_id:
            continue
        origin_run_id = _norm_id(block.get("origin_run_id"))
        if not origin_run_id:
            continue
        dna = run_to_pick.get(origin_run_id)
        if not dna:
            missing_dna.append(block_id)
            if args.allow_missing_dna:
                continue
            continue
        row = dict(dna)
        canon_block_id = block_id
        row["origin_run_id"] = origin_run_id
        if runs_full is not None:
            canon_block_id = f"ola1_{_short_hash(origin_run_id)}"
        row["block_id"] = canon_block_id
        omega_ref_proxy = row.get("omega_ref_proxy")
        try:
            omega_ref_proxy_val = float(omega_ref_proxy)
        except Exception:
            omega_ref_proxy_val = float("nan")
        if not math.isfinite(omega_ref_proxy_val):
            raise RuntimeError(f"Invalid omega_ref_proxy for block_id={canon_block_id}")
        genes_min = row.get("genes_min")
        if isinstance(genes_min, dict):
            row["genes_min"] = json.dumps(genes_min, sort_keys=True)
        elif isinstance(genes_min, str) and genes_min.strip():
            row["genes_min"] = genes_min
        else:
            raise RuntimeError(f"Invalid genes_min for block_id={canon_block_id}")
        if "dna_cluster_id" not in row:
            row["dna_cluster_id"] = ""
        out_rows.append(row)

        if runs_full is not None:
            if origin_run_id in seen_run_ids:
                raise RuntimeError(f"Duplicate origin_run_id in blocks: {origin_run_id}")
            seen_run_ids.add(origin_run_id)
            run_rec = runs_full.get(origin_run_id)
            if not run_rec:
                raise RuntimeError(f"Missing run_id in runs_full.jsonl: {origin_run_id}")
            theta_internal = run_rec.get("theta_internal")
            if not isinstance(theta_internal, dict):
                raise RuntimeError(f"Missing theta_internal for run_id={origin_run_id}")
            validate_theta_internal(theta_internal)
            omega_ref = block.get("omega_ref")
            try:
                omega_ref_val = float(omega_ref)
            except Exception:
                omega_ref_val = float("nan")
            if not math.isfinite(omega_ref_val):
                raise RuntimeError(f"Invalid omega_ref for block_id={block_id} run_id={origin_run_id}")
            canonical_blocks.append(
                {
                    "block_id": f"ola1_{_short_hash(origin_run_id)}",
                    "origin_run_id": origin_run_id,
                    "omega_ref": omega_ref_val,
                    "theta_internal": theta_internal,
                    "provenance": {},
                }
            )

    if missing_dna and not args.allow_missing_dna:
        sample = ", ".join(missing_dna[:5])
        raise RuntimeError(f"Missing DNA for {len(missing_dna)} blocks (e.g. {sample})")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dna_fields)
    if "block_id" not in fieldnames:
        fieldnames.insert(0, "block_id")
    if "origin_run_id" not in fieldnames:
        fieldnames.insert(1, "origin_run_id")
    if "dna_cluster_id" not in fieldnames:
        fieldnames.append("dna_cluster_id")
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"[dna_export] rows_in={len(dna_rows)} rows_out={len(out_rows)}")
    print(f"[dna_export] run_ids_with_multiple_rows={multi_runs} dna_row_pick_policy=first_row")
    if args.allow_missing_dna and missing_dna:
        print(f"[dna_export] skipped_blocks_missing_dna={len(missing_dna)}")
    print(f"[dna_export] wrote {args.output}")

    if args.blocks_output:
        blocks_out = args.blocks_output
        inputs_hash = _hash_file(args.blocks_json)
        runs_hash = _hash_file(args.runs_full_jsonl) if args.runs_full_jsonl else ""
        inputs_hash = _short_hash(f"{inputs_hash}|{runs_hash}", keep=64)
        code_hash = _hash_file(Path(__file__))
        for block in canonical_blocks:
            block["provenance"] = {
                "source_ola": 1,
                "inputs_hash": inputs_hash,
                "code_hash": code_hash,
            }
        blocks_out.parent.mkdir(parents=True, exist_ok=True)
        blocks_out.write_text(json.dumps(canonical_blocks, indent=2))
        print(f"[dna_export] wrote {blocks_out}")


if __name__ == "__main__":
    main()
