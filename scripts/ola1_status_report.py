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
    def _to_float(val):
        try:
            return float(val)
        except Exception:
            return 0.0
    q = max(_to_float(weights.get("Q", 0.0)), 0.0)
    s1 = max(_to_float(weights.get("S1", 0.0)), 0.0)
    s2 = max(_to_float(weights.get("S2", 0.0)), 0.0)
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


@lru_cache()
def load_sm_jpc(path: Path) -> Dict[str, str]:
    """Load SM J^PC (if present) from sm_universe JSON keyed by particle name."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    out = {}
    for item in data.get("particles", []):
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        jpc = item.get("jpc")
        if jpc is not None:
            out[name] = str(jpc)
    return out


def _mini_bar(val: float, max_val: float, width: int = 20) -> str:
    if max_val <= 0 or val is None or not math.isfinite(val):
        return ""
    filled = int(min(max(val / max_val, 0.0), 1.0) * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


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


def load_dof_catalog(path: Path) -> List[Dict]:
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
            try:
                row["run_sector_confidence"] = float(row.get("run_sector_confidence", "nan"))
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
    parser.add_argument("--dof-dna-catalog", type=Path, default=None, help="Override path a dof_dna_catalog.csv")
    parser.add_argument("--simple-blocks", type=Path, default=None, help="Override path a simple_blocks.json")
    parser.add_argument("--zoo-matches", type=Path, default=None, help="Override path a zoo_matches.csv")
    parser.add_argument("--sweep-results", type=Path, default=None, help="Override path a sweep_results.json")
    parser.add_argument("--d-threshold-radar", type=float, default=5.0, help="Umbral d_total para radar de zoo.")
    parser.add_argument(
        "--harmonic-guard-enabled",
        action="store_true",
        help="Aplicar harmonic-guard (solo en reportes) para mass_sim_gev.",
    )
    parser.add_argument(
        "--harmonic-ratio-max",
        type=float,
        default=1.9,
        help="Umbral max de mass_sim_gev/first_energy para activar guard.",
    )
    parser.add_argument(
        "--harmonic-err-trigger",
        type=float,
        default=0.20,
        help="Umbral de error relativo vs SM para activar guard (0.20=20%).",
    )
    parser.add_argument("--output", type=Path, default=None, help="Reporte markdown de salida.")
    args = parser.parse_args()

    proc = args.processed_dir
    case = args.case
    selection_path = args.selection_log or proc / "ola1_blocks_selection.csv"
    dna_path = args.dof_dna_catalog or proc / "dof_dna_catalog.csv"
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
    dna_rows = load_dof_catalog(dna_path)
    blocks = load_simple_blocks(blocks_path)
    zoo = load_zoo_matches(zoo_path)
    sm_masses = load_sm_masses(Path("data/raw/sm_universe.json"))
    sm_jpc = load_sm_jpc(Path("data/raw/sm_universe.json"))
    # Collect per-run chaos/disorder for cosmic averages
    cosmic_pe_vals: List[float] = []
    cosmic_hlock_vals: List[float] = []

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
        e_int = r.get("E_internal")
        if e_int is not None:
            try:
                e_val = float(e_int)
                if math.isfinite(e_val):
                    cosmic_pe_vals  # keep lint happy
            except Exception:
                pass
        ec = r.get("entropy_chaos") or {}
        pe_val = ec.get("PE_tick_norm")
        mh_val = ec.get("mean_H_lock_norm")
        if pe_val is not None and math.isfinite(pe_val):
            cosmic_pe_vals.append(float(pe_val))
        if mh_val is not None and math.isfinite(mh_val):
            cosmic_hlock_vals.append(float(mh_val))

    block_lines: List[str] = []
    chaos_rows: List[Tuple[int, str, Optional[float], Optional[float], Optional[float]]] = []
    mass_errors_by_particle: Dict[str, List[float]] = defaultdict(list)
    mass_sim_errors_by_particle: Dict[str, List[float]] = defaultdict(list)
    if blocks and runs_by_id:
        for b in blocks:
            rid_raw = b.get("origin_run_id")
            rid = _to_int(rid_raw)
            run = runs_by_id.get(rid)
            ec = run.get("entropy_chaos") if run else None
            block_lines.append(f"### {b.get('block_id', 'block')} (run_id={rid})")
            block_lines.append(f"- Partícula: {b.get('particle_name')}, tier: {b.get('structure_tier')}, s2_state: {b.get('s2_state')}")
            ms = b.get("match_score", {}) or {}
            d_total = ms.get("d_total")
            if d_total is not None:
                try:
                    block_lines.append(f"- match_score.d_total: {float(d_total):.3f}")
                except Exception:
                    block_lines.append(f"- match_score.d_total: {d_total}")
            block_lines.append(f"- Bandas: count={b.get('band_count')}, s2_band_fraction={b.get('s2_band_fraction')}")
            fm = None
            h_block = None
            sm_mass = None
            capture = None
            pname = str(b.get("particle_name", "")).strip()
            if pname and sm_masses:
                sm_mass = sm_masses.get(pname)
            if run:
                energies = run.get("band_energies_gev") or []
                capture = run.get("band_power_capture")
                block_lines.append(f"- band_energies_gev: {energies}")
                if energies:
                    try:
                        fm = float(min(energies))
                        block_lines.append(f"- F_m (base): {fm:.3f} GeV")
                    except Exception:
                        fm = energies[0]
                        block_lines.append(f"- F_m (base): {fm} GeV")
                lq = b.get("lock_quality") or {}
                if lq:
                    h_block = _lock_entropy_norm_from_weights(lq)
                m_eff = run.get("mass_effective") or run.get("effective_mass") or run.get("mass")
                if m_eff is not None:
                    try:
                        m_eff_val = float(m_eff)
                        block_lines.append(f"- M_eff (run): {m_eff_val:.3f}")
                    except Exception:
                        block_lines.append(f"- M_eff (run): {m_eff}")
                elif fm is not None:
                    block_lines.append(f"- M_eff (base≈F_m): {fm:.3f}")
                    if h_block is not None:
                        m_corr = fm * (1.0 - h_block)
                        if m_corr < 0:
                            m_corr = 0.0
                        block_lines.append(f"- M_corrected (F_m*(1-H_block)): {m_corr:.3f} (H_block={h_block:.3f})")
            if sm_mass is not None:
                block_lines.append(f"- sm_mass_gev: {sm_mass:.3f}")
                # OLD (deprecated): F_m-based mass error vs SM.
                # Disabled to avoid mixing the legacy estimator with the current hbar_sim method.
                # if fm is not None:
                #     dev = ((fm - sm_mass) / sm_mass) * 100.0
                #     block_lines.append(f"- Δ_mass vs SM: {dev:+.4f}%")
                #     mass_errors_by_particle[pname].append(dev)
                dev = None
                # NEW (current): mass_sim_used_gev from harmonic-aware selection (if present).
                msim_raw = b.get("mass_sim_raw_gev") or b.get("mass_sim_gev")
                msim_used = None
                omega_used = None
                if run:
                    msim_used = run.get("mass_sim_used_gev")
                    omega_used = run.get("omega_eff")
                if msim_used is None and b.get("mass_sim_used_gev") is not None:
                    msim_used = b.get("mass_sim_used_gev")
                if omega_used is None and b.get("omega_eff") is not None:
                    omega_used = b.get("omega_eff")
                if msim_used is not None:
                    try:
                        msim_used_val = float(msim_used)
                        dev_sim = ((msim_used_val - sm_mass) / sm_mass) * 100.0
                        if msim_raw is not None:
                            block_lines.append(f"- mass_sim_raw_gev: {float(msim_raw):.6g}")
                        if omega_used is not None:
                            block_lines.append(f"- omega_ref_used: {float(omega_used):.6g}")
                        block_lines.append(f"- mass_sim_used_gev: {msim_used_val:.6g}")
                        block_lines.append(f"- Δ_mass_sim vs SM: {dev_sim:+.4f}%")
                        mass_sim_errors_by_particle[pname].append(dev_sim)
                    except Exception:
                        pass
                elif msim_raw is not None:
                    # Fallback: report-only harmonic guard (legacy runs).
                    try:
                        msim_val = float(msim_raw)
                        omega_raw = None
                        if b.get("omega_ref") is not None:
                            try:
                                omega_raw = float(b.get("omega_ref"))
                            except Exception:
                                omega_raw = None
                        if omega_raw is None and b.get("omega_ref_interp") is not None:
                            try:
                                omega_raw = float(b.get("omega_ref_interp"))
                            except Exception:
                                omega_raw = None
                        first_energy = None
                        if run:
                            energies = run.get("band_energies_gev") or []
                            try:
                                energies_f = [float(x) for x in energies if math.isfinite(float(x))]
                                if energies_f:
                                    first_energy = min(energies_f)
                            except Exception:
                                first_energy = None
                        hbar_est = None
                        if omega_raw is not None and omega_raw > 0:
                            hbar_est = msim_val / omega_raw
                        harmonic_ratio = None
                        if first_energy is not None and first_energy > 0:
                            harmonic_ratio = msim_val / first_energy
                        omega_used = omega_raw
                        msim_used = msim_val
                        guard_applied = False
                        err_raw = None
                        err_fix = None
                        if sm_mass is not None and sm_mass != 0:
                            err_raw = abs(msim_val - sm_mass) / sm_mass
                            if first_energy is not None:
                                err_fix = abs(first_energy - sm_mass) / sm_mass
                        if (
                            args.harmonic_guard_enabled
                            and hbar_est is not None
                            and first_energy is not None
                            and err_raw is not None
                            and err_fix is not None
                            and err_raw > args.harmonic_err_trigger
                            and err_fix < err_raw
                        ):
                            if harmonic_ratio is not None and harmonic_ratio > args.harmonic_ratio_max:
                                omega_used = first_energy / hbar_est
                                msim_used = first_energy
                                guard_applied = True
                        dev_sim = ((msim_used - sm_mass) / sm_mass) * 100.0
                        block_lines.append(f"- mass_sim_raw_gev: {msim_val:.6g}")
                        if omega_raw is not None:
                            block_lines.append(f"- omega_ref_raw: {omega_raw:.6g}")
                        if first_energy is not None:
                            block_lines.append(f"- first_energy: {first_energy:.6g}")
                        if harmonic_ratio is not None:
                            block_lines.append(f"- harmonic_ratio: {harmonic_ratio:.3f}")
                        if err_raw is not None:
                            block_lines.append(f"- err_raw_vs_sm: {err_raw:.3f}")
                        if err_fix is not None:
                            block_lines.append(f"- err_fix_vs_sm: {err_fix:.3f}")
                        if guard_applied:
                            block_lines.append("- omega_ref_guard_applied: true (sm_err_better)")
                            if omega_used is not None:
                                block_lines.append(f"- omega_ref_used: {omega_used:.6g}")
                            block_lines.append(f"- mass_sim_used_gev: {msim_used:.6g}")
                        else:
                            block_lines.append("- omega_ref_guard_applied: false")
                        block_lines.append(f"- Δ_mass_sim vs SM: {dev_sim:+.4f}%")
                        mass_sim_errors_by_particle[pname].append(dev_sim)
                    except Exception:
                        pass
            else:
                dev = None
            if h_block is not None:
                block_lines.append(f"- H_block (lock_quality): {h_block:.3f}")
            if capture is not None:
                block_lines.append(f"- band_power_capture: {capture}")
            if ec:
                block_lines.append(
                    f"- chaos_mode={ec.get('chaos_mode')}, PE_tick_norm={ec.get('PE_tick_norm')}, T_ticks={ec.get('T_ticks')}"
                )
                block_lines.append(
                    f"- mean_H_lock_norm={ec.get('mean_H_lock_norm')}, mixture_entropy_blocks_norm={ec.get('mixture_entropy_blocks_norm')}, structure_mix_norm={ec.get('structure_mix_norm')}"
                )
                block_lines.append(f"- fraction_structured={ec.get('fraction_structured')}")
                series = ec.get("lock_S1_series") or []
                if isinstance(series, list) and series:
                    s_mean = statistics.mean(series)
                    s_min = min(series)
                    s_max = max(series)
                    block_lines.append(f"- lock_S1_series (mean/min/max): {s_mean:.4f} / {s_min:.4f} / {s_max:.4f}")
            else:
                block_lines.append("- entropy_chaos: no encontrado para este run.")
            pe_val = ec.get("PE_tick_norm") if ec else None
            mh_val = ec.get("mean_H_lock_norm") if ec else None
            chaos_rows.append((rid if rid is not None else -1, pname or "", pe_val if pe_val is not None else None, mh_val if mh_val is not None else None, dev))
            block_lines.append("")
    else:
        block_lines.append("Sin bloques aceptados o no se encontraron runs para mapear entropy_chaos.")
        block_lines.append("")

    if dna_rows:
        lines.append("## DNA Catalog (DOF Individuals)")

        def _fmt_dna(v):
            if isinstance(v, str):
                return v
            try:
                f = float(v)
                return f"{f:.17g}"
            except Exception:
                return str(v) if v is not None else ""

        def _fmt_run_id(val):
            try:
                return str(int(float(val)))
            except Exception:
                return str(val) if val is not None else ""

        def _emit_grade(title: str, rows: List[Dict]):
            lines.append(title)
            lines.append("| run_id | d_total | dna_grade | R_S1_Q | R_S2_S1 | dominant_parity | lock_Q0_S1_0_1-1_ratio | band_count | rho_lock | lock_quality_Q | participation_entropy |")
            lines.append("|--------|---------|-----------|--------|---------|-----------------|------------------------|-----------|---------|---------------|-----------------------|")
            for r in rows:
                lines.append(
                    f"| {_fmt_run_id(r.get('run_id'))} | {_fmt_dna(r.get('d_total'))} | {r.get('dna_grade')} | {_fmt_dna(r.get('R_S1_Q'))} | "
                    f"{_fmt_dna(r.get('R_S2_S1'))} | {r.get('dominant_parity')} | {_fmt_dna(r.get('lock_Q0_S1_0_1-1_ratio'))} | "
                    f"{_fmt_dna(r.get('band_count'))} | {_fmt_dna(r.get('rho_lock'))} | {_fmt_dna(r.get('lock_quality_Q'))} | "
                    f"{_fmt_dna(r.get('participation_entropy'))} |"
                )

        def _dof_val(r):
            try:
                return float(r.get("d_total"))
            except Exception:
                return None

        grade_a = [r for r in dna_rows if (v := _dof_val(r)) is not None and v < 0.5]
        grade_b = [r for r in dna_rows if (v := _dof_val(r)) is not None and 0.5 <= v < 1.5]
        grade_c = [r for r in dna_rows if _dof_val(r) is None or _dof_val(r) >= 1.5]

        _emit_grade("### DOF Grade A (Excellent): d_total < 0.5", grade_a)
        lines.append("")
        _emit_grade("### DOF Grade B (Acceptable): 0.5 <= d_total < 1.5", grade_b)
        lines.append("")
        _emit_grade("### DOF Grade C (Noise/Ghosts): d_total >= 1.5", grade_c)
        lines.append("")
        lines.append("### DNA Pareto (R1/R2 agrupados a 2 decimales)")
        lines.append("| R_S1_Q_2dp | R_S2_S1_2dp | n | grade_A | grade_B | grade_C |")
        lines.append("|-----------|------------|---|---------|---------|---------|")

        def _round_2(val):
            try:
                return f"{float(val):.2f}"
            except Exception:
                return ""

        def _grade_from_d_total(val):
            try:
                f = float(val)
            except Exception:
                return "C"
            if f < 0.5:
                return "A"
            if f < 1.5:
                return "B"
            return "C"

        group_counts: Dict[tuple, Dict[str, int]] = {}
        for r in dna_rows:
            r1 = _round_2(r.get("R_S1_Q"))
            r2 = _round_2(r.get("R_S2_S1"))
            if not r1 or not r2:
                continue
            key = (r1, r2)
            bucket = group_counts.setdefault(key, {"n": 0, "A": 0, "B": 0, "C": 0})
            bucket["n"] += 1
            bucket[_grade_from_d_total(r.get("d_total"))] += 1

        for (r1, r2), counts in sorted(group_counts.items(), key=lambda kv: (-kv[1]["n"], kv[0][0], kv[0][1])):
            lines.append(
                f"| {r1} | {r2} | {counts['n']} | {counts['A']} | {counts['B']} | {counts['C']} |"
            )
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

    # Energía interna (E_internal) en runs y bloques
    def _energy_stats(vals: List[float]):
        if not vals:
            return None
        vals_sorted = sorted(vals)
        mid = len(vals_sorted) // 2
        med = (
            (vals_sorted[mid - 1] + vals_sorted[mid]) / 2
            if len(vals_sorted) % 2 == 0 and len(vals_sorted) > 1
            else vals_sorted[mid]
        )
        return statistics.mean(vals_sorted), med, vals_sorted[0], vals_sorted[-1]

    run_energy_vals: List[float] = []
    for r in run_records:
        try:
            val = float(r.get("E_internal"))
            if math.isfinite(val):
                run_energy_vals.append(val)
        except Exception:
            continue
    block_energy_vals: List[float] = []
    block_mass_vals: List[float] = []
    block_mass_sim_vals: List[float] = []
    mass_sim_rows: List[Tuple[int, str, str, float, float, float, float, bool]] = []
    harmonic_records: List[Dict[str, Any]] = []
    for b in blocks:
        try:
            val = float(b.get("internal_energy"))
            if math.isfinite(val):
                block_energy_vals.append(val)
        except Exception:
            pass
        try:
            mval = float(b.get("mass_gev"))
            if math.isfinite(mval):
                block_mass_vals.append(mval)
        except Exception:
            pass
        try:
            msim = float(b.get("mass_sim_gev"))
            if math.isfinite(msim):
                block_mass_sim_vals.append(msim)
        except Exception:
            pass
        # lock/mass proxies
        if b.get("M2") is not None:
            try:
                m2_val = float(b.get("M2"))
                if math.isfinite(m2_val):
                    block_lines.append(f"- M2 (omega_ref*V_lock*D_stat): {m2_val:.6g}")
            except Exception:
                pass
        if b.get("M3") is not None:
            try:
                m3_val = float(b.get("M3"))
                if math.isfinite(m3_val):
                    block_lines.append(f"- M3 (omega_ref*V_lock*rho_lock): {m3_val:.6g}")
            except Exception:
                pass
        # mass_sim summary rows
        omega_row = _to_int(b.get("origin_run_id"))
        pname_row = b.get("particle_name")
        fam_row = b.get("family")
        if b.get("mass_sim_gev") is not None and pname_row:
            try:
                msim_val = float(b.get("mass_sim_gev"))
                if math.isfinite(msim_val):
                    sm_ref = sm_masses.get(str(pname_row))
                    run = runs_by_id.get(omega_row) if omega_row is not None else None
                    msim_raw = msim_val
                    omega_raw = b.get("omega_ref") or b.get("omega_ref_interp")
                    omega_raw_val = None
                    if omega_raw is not None:
                        try:
                            omega_raw_val = float(omega_raw)
                        except Exception:
                            omega_raw_val = None
                    msim_used = None
                    omega_used = None
                    guard_applied = False
                    if run:
                        msim_used = run.get("mass_sim_used_gev")
                        omega_used = run.get("omega_eff")
                    if msim_used is not None:
                        try:
                            msim_used = float(msim_used)
                        except Exception:
                            msim_used = None
                    if omega_used is not None:
                        try:
                            omega_used = float(omega_used)
                        except Exception:
                            omega_used = None
                    if msim_used is None:
                        # Fallback to report-only guard for legacy runs.
                        first_energy = None
                        if run:
                            energies = run.get("band_energies_gev") or []
                            try:
                                energies_f = [float(x) for x in energies if math.isfinite(float(x))]
                                if energies_f:
                                    first_energy = min(energies_f)
                            except Exception:
                                first_energy = None
                        hbar_est = None
                        if omega_raw_val is not None and omega_raw_val > 0:
                            hbar_est = msim_val / omega_raw_val
                        harmonic_ratio = None
                        if first_energy is not None and first_energy > 0:
                            harmonic_ratio = msim_val / first_energy
                        omega_used = omega_raw_val
                        msim_used = msim_val
                        err_raw = None
                        err_fix = None
                        if sm_ref is not None and sm_ref != 0:
                            err_raw = abs(msim_val - sm_ref) / sm_ref
                            if first_energy is not None:
                                err_fix = abs(first_energy - sm_ref) / sm_ref
                        if (
                            args.harmonic_guard_enabled
                            and hbar_est is not None
                            and first_energy is not None
                            and err_raw is not None
                            and err_fix is not None
                            and err_raw > args.harmonic_err_trigger
                            and err_fix < err_raw
                        ):
                            if harmonic_ratio is not None and harmonic_ratio > args.harmonic_ratio_max:
                                omega_used = first_energy / hbar_est
                                msim_used = first_energy
                                guard_applied = True
                    rel_err = None
                    if sm_ref and msim_used is not None:
                        rel_err = (msim_used - sm_ref) / sm_ref
                    mass_sim_rows.append(
                        (
                            omega_row if omega_row is not None else -1,
                            pname_row,
                            fam_row,
                            omega_raw_val,
                            omega_used,
                            msim_used,
                            rel_err if rel_err is not None else None,
                            guard_applied,
                        )
                    )
            except Exception:
                pass

        # Harmonic structure proxy (v1, evidence-based)
        omega_raw_val = None
        omega_raw = b.get("omega_ref") or b.get("omega_ref_interp")
        if omega_raw is not None:
            try:
                omega_raw_val = float(omega_raw)
            except Exception:
                omega_raw_val = None
        first_energy = None
        band_energies = None
        run = runs_by_id.get(omega_row) if omega_row is not None else None
        if run:
            band_energies = run.get("band_energies_gev") or []
        omega_band = None
        hbar_est = None
        if omega_raw_val is not None and b.get("mass_sim_gev") is not None:
            try:
                hbar_est = float(b.get("mass_sim_gev")) / omega_raw_val if omega_raw_val else None
            except Exception:
                hbar_est = None
        if band_energies and hbar_est:
            try:
                energies_f = [float(x) for x in band_energies if math.isfinite(float(x))]
                if energies_f:
                    median_energy = statistics.median(energies_f)
                    if hbar_est and hbar_est > 0:
                        omega_band = median_energy / hbar_est
                        first_energy = min(energies_f)
            except Exception:
                omega_band = None
        if omega_band is not None and omega_raw_val is not None and omega_band > 0:
            ratio = omega_raw_val / omega_band
            k_scores = {}
            score_sum = 0.0
            for k in range(1, 6):
                score = math.exp(-((ratio - k) ** 2) / (2 * (0.07 ** 2)))
                k_scores[k] = score
                score_sum += score
            dominant_k = max(k_scores, key=lambda k: k_scores[k])
            dominant_parity = "odd" if dominant_k % 2 == 1 else "even"
            odd_score = sum(v for k, v in k_scores.items() if k % 2 == 1)
            even_score = sum(v for k, v in k_scores.items() if k % 2 == 0)
            odd_frac = odd_score / score_sum if score_sum > 0 else 0.0
            even_frac = even_score / score_sum if score_sum > 0 else 0.0
            sector_conf = (k_scores[dominant_k] / score_sum) if score_sum > 0 else 0.0
            harmonic_records.append(
                {
                    "particle": str(pname_row),
                    "family": str(fam_row),
                    "jpc": sm_jpc.get(str(pname_row)),
                    "dominant_k": dominant_k,
                    "dominant_parity": dominant_parity,
                    "sector_confidence_v1": sector_conf,
                    "odd_evidence_frac": odd_frac,
                    "even_evidence_frac": even_frac,
                    "ratio": ratio,
                    "scores": k_scores,
                }
            )

    lines.append("## Energía interna (E_internal)")
    lines.append(f"- Runs con E_internal: {len(run_energy_vals)} / {len(run_records)}")
    stats_runs = _energy_stats(run_energy_vals)
    if stats_runs:
        lines.append(
            f"- E_internal runs (mean/med/min/max): {stats_runs[0]:.6g} / {stats_runs[1]:.6g} / {stats_runs[2]:.6g} / {stats_runs[3]:.6g}"
        )
    else:
        lines.append("- E_internal runs: n/d")
    lines.append(f"- Bloques con internal_energy: {len(block_energy_vals)} / {len(blocks)}")
    stats_blocks = _energy_stats(block_energy_vals)
    if stats_blocks:
        lines.append(
            f"- internal_energy bloques (mean/med/min/max): {stats_blocks[0]:.6g} / {stats_blocks[1]:.6g} / {stats_blocks[2]:.6g} / {stats_blocks[3]:.6g}"
        )
    else:
        lines.append("- internal_energy bloques: n/d")
    if block_mass_vals:
        stats_mass = _energy_stats(block_mass_vals)
        if stats_mass:
            lines.append(
                f"- mass_gev bloques (mean/med/min/max): {stats_mass[0]:.6g} / {stats_mass[1]:.6g} / {stats_mass[2]:.6g} / {stats_mass[3]:.6g}"
            )
    if block_mass_sim_vals:
        stats_mass_sim = _energy_stats(block_mass_sim_vals)
        if stats_mass_sim:
            lines.append(
                f"- mass_sim_gev bloques (mean/med/min/max): {stats_mass_sim[0]:.6g} / {stats_mass_sim[1]:.6g} / {stats_mass_sim[2]:.6g} / {stats_mass_sim[3]:.6g}"
            )
    lines.append("")

    # Proxies de masa/lock (M_spec/M1/M2/M3)
    lines.append("## Proxies de masa/lock (unidades internas)")
    proxy_rows = []
    for b in blocks:
        rid = _to_int(b.get("origin_run_id"))
        pname = b.get("particle_name")
        fam = b.get("family")
        omega_ref = b.get("omega_ref")
        m_spec = b.get("M_spec")
        m1 = b.get("M1")
        m2 = b.get("M2")
        m3 = b.get("M3")
        proxy_rows.append((rid if rid is not None else -1, pname, fam, omega_ref, m_spec, m1, m2, m3))
    if proxy_rows:
        proxy_rows_sorted = sorted(proxy_rows, key=lambda x: (str(x[1]), x[0]))
        lines.append("| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |")
        lines.append("|-----|----------|--------|-----------|--------|----|----|----|")
        def _fmt(val):
            try:
                xv = float(val)
                if math.isfinite(xv):
                    return f"{xv:.3e}"
            except Exception:
                return "n/d"
            return "n/d"
        for r in proxy_rows_sorted[:100]:
            rid, pname, fam, omega_ref, m_spec, m1, m2, m3 = r
            lines.append(
                f"| {rid} | {pname} | {fam} | {_fmt(omega_ref)} | {_fmt(m_spec)} | {_fmt(m1)} | {_fmt(m2)} | {_fmt(m3)} |"
            )
    else:
        lines.append("- No hay proxies de masa disponibles.")
    lines.append("")

    # Tabla de energía calibrada por bloque (si hay mass_gev o internal_energy)
    def _load_calibration(proc_dir: Path) -> float | None:
        candidates = [
            proc_dir / "energy_calibration.json",
            proc_dir.parent / "ola1-chaos" / "energy_calibration.json",
        ]
        for c in candidates:
            if c.exists():
                try:
                    data = json.loads(c.read_text())
                    K = float(data.get("scale_K"))
                    if math.isfinite(K):
                        return K
                except Exception:
                    continue
        return None

    K_cal = _load_calibration(proc)
    energy_rows = []
    for b in blocks:
        rid = _to_int(b.get("origin_run_id"))
        pname = b.get("particle_name")
        fam = b.get("family")
        e_int = b.get("internal_energy")
        mass_sm = sm_masses.get(str(pname)) if sm_masses else None
        try:
            e_val = float(e_int)
        except Exception:
            e_val = None
        mass_doft = None
        if b.get("mass_gev") is not None:
            try:
                mass_doft = float(b.get("mass_gev"))
            except Exception:
                mass_doft = None
        if mass_doft is None and e_val is not None and K_cal is not None:
            mass_doft = K_cal * e_val
        if e_val is None or mass_doft is None or mass_sm is None or mass_sm == 0:
            continue
        rel_err = (mass_doft - mass_sm) / mass_sm
        energy_rows.append(
            (
                rid if rid is not None else -1,
                str(pname),
                str(fam),
                e_val,
                mass_doft,
                mass_sm,
                rel_err,
            )
        )

    lines.append("## Energía calibrada por bloque")
    if energy_rows:
        energy_rows_sorted = sorted(energy_rows, key=lambda x: (x[1], x[0]))
        lines.append("| run | best_target | family | E_internal | m_DOFT (GeV) | m_SM (GeV) | rel_error |")
        lines.append("|-----|-------------|--------|------------|--------------|-----------:|----------:|")
        for row in energy_rows_sorted[:100]:
            rid, pname, fam, e_val, m_doft, m_sm, rel_err = row
            lines.append(
                f"| {rid} | {pname} | {fam} | {e_val:.3e} | {m_doft:.4f} | {m_sm:.4f} | {rel_err:+.3f} |"
            )
    else:
        lines.append("- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).")
    lines.append("")

    # OLD (deprecated): F_m-based mass error vs SM.
    # Disabled to keep reports focused on the calibrated hbar_sim method.
    # lines.append("## Error de masa vs SM")
    # if mass_errors_by_particle:
    #     lines.append("| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |")
    #     lines.append("|-----------|---------|--------|--------|---|")
    #     for pname, vals in sorted(mass_errors_by_particle.items()):
    #         if vals:
    #             mean = statistics.mean(vals)
    #             vmin = min(vals)
    #             vmax = max(vals)
    #             lines.append(f"| {pname} | {mean:+.4f}% | {vmin:+.4f}% | {vmax:+.4f}% | {len(vals)} |")
    # else:
    #     lines.append("Sin desviaciones de masa calculadas (no hay sm_mass o F_m).")
    # lines.append("")

    # NEW (current): mass_sim_gev vs SM using hbar_sim calibration.
    lines.append("## Error de mass_sim_used vs SM")
    if mass_sim_errors_by_particle:
        lines.append("| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |")
        lines.append("|-----------|---------|--------|--------|---|")
        for pname, vals in sorted(mass_sim_errors_by_particle.items()):
            if vals:
                mean = statistics.mean(vals)
                vmin = min(vals)
                vmax = max(vals)
                lines.append(f"| {pname} | {mean:+.4f}% | {vmin:+.4f}% | {vmax:+.4f}% | {len(vals)} |")
    else:
        lines.append("Sin desviaciones mass_sim calculadas (no hay mass_sim_used_gev).")
    lines.append("")

    lines.append("## Masa por frecuencia (mass_sim_used_gev)")
    if mass_sim_rows:
        rows_sorted = sorted(mass_sim_rows, key=lambda x: (str(x[1]), x[0]))
        lines.append("| run | particle | family | omega_ref_raw | omega_ref_used | mass_sim_used_gev | rel_err_vs_SM | guard |")
        lines.append("|-----|----------|--------|--------------|----------------|------------------|---------------|-------|")
        def _fmt(val):
            try:
                xv = float(val)
                if math.isfinite(xv):
                    return f"{xv:.6g}"
            except Exception:
                return "n/d"
            return "n/d"
        for r in rows_sorted[:100]:
            rid, pname, fam, omega_raw, omega_used, msim_used, rel_err, guard_applied = r
            rel = f"{rel_err:+.4f}" if rel_err is not None else "n/d"
            guard_str = "yes" if guard_applied else "no"
            pname_mark = f"{pname}*" if guard_applied else pname
            lines.append(
                f"| {rid} | {pname_mark} | {fam} | {_fmt(omega_raw)} | {_fmt(omega_used)} | {_fmt(msim_used)} | {rel} | {guard_str} |"
            )
        lines.append("")
        lines.append("* = harmonic-guard aplicado")
    else:
        lines.append("- No hay mass_sim_used_gev disponibles (ejecute la calibración hbar_sim).")
    lines.append("")

    # Harmonic structure vs SM quantum numbers (v1 proxy)
    lines.append("## Harmonic Structure vs SM Quantum Numbers (v1 proxy)")
    lines.append(
        "Proceed with v1 using only the stored main FFT peak (plus km1/kp1 if frequency is available) "
        "and band_energies anchor. Evidence is score-based (not power-based)."
    )
    lines.append(
        "dominant_k, dominant_parity, sector_confidence_v1 computed from k-matching scores "
        "(k_tol=0.07, k in 1..5). odd/even evidence fractions are sums of scores."
    )
    lines.append("")
    if harmonic_records:
        # By family
        lines.append("### By family")
        lines.append("| family | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |")
        lines.append("|--------|-------|---------------|----------------|-------------------|")
        fam_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in harmonic_records:
            fam_groups[str(r.get("family"))].append(r)
        for fam, rows in sorted(fam_groups.items()):
            count = len(rows)
            odd_mean = statistics.mean(r["odd_evidence_frac"] for r in rows)
            even_mean = statistics.mean(r["even_evidence_frac"] for r in rows)
            odd_dom = sum(1 for r in rows if r["dominant_parity"] == "odd") / count if count else 0.0
            lines.append(f"| {fam} | {count} | {odd_mean:.3f} | {even_mean:.3f} | {odd_dom:.3f} |")
        lines.append("")

        # By J^PC
        lines.append("### By J^PC")
        lines.append("| jpc | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |")
        lines.append("|-----|-------|---------------|----------------|-------------------|")
        jpc_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in harmonic_records:
            jpc_groups[str(r.get("jpc") or "unknown")].append(r)
        for jpc, rows in sorted(jpc_groups.items()):
            count = len(rows)
            odd_mean = statistics.mean(r["odd_evidence_frac"] for r in rows)
            even_mean = statistics.mean(r["even_evidence_frac"] for r in rows)
            odd_dom = sum(1 for r in rows if r["dominant_parity"] == "odd") / count if count else 0.0
            lines.append(f"| {jpc} | {count} | {odd_mean:.3f} | {even_mean:.3f} | {odd_dom:.3f} |")
        lines.append("")

        # Top particles by odd/even evidence
        particle_scores: Dict[str, Dict[str, float]] = defaultdict(lambda: {"odd": 0.0, "even": 0.0})
        for r in harmonic_records:
            pname = r.get("particle") or ""
            particle_scores[pname]["odd"] += r["odd_evidence_frac"]
            particle_scores[pname]["even"] += r["even_evidence_frac"]
        particles = []
        for pname, vals in particle_scores.items():
            total = vals["odd"] + vals["even"]
            if total <= 0:
                continue
            particles.append((pname, vals["odd"] / total, vals["even"] / total))
        top_odd = sorted(particles, key=lambda x: x[1], reverse=True)[:10]
        top_even = sorted(particles, key=lambda x: x[2], reverse=True)[:10]
        lines.append("### Top 10 particles by odd evidence")
        lines.append("| particle | odd_evidence_frac | even_evidence_frac |")
        lines.append("|----------|-------------------|--------------------|")
        for pname, odd_f, even_f in top_odd:
            lines.append(f"| {pname} | {odd_f:.3f} | {even_f:.3f} |")
        lines.append("")
        lines.append("### Top 10 particles by even evidence")
        lines.append("| particle | odd_evidence_frac | even_evidence_frac |")
        lines.append("|----------|-------------------|--------------------|")
        for pname, odd_f, even_f in top_even:
            lines.append(f"| {pname} | {odd_f:.3f} | {even_f:.3f} |")
        lines.append("")

        # Outliers (k=3 or k=4, high confidence)
        outliers = [r for r in harmonic_records if r["dominant_k"] in (3, 4) and r["sector_confidence_v1"] >= 0.6]
        if outliers:
            lines.append("### Outliers (k=3 or k=4 with high confidence)")
            lines.append("| particle | family | jpc | k | conf | ratio |")
            lines.append("|----------|--------|-----|---|------|-------|")
            for r in outliers[:50]:
                lines.append(
                    f"| {r['particle']} | {r['family']} | {r.get('jpc') or 'unknown'} | {r['dominant_k']} | {r['sector_confidence_v1']:.3f} | {r['ratio']:.3f} |"
                )
            lines.append("")
    else:
        lines.append("- No harmonic evidence computed (missing omega_ref or band_energies_gev).")
        lines.append("")

    # OLD (disabled): mass_sim-based error tables.
    # This method is kept for reference but is not written to reports to avoid
    # polluting XLS exports with a deprecated mass calculation.
    #
    # lines.append("## Error de mass_sim vs SM")
    # if mass_sim_errors_by_particle:
    #     lines.append("| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |")
    #     lines.append("|-----------|---------|--------|--------|---|")
    #     for pname, vals in sorted(mass_sim_errors_by_particle.items()):
    #         if vals:
    #             mean = statistics.mean(vals)
    #             vmin = min(vals)
    #             vmax = max(vals)
    #             lines.append(f"| {pname} | {mean:+.4f}% | {vmin:+.4f}% | {vmax:+.4f}% | {len(vals)} |")
    # else:
    #     lines.append("Sin desviaciones mass_sim calculadas (no hay mass_sim_gev).")
    # lines.append("")
    #
    # lines.append("## Masa por frecuencia (mass_sim_gev)")
    # if mass_sim_rows:
    #     rows_sorted = sorted(mass_sim_rows, key=lambda x: (str(x[1]), x[0]))
    #     lines.append("| run | particle | family | omega_ref | mass_sim_gev | rel_err_vs_SM |")
    #     lines.append("|-----|----------|--------|-----------|--------------|---------------|")
    #     def _fmt(val):
    #         try:
    #             xv = float(val)
    #             if math.isfinite(xv):
    #                 return f"{xv:.6g}"
    #         except Exception:
    #             return "n/d"
    #         return "n/d"
    #     for r in rows_sorted[:100]:
    #         rid, pname, fam, omega_val, msim_val, rel_err = r
    #         rel = f"{rel_err:+.4f}" if rel_err is not None else "n/d"
    #         lines.append(f"| {rid} | {pname} | {fam} | {_fmt(omega_val)} | {_fmt(msim_val)} | {rel} |")
    # else:
    #     lines.append("- No hay mass_sim_gev disponibles (ejecute la calibración hbar_sim).")
    # lines.append("")

    if cosmic_pe_vals or cosmic_hlock_vals:
        lines.append("## Promedio cósmico (Ola1)")
        if cosmic_pe_vals:
            lines.append(f"- cosmic_chaos_temp (PE avg): {statistics.mean(cosmic_pe_vals):.4f}")
        if cosmic_hlock_vals:
            lines.append(f"- cosmic_disorder (H_mean avg): {statistics.mean(cosmic_hlock_vals):.4f}")
        lines.append("")

    if chaos_rows:
        lines.append("## Caos/desorden por run")
        chaos_rows_sorted = sorted(chaos_rows, key=lambda x: x[0] if x[0] is not None else -1)
        lines.append("| Run ID | PE_tick_norm | mean_H_lock_norm |")
        lines.append("|--------|--------------|------------------|")
        for rid, _, pe_val, mh_val, _ in chaos_rows_sorted:
            pe_str = f"{pe_val:.4f}" if pe_val is not None else "n/d"
            mh_str = f"{mh_val:.4f}" if mh_val is not None else "n/d"
            lines.append(f"| {rid} | {pe_str} | {mh_str} |")
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

    lines.append("## Harmonic Policy Rejects (tagger)")
    policy_rejects = []
    for row in zoo:
        try:
            rejected = str(row.get("policy_rejected", "0")).lower() in {"1", "true", "yes"}
        except Exception:
            rejected = False
        if rejected:
            policy_rejects.append(row)
    if policy_rejects:
        for row in policy_rejects[:20]:
            target = row.get("target_name", "unknown")
            jpc = row.get("jpc", "n/a")
            policy_parity = row.get("policy_preferred_parity", "any")
            policy_k = row.get("policy_allowed_k", "[]")
            run_parity = row.get("run_dominant_parity", "n/a")
            run_k = row.get("run_k_used", "n/a")
            run_conf = row.get("run_sector_confidence", "n/a")
            reason = row.get("policy_reason", "policy_mismatch")
            lines.append(
                f"- run_id={row.get('run_id')} candidate jpc={jpc} -> policy {policy_parity}/{policy_k} | "
                f"run parity={run_parity}, k={run_k}, conf={run_conf} -> REJECT ({reason})"
            )
    else:
        lines.append("Sin rechazos por política armónica.")
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

    # Append block-level details at the end
    lines.append("## Bloques aceptados con métricas de entropía/caos")
    lines.extend(block_lines)

    output_path = args.output or proc / f"{case}_ola1_report.md"
    output_path.write_text("\n".join(lines))
    print(f"[report] escrito {output_path}")


if __name__ == "__main__":
    main()
