"""Analyze family distribution inside/outside the S2-friendly zone."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Dict, List

import numpy as np


def parse_float(v: str) -> float:
    try:
        return float(v)
    except Exception:
        return float("nan")


def read_csv(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: parse_float(v) for k, v in row.items()})
    return rows


def main():
    parser = argparse.ArgumentParser(description="Analyze families inside/outside S2-friendly zone.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = read_csv(args.proxies_csv)
    if not rows:
        raise SystemExit("No data in proxies CSV.")

    fe = np.array([r.get("first_energy", np.nan) for r in rows])
    sm = np.array([r.get("spacing_mean", np.nan) for r in rows])
    dN = np.array([r.get("Nucleon_like_d_spacing", np.nan) for r in rows])
    dR = np.array([r.get("Rho_like_d_spacing", np.nan) for r in rows])
    dP = np.array([r.get("Pion_like_d_spacing", np.nan) for r in rows])
    has_s2 = np.array([r.get("has_s2_dominant", 0) for r in rows], dtype=int)

    in_friendly = (fe < 0.8) & (sm > 0.50) & (dN > 5.5)

    LARGE = 1e9
    dN_f = np.where(np.isfinite(dN), dN, LARGE)
    dR_f = np.where(np.isfinite(dR), dR, LARGE)
    dP_f = np.where(np.isfinite(dP), dP, LARGE)

    closest = []
    for n, r, p in zip(dN_f, dR_f, dP_f):
        if n <= r and n <= p:
            closest.append("nucleon_like")
        elif r <= p:
            closest.append("rho_like")
        else:
            closest.append("pion_like")
    closest = np.array(closest)

    rows_out: List[Dict] = []
    for fam in ["nucleon_like", "rho_like", "pion_like"]:
        mask_fam = closest == fam
        for zone_name, zone_mask in [("friendly", in_friendly), ("out", ~in_friendly)]:
            mask = mask_fam & zone_mask
            n_runs = int(mask.sum())
            if n_runs == 0:
                continue
            sub_idx = np.where(mask)[0]
            n_s2 = int(has_s2[mask].sum())
            p_s2 = n_s2 / n_runs if n_runs else 0.0
            rows_out.append(
                {
                    "family": fam,
                    "zone": zone_name,
                    "n_runs": n_runs,
                    "n_s2": n_s2,
                    "p_s2": p_s2,
                    "first_energy_mean": float(np.nanmean(fe[sub_idx])),
                    "spacing_mean_mean": float(np.nanmean(sm[sub_idx])),
                    "Nucleon_like_d_spacing_mean": float(np.nanmean(dN[sub_idx])),
                }
            )

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "family_zone_summary.csv"
    if rows_out:
        with out_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows_out[0].keys())
            writer.writeheader()
            writer.writerows(rows_out)


if __name__ == "__main__":
    main()
