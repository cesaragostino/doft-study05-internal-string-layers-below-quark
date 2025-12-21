"""
Inventory manager for wave harvesting and merging.

Subcommands:
- harvest: lee CSVs de resultados (ola2/ola3) y genera un JSON de bloques.
- merge: combina varios JSON de bloques en uno solo.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def _parse_list(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            return list(ast.literal_eval(val))
        except Exception:
            return []
    return []


def _parse_float(val: Any) -> float | None:
    try:
        v = float(val)
    except Exception:
        return None
    return v if math.isfinite(v) else None


def harvest(config: Path, root_dir: Path, output: Path, min_lock: float) -> int:
    cfg = json.loads(config.read_text())
    targets = cfg.get("targets", [])
    harvested: List[Dict[str, Any]] = []
    for tgt in targets:
        name = tgt.get("name")
        particle = tgt.get("particle_name") or name
        if not name:
            continue
        csv_path = root_dir / f"ola2_{name}.csv"
        if not csv_path.exists():
            print(f"[inventory] skip {name}: no CSV en {csv_path}")
            continue
        df = pd.read_csv(csv_path)
        if "success" in df.columns:
            df = df[df["success"] == True]  # noqa: E712
        elif "reason" in df.columns:
            df = df[df["reason"] == "locked"]
        df = df[df.get("R_final", 0) >= min_lock]
        if df.empty:
            print(f"[inventory] target={name}: sin filas tras filtro")
            continue
        for _, row in df.iterrows():
            run_id = int(float(row.get("run_id", 0)))
            particles = _parse_list(row.get("block_particles"))
            qual = _parse_float(row.get("QualityLock"))
            if qual is None:
                qual = _parse_float(row.get("R_final")) or 0.0
            block = {
                "id": f"{particle}_run_{run_id:04d}",
                "name": particle,
                "particle_name": particle,
                "family": particle,
                "mass": float(row.get("M_final", 0.0)),
                "source_run": run_id,
                "composition": particles,
                "particles": particles,
                "binding_energy": float(row.get("E_bind_mass", 0.0)),
                "quality": float(row.get("R_final", 0.0)),
                "lock_quality": {"Q": qual, "S1": 0.0, "S2": 0.0},
            }
            harvested.append(block)
        print(f"[inventory] target={name}: cosechados {len(df)} bloques")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(harvested, indent=2))
    print(f"[inventory] total bloques: {len(harvested)} -> {output}")
    return len(harvested)


def merge(inputs: List[Path], output: Path) -> int:
    combined: List[Dict[str, Any]] = []
    for p in inputs:
        if not p.exists():
            print(f"[inventory] skip merge input {p} (no existe)")
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            print(f"[inventory] no se pudo leer {p}")
            continue
        if not isinstance(data, list):
            print(f"[inventory] {p} no es lista; se omite")
            continue
        for blk in data:
            mass = _parse_float(blk.get("mass"))
            if mass is None:
                continue
            combined.append(blk)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(combined, indent=2))
    print(f"[inventory] combinados {len(combined)} bloques -> {output}")
    return len(combined)


def main():
    parser = argparse.ArgumentParser(description="Gestor de inventario para olas.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("harvest", help="Cosecha CSV de resultados a JSON de bloques.")
    h.add_argument("--config", type=Path, required=True, help="Config de la ola (targets).")
    h.add_argument("--root-dir", type=Path, required=True, help="Directorio con los CSV ola2_<target>.csv.")
    h.add_argument("--output", type=Path, required=True, help="JSON de salida.")
    h.add_argument("--min-lock", type=float, default=0.90, help="Filtro mínimo de R_final.")

    m = sub.add_parser("merge", help="Fusiona JSON de bloques en uno solo.")
    m.add_argument("--inputs", type=Path, nargs="+", required=True, help="JSONs a combinar.")
    m.add_argument("--output", type=Path, required=True, help="JSON de salida combinado.")

    args = parser.parse_args()
    if args.cmd == "harvest":
        harvest(args.config, args.root_dir, args.output, args.min_lock)
    elif args.cmd == "merge":
        merge(args.inputs, args.output)


if __name__ == "__main__":
    main()
