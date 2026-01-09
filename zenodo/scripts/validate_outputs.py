#!/usr/bin/env python3
"""Hard-fail validation for Ola1/Ola2 bridge outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

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


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"blocks_json missing: {path}")
    raw = json.loads(path.read_text())
    if isinstance(raw, dict) and isinstance(raw.get("blocks"), list):
        return raw["blocks"]
    if isinstance(raw, list):
        return raw
    raise RuntimeError(f"blocks_json must be a list: {path}")


def _load_runs(path: Path) -> Dict[str, Dict[str, Any]]:
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


def _load_dna(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"dna_csv missing: {path}")
    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    if not rows:
        raise RuntimeError(f"dna_csv empty: {path}")
    return rows


def _is_finite(val: Any) -> bool:
    try:
        return math.isfinite(float(val))
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Ola1/Ola2 bridge outputs.")
    parser.add_argument("--blocks-json", type=Path, required=True)
    parser.add_argument("--dna-csv", type=Path, required=True)
    parser.add_argument("--runs-full-jsonl", type=Path, required=True)
    args = parser.parse_args()

    blocks = _load_blocks(args.blocks_json)
    runs = _load_runs(args.runs_full_jsonl)
    dna_rows = _load_dna(args.dna_csv)

    block_ids: Set[str] = set()
    for block in blocks:
        block_id = _norm_id(block.get("block_id"))
        origin_run_id = _norm_id(block.get("origin_run_id"))
        if not block_id:
            raise RuntimeError("blocks_json missing block_id")
        if block_id in block_ids:
            raise RuntimeError(f"Duplicate block_id in blocks_json: {block_id}")
        block_ids.add(block_id)
        if not origin_run_id:
            raise RuntimeError(f"Missing origin_run_id for block_id={block_id}")
        if block_id != origin_run_id:
            raise RuntimeError(f"block_id mismatch for run_id={origin_run_id}: {block_id} != {origin_run_id}")
        run_rec = runs.get(origin_run_id)
        if not run_rec:
            raise RuntimeError(f"origin_run_id not found in runs_full.jsonl: {origin_run_id}")
        theta_internal = block.get("theta_internal")
        if not isinstance(theta_internal, dict):
            raise RuntimeError(f"Missing theta_internal for block_id={block_id}")
        validate_theta_internal(theta_internal)
        omega_ref = block.get("omega_ref")
        if not _is_finite(omega_ref):
            raise RuntimeError(f"Invalid omega_ref for block_id={block_id}")

    dna_block_ids: Set[str] = set()
    for row in dna_rows:
        block_id = _norm_id(row.get("block_id"))
        if not block_id:
            raise RuntimeError("dna_csv missing block_id")
        if block_id in dna_block_ids:
            raise RuntimeError(f"Duplicate block_id in dna_csv: {block_id}")
        dna_block_ids.add(block_id)
        omega_ref_proxy = row.get("omega_ref_proxy")
        if not _is_finite(omega_ref_proxy):
            raise RuntimeError(f"Invalid omega_ref_proxy for block_id={block_id}")
        genes_min = row.get("genes_min")
        if genes_min is None or str(genes_min).strip() == "":
            raise RuntimeError(f"Missing genes_min for block_id={block_id}")

    missing_in_dna = sorted(block_ids.difference(dna_block_ids))
    if missing_in_dna:
        sample = ", ".join(missing_in_dna[:5])
        raise RuntimeError(f"dna_csv missing block_id(s): {sample}")

    print("[validate_outputs] OK")


if __name__ == "__main__":
    main()
