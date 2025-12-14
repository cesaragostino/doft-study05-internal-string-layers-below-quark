#!/usr/bin/env python3
"""
Generate a quick health/inventory report for Ola1 outputs.

Inputs (defaults point to data/processed/ola1):
  - sweep_results JSON (for run counts)
  - selection_log CSV (for accept/reject reasons)
  - simple_blocks.json (for accepted blocks inventory)
  - zoo_matches.csv (for radar: good matches que no fueron aceptados)

Output:
  - Markdown report with semáforo, inventario, radar, y pareto de rechazos.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def load_sweep_results(path_candidates: List[Path]) -> Tuple[int, int]:
    """Return runs_requested, runs_valid from first existing candidate."""
    for p in path_candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                summary = data.get("summary", {})
                return int(summary.get("runs_requested", 0)), int(summary.get("runs_valid", 0))
            except Exception:
                continue
    return 0, 0


def load_selection_log(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    if not path.exists():
        return rows
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_simple_blocks(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def load_zoo_matches(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    if not path.exists():
        return rows
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["d_total"] = float(row.get("d_total", "nan"))
            except Exception:
                pass
            rows.append(row)
    return rows


def summarize_inventory(blocks: List[Dict]) -> List[Tuple[str, int, float, float]]:
    by_particle: Dict[str, List[float]] = defaultdict(list)
    for b in blocks:
        try:
            d = b.get("match_score", {}).get("d_total")
            if d is None:
                continue
            d = float(d)
        except Exception:
            continue
        by_particle[b.get("particle_name", "unknown")].append(d)
    summary = []
    for particle, vals in sorted(by_particle.items()):
        best = min(vals) if vals else float("nan")
        avg = sum(vals) / len(vals) if vals else float("nan")
        summary.append((particle, len(vals), best, avg))
    return summary


def summarize_blocks_extended(blocks: List[Dict]) -> List[Dict]:
    stats: Dict[str, Dict] = {}
    for b in blocks:
        pname = b.get("particle_name", "unknown")
        st = stats.setdefault(
            pname,
            {
                "d": [],
                "tier": Counter(),
                "s2": Counter(),
            },
        )
        try:
            d = float(b.get("match_score", {}).get("d_total"))
            st["d"].append(d)
        except Exception:
            pass
        st["tier"][str(b.get("structure_tier", "unknown"))] += 1
        st["s2"][str(b.get("s2_state", "unknown"))] += 1

    out: List[Dict] = []
    for pname in sorted(stats.keys()):
        dvals = sorted(stats[pname]["d"])
        if dvals:
            d_min = dvals[0]
            d_max = dvals[-1]
            mid = len(dvals) // 2
            if len(dvals) % 2 == 0 and len(dvals) > 1:
                d_med = (dvals[mid - 1] + dvals[mid]) / 2
            else:
                d_med = dvals[mid]
        else:
            d_min = d_med = d_max = float("nan")
        out.append(
            {
                "particle": pname,
                "count": len(dvals),
                "d_min": d_min,
                "d_med": d_med,
                "d_max": d_max,
                "tier_counts": dict(stats[pname]["tier"]),
                "s2_counts": dict(stats[pname]["s2"]),
            }
        )
    return out


def _to_int(val) -> Optional[int]:
    try:
        return int(float(val))
    except Exception:
        return None


def radar_candidates(zoo: List[Dict], selection: List[Dict], d_threshold: float) -> List[Tuple[str, int, float]]:
    """Find particles with good matches (d_total < threshold) that were not accepted."""
    accepted_runs: set[int] = set()
    for r in selection:
        rid = _to_int(r.get("run_id"))
        if rid is None:
            continue
        if r.get("accepted") == "1" or r.get("accepted") == 1:
            accepted_runs.add(rid)
    bucket: Dict[str, List[float]] = defaultdict(list)
    for row in zoo:
        try:
            d = float(row.get("d_total", "nan"))
        except Exception:
            continue
        if not (d < d_threshold):
            continue
        rid = _to_int(row.get("run_id"))
        if rid is None:
            rid = -1
        if rid in accepted_runs:
            continue
        bucket[row.get("particle_name", "unknown")].append(d)
    out = []
    for particle, vals in sorted(bucket.items()):
        out.append((particle, len(vals), min(vals)))
    return out


def rejection_pareto(selection: List[Dict]) -> Counter:
    c = Counter()
    for row in selection:
        reasons = row.get("reasons", "")
        if not reasons:
            continue
        for r in reasons.split(";"):
            r = r.strip()
            if r:
                c[r] += 1
    return c


def main():
    parser = argparse.ArgumentParser(description="Generar informe de Ola1.")
    parser.add_argument("--case", default="Ola1_Discovery_3-2-5", help="Nombre del caso (para ubicar archivos).")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/ola1"), help="Dir base processed.")
    parser.add_argument("--selection-log", type=Path, default=None, help="Override path a ola1_blocks_selection.csv")
    parser.add_argument("--simple-blocks", type=Path, default=None, help="Override path a simple_blocks.json")
    parser.add_argument("--zoo-matches", type=Path, default=None, help="Override path a zoo_matches.csv")
    parser.add_argument("--sweep-results", type=Path, default=None, help="Override path a sweep_results.json")
    parser.add_argument("--d-threshold-radar", type=float, default=5.0, help="Umbral d_total para radar de zoo.")
    parser.add_argument("--output", type=Path, default=None, help="Reporte markdown de salida.")
    args = parser.parse_args()

    proc = args.processed_dir
    case = args.case
    selection_path = args.selection_log or proc / "ola1_blocks_selection.csv"
    blocks_path = args.simple_blocks or proc / "simple_blocks.json"
    zoo_path = args.zoo_matches or proc / "zoo_matches.csv"
    sweep_candidates = []
    if args.sweep_results:
        sweep_candidates.append(args.sweep_results)
    else:
        sweep_candidates.extend(
            [
                proc / f"{case}_study05_sweep_results.json",
                proc / "global" / "study05_sweep_results.json",
                proc / case / "study05_sweep_results.json",
            ]
        )

    runs_total, runs_valid = load_sweep_results(sweep_candidates)
    success_rate = (runs_valid / runs_total * 100.0) if runs_total else 0.0

    selection_rows = load_selection_log(selection_path)
    blocks = load_simple_blocks(blocks_path)
    zoo = load_zoo_matches(zoo_path)

    # fallback: if no sweep_results, infer totals from proxies/selection
    if runs_total == 0:
        proxies_path = proc / f"{case}_all_runs_proxies.csv"
        if proxies_path.exists():
            try:
                import csv

                with proxies_path.open() as f:
                    runs_total = sum(1 for _ in csv.DictReader(f))
            except Exception:
                runs_total = 0
        if runs_valid == 0 and selection_rows:
            runs_valid = sum(1 for r in selection_rows if str(r.get("accepted")).lower() in {"1", "true", "yes"})
        success_rate = (runs_valid / runs_total * 100.0) if runs_total else 0.0

    # Alerts
    reasons_counter = rejection_pareto(selection_rows)
    max_blocks_hits = reasons_counter.get("max_blocks_reached", 0)
    memory_hits = sum(v for k, v in reasons_counter.items() if "memory" in k.lower())
    alerts = []
    if max_blocks_hits > 0:
        alerts.append(f"ALERTA ROJA: max_blocks_reached={max_blocks_hits}")
    if memory_hits > 0:
        alerts.append(f"ALERTA AMARILLA: rechazos por memoria/overflow={memory_hits}")

    inventory = summarize_inventory(blocks)
    detailed = summarize_blocks_extended(blocks)
    radar = radar_candidates(zoo, selection_rows, args.d_threshold_radar)
    pareto = reasons_counter.most_common()

    lines = []
    lines.append(f"# Informe Ola1 – {case}")
    lines.append("")
    lines.append("## Semáforo de salud")
    lines.append(f"- Runs totales: {runs_total}")
    lines.append(f"- Runs aceptados: {runs_valid} ({success_rate:.1f}%)")
    if alerts:
        for a in alerts:
            lines.append(f"- {a}")
    else:
        lines.append("- Alertas: ninguna")
    lines.append("")

    lines.append("## Inventario (cosecha)")
    if inventory:
        lines.append("| Partícula | Cantidad | Mejor d_total | Promedio d_total |")
        lines.append("|-----------|----------|---------------|------------------|")
        for particle, count, best, avg in inventory:
            lines.append(f"| {particle} | {count} | {best:.3f} | {avg:.3f} |")
    else:
        lines.append("Sin bloques aceptados.")
    lines.append("")

    lines.append("## Detalle por partícula (d_total y conteos)")
    if detailed:
        lines.append("| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |")
        lines.append("|-----------|-------|-------|-------|-------|-------|-----------|")
        for item in detailed:
            tiers = ", ".join(f"{k}:{v}" for k, v in sorted(item["tier_counts"].items()))
            s2s = ", ".join(f"{k}:{v}" for k, v in sorted(item["s2_counts"].items()))
            lines.append(
                f"| {item['particle']} | {item['count']} | {item['d_min']:.3f} | "
                f"{item['d_med']:.3f} | {item['d_max']:.3f} | {tiers} | {s2s} |"
            )
    else:
        lines.append("Sin bloques aceptados.")
    lines.append("")

    lines.append(f"## Radar del Zoo (d_total < {args.d_threshold_radar}) no aceptados")
    if radar:
        lines.append("| Partícula | Cantidad | Mejor d_total |")
        lines.append("|-----------|----------|---------------|")
        for particle, count, best in radar:
            lines.append(f"| {particle} | {count} | {best:.3f} |")
    else:
        lines.append("Sin candidatos cercanos fuera de la selección.")
    lines.append("")

    lines.append("## Pareto de rechazos (causas en selección)")
    if pareto:
        lines.append("| Razón | Cuenta |")
        lines.append("|-------|--------|")
        for reason, count in pareto:
            lines.append(f"| {reason} | {count} |")
    else:
        lines.append("No hay registros de rechazo (o no se encontró el log).")
    lines.append("")

    output_path = args.output or proc / f"{case}_ola1_report.md"
    output_path.write_text("\n".join(lines))
    print(f"[report] escrito {output_path}")


if __name__ == "__main__":
    main()
