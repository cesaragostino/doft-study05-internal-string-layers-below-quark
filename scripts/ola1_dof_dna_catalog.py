"""Generate DOF DNA catalog from sweep proxies (no SM naming)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from study06.sm_matching import compute_match_stats, extract_levels, load_universe


def _to_float(value) -> Optional[float]:
    try:
        f = float(value)
        if np.isfinite(f):
            return f
    except Exception:
        pass
    return None


def _grade_from_d_total(d_total: Optional[float]) -> str:
    if d_total is None or not np.isfinite(d_total):
        return "C"
    if d_total < 0.5:
        return "A"
    if d_total < 1.5:
        return "B"
    return "C"


def _fill_harmonic_fields(rows: List[Dict], hbar_sim: Optional[float]) -> int:
    filled = 0
    k_tol = 0.07
    for row in rows:
        k_used = row.get("k_used")
        dominant_parity = row.get("dominant_parity")
        sector_conf = row.get("sector_confidence")
        if k_used not in (None, "", "nan") and dominant_parity and sector_conf not in (None, "", "nan"):
            continue

        omega_raw = _to_float(row.get("omega_ref") or row.get("omega_ref_interp"))
        if omega_raw is None:
            continue
        energies = extract_levels(row.get("band_energies_gev", "[]"))
        energies = [e for e in energies if np.isfinite(e)]
        if not energies or not hbar_sim:
            continue
        omega_band = statistics.median(energies) / float(hbar_sim)
        if omega_band <= 0:
            continue
        ratio = omega_raw / omega_band
        k_scores = {}
        score_sum = 0.0
        for k in range(1, 6):
            score = math.exp(-((ratio - k) ** 2) / (2 * (k_tol**2)))
            k_scores[k] = score
            score_sum += score
        k_used = max(k_scores, key=lambda k: k_scores[k])
        dominant_parity = "odd" if k_used % 2 == 1 else "even"
        sector_conf = (k_scores[k_used] / score_sum) if score_sum > 0 else 0.0
        omega_eff = omega_raw / float(k_used)
        mass_sim_used = hbar_sim * omega_eff if hbar_sim is not None else None

        row["k_used"] = k_used
        row["dominant_parity"] = dominant_parity
        row["sector_confidence"] = f"{sector_conf:.6g}"
        row["omega_eff"] = f"{omega_eff:.12g}"
        if mass_sim_used is not None:
            row["mass_sim_used_gev"] = f"{mass_sim_used:.12g}"
        filled += 1
    return filled


def _cluster_id(r1: Optional[float], r2: Optional[float]) -> str:
    if r1 is None or r2 is None:
        return ""
    return f"R1_{r1!r}_R2_{r2!r}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate DOF DNA catalog from proxies.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1/dof_dna_catalog.csv"))
    parser.add_argument("--hbar-sim", type=Path, default=None)
    parser.add_argument("--use-mass-sim", action="store_true", help="Ignored for DNA; kept for compatibility.")
    parser.add_argument("--update-proxies", action="store_true")
    parser.add_argument("--cluster-radii", action="store_true")
    args = parser.parse_args()

    with args.proxies_csv.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    hbar_sim = None
    if args.hbar_sim and args.hbar_sim.exists():
        try:
            data_h = json.loads(args.hbar_sim.read_text())
            hbar_sim = float(data_h.get("hbar_sim"))
        except Exception:
            hbar_sim = None

    filled = _fill_harmonic_fields(rows, hbar_sim)
    if filled:
        print(f"[dof_dna] harmonic fields filled in {filled} rows")

    universe = load_universe(args.sm_universe)
    catalog = universe.get("particles", [])

    dna_rows: List[Dict[str, object]] = []
    if args.use_mass_sim:
        print("[dof_dna] --use-mass-sim ignored: DNA catalog uses raw band_energies_gev only.")

    for row in rows:
        levels_full = extract_levels(row.get("band_energies_gev", "[]"))

        best_raw = float("inf")
        for particle in catalog:
            levels = [e for e in levels_full if _in_window(e, particle.get("energy_window", [0.0, 10.0]))]
            res = compute_match_stats(levels, particle.get("masses_gev", []), particle.get("tolerances", {}))
            if np.isfinite(res["d_total"]) and res["d_total"] < best_raw:
                best_raw = res["d_total"]
        d_total = best_raw if np.isfinite(best_raw) else None
        dna_grade = _grade_from_d_total(d_total)
        r1 = _to_float(row.get("R_S1_Q"))
        r2 = _to_float(row.get("R_S2_S1"))
        cluster_id = _cluster_id(r1, r2) if args.cluster_radii else ""
        dna_rows.append(
            {
                "run_id": row.get("run_id"),
                "R_S1_Q": row.get("R_S1_Q"),
                "R_S2_S1": row.get("R_S2_S1"),
                "dominant_parity": row.get("dominant_parity"),
                "lock_Q0_S1_0_1-1_ratio": row.get("lock_Q0_S1_0_1-1_ratio"),
                "band_count": row.get("band_count"),
                "rho_lock": row.get("rho_lock"),
                "lock_quality_Q": row.get("lock_quality_Q"),
                "participation_entropy": row.get("participation_entropy"),
                "d_total": d_total,
                "dna_grade": dna_grade,
                "dna_cluster_id": cluster_id,
            }
        )

    if args.cluster_radii:
        counts: Dict[str, int] = {}
        for r in dna_rows:
            cid = r.get("dna_cluster_id") or ""
            counts[cid] = counts.get(cid, 0) + 1
        for r in dna_rows:
            r["dna_cluster_size"] = counts.get(r.get("dna_cluster_id") or "", 0)

    dna_rows.sort(key=lambda r: (r.get("d_total") is None, r.get("d_total")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_id",
        "R_S1_Q",
        "R_S2_S1",
        "dominant_parity",
        "lock_Q0_S1_0_1-1_ratio",
        "band_count",
        "rho_lock",
        "lock_quality_Q",
        "participation_entropy",
        "d_total",
        "dna_grade",
        "dna_cluster_id",
    ]
    if args.cluster_radii:
        fieldnames.append("dna_cluster_size")
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dna_rows)
    print(f"[dof_dna] catalog escrito -> {args.output}")

    if args.update_proxies:
        fieldnames = sorted({k for r in rows for k in r.keys()})
        with args.proxies_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[dof_dna] proxies updated -> {args.proxies_csv}")


def _in_window(val: float, window):
    try:
        lo, hi = window
        v = float(val)
        return lo <= v <= hi
    except Exception:
        return False


if __name__ == "__main__":
    main()
