"""
Harvest Ola2 reloaded outputs into blocks for Ola3.

Toma los CSV `ola2_<target>.csv` de Ola2 reloaded, filtra éxitos con buen lock
y genera un JSON de bloques que servirán de entrada para Ola3.
"""

from __future__ import annotations

import argparse
import ast
import json
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


def harvest(config_path: Path, ola2_root: Path, output: Path, min_lock: float) -> int:
    cfg = json.loads(config_path.read_text())
    targets = cfg.get("targets", [])
    harvested: List[Dict[str, Any]] = []

    for tgt in targets:
        name = tgt.get("name")
        particle = tgt.get("particle_name") or name
        if not name:
            continue
        csv_path = ola2_root / f"ola2_{name}.csv"
        if not csv_path.exists():
            print(f"[harvest] skip target={name}: no CSV en {csv_path}")
            continue
        df = pd.read_csv(csv_path)
        # filtros de éxito
        if "success" in df.columns:
            df = df[df["success"] == True]  # noqa: E712
        elif "reason" in df.columns:
            df = df[df["reason"] == "locked"]
        df = df[df.get("R_final", 0) >= min_lock]
        if df.empty:
            print(f"[harvest] target={name}: sin filas tras filtro")
            continue

        for _, row in df.iterrows():
            run_id = int(float(row.get("run_id", 0)))
            particles = _parse_list(row.get("block_particles"))
            block = {
                "id": f"{particle}_run_{run_id:04d}",
                "name": particle,
                "particle_name": particle,
                "family": particle,
                "mass": float(row.get("M_final", 0.0)),
                "source_run": run_id,
                "composition": particles,  # clave original
                "particles": particles,  # alias por compatibilidad
                "binding_energy": float(row.get("E_bind_mass", 0.0)),
                "quality": float(row.get("R_final", 0.0)),
                "lock_quality": {"Q": float(row.get("R_final", 0.0)), "S1": 0.0, "S2": 0.0},
            }
            harvested.append(block)
        print(f"[harvest] target={name}: cosechados {len(df)} bloques")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(harvested, indent=2))
    print(f"[harvest] total bloques: {len(harvested)} -> {output}")
    return len(harvested)


def main():
    parser = argparse.ArgumentParser(description="Cosecha bloques Ola2 para Ola3.")
    parser.add_argument("--config", type=Path, required=True, help="Config de Ola2 (wave2_compounds*.json).")
    parser.add_argument(
        "--ola2-root",
        type=Path,
        default=Path("data/processed/ola2_reloaded"),
        help="Directorio con los CSV ola2_<target>.csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ola2/harvested_blocks.json"),
        help="Ruta del JSON de salida para Ola3.",
    )
    parser.add_argument("--min-lock", type=float, default=0.95, help="Umbral mínimo de R_final para aceptar.")
    args = parser.parse_args()
    harvest(args.config, args.ola2_root, args.output, args.min_lock)


if __name__ == "__main__":
    main()
