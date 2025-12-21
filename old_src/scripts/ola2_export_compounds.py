#!/usr/bin/env python3
"""
Exporta los intentos de Ola2 (CSV por target) a un JSON de "compounds" similar a simple_blocks.

Entrada: los CSV generados por study06.run_ola2_compounds (ola2_<target>.csv).
Salida: un único JSON con la lista de compounds.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


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
        return float(val)
    except Exception:
        return None


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "t"}


def convert_csv(csv_path: Path, include_fails: bool) -> List[Dict[str, Any]]:
    compounds: List[Dict[str, Any]] = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            success = _parse_bool(row.get("success"))
            if not include_fails and not success:
                continue

            run_id = int(float(row.get("run_id", 0.0)))
            target = row.get("target", "")
            compound_id = f"{target}_run_{run_id:04d}"

            block_ids = _parse_list(row.get("block_ids"))
            block_particles = _parse_list(row.get("block_particles"))
            block_families = _parse_list(row.get("block_families"))
            fm_list = [_parse_float(x) for x in _parse_list(row.get("F_m_list")) if _parse_float(x) is not None]
            mass_list = [_parse_float(x) for x in _parse_list(row.get("mass_list")) if _parse_float(x) is not None]
            origin_run_ids = _parse_list(row.get("origin_run_ids"))

            compounds.append(
                {
                    "compound_id": compound_id,
                    "run_id": run_id,
                    "target": target,
                    "template": row.get("template_name"),
                    "status": row.get("status"),
                    "success": success,
                    "reason": row.get("reason"),
                    "metrics": {
                        "R_final": _parse_float(row.get("R_final")),
                        "R_mean_lastW": _parse_float(row.get("R_mean_lastW")),
                        "phase_var_lastW": _parse_float(row.get("phase_var_lastW")),
                        "PE_tick_norm": _parse_float(row.get("PE_tick_norm")),
                        "memory_score_k10": _parse_float(row.get("memory_score_k10")),
                        "QualityLock": _parse_float(row.get("QualityLock")),
                        "entropy_quality": _parse_float(row.get("entropy_quality")),
                        "H_block_mean": _parse_float(row.get("H_block_mean")),
                    },
                    "mass": {
                        "sumM": _parse_float(row.get("sumM")),
                        "M_final": _parse_float(row.get("M_final")),
                        "mass_defect": _parse_float(row.get("mass_defect")),
                        "E_bind_mass": _parse_float(row.get("E_bind_mass")),
                    },
                    "topology": {
                        "nodes": _parse_float(row.get("nodes")),
                        "edges_count": _parse_float(row.get("edges_count")),
                        "degree_raw": _parse_list(row.get("degree_raw")),
                        "degree_normalized": _parse_list(row.get("degree_normalized")),
                        "effective_degree": _parse_list(row.get("effective_degree")),
                    },
                    "blocks": {
                        "block_ids": block_ids,
                        "block_particles": block_particles,
                        "block_families": block_families,
                        "F_m_list": fm_list,
                        "mass_list": mass_list,
                        "origin_run_ids": origin_run_ids,
                        "fm_missing": _parse_bool(row.get("fm_missing")),
                    },
                }
            )
    return compounds


def main():
    parser = argparse.ArgumentParser(description="Exporta los CSV de Ola2 reloaded a JSON de compounds.")
    parser.add_argument("--input-root", type=Path, default=Path("data/processed/ola2_reloaded"), help="Carpeta con ola2_*.csv")
    parser.add_argument("--output-json", type=Path, default=Path("data/processed/ola2_reloaded/ola2_compounds.json"))
    parser.add_argument("--include-fails", action="store_true", help="Incluir intentos fallidos (por defecto solo success).")
    parser.add_argument("--targets", nargs="*", help="Filtrar por nombres de target (coinciden con ola2_<target>.csv)")
    args = parser.parse_args()

    files = sorted(args.input_root.glob("ola2_*.csv"))
    if args.targets:
        wanted = {t.lower() for t in args.targets}
        files = [f for f in files if f.stem.replace("ola2_", "").lower() in wanted]

    all_compounds: List[Dict[str, Any]] = []
    for csv_file in files:
        all_compounds.extend(convert_csv(csv_file, include_fails=args.include_fails))

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(all_compounds, indent=2))
    print(f"[ola2] exportados {len(all_compounds)} compounds a {args.output_json}")


if __name__ == "__main__":
    main()
