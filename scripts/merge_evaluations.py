#!/usr/bin/env python3
"""Merge sweep evaluations with dedupe by eval_id."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set


def _iter_inputs(paths: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.exists():
            out.append(p)
            continue
        matches = list(Path().glob(raw))
        out.extend(sorted(matches))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge evaluations.jsonl shards with dedupe.")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input evaluations.jsonl files or globs.")
    parser.add_argument("--output", required=True, help="Output merged evaluations.jsonl.")
    parser.add_argument("--stats-output", required=False, help="Write merge stats JSON.")
    parser.add_argument("--sample-size", type=int, default=50, help="Duplicate sample size.")
    args = parser.parse_args()

    inputs = _iter_inputs(args.inputs)
    if not inputs:
        raise SystemExit("No input files found.")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    seen: Set[str] = set()
    duplicate_eval_ids_total = 0
    duplicate_eval_ids_sample: List[str] = []
    shard_sources: Dict[str, int] = {}
    written = 0

    with output_path.open("w") as out_f:
        for path in inputs:
            count = 0
            with path.open() as in_f:
                for line in in_f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    eval_id = rec.get("eval_id")
                    if not eval_id:
                        continue
                    if eval_id in seen:
                        duplicate_eval_ids_total += 1
                        if len(duplicate_eval_ids_sample) < args.sample_size:
                            duplicate_eval_ids_sample.append(str(eval_id))
                        continue
                    seen.add(str(eval_id))
                    out_f.write(json.dumps(rec) + "\n")
                    written += 1
                    count += 1
            shard_sources[str(path)] = count

    stats = {
        "inputs": [str(p) for p in inputs],
        "output": str(output_path),
        "written": written,
        "duplicate_eval_ids_total": duplicate_eval_ids_total,
        "duplicate_eval_ids_sample": duplicate_eval_ids_sample,
        "shard_sources": shard_sources,
    }
    if args.stats_output:
        stats_path = Path(args.stats_output)
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.write_text(json.dumps(stats, indent=2))
    else:
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
