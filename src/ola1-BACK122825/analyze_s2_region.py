"""Analyze S2-friendly proxy region from an existing proxies CSV.

This does not run simulations; it only slices `Case*_all_runs_proxies.csv`
to measure how S2 dominance correlates with simple proxy cuts.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def parse_float(value: str) -> float:
    try:
        if value == "":
            return float("nan")
        return float(value)
    except Exception:
        return float("nan")


def read_proxies_csv(path: Path) -> Tuple[List[Dict], List[str]]:
    rows: List[Dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for row in reader:
            parsed = {}
            for k, v in row.items():
                parsed[k] = parse_float(v) if k != "proxy" else v
            rows.append(parsed)
    return rows, headers


def frac_ci(k: int, n: int) -> Tuple[float, float, float]:
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    se = (p * (1 - p) / n) ** 0.5
    return p, p - 1.96 * se, p + 1.96 * se


def summarise(cols: List[float], mask: np.ndarray) -> Dict[str, float]:
    arr = np.array(cols)
    arr_in = arr[mask]
    arr_out = arr[~mask]
    return {
        "region_mean": float(np.nanmean(arr_in)) if arr_in.size else float("nan"),
        "region_std": float(np.nanstd(arr_in)) if arr_in.size else float("nan"),
        "out_mean": float(np.nanmean(arr_out)) if arr_out.size else float("nan"),
        "out_std": float(np.nanstd(arr_out)) if arr_out.size else float("nan"),
    }


def save_csv(rows: List[Dict], headers: List[str], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_outputs(df: Dict[str, np.ndarray], mask: np.ndarray, out_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    # Scatter first_energy vs spacing_mean
    plt.figure()
    colors = ["tab:blue" if s2 == 0 else "tab:red" for s2 in df["has_s2_dominant"]]
    plt.scatter(df["first_energy"], df["spacing_mean"], c=colors, alpha=0.6, edgecolors="none")
    plt.scatter(
        df["first_energy"][mask],
        df["spacing_mean"][mask],
        facecolors="none",
        edgecolors="k",
        label="in region",
    )
    plt.xlabel("first_energy (GeV)")
    plt.ylabel("spacing_mean (GeV)")
    plt.title("First energy vs spacing mean (color=S2 dominance)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "scatter_first_vs_spacing.png", dpi=200)
    plt.close()

    # Hist spacing_mean inside/out
    plt.figure()
    plt.hist(df["spacing_mean"][mask], bins=30, alpha=0.6, label="in region", density=True)
    plt.hist(df["spacing_mean"][~mask], bins=30, alpha=0.6, label="out region", density=True)
    plt.xlabel("spacing_mean (GeV)")
    plt.ylabel("density")
    plt.title("Spacing mean distribution")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "hist_spacing_mean.png", dpi=200)
    plt.close()

    # Bar chart p(S2)
    def frac(k, n):
        return (k / n) if n else 0.0

    n_region = mask.sum()
    n_out = (~mask).sum()
    k_region = int((df["has_s2_dominant"] * mask).sum())
    k_out = int((df["has_s2_dominant"] * (~mask)).sum())
    p_reg = frac(k_region, n_region)
    p_out = frac(k_out, n_out)
    se_reg = (p_reg * (1 - p_reg) / n_region) ** 0.5 if n_region else 0.0
    se_out = (p_out * (1 - p_out) / n_out) ** 0.5 if n_out else 0.0

    plt.figure()
    plt.bar(["region", "out"], [p_reg, p_out], yerr=[se_reg, se_out], capsize=5)
    plt.ylabel("p(S2 dominant)")
    plt.title("S2 dominance fraction")
    plt.tight_layout()
    plt.savefig(out_dir / "p_s2_bar.png", dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze S2-friendly region from proxies CSV.")
    parser.add_argument("--case", required=True, help="Case label (for summary).")
    parser.add_argument("--proxies-csv", type=Path, required=True, help="Path to all_runs_proxies CSV.")
    parser.add_argument("--first-energy-max", type=float, default=0.8)
    parser.add_argument("--spacing-mean-min", type=float, default=0.45)
    parser.add_argument("--nucleon-d-spacing-min", type=float, default=6.0)
    parser.add_argument("--output", type=Path, required=True, help="Output directory.")
    args = parser.parse_args()

    rows, headers = read_proxies_csv(args.proxies_csv)
    if not rows:
        raise SystemExit("No rows found in proxies CSV.")

    # Build arrays
    df = {
        "first_energy": np.array([r.get("first_energy", np.nan) for r in rows]),
        "spacing_mean": np.array([r.get("spacing_mean", np.nan) for r in rows]),
        "nucleon_like_d_spacing": np.array([r.get("Nucleon_like_d_spacing", np.nan) for r in rows]),
        "has_s2_dominant": np.array([r.get("has_s2_dominant", 0) for r in rows], dtype=float),
        "R_S1_Q": np.array([r.get("R_S1_Q", np.nan) for r in rows]),
        "R_S2_S1": np.array([r.get("R_S2_S1", np.nan) for r in rows]),
        "band_count": np.array([r.get("band_count", np.nan) for r in rows]),
    }

    mask = (
        (df["first_energy"] < args.first_energy_max)
        & (df["spacing_mean"] > args.spacing_mean_min)
        & (df["nucleon_like_d_spacing"] > args.nucleon_d_spacing_min)
    )
    mask = mask & np.isfinite(df["first_energy"]) & np.isfinite(df["spacing_mean"]) & np.isfinite(df["nucleon_like_d_spacing"])

    n_total = len(rows)
    n_region = int(mask.sum())
    n_out = n_total - n_region
    has_s2 = df["has_s2_dominant"] == 1
    k_region = int((has_s2 & mask).sum())
    k_out = int((has_s2 & ~mask).sum())

    p_region, lo_region, hi_region = frac_ci(k_region, n_region)
    p_out, lo_out, hi_out = frac_ci(k_out, n_out)

    stats_cols = ["first_energy", "spacing_mean", "nucleon_like_d_spacing", "R_S1_Q", "R_S2_S1", "band_count"]
    proxy_stats = {col: summarise(df[col].tolist(), mask) for col in stats_cols}

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "case": args.case,
        "cuts": {
            "first_energy_max": args.first_energy_max,
            "spacing_mean_min": args.spacing_mean_min,
            "nucleon_d_spacing_min": args.nucleon_d_spacing_min,
        },
        "counts": {
            "n_total": n_total,
            "n_region": n_region,
            "n_out": n_out,
            "k_region_s2": k_region,
            "k_out_s2": k_out,
        },
        "s2_fractions": {
            "region": {"p": p_region, "ci95": [lo_region, hi_region]},
            "out": {"p": p_out, "ci95": [lo_out, hi_out]},
        },
        "proxy_stats": proxy_stats,
    }
    (out_dir / "s2_region_summary.json").write_text(json.dumps(summary, indent=2))

    # Save region splits
    save_csv([r for r, m in zip(rows, mask) if m], headers, out_dir / "s2_region_in.csv")
    save_csv([r for r, m in zip(rows, mask) if not m], headers, out_dir / "s2_region_out.csv")

    # Plots
    plot_outputs(df, mask, out_dir)


if __name__ == "__main__":
    main()
