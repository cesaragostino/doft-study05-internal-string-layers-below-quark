#!/usr/bin/env python3
"""
Reporte Ola2 a partir de harvest_full.jsonl (sin depender de CSV).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def load_harvest(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def mean(vals: List[float]) -> float:
    arr = [v for v in vals if v is not None and np.isfinite(v)]
    return float(np.mean(arr)) if arr else float("nan")


def compute_stats(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    stats: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        tgt = r.get("target_name") or r.get("particle_name") or "unknown"
        stats.setdefault(tgt, {"rows": [], "success": []})
        stats[tgt]["rows"].append(r)
        if str(r.get("status", "")).lower() == "ok":
            stats[tgt]["success"].append(r)
    return stats


def render_report(stats: Dict[str, Dict[str, Any]], output: Path):
    lines: List[str] = []
    lines.append("# Ola2 – Reporte desde harvest_full.jsonl")
    lines.append("## Rendimiento por target")
    lines.append("| Target | Runs | Éxitos | Éxito % | R_final (mean) | PE (mean) | H_lock (mean) | Mass (mean) | Binding (mean) |")
    lines.append("|--------|------|--------|---------|-----------------|-----------|---------------|-------------|----------------|")
    for tgt, d in stats.items():
        all_rows = d["rows"]
        succ = d["success"]
        total = len(all_rows)
        succ_n = len(succ)
        pct = 100.0 * succ_n / total if total else 0.0
        lines.append(
            f"| {tgt} | {total} | {succ_n} | {pct:.1f}% | "
            f"{mean([r.get('R_final') for r in succ]):.3f} | "
            f"{mean([r.get('PE') for r in succ]):.3f} | "
            f"{mean([r.get('H_lock') for r in succ]):.4f} | "
            f"{mean([r.get('mass_gev') for r in succ]):.3f} | "
            f"{mean([r.get('binding_energy') for r in succ]):.4f} |"
        )
    output.write_text("\n".join(lines))
    print(f"[ola2] reporte (harvest) escrito en {output}")


def main():
    parser = argparse.ArgumentParser(description="Reporte Ola2 desde harvest_full.jsonl.")
    parser.add_argument("--harvest-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola2/ola2_report_from_harvest.md"))
    args = parser.parse_args()

    if not args.harvest_jsonl.exists():
        print(f"[ola2] no existe harvest en {args.harvest_jsonl}")
        return
    rows = load_harvest(args.harvest_jsonl)
    stats = compute_stats(rows)
    render_report(stats, args.output)


if __name__ == "__main__":
    main()
