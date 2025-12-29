"""Threshold scan for S2-friendly regions in proxy space.

Scans grids of (first_energy_max, spacing_mean_min, nucleon_like_d_spacing_min)
over an existing proxies CSV and reports S2 prevalence and z-scores.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def parse_float(v: str) -> float:
    try:
        return float(v)
    except Exception:
        return float("nan")


def read_proxies_csv(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {k: parse_float(v) for k, v in row.items()}
            rows.append(parsed)
    return rows


def frac_se(k: int, n: int) -> Tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    se = np.sqrt(p * (1 - p) / n)
    return p, se


def write_csv(rows: List[Dict], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Scan proxy thresholds for S2 enrichment.")
    parser.add_argument("--proxies-csv", type=Path, required=True, help="CSV with all runs proxies.")
    parser.add_argument("--output", type=Path, required=True, help="Output directory.")
    parser.add_argument("--first-grid", type=float, nargs="+", default=[0.6, 0.7, 0.8, 0.9])
    parser.add_argument("--spacing-grid", type=float, nargs="+", default=[0.40, 0.45, 0.50])
    parser.add_argument("--dspacing-grid", type=float, nargs="+", default=[5.5, 6.0, 6.5])
    args = parser.parse_args()

    rows = read_proxies_csv(args.proxies_csv)
    if not rows:
        raise SystemExit("No data in proxies CSV.")

    fe = np.array([r.get("first_energy", np.nan) for r in rows])
    sm = np.array([r.get("spacing_mean", np.nan) for r in rows])
    ds = np.array([r.get("Nucleon_like_d_spacing", np.nan) for r in rows])
    s2 = np.array([r.get("has_s2_dominant", 0) for r in rows], dtype=int)

    n_total = len(rows)
    results: List[Dict] = []

    for f_max in args.first_grid:
        for s_min in args.spacing_grid:
            for d_min in args.dspacing_grid:
                mask = (fe < f_max) & (sm > s_min) & (ds > d_min)
                mask = mask & np.isfinite(fe) & np.isfinite(sm) & np.isfinite(ds)
                n_region = int(mask.sum())
                n_out = n_total - n_region
                if n_region == 0 or n_out == 0:
                    continue
                k_region = int((s2 & mask).sum())
                k_out = int((s2 & (~mask)).sum())

                p_reg, se_reg = frac_se(k_region, n_region)
                p_out, se_out = frac_se(k_out, n_out)
                delta_p = p_reg - p_out
                se_delta = np.sqrt(se_reg**2 + se_out**2)
                z_score = delta_p / se_delta if se_delta > 0 else 0.0

                results.append(
                    {
                        "first_max": f_max,
                        "spacing_min": s_min,
                        "dspacing_min": d_min,
                        "n_total": n_total,
                        "n_region": n_region,
                        "k_region_s2": k_region,
                        "p_region": p_reg,
                        "se_region": se_reg,
                        "n_out": n_out,
                        "k_out_s2": k_out,
                        "p_out": p_out,
                        "se_out": se_out,
                        "delta_p": delta_p,
                        "z_score": z_score,
                    }
                )

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(results, out_dir / "s2_scan_results.csv")


if __name__ == "__main__":
    main()
