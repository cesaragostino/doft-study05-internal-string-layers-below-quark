#!/usr/bin/env python3
"""
QA global de estabilidad nuclear (olas 1-4).

Lee data/config/physics_constants.json para saber qué CSVs revisar y
genera data/reports/GLOBAL_QA_REPORT.md + stability_curve.png
comparando energía de enlace y masas contra valores reales.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
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


def validate_composition(row_particles_str: Any, expected: List[str]) -> bool:
    current = _parse_list(row_particles_str)
    return sorted(current) == sorted(expected)


def analyze_target(entry: Dict[str, Any]) -> Tuple[Dict[str, float], int]:
    csv_path = Path(entry["csv_path"])
    if not csv_path.exists():
        return {"mass_sim": np.nan, "eb_per_a_sim": np.nan, "precision": np.nan}, 0
    df = pd.read_csv(csv_path)
    if "success" in df.columns:
        df = df[df["success"] == True]  # noqa: E712
    elif "reason" in df.columns:
        df = df[df["reason"] == "locked"]
    expected = entry.get("filter_composition") or []
    if expected:
        df = df[df["block_particles"].apply(lambda x: validate_composition(x, expected))]
    count = len(df)
    if count == 0:
        return {"mass_sim": np.nan, "eb_per_a_sim": np.nan, "precision": np.nan}, 0
    A = float(entry["A"])
    mass_sim = df["M_final"].mean()
    eb_mev = df["E_bind_mass"].mean() * 1000.0
    eb_per_a = eb_mev / A if A else np.nan
    mass_real = float(entry["real_mass_gev"])
    precision = abs(mass_sim - mass_real) / mass_real * 100.0 if mass_real else np.nan
    return {"mass_sim": mass_sim, "eb_per_a_sim": eb_per_a, "precision": precision}, count


def render_report(entries: List[Dict[str, Any]], results: List[Dict[str, Any]], output_md: Path, plot_path: Path):
    lines: List[str] = []
    lines.append("# QA Global – Estabilidad Nuclear (olas 1–4)")
    lines.append("## Tabla de la verdad")
    lines.append("| Ola | Partícula | Éxitos (filtrados) | Masa Sim (GeV) | Masa Real (GeV) | Precisión (%) | Eb/A Sim (MeV) | Eb/A Real (MeV) |")
    lines.append("|-----|-----------|--------------------|----------------|-----------------|---------------|----------------|-----------------|")
    A_vals = []
    sim_vals = []
    real_vals = []
    for entry, res in zip(entries, results):
        lines.append(
            f"| {entry['wave']} | {entry['particle']} | {res['count']} | "
            f"{res['mass_sim']:.3f} | {entry['real_mass_gev']:.3f} | {res['precision']:.2f}% | "
            f"{res['eb_per_a_sim']:.2f} | {entry['real_binding_energy_per_nucleon_mev']:.2f} |"
        )
        if np.isfinite(res["eb_per_a_sim"]):
            A_vals.append(entry["A"])
            sim_vals.append(res["eb_per_a_sim"])
            real_vals.append(entry["real_binding_energy_per_nucleon_mev"])
    lines.append("")
    if plot_path:
        lines.append("## Curva de estabilidad")
        lines.append(f"![stability]({plot_path.name})")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines))
    print(f"[qa] reporte escrito en {output_md}")

    if A_vals:
        plt.figure(figsize=(6, 4))
        plt.plot(A_vals, sim_vals, marker="o", color="tab:blue", label="Simulado")
        plt.plot(A_vals, real_vals, marker="o", linestyle="--", color="tab:red", label="Real")
        plt.xlabel("Número de nucleones (A)")
        plt.ylabel("Eb/A (MeV)")
        plt.title("Curva de energía de enlace")
        plt.legend()
        plot_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        print(f"[qa] gráfico guardado en {plot_path}")


def main():
    parser = argparse.ArgumentParser(description="QA global de estabilidad nuclear.")
    parser.add_argument("--config", type=Path, default=Path("data/config/physics_constants.json"))
    parser.add_argument("--output-md", type=Path, default=Path("data/reports/GLOBAL_QA_REPORT.md"))
    parser.add_argument("--plot-path", type=Path, default=Path("data/reports/stability_curve.png"))
    args = parser.parse_args()

    cfg = json.loads(args.config.read_text())
    entries = cfg.get("qa_targets", [])
    results = []
    for entry in entries:
        res, count = analyze_target(entry)
        res["count"] = count
        results.append(res)
    render_report(entries, results, args.output_md, args.plot_path)


if __name__ == "__main__":
    main()
