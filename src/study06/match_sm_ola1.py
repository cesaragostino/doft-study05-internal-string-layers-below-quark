"""Match per-run spectra against SM catalog (Ola1)."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

import numpy as np

from study06.sm_matching import compute_match_stats, extract_levels, load_universe


def parse_proxies_csv(path: Path) -> List[Dict]:
    rows = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                try:
                    parsed[k] = float(v)
                except Exception:
                    parsed[k] = v
            rows.append(parsed)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Match spectra against SM catalog (Ola1).")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1"))
    parser.add_argument("--digest", type=Path, default=Path("data/processed/digest/ola1"), help="Directory to store summary outputs.")
    parser.add_argument(
        "--hbar-sim",
        type=Path,
        default=None,
        help="Optional path to hbar_sim_calibration.json to compute mass_sim_gev when proxies lack it.",
    )
    parser.add_argument(
        "--use-mass-sim",
        action="store_true",
        help="Usar mass_sim_gev/omega_ref en lugar de band_energies_gev para el matching. Útil en fase 2/3.",
    )
    args = parser.parse_args()

    universe = load_universe(args.sm_universe)
    catalog = universe.get("particles", [])
    rows = parse_proxies_csv(args.proxies_csv)
    match_rows: List[Dict] = []
    best_rows: List[Dict] = []

    hbar_sim = None
    if args.hbar_sim and args.hbar_sim.exists():
        try:
            data_h = json.loads(args.hbar_sim.read_text())
            hbar_sim = float(data_h.get("hbar_sim"))
        except Exception:
            hbar_sim = None
    else:
        # fallback: default locations
        for cand in [Path("data/processed/ola1/hbar_sim_calibration.json"), Path("data/processed/ola1-chaos/hbar_sim_calibration.json")]:
            if cand.exists():
                try:
                    data_h = json.loads(cand.read_text())
                    hbar_sim = float(data_h.get("hbar_sim"))
                    break
                except Exception:
                    hbar_sim = None

    for row in rows:
        mass_sim = None
        if args.use_mass_sim:
            mass_sim = row.get("mass_sim_gev")
            if mass_sim is None and hbar_sim is not None:
                omega_ref = row.get("omega_ref") or row.get("omega_ref_interp")
                try:
                    omega_ref_f = float(omega_ref)
                    if np.isfinite(omega_ref_f):
                        mass_sim = hbar_sim * omega_ref_f
                except Exception:
                    pass
        levels_full = []
        if args.use_mass_sim and mass_sim is not None:
            try:
                m_val = float(mass_sim)
                if np.isfinite(m_val):
                    levels_full = [m_val]
            except Exception:
                levels_full = []
        if not levels_full:
            levels_full = extract_levels(row.get("band_energies_gev", "[]"))
        run_id = row.get("run_id", row.get("id", len(match_rows)))
        best = {"run_id": run_id, "best_target": None, "best_family": None, "best_d_total": float("inf")}
        second: Dict[str, object] = {"target": None, "family": None, "d_total": float("inf")}
        for particle in catalog:
            levels = [e for e in levels_full if _in_window(e, particle.get("energy_window", [0.0, 10.0]))]
            res = compute_match_stats(levels, particle.get("masses_gev", []), particle.get("tolerances", {}))
            match_rows.append(
                {
                    "run_id": run_id,
                    "target_name": particle["name"],
                    "family": particle.get("family"),
                    "type": particle.get("type"),
                    "d_total": res["d_total"],
                    "d_spacing": res["d_spacing"],
                    "d_mass": res["d_mass"],
                    "enough_levels_full": int(res["has_enough_levels_full"]),
                    "enough_levels_partial": int(res["has_enough_levels_partial"]),
                    "n_levels_sim": res["n_levels_sim"],
                }
            )
            if np.isfinite(res["d_total"]):
                if res["d_total"] < best["best_d_total"]:
                    # shift best to second
                    second = {
                        "target": best.get("best_target"),
                        "family": best.get("best_family"),
                        "d_total": best.get("best_d_total"),
                    }
                    best.update(
                        {
                            "best_target": particle["name"],
                            "best_family": particle.get("family"),
                            "best_d_total": res["d_total"],
                        }
                    )
                elif res["d_total"] < second.get("d_total", float("inf")):
                    second = {"target": particle["name"], "family": particle.get("family"), "d_total": res["d_total"]}
        # margin
        delta_margin = None
        if np.isfinite(best.get("best_d_total", np.inf)) and np.isfinite(second.get("d_total", np.inf)):
            delta_margin = second.get("d_total") - best.get("best_d_total")
        best["second_best_target"] = second.get("target")
        best["second_best_family"] = second.get("family")
        best["second_best_d_total"] = second.get("d_total")
        best["delta_margin"] = delta_margin
        best_rows.append(best)

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    zoo_path = out_dir / "zoo_matches.csv"
    best_path = out_dir / "best_match_per_run.csv"
    with zoo_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=match_rows[0].keys())
        writer.writeheader()
        writer.writerows(match_rows)

    with best_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=best_rows[0].keys())
        writer.writeheader()
        writer.writerows(best_rows)

    # Optional digest copy for quick lookup of best matches
    if args.digest:
        args.digest.mkdir(parents=True, exist_ok=True)
        digest_best = args.digest / best_path.name
        digest_best.write_text(best_path.read_text())


def _in_window(val: float, window):
    try:
        lo, hi = window
        v = float(val)
        return lo <= v <= hi
    except Exception:
        return False


if __name__ == "__main__":
    main()
