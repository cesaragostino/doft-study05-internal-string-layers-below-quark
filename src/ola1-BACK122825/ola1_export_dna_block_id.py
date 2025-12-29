"""Export DOF DNA catalog keyed by block_id (Ola1 -> Ola2 adapter)."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from olar.explorer_pool import load_simple_blocks


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
        "--allow-missing-dna",
        action="store_true",
        help="Skip blocks without DNA instead of erroring.",
    )
    args = parser.parse_args()

    blocks = load_simple_blocks(args.blocks_json)
    dna_rows, dna_fields = _load_dna_rows(args.dna_csv)

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
        row["block_id"] = block_id
        row["origin_run_id"] = origin_run_id
        out_rows.append(row)

    if missing_dna and not args.allow_missing_dna:
        sample = ", ".join(missing_dna[:5])
        raise RuntimeError(f"Missing DNA for {len(missing_dna)} blocks (e.g. {sample})")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dna_fields)
    if "block_id" not in fieldnames:
        fieldnames.insert(0, "block_id")
    if "origin_run_id" not in fieldnames:
        fieldnames.insert(1, "origin_run_id")
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"[dna_export] rows_in={len(dna_rows)} rows_out={len(out_rows)}")
    print(f"[dna_export] run_ids_with_multiple_rows={multi_runs} dna_row_pick_policy=first_row")
    if args.allow_missing_dna and missing_dna:
        print(f"[dna_export] skipped_blocks_missing_dna={len(missing_dna)}")
    print(f"[dna_export] wrote {args.output}")


if __name__ == "__main__":
    main()
