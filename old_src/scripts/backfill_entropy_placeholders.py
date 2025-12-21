"""Add entropy/chaos placeholder fields to existing Study05 sweep outputs.

This does NOT compute any new metrics; it only ensures that older runs
carry the new keys with null values so the schema is consistent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


NEW_FIELDS = {
    "entropy_status": "skipped",
    "entropy_reason": "backfill_placeholder",
    "lyapunov_local": None,
    "lyapunov_mean": None,
    "phase_compactness": None,
    "phase_occupancy": None,
    "entropy_flags": None,
}


def _patch_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in NEW_FIELDS.items():
        rec.setdefault(k, v)
    return rec


def _patch_jsonl(path_in: Path, path_out: Path):
    lines_out: List[str] = []
    for line in path_in.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        rec = _patch_record(rec)
        lines_out.append(json.dumps(rec))
    path_out.write_text("\n".join(lines_out) + ("\n" if lines_out else ""))


def _patch_json(path_in: Path, path_out: Path):
    data = json.loads(path_in.read_text())
    if isinstance(data, dict) and "runs" in data and isinstance(data["runs"], list):
        data["runs"] = [_patch_record(r) for r in data["runs"]]
    else:
        data = _patch_record(data) if isinstance(data, dict) else data
    path_out.write_text(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Backfill entropy placeholder fields into existing sweep outputs.")
    parser.add_argument("input", type=Path, help="Input file (.jsonl or .json).")
    parser.add_argument("--output", type=Path, default=None, help="Output file. If omitted, overwrite input.")
    args = parser.parse_args()

    path_in = args.input
    path_out = args.output or path_in

    if not path_in.exists():
        raise SystemExit(f"Input file not found: {path_in}")

    if path_in.suffix.lower() == ".jsonl":
        _patch_jsonl(path_in, path_out)
    elif path_in.suffix.lower() == ".json":
        _patch_json(path_in, path_out)
    else:
        raise SystemExit("Unsupported file type. Use .json or .jsonl.")

    print(f"Backfilled entropy placeholders into {path_out}")


if __name__ == "__main__":
    main()
