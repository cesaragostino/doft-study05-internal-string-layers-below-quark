"""Aggregate per-family sweep results into summary tables and plots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from study05 import plots


def load_summary(path: Path) -> Dict:
    data = json.loads(path.read_text())
    return data.get("summary", {}), data.get("runs", [])


def build_family_row(family: str, summary: Dict) -> Dict:
    spacing_stats = summary.get("spacing_stats", {}) or {}
    dist_stats = summary.get("family_distance_stats", {}) or {}
    return {
        "family": family,
        "runs_valid": summary.get("runs_valid", 0),
        "runs_with_s2": summary.get("runs_with_s2_dominant", 0),
        "band_count_mean": summary.get("band_count_mean", 0.0),
        "band_count_std": summary.get("band_count_std", 0.0),
        "spacing_mean": spacing_stats.get("mean"),
        "spacing_std": spacing_stats.get("std"),
        "runs_family_match_total": summary.get("family_match_stats", {}).get("runs_family_match_total", 0),
        "runs_family_match_with_s2": summary.get("family_match_stats", {}).get("runs_family_match_with_s2", 0),
        "runs_family_match_without_s2": summary.get("family_match_stats", {}).get("runs_family_match_without_s2", 0),
        "runs_off_family_with_s2": summary.get("family_match_stats", {}).get("runs_off_family_with_s2", 0),
        "d_total_mean": dist_stats.get("d_total_mean"),
        "d_total_std": dist_stats.get("d_total_std"),
        "d_total_min": dist_stats.get("d_total_min"),
        "d_total_max": dist_stats.get("d_total_max"),
    }


def save_csv(rows: List[Dict], path: Path) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    lines = [",".join(keys)]
    for row in rows:
        lines.append(",".join(str(row.get(k, "")) for k in keys))
    path.write_text("\n".join(lines))


def plot_s2_fraction(rows: List[Dict], output_dir: Path) -> None:
    fractions = []
    families = []
    for r in rows:
        rv = r["runs_valid"] or 1
        frac = (r["runs_with_s2"] / rv) if rv else 0.0
        families.append(r["family"])
        fractions.append(frac)
    if not families:
        return
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    plt.figure()
    plt.bar(families, fractions)
    plt.ylabel("S2-dominant fraction")
    plt.tight_layout()
    plt.savefig(output_dir / "s2_fraction_bar.png", dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Aggregate family sweep results.")
    parser.add_argument("--case", required=True, help="Case name (e.g., CaseB_debug).")
    parser.add_argument("--families", nargs="+", required=True, help="Family names to include.")
    parser.add_argument("--output", type=Path, default=Path("reports"), help="Output directory/prefix.")
    args = parser.parse_args()

    rows: List[Dict] = []
    d_total_data: Dict[str, List[float]] = {}
    base_processed = Path("data/processed") / args.case
    output_dir = args.output if args.output.suffix == "" else args.output.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    for fam in args.families:
        # try to resolve directory in a case-insensitive way
        candidates = [
            base_processed / fam,
            base_processed / fam.lower(),
            base_processed / fam.capitalize(),
        ]
        if base_processed.exists():
            candidates += [p for p in base_processed.iterdir() if p.is_dir() and p.name.lower() == fam.lower()]
        res_path = None
        for cand in candidates:
            path = cand / "study05_sweep_results.json"
            if path.exists():
                res_path = path
                fam = cand.name  # canonical dir name
                break
        if not res_path:
            continue
        summary, runs = load_summary(res_path)
        rows.append(build_family_row(fam, summary))
        d_vals = [r["family_distance"]["d_total"] for r in runs if r.get("family_distance")]
        if d_vals:
            d_total_data[fam] = d_vals

    if not rows:
        print("No family results found.")
        return

    output_prefix = output_dir / f"{args.case}_families"
    save_csv(rows, Path(str(output_prefix) + "_summary.csv"))
    Path(str(output_prefix) + "_summary.json").write_text(json.dumps(rows, indent=2))

    # Plots
    plot_s2_fraction(rows, output_dir)
    # Boxplot for d_total if data available
    if d_total_data:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return
        plt.figure()
        labels = list(d_total_data.keys())
        data = [d_total_data[k] for k in labels]
        plt.boxplot(data, tick_labels=labels)
        plt.ylabel("d_total")
        plt.tight_layout()
        plt.savefig(output_dir / "d_total_boxplot.png", dpi=200)
        plt.close()


if __name__ == "__main__":
    main()
