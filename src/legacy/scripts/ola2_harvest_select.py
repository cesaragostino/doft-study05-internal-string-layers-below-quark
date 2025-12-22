#!/usr/bin/env python3
"""
Selector/tagger para Ola2 a partir de harvest_full.jsonl.

Lee un JSONL de harvest (todas las corridas) y genera compounds.json
filtrando éxito y opcionalmente un archivo con los rechazados.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def load_harvest(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def main():
    parser = argparse.ArgumentParser(description="Selecciona/taggea Ola2 desde harvest_full.jsonl")
    parser.add_argument("--harvest-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola2/compounds.json"))
    parser.add_argument("--rejections-jsonl", type=Path, default=Path("data/processed/ola2/harvest_rejections.jsonl"))
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"), help="Opcional: catalogo SM para match o fallback unknown.")
    args = parser.parse_args()

    if not args.harvest_jsonl.exists():
        print(json.dumps({"status": "skip", "reason": "no_harvest", "path": str(args.harvest_jsonl)}))
        return

    sm_names = set()
    if args.sm_universe.exists():
        try:
            sm_data = json.loads(args.sm_universe.read_text())
            sm_names = {p.get("name", "").lower() for p in sm_data.get("particles", [])}
        except Exception:
            sm_names = set()

    rows = load_harvest(args.harvest_jsonl)
    accepted = []
    rejected = []
    for r in rows:
        status = str(r.get("status", "")).lower()
        reason = str(r.get("reason", ""))
        if status == "ok" and reason != "geometry_mismatch":
            pname = str(r.get("particle_name") or r.get("target_name") or "unknown").lower()
            r["sm_match"] = pname if pname in sm_names else "unknown"
            accepted.append(r)
        else:
            rejected.append(r)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(accepted, indent=2))
    print(json.dumps({"status": "ok", "accepted": len(accepted), "rejected": len(rejected), "output": str(args.output)}))
    if rejected and args.rejections_jsonl:
        args.rejections_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with args.rejections_jsonl.open("w") as f:
            for r in rejected:
                f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
