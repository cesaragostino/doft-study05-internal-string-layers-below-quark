"""Assemble Ola1 artifacts for OLAR (DNA-first)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
from pathlib import Path
from typing import Any, Dict, List, Tuple

from core.ids.hashing import hash_file, hash_text, stable_dumps
from core.ids.time import utc_now_iso
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


def _as_float(val: Any) -> float | None:
    try:
        f = float(val)
        if math.isfinite(f):
            return f
    except Exception:
        return None
    return None


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
            status = rec.get("status")
            if status not in {"ok", "unstable"}:
                raise RuntimeError(f"runs_full.jsonl contains non-ok status: run_id={rid} status={status}")
            theta_internal = rec.get("theta_internal")
            if not isinstance(theta_internal, dict):
                raise RuntimeError(f"runs_full.jsonl missing theta_internal for run_id={rid}")
            validate_theta_internal(theta_internal)
            runs[rid] = rec
    if not runs:
        raise RuntimeError(f"runs_full.jsonl empty: {path}")
    return runs


def _load_dna_rows(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    if not path.exists():
        raise RuntimeError(f"DNA catalog missing: {path}")
    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    if not rows:
        raise RuntimeError(f"DNA catalog empty: {path}")
    required = {
        "run_id",
        "omega_ref_proxy",
        "genes_min",
        "dof_grade",
        "dof_family_id",
        "dof_family_friendly",
    }
    missing = sorted(col for col in required if col not in fieldnames)
    if missing:
        raise RuntimeError(f"DNA catalog missing columns: {missing}")
    return rows, fieldnames


def _parse_genes_min(raw: Any, run_id: str) -> Dict[str, Any]:
    if raw is None or str(raw).strip() == "":
        raise RuntimeError(f"genes_min missing for run_id={run_id}")
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(str(raw))
    except Exception as exc:
        raise RuntimeError(f"genes_min invalid JSON for run_id={run_id}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"genes_min must be object for run_id={run_id}")
    return data


def _build_block_id(run_id: str, policy: str) -> str:
    if policy == "run_id":
        return run_id
    if policy == "run_prefix":
        return f"run_{run_id}"
    raise RuntimeError(f"Unknown block_id policy: {policy}")


def _build_block(
    run_id: str,
    dna_row: Dict[str, Any],
    run_rec: Dict[str, Any],
    block_id_policy: str,
) -> Dict[str, Any]:
    omega_ref_proxy = _as_float(dna_row.get("omega_ref_proxy"))
    if omega_ref_proxy is None:
        raise RuntimeError(f"Invalid omega_ref_proxy for run_id={run_id}")
    genes_min = _parse_genes_min(dna_row.get("genes_min"), run_id)
    provenance = run_rec.get("provenance") if isinstance(run_rec.get("provenance"), dict) else {}
    config_hash = provenance.get("config_hash")
    code_hash = provenance.get("code_hash")
    inputs_hash = provenance.get("inputs_hash")
    run_session_id = run_rec.get("run_session_id")
    seed_policy = run_rec.get("seed_policy")
    if not config_hash or not code_hash or not inputs_hash:
        raise RuntimeError(f"Missing provenance hashes for run_id={run_id}")
    if run_session_id is None:
        run_session_id = ""
    if not seed_policy:
        raise RuntimeError(f"Missing seed_policy for run_id={run_id}")
    block_id = _build_block_id(run_id, block_id_policy)
    return {
        "schema_version": "olar_block_v1",
        "block_id": block_id,
        "origin_run_id": run_id,
        "omega_ref": omega_ref_proxy,
        "dof_grade": str(dna_row.get("dof_grade") or ""),
        "dof_family_id": str(dna_row.get("dof_family_id") or ""),
        "dof_family_friendly": str(dna_row.get("dof_family_friendly") or ""),
        "genes_min": genes_min,
        "theta_internal": run_rec.get("theta_internal"),
        "provenance": {
            "config_hash": config_hash,
            "code_hash": code_hash,
            "inputs_hash": inputs_hash,
            "run_session_id": run_session_id,
            "seed_policy": seed_policy,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble Ola1 canonical inputs for OLAR.")
    parser.add_argument("--runs-full-jsonl", type=Path, required=True)
    parser.add_argument("--dna-csv", type=Path, required=True)
    parser.add_argument("--blocks-output", type=Path, required=True)
    parser.add_argument("--dna-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, default=None)
    parser.add_argument(
        "--block-id-policy",
        choices=("run_id", "run_prefix"),
        default="run_id",
        help="Deterministic block_id policy.",
    )
    parser.add_argument("--allow-missing-runs", action="store_true")
    args = parser.parse_args()

    runs_full = _load_runs_full(args.runs_full_jsonl)
    dna_rows, dna_fields = _load_dna_rows(args.dna_csv)

    blocks: List[Dict[str, Any]] = []
    out_rows: List[Dict[str, Any]] = []
    missing_runs: List[str] = []

    for row in dna_rows:
        run_id = _norm_id(row.get("run_id"))
        if not run_id:
            raise RuntimeError("DNA catalog row missing run_id")
        run_rec = runs_full.get(run_id)
        if not run_rec:
            missing_runs.append(run_id)
            if args.allow_missing_runs:
                continue
            raise RuntimeError(f"run_id missing in runs_full.jsonl: {run_id}")
        block = _build_block(run_id, row, run_rec, args.block_id_policy)
        blocks.append(block)

        genes_min = _parse_genes_min(row.get("genes_min"), run_id)
        row_out = dict(row)
        row_out["block_id"] = block["block_id"]
        row_out["origin_run_id"] = run_id
        row_out["genes_min"] = json.dumps(genes_min, sort_keys=True, separators=(",", ":"))
        out_rows.append(row_out)

    args.blocks_output.parent.mkdir(parents=True, exist_ok=True)
    args.dna_output.parent.mkdir(parents=True, exist_ok=True)
    args.blocks_output.write_text(json.dumps(blocks, indent=2, ensure_ascii=True))

    fieldnames = list(dna_fields)
    if "block_id" not in fieldnames:
        fieldnames.insert(0, "block_id")
    if "origin_run_id" not in fieldnames:
        fieldnames.insert(1, "origin_run_id")
    with args.dna_output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    manifest_path = args.manifest_output or (args.blocks_output.parent / "ola1_olar_manifest.json")
    manifest = {
        "schema_version": "ola1_olar_manifest_v1",
        "timestamp_utc": utc_now_iso(),
        "inputs": {
            "runs_full_jsonl": str(args.runs_full_jsonl),
            "dna_csv": str(args.dna_csv),
        },
        "outputs": {
            "blocks_json": str(args.blocks_output),
            "dna_csv": str(args.dna_output),
        },
        "hashes": {
            "runs_full_jsonl": f"sha256:{hash_file(args.runs_full_jsonl)}",
            "dna_csv": f"sha256:{hash_file(args.dna_csv)}",
            "blocks_json": f"sha256:{hash_text(stable_dumps(blocks))}",
            "code_hash": f"sha256:{hash_file(Path(__file__))}",
        },
        "counts": {
            "runs_full": len(runs_full),
            "dna_rows": len(dna_rows),
            "blocks": len(blocks),
            "missing_runs": len(missing_runs),
        },
        "machine": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "notes": {
            "block_id_policy": args.block_id_policy,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True))

    print(f"[ola1_assemble] blocks={len(blocks)} dna_rows={len(out_rows)}")
    if missing_runs:
        print(f"[ola1_assemble] missing_runs={len(missing_runs)}")


if __name__ == "__main__":
    main()
