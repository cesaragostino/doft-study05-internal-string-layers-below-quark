#!/usr/bin/env python3
"""
Genera un reporte Markdown para Ola2 reloaded, comparando contra Ola1.

Entradas:
- Ola1: data/processed/ola1-chaos/Ola1_3-2-5_all_runs_proxies.csv (PE_tick_norm, mean_H_lock_norm)
- Ola2: data/processed/ola2_reloaded/ola2_*.csv (solo éxitos).

Salida:
- Markdown con Termómetro Cósmico, Yield, Defecto de masa, Memoria y Topología.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import math
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


def load_ola1_baseline(csv_path: Path) -> Tuple[float, float]:
    pe_vals: List[float] = []
    h_vals: List[float] = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            pe = _parse_float(row.get("PE_tick_norm"))
            h = _parse_float(row.get("mean_H_lock_norm"))
            if pe is not None and math.isfinite(pe):
                pe_vals.append(pe)
            if h is not None and math.isfinite(h):
                h_vals.append(h)
    pe_mean = float(np.mean(pe_vals)) if pe_vals else float("nan")
    h_mean = float(np.mean(h_vals)) if h_vals else float("nan")
    return pe_mean, h_mean


def load_ola2_runs(csv_root: Path):
    files = sorted(csv_root.glob("ola2_*.csv"))
    runs: List[Dict[str, Any]] = []
    for fpath in files:
        with fpath.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["__target"] = fpath.stem.replace("ola2_", "")
                runs.append(row)
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
    # Eb por nodo (nucleón) si nodes existe
    nodes_vals = []
    for r in rows:
        n = _parse_float(r.get("nodes"))
        if n is not None and n > 0:
            nodes_vals.append(n)
    nodes_mean = float(np.mean(nodes_vals)) if nodes_vals else float("nan")
    eb_per_node = defect / nodes_mean if nodes_mean and math.isfinite(nodes_mean) else float("nan")
    return {"sumM": sumM, "M_final": M_final, "mass_defect": defect, "Eb_per_node": eb_per_node}


def best_binding(rows: List[Dict[str, Any]], top: int = 5) -> List[Dict[str, Any]]:
    successes = [r for r in rows if _parse_bool(r.get("success"))]
    successes.sort(key=lambda r: _parse_float(r.get("mass_defect")) or 0.0, reverse=True)
    out = []
    for r in successes[:top]:
        out.append(
            {
                "compound_id": f"{r.get('target','')}_run_{int(float(r.get('run_id',0))):04d}",
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
):
    lines: List[str] = []
    lines.append("# Ola2 – Reporte de Entropía / Caos / Masa")
    # Termómetro cósmico
    all_success = [r for v in stats.values() for r in v["success_rows"]]
    ola2_pe = mean_of("PE_tick_norm", all_success)
    ola2_h = mean_of("H_block_mean", all_success)
    ola2_strain = avg_dynamic_strain(all_success)
    lines.append("## Termómetro cósmico (Ola1 → Ola2)")
    lines.append("| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |")
    lines.append("|---------|------------------------|------------------------|-----------------|")
    lines.append(f"| Caos dinámico (PE) | {ola1_pe:.3f} | {ola2_pe:.3f} | {ola2_pe - ola1_pe:+.3f} |")
    lines.append(f"| Entropía (H_lock) | {ola1_h:.4f} | {ola2_h:.4f} | {ola2_h - ola1_h:+.4f} |")
    lines.append(f"| Dynamic Strain (1-R_final) | n/a | {ola2_strain:.4f} | n/a |")
    lines.append("")

    # Yield
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

    # Defecto de masa
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
            f"| {r['compound_id']} | {r['compound_id'].split('_run_')[0]} | {r['sumM']:.3f} | "
            f"{r['M_final']:.3f} | {r['mass_defect']:.4f} | {r['nodes'] or 0:.0f} | "
            f"{', '.join(r['particles'])} |"
        )
    lines.append("")

    # Memoria y topología
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

    output.write_text("\n".join(lines))
    print(f"[ola2] reporte escrito en {output}")


def main():
    parser = argparse.ArgumentParser(description="Reporte Markdown para Ola2 reloaded.")
    parser.add_argument("--ola1-proxies", type=Path, default=Path("data/processed/ola1-chaos/Ola1_3-2-5_all_runs_proxies.csv"))
    parser.add_argument("--ola2-root", type=Path, default=Path("data/processed/ola2_reloaded"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola2_reloaded/ola2_report.md"))
    args = parser.parse_args()

    ola1_pe, ola1_h = load_ola1_baseline(args.ola1_proxies)
    runs = load_ola2_runs(args.ola2_root)
    stats = compute_stats(runs)
    render_report(ola1_pe, ola1_h, stats, args.output)


if __name__ == "__main__":
    main()
