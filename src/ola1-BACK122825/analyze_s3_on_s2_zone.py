"""Analyze S3 behavior inside/outside the S2-friendly zone."""

from __future__ import annotations

import argparse
import csv
import json
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
    parser = argparse.ArgumentParser(description="Analyze S3 state inside/outside S2-friendly zone.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = read_csv(args.proxies_csv)
    if not rows:
        raise SystemExit("No data in proxies CSV.")

    fe = np.array([r.get("first_energy", np.nan) for r in rows])
    sm = np.array([r.get("spacing_mean", np.nan) for r in rows])
    dN = np.array([r.get("Nucleon_like_d_spacing", np.nan) for r in rows])
    in_friendly = (fe < 0.8) & (sm > 0.50) & (dN > 5.5)

    has_s2 = np.array([r.get("has_s2_dominant", 0) for r in rows], dtype=int)
    has_s3 = np.array([r.get("has_s3_dominant", 0) for r in rows], dtype=int)
    s3_state = np.array([r.get("s3_state", "") for r in rows])
    s3_band = np.array([r.get("s3_band_fraction", np.nan) for r in rows])
    s3_total = np.array([r.get("s3_total_fraction", np.nan) for r in rows])

    results = []
    for zone_name, mask in [("friendly", in_friendly), ("out", ~in_friendly)]:
        sub_idx = np.where(mask)[0]
        n_runs = int(mask.sum())
        if n_runs == 0:
            continue
        n_s2 = int(has_s2[mask].sum())
        n_s3_dom = int(has_s3[mask].sum())
        n_s3_noise = int((s3_state[mask] == "noise_tail").sum())
        band_mean = float(np.nanmean(s3_band[sub_idx])) if np.isfinite(s3_band[sub_idx]).any() else float("nan")
        total_mean = float(np.nanmean(s3_total[sub_idx])) if np.isfinite(s3_total[sub_idx]).any() else float("nan")

        results.append(
            {
                "zone": zone_name,
                "n_runs": n_runs,
                "n_s2_dom": n_s2,
                "p_s2_dom": n_s2 / n_runs if n_runs else 0.0,
                "n_s3_dom": n_s3_dom,
                "p_s3_dom": n_s3_dom / n_runs if n_runs else 0.0,
                "n_s3_noise": n_s3_noise,
                "p_s3_noise": n_s3_noise / n_runs if n_runs else 0.0,
                "s3_band_fraction_mean": band_mean,
                "s3_total_fraction_mean": total_mean,
            }
        )

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "s3_zone_summary.json").write_text(json.dumps({"summary": results}, indent=2))


if __name__ == "__main__":
    main()
