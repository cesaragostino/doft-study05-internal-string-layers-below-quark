"""Match per-run spectra against SM catalog (Ola1)."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

import numpy as np


def load_catalog(path: Path) -> List[Dict]:
    return json.loads(path.read_text())


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


def extract_levels(row: Dict) -> List[float]:
    val = row.get("band_energies_gev", "[]")
    try:
        levels = json.loads(val) if isinstance(val, str) else list(val)
    except Exception:
        levels = []
    return sorted([float(x) for x in levels if isinstance(x, (int, float)) or str(x).replace(".", "", 1).isdigit()])


def compute_match(levels: List[float], particle: Dict) -> Dict:
    win = particle.get("energy_window", [0.0, 10.0])
    levels_win = [e for e in levels if win[0] <= e <= win[1]]
    masses = particle.get("masses_gev", [])
    if not levels_win or not masses:
        return {"enough_levels": False, "d_spacing": float("nan"), "d_mass": float("nan"), "d_total": float("nan")}
    target_spacings = np.diff(masses)
    sim_spacings_full = np.diff(levels_win)
    enough = len(levels_win) >= len(masses)
    sim_spacings = sim_spacings_full[: target_spacings.size] if target_spacings.size else np.array([])
    spacing_rel = particle.get("tolerances", {}).get("spacing_rel", 0.2)
    mass_abs = particle.get("tolerances", {}).get("mass_abs", 0.1)

    if sim_spacings.size and target_spacings.size:
        d_spacing = float(np.mean(np.abs(sim_spacings - target_spacings) / (spacing_rel * target_spacings + 1e-9)))
    else:
        d_spacing = float("nan")

    sim_masses = np.array(levels_win[: len(masses)])
    tgt_masses = np.array(masses)
    if sim_masses.size and tgt_masses.size == sim_masses.size:
        d_mass = float(np.mean(np.abs(sim_masses - tgt_masses) / (mass_abs + 1e-9)))
    else:
        d_mass = float("nan")

    d_total = np.nansum([d_spacing, d_mass])
    return {
        "enough_levels": enough,
        "d_spacing": d_spacing,
        "d_mass": d_mass,
        "d_total": d_total,
    }


def main():
    parser = argparse.ArgumentParser(description="Match spectra against SM catalog (Ola1).")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--sm-catalog", type=Path, default=Path("data/raw/sm_catalog/particles.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1_matches"))
    parser.add_argument("--digest", type=Path, default=Path("digest/ola1"), help="Directory to store summary outputs.")
    args = parser.parse_args()

    catalog = load_catalog(args.sm_catalog)
    rows = parse_proxies_csv(args.proxies_csv)
    match_rows: List[Dict] = []
    best_rows: List[Dict] = []

    for row in rows:
        levels = extract_levels(row)
        run_id = row.get("run_id", row.get("id", len(match_rows)))
        best = {"run_id": run_id, "best_target": None, "best_family": None, "best_d_total": float("inf")}
        for particle in catalog:
            res = compute_match(levels, particle)
            match_rows.append(
                {
                    "run_id": run_id,
                    "target_name": particle["name"],
                    "family": particle.get("family"),
                    "type": particle.get("type"),
                    "d_total": res["d_total"],
                    "d_spacing": res["d_spacing"],
                    "d_mass": res["d_mass"],
                    "enough_levels": int(res["enough_levels"]),
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


if __name__ == "__main__":
    main()
