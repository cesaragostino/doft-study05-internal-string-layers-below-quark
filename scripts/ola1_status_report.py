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
from typing import Dict, List, Tuple, Optional
import math
import statistics
from functools import lru_cache

CHAOS_EPS = 1e-12


def _lock_entropy_norm_from_weights(weights: Dict[str, float]) -> float:
    """Shannon entropy normalized for 3 components (Q, S1, S2)."""
    q = max(float(weights.get("Q", 0.0)), 0.0)
    s1 = max(float(weights.get("S1", 0.0)), 0.0)
    s2 = max(float(weights.get("S2", 0.0)), 0.0)
    s = q + s1 + s2
    if s <= CHAOS_EPS:
        p = [1 / 3, 1 / 3, 1 / 3]
    else:
        p = [q / s, s1 / s, s2 / s]
    return float(-sum(pi * math.log(pi + CHAOS_EPS) for pi in p) / math.log(3))


@lru_cache()
def load_sm_masses(path: Path) -> Dict[str, float]:
    """Load SM masses from sm_universe JSON keyed by particle name."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    masses = {}
    for item in data.get("particles", []):
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        sm_val = item.get("sm_mass_gev")
        try:
            sm_val = float(sm_val)
        except Exception:
            continue
        masses[name] = sm_val
    return masses


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


def _aggregate_entropy(runs: List[Dict]) -> Optional[Dict]:
    pe_vals = []
    ticks_vals = []
    chaos_mode_counts: Counter = Counter()
    hlock_mean_vals = []
    mix_vals = []
    struct_mix_vals = []
    frac_struct_vals = []
    for r in runs:
        ec = r.get("entropy_chaos") or {}
        if not isinstance(ec, dict):
            continue
        chaos_mode = ec.get("chaos_mode")
        if chaos_mode:
            chaos_mode_counts[chaos_mode] += 1
        pe = ec.get("PE_tick_norm")
        if pe is not None and math.isfinite(pe):
            pe_vals.append(float(pe))
        t_ticks = ec.get("T_ticks")
        if t_ticks is not None and math.isfinite(t_ticks):
            ticks_vals.append(float(t_ticks))
        mh = ec.get("mean_H_lock_norm")
        if mh is not None and math.isfinite(mh):
            hlock_mean_vals.append(float(mh))
        mix = ec.get("mixture_entropy_blocks_norm")
        if mix is not None and math.isfinite(mix):
            mix_vals.append(float(mix))
        smix = ec.get("structure_mix_norm")
        if smix is not None and math.isfinite(smix):
            struct_mix_vals.append(float(smix))
        fstr = ec.get("fraction_structured")
        if fstr is not None and math.isfinite(fstr):
            frac_struct_vals.append(float(fstr))
    total = sum(chaos_mode_counts.values())
    if total == 0:
        return {"total_runs": 0, "chaos_mode": {}}

    def _safe_stats(vals: List[float]):
        if not vals:
            return None, None, None, None
        vals_sorted = sorted(vals)
        mid = len(vals_sorted) // 2
        median = (
            (vals_sorted[mid - 1] + vals_sorted[mid]) / 2
            if len(vals_sorted) % 2 == 0 and len(vals_sorted) > 1
            else vals_sorted[mid]
        )
        return float(sum(vals_sorted) / len(vals_sorted)), median, float(min(vals_sorted)), float(max(vals_sorted))

    pe_stats = _safe_stats(pe_vals)
    ticks_stats = _safe_stats(ticks_vals)
    hlock_stats = _safe_stats(hlock_mean_vals)
    mix_stats = _safe_stats(mix_vals)
    struct_mix_stats = _safe_stats(struct_mix_vals)
    frac_struct_stats = _safe_stats(frac_struct_vals)

    return {
        "total_runs": total,
        "chaos_mode": dict(chaos_mode_counts),
        "pe_stats": pe_stats,  # mean, median, min, max
        "ticks_stats": ticks_stats,
        "hlock_mean_stats": hlock_stats,
        "mix_stats": mix_stats,
        "struct_mix_stats": struct_mix_stats,
        "frac_struct_stats": frac_struct_stats,
    }


def load_entropy_summary(path_candidates: List[Path]) -> Optional[Dict]:
    """Aggregate entropy/caos metrics from the first sweep_results found."""
    for p in path_candidates:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
            runs = data.get("runs", [])
        except Exception:
            continue
        summary = _aggregate_entropy(runs)
        if summary:
            return summary
    return None


def load_entropy_summary_partial(path_candidates: List[Path]) -> Optional[Dict]:
    """Aggregate entropy/caos metrics from partial JSONL runs."""
    for p in path_candidates:
        if not p.exists():
            continue
        runs = []
        try:
            with p.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        runs.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue
        if not runs:
            continue
        pe_vals = []
        ticks_vals = []
        chaos_mode_counts: Counter = Counter()
        hlock_mean_vals = []
        mix_vals = []
        struct_mix_vals = []
        frac_struct_vals = []
        summary = _aggregate_entropy(runs)
        if summary:
            return summary
    return None


def load_runs_any(proc: Path, case: str, sweep_candidates: List[Path]) -> List[Dict]:
    """Return runs from sweep_results if present; otherwise from partial JSONL."""
    for p in sweep_candidates:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
            runs = data.get("runs", [])
            if runs:
                return runs
        except Exception:
            continue
    partial_candidates = [
        proc / "partial" / "runs_partial.jsonl",
        proc / "global" / "partial" / "runs_partial.jsonl",
        proc / case / "partial" / "runs_partial.jsonl",
    ]
    for p in partial_candidates:
        if not p.exists():
            continue
        runs = []
        try:
            with p.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        runs.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue
        if runs:
            return runs
    return []


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
    entropy_source = "sweep_results"
    entropy_summary = load_entropy_summary(sweep_candidates)

    selection_rows = load_selection_log(selection_path)
    blocks = load_simple_blocks(blocks_path)
    zoo = load_zoo_matches(zoo_path)
    sm_masses = load_sm_masses(Path("data/raw/sm_universe.json"))

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
    # Fallback: try partial runs if no entropy from sweep_results
    partial_candidates = [
        proc / "partial" / "runs_partial.jsonl",
        proc / "global" / "partial" / "runs_partial.jsonl",
        proc / case / "partial" / "runs_partial.jsonl",
    ]
    if (not entropy_summary) or entropy_summary.get("total_runs", 0) == 0:
        entropy_summary_partial = load_entropy_summary_partial(partial_candidates)
        if entropy_summary_partial and entropy_summary_partial.get("total_runs", 0) > 0:
            entropy_summary = entropy_summary_partial
            entropy_source = "partial_runs"

    run_records = load_runs_any(proc, case, sweep_candidates)
    runs_by_id = {}
    for r in run_records:
        rid = _to_int(r.get("run_id"))
        if rid is None:
            continue
        runs_by_id[rid] = r

    lines.append("## Bloques aceptados con métricas de entropía/caos")
    if blocks and runs_by_id:
        for b in blocks:
            rid_raw = b.get("origin_run_id")
            rid = _to_int(rid_raw)
            run = runs_by_id.get(rid)
            ec = run.get("entropy_chaos") if run else None
            lines.append(f"### {b.get('block_id', 'block')} (run_id={rid})")
            lines.append(f"- Partícula: {b.get('particle_name')}, tier: {b.get('structure_tier')}, s2_state: {b.get('s2_state')}")
            ms = b.get("match_score", {}) or {}
            d_total = ms.get("d_total")
            if d_total is not None:
                try:
                    lines.append(f"- match_score.d_total: {float(d_total):.3f}")
                except Exception:
                    lines.append(f"- match_score.d_total: {d_total}")
            lines.append(f"- Bandas: count={b.get('band_count')}, s2_band_fraction={b.get('s2_band_fraction')}")
            if run:
                energies = run.get("band_energies_gev") or []
                capture = run.get("band_power_capture")
                lines.append(f"- band_energies_gev: {energies}")
                if energies:
                    try:
                        fm = float(min(energies))
                        lines.append(f"- F_m (base): {fm:.3f} GeV")
                    except Exception:
                        fm = energies[0]
                        lines.append(f"- F_m (base): {fm} GeV")
                else:
                    fm = None
                # mass proxies
                h_block = None
                lq = b.get("lock_quality") or {}
                if lq:
                    h_block = _lock_entropy_norm_from_weights(lq)
                sm_mass = None
                pname = str(b.get("particle_name", "")).strip()
                if pname and sm_masses:
                    sm_mass = sm_masses.get(pname)
                m_eff = run.get("mass_effective") or run.get("effective_mass") or run.get("mass")
                if m_eff is not None:
                    try:
                        m_eff_val = float(m_eff)
                        lines.append(f"- M_eff (run): {m_eff_val:.3f}")
                    except Exception:
                        lines.append(f"- M_eff (run): {m_eff}")
                elif fm is not None:
                    lines.append(f"- M_eff (base≈F_m): {fm:.3f}")
                    if h_block is not None:
                            m_corr = fm * (1.0 - h_block)
                            if m_corr < 0:
                                m_corr = 0.0
                            lines.append(f"- M_corrected (F_m*(1-H_block)): {m_corr:.3f} (H_block={h_block:.3f})")
                if sm_mass is not None:
                    lines.append(f"- sm_mass_gev: {sm_mass:.3f}")
                    if fm is not None:
                        dev = ((fm - sm_mass) / sm_mass) * 100.0
                        lines.append(f"- Δ_mass vs SM: {dev:+.4f}%")
                if h_block is not None:
                    lines.append(f"- H_block (lock_quality): {h_block:.3f}")
                else:
                    lines.append("- M_eff: n/d")
                if capture is not None:
                    lines.append(f"- band_power_capture: {capture}")
            if ec:
                lines.append(
                    f"- chaos_mode={ec.get('chaos_mode')}, PE_tick_norm={ec.get('PE_tick_norm')}, T_ticks={ec.get('T_ticks')}"
                )
                lines.append(
                    f"- mean_H_lock_norm={ec.get('mean_H_lock_norm')}, mixture_entropy_blocks_norm={ec.get('mixture_entropy_blocks_norm')}, structure_mix_norm={ec.get('structure_mix_norm')}"
                )
                lines.append(f"- fraction_structured={ec.get('fraction_structured')}")
                series = ec.get("lock_S1_series") or []
                if isinstance(series, list) and series:
                    s_mean = statistics.mean(series)
                    s_min = min(series)
                    s_max = max(series)
                    lines.append(f"- lock_S1_series (mean/min/max): {s_mean:.4f} / {s_min:.4f} / {s_max:.4f}")
            else:
                lines.append("- entropy_chaos: no encontrado para este run.")
            lines.append("")
    else:
        lines.append("Sin bloques aceptados o no se encontraron runs para mapear entropy_chaos.")
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

    lines.append("## Entropía / Caos (nuevo)")
    if entropy_summary and entropy_summary.get("total_runs", 0) > 0:
        lines.append(f"- Fuente de datos: {entropy_source}")
        cm = entropy_summary.get("chaos_mode", {})
        lines.append(f"- Runs con entropy_chaos: {entropy_summary['total_runs']}")
        lines.append(f"- chaos_mode: dynamic={cm.get('dynamic', 0)}, ensemble={cm.get('ensemble', 0)}")
        pe = entropy_summary.get("pe_stats")
        if pe and pe[0] is not None:
            lines.append(f"- PE_tick_norm (mean/med/min/max): {pe[0]:.3f} / {pe[1]:.3f} / {pe[2]:.3f} / {pe[3]:.3f}")
        ticks = entropy_summary.get("ticks_stats")
        if ticks and ticks[0] is not None:
            lines.append(f"- T_ticks (mean/med/min/max): {ticks[0]:.1f} / {ticks[1]:.1f} / {ticks[2]:.0f} / {ticks[3]:.0f}")
        hlock = entropy_summary.get("hlock_mean_stats")
        if hlock and hlock[0] is not None:
            lines.append(f"- mean_H_lock_norm (mean/med): {hlock[0]:.3f} / {hlock[1]:.3f}")
        mix = entropy_summary.get("mix_stats")
        if mix and mix[0] is not None:
            lines.append(f"- mixture_entropy_blocks_norm (mean/med): {mix[0]:.3f} / {mix[1]:.3f}")
        smix = entropy_summary.get("struct_mix_stats")
        if smix and smix[0] is not None:
            lines.append(f"- structure_mix_norm (mean/med): {smix[0]:.3f} / {smix[1]:.3f}")
        fstr = entropy_summary.get("frac_struct_stats")
        if fstr and fstr[0] is not None:
            lines.append(f"- fraction_structured (mean/med): {fstr[0]:.3f} / {fstr[1]:.3f}")
    else:
        lines.append("- No se encontraron métricas de entropía/caos en sweep_results.")
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
