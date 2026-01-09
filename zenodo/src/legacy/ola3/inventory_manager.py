"""
Inventory manager for wave harvesting and merging.

Subcommands:
- harvest: lee CSVs de resultados (ola2/ola3) y genera un JSON de bloques.
- harvest-species: lee species_catalog.jsonl + simple_blocks.json y genera un JSON de bloques.
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


def _load_species_catalog(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def _load_simple_blocks(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for blk in data:
        bid = blk.get("block_id") or blk.get("id")
        if bid:
            out[str(bid)] = blk
    return out


def _load_hbar(path: Path | None) -> float | None:
    if not path or not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return float(data.get("hbar_sim"))
    except Exception:
        return None


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


def harvest_species(
    species_catalog: Path,
    simple_blocks: Path,
    hbar_path: Path | None,
    output: Path,
    min_lock: float,
) -> int:
    rows = _load_species_catalog(species_catalog)
    if not rows:
        print(f"[inventory] no species rows in {species_catalog}")
        return 0
    blocks_map = _load_simple_blocks(simple_blocks)
    if not blocks_map:
        print(f"[inventory] warning: no blocks found in {simple_blocks} (mass sum may be empty)")
    hbar_sim = _load_hbar(hbar_path)
    if hbar_sim is None:
        print("[inventory] warning: hbar_sim missing; M_final will be null")

    harvested: List[Dict[str, Any]] = []
    for row in rows:
        best = row.get("best_metrics") or {}
        r_final = _parse_float(best.get("R_final")) or 0.0
        if r_final < min_lock:
            continue
        assignment = row.get("assignment") or []
        if not isinstance(assignment, list):
            assignment = []
        sum_mass = 0.0
        has_mass = False
        for bid in assignment:
            blk = blocks_map.get(str(bid))
            if not blk:
                continue
            m = _parse_float(blk.get("mass_sim_gev"))
            if m is None:
                m = _parse_float(blk.get("mass_gev"))
            if m is None:
                continue
            sum_mass += m
            has_mass = True
        omega_eff = _parse_float(best.get("omega_eff"))
        m_final = (hbar_sim * omega_eff) if (hbar_sim is not None and omega_eff is not None) else None
        e_bind = None
        if m_final is not None and has_mass:
            e_bind = sum_mass - m_final

        qual = _parse_float(best.get("QualityLock"))
        if qual is None:
            qual = r_final
        species_id = row.get("species_id") or row.get("structure_id")
        block = {
            "id": str(species_id),
            "name": str(species_id),
            "particle_name": str(species_id),
            "family": "species",
            "mass": m_final,
            "mass_units": "GeV" if m_final is not None else None,
            "source_run": None,
            "composition": assignment,
            "particles": assignment,
            "binding_energy": e_bind,
            "quality": r_final,
            "lock_quality": {"Q": qual, "S1": 0.0, "S2": 0.0},
            "template_name": row.get("template_name"),
            "seed_stability": row.get("seed_stability"),
            "n_trials": row.get("n_trials"),
            "n_viable": row.get("n_viable"),
            "omega_eff": omega_eff,
        }
        harvested.append(block)

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

    hs = sub.add_parser("harvest-species", help="Cosecha species_catalog.jsonl a JSON de bloques.")
    hs.add_argument("--species-catalog", type=Path, required=True, help="species_catalog.jsonl")
    hs.add_argument("--simple-blocks", type=Path, required=True, help="simple_blocks.json para sumas de masa")
    hs.add_argument("--hbar-sim", type=Path, default=None, help="hbar_sim_calibration.json")
    hs.add_argument("--output", type=Path, required=True, help="JSON de salida.")
    hs.add_argument("--min-lock", type=float, default=0.90, help="Filtro mínimo de R_final.")

    args = parser.parse_args()
    if args.cmd == "harvest":
        harvest(args.config, args.root_dir, args.output, args.min_lock)
    elif args.cmd == "merge":
        merge(args.inputs, args.output)
    elif args.cmd == "harvest-species":
        harvest_species(args.species_catalog, args.simple_blocks, args.hbar_sim, args.output, args.min_lock)


if __name__ == "__main__":
    main()
