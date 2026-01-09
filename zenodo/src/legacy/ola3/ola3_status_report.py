#!/usr/bin/env python3
"""
Reporte Markdown para Ola3.

Puede leer:
- CSV ola2_<target>.csv (legacy), o
- JSON de bloques generado por inventory_manager harvest-species.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


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


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "t"}


def _parse_float(val: Any) -> float | None:
    try:
        v = float(val)
        return v
    except Exception:
        return None


def load_ola1_baseline(csv_path: Path, partial_path: Path | None = None) -> Tuple[float, float]:
    pe_vals: List[float] = []
    h_vals: List[float] = []
    if csv_path.exists():
        with csv_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                pe = _parse_float(row.get("PE_tick_norm"))
                h = _parse_float(row.get("mean_H_lock_norm"))
                if pe is not None and math.isfinite(pe):
                    pe_vals.append(pe)
                if h is not None and math.isfinite(h):
                    h_vals.append(h)
    if (not pe_vals or not h_vals) and partial_path and partial_path.exists():
        for line in partial_path.read_text().splitlines():
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ec = obj.get("entropy_chaos") or {}
            pe = ec.get("PE_tick_norm")
            h = ec.get("mean_H_lock_norm")
            if pe is not None and math.isfinite(pe):
                pe_vals.append(float(pe))
            if h is not None and math.isfinite(h):
                h_vals.append(float(h))
    pe_mean = float(np.mean(pe_vals)) if pe_vals else float("nan")
    h_mean = float(np.mean(h_vals)) if h_vals else float("nan")
    return pe_mean, h_mean


def load_runs(csv_root: Path):
    files = sorted(csv_root.glob("ola2_*.csv"))
    runs: List[Dict[str, Any]] = []
    for fpath in files:
        with fpath.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["__target"] = fpath.stem.replace("ola2_", "")
                runs.append(row)
    return runs


def load_runs_blocks(blocks_json: Path) -> List[Dict[str, Any]]:
    if not blocks_json.exists():
        return []
    data = json.loads(blocks_json.read_text())
    if not isinstance(data, list):
        return []
    runs: List[Dict[str, Any]] = []
    for idx, blk in enumerate(data):
        particles = blk.get("particles") or blk.get("composition") or []
        if not isinstance(particles, list):
            particles = []
        qual = _parse_float((blk.get("lock_quality") or {}).get("Q"))
        r_final = _parse_float(blk.get("quality")) or 0.0
        mass_final = _parse_float(blk.get("mass"))
        bind = _parse_float(blk.get("binding_energy"))
        sumM = None
        if mass_final is not None and bind is not None:
            sumM = mass_final + bind
        target = blk.get("template_name") or blk.get("family") or "species"
        runs.append(
            {
                "__target": target,
                "run_id": blk.get("source_run") if blk.get("source_run") is not None else idx,
                "success": True,
                "reason": "locked",
                "block_particles": particles,
                "R_final": r_final,
                "QualityLock": qual,
                "M_final": mass_final,
                "sumM": sumM,
                "mass_defect": bind,
                "nodes": len(particles),
                "memory_score_k10": None,
                "PE_tick_norm": None,
                "H_block_mean": None,
                "effective_degree": None,
            }
        )
    return runs


def compute_stats(runs: List[Dict[str, Any]]):
    stats: Dict[str, Dict[str, Any]] = {}
    for r in runs:
        tgt = r["__target"]
        stats.setdefault(tgt, {"rows": [], "success_rows": []})
        stats[tgt]["rows"].append(r)
        if _parse_bool(r.get("success")):
            stats[tgt]["success_rows"].append(r)
    return stats


def mean_of(col: str, rows: List[Dict[str, Any]]) -> float:
    vals = []
    for r in rows:
        v = _parse_float(r.get(col))
        if v is not None and math.isfinite(v):
            vals.append(v)
    return float(np.mean(vals)) if vals else float("nan")


def avg_effective_degree(rows: List[Dict[str, Any]]) -> float:
    vals = []
    for r in rows:
        deg_list = _parse_list(r.get("effective_degree"))
        try:
            nums = [float(x) for x in deg_list]
        except Exception:
            nums = []
        if nums:
            vals.append(np.mean(nums))
    return float(np.mean(vals)) if vals else float("nan")


def avg_dynamic_strain(rows: List[Dict[str, Any]]) -> float:
    vals = []
    for r in rows:
        r_final = _parse_float(r.get("R_final"))
        if r_final is not None and math.isfinite(r_final):
            vals.append(1.0 - r_final)
    return float(np.mean(vals)) if vals else float("nan")


def summarize_mass(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    sumM = mean_of("sumM", rows)
    M_final = mean_of("M_final", rows)
    defect = mean_of("mass_defect", rows)
    nodes_vals = []
    for r in rows:
        n = _parse_float(r.get("nodes"))
        if n is not None and n > 0:
            nodes_vals.append(n)
    nodes_mean = float(np.mean(nodes_vals)) if nodes_vals else float("nan")
    eb_per_node = defect / nodes_mean if nodes_mean and math.isfinite(nodes_mean) else float("nan")
    return {"sumM": sumM, "M_final": M_final, "mass_defect": defect, "Eb_per_node": eb_per_node}


def best_binding(rows: List[Dict[str, Any]], top: int = 10) -> List[Dict[str, Any]]:
    successes = [r for r in rows if _parse_bool(r.get("success"))]
    successes.sort(key=lambda r: _parse_float(r.get("mass_defect")) or 0.0, reverse=True)
    out = []
    for r in successes[:top]:
        out.append(
            {
                "compound_id": f"{r.get('target','')}_run_{int(float(r.get('run_id',0))):04d}",
                "target": r.get("target") or r.get("__target"),
                "sumM": _parse_float(r.get("sumM")),
                "M_final": _parse_float(r.get("M_final")),
                "mass_defect": _parse_float(r.get("mass_defect")),
                "nodes": _parse_float(r.get("nodes")),
                "particles": _parse_list(r.get("block_particles")),
            }
        )
    return out


def render_report(
    ola1_pe: float,
    ola1_h: float,
    stats: Dict[str, Dict[str, Any]],
    output: Path,
    list_max_per_target: int = 20,
):
    lines: List[str] = []
    lines.append("# Ola3 – Reporte de Entropía / Caos / Masa")
    lines.append("## Cómo se calcula la masa")
    lines.append("")
    lines.append("Energía de enlace en Ola3 (motor Ola2 reloaded):")
    lines.append("- $E_{bind} = \\gamma \\cdot (\\sum M_{iniciales}) \\cdot R_{final} \\cdot Q_{lock}$")
    lines.append("- $M_{final} = \\sum M_{iniciales} - E_{bind}$")
    lines.append("Nota: $\\gamma$ según la config de Ola3; $Q_{lock}$ es la calidad media del lock.")
    lines.append("")

    all_success = [r for v in stats.values() for r in v["success_rows"]]
    ola3_pe = mean_of("PE_tick_norm", all_success)
    ola3_h = mean_of("H_block_mean", all_success)
    ola3_strain = avg_dynamic_strain(all_success)
    lines.append("## Termómetro cósmico (Ola1 → Ola3)")
    lines.append("| Métrica | Promedio Ola1 (inputs) | Promedio Ola3 (éxitos) | Δ (Ola3 - Ola1) |")
    lines.append("|---------|------------------------|------------------------|-----------------|")
    lines.append(f"| Caos dinámico (PE) | {ola1_pe:.3f} | {ola3_pe:.3f} | {ola3_pe - ola1_pe:+.3f} |")
    lines.append(f"| Entropía (H_lock) | {ola1_h:.4f} | {ola3_h:.4f} | {ola3_h - ola1_h:+.4f} |")
    lines.append(f"| Dynamic Strain (1-R_final) | n/a | {ola3_strain:.4f} | n/a |")
    lines.append("")

    lines.append("## Rendimiento del reactor")
    lines.append("| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |")
    lines.append("|--------|------|--------|---------|-------------------|---------|-------|")
    for tgt, d in stats.items():
        rows = d["rows"]
        succ = d["success_rows"]
        total = len(rows)
        succ_n = len(succ)
        geom = sum(1 for r in rows if str(r.get("reason")) == "geometry_mismatch")
        nolock = sum(1 for r in rows if str(r.get("reason")) == "no_lock")
        otros = total - succ_n - geom - nolock
        pct = 100.0 * succ_n / total if total else 0.0
        lines.append(f"| {tgt} | {total} | {succ_n} | {pct:.1f}% | {geom} | {nolock} | {otros} |")
    lines.append("")

    lines.append("## Tabla de fusión (defecto de masa)")
    lines.append("| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |")
    lines.append("|--------|------|-----------|-------|------------|")
    for tgt, d in stats.items():
        m = summarize_mass(d["success_rows"])
        lines.append(
            f"| {tgt} | {m['sumM']:.3f} | {m['M_final']:.3f} | {m['mass_defect']:.4f} | {m['Eb_per_node']:.4f} |"
        )
    lines.append("")

    lines.append("### Top binding (mayor E_b)")
    lines.append("| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |")
    lines.append("|----------|--------|----|---------|-----|-------|------------|")
    top_global = best_binding(all_success, top=10)
    for r in top_global:
        lines.append(
            f"| {r['compound_id']} | {r['target']} | {r['sumM']:.3f} | "
            f"{r['M_final']:.3f} | {r['mass_defect']:.4f} | {r['nodes'] or 0:.0f} | "
            f"{', '.join(r['particles'])} |"
        )
    lines.append("")

    lines.append("## Dinámica de memoria y topología")
    lines.append("| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |")
    lines.append("|--------|--------------------|-------------------|------------------|")
    for tgt, d in stats.items():
        succ = d["success_rows"]
        mem = mean_of("memory_score_k10", succ)
        strain = avg_dynamic_strain(succ)
        deg = avg_effective_degree(succ)
        lines.append(f"| {tgt} | {mem:.4f} | {strain:.4f} | {deg:.3f} |")
    lines.append("")

    lines.append("## Compuestos aceptados (detalle)")
    for tgt, d in stats.items():
        succ = d["success_rows"]
        if not succ:
            continue
        lines.append(f"### {tgt}")
        lines.append("| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |")
        lines.append("|--------|----|---------|-----|---------|--------|----|---------|------------|")
        rows = succ if list_max_per_target < 0 else succ[:list_max_per_target]
        for r in rows:
            particles = ", ".join(_parse_list(r.get("block_particles")))
            lines.append(
                f"| {int(float(r.get('run_id',0)))} | "
                f"{_parse_float(r.get('sumM')) or 0:.3f} | "
                f"{_parse_float(r.get('M_final')) or 0:.3f} | "
                f"{_parse_float(r.get('mass_defect')) or 0:.4f} | "
                f"{_parse_float(r.get('R_final')) or 0:.3f} | "
                f"{_parse_float(r.get('QualityLock')) or 0:.3f} | "
                f"{_parse_float(r.get('PE_tick_norm')) or 0:.3f} | "
                f"{_parse_float(r.get('H_block_mean')) or 0:.4f} | "
                f"{particles} |"
            )
        if list_max_per_target >= 0 and len(succ) > list_max_per_target:
            lines.append(f"_({len(succ) - list_max_per_target} más…)_")
        lines.append("")

    output.write_text("\n".join(lines))
    print(f"[ola3] reporte escrito en {output}")


def main():
    parser = argparse.ArgumentParser(description="Reporte Markdown para Ola3.")
    parser.add_argument("--ola1-proxies", type=Path, default=Path("data/processed/ola1-chaos/Ola1_3-2-5_all_runs_proxies.csv"))
    parser.add_argument("--ola1-partial", type=Path, default=Path("data/processed/ola1-chaos/partial/runs_partial.jsonl"))
    parser.add_argument("--ola3-root", type=Path, default=Path("data/processed/ola3"))
    parser.add_argument("--blocks-json", type=Path, default=None, help="JSON de bloques (inventory_manager harvest-species).")
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola3/ola3_report.md"))
    parser.add_argument("--list-max-per-target", type=int, default=20, help="Máximo de compuestos listados por target (-1 para todos).")
    args = parser.parse_args()

    ola1_pe, ola1_h = load_ola1_baseline(args.ola1_proxies, args.ola1_partial)
    if args.blocks_json:
        runs = load_runs_blocks(args.blocks_json)
    else:
        runs = load_runs(args.ola3_root)
    stats = compute_stats(runs)
    render_report(ola1_pe, ola1_h, stats, args.output, list_max_per_target=args.list_max_per_target)


if __name__ == "__main__":
    main()
