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
    args = parser.parse_args()

    universe = load_universe(args.sm_universe)
    catalog = universe.get("particles", [])
    rows = parse_proxies_csv(args.proxies_csv)
    match_rows: List[Dict] = []
    best_rows: List[Dict] = []

    for row in rows:
        levels_full = extract_levels(row.get("band_energies_gev", "[]"))
        run_id = row.get("run_id", row.get("id", len(match_rows)))
        best = {"run_id": run_id, "best_target": None, "best_family": None, "best_d_total": float("inf")}
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
            if np.isfinite(res["d_total"]) and res["d_total"] < best["best_d_total"]:
                best.update(
                    {
                        "best_target": particle["name"],
                        "best_family": particle.get("family"),
                        "best_d_total": res["d_total"],
                    }
                )
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
