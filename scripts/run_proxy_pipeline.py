#!/usr/bin/env python3
"""Run an agnostic sweep + proxy analysis for specified families.

Usage example:
    PYTHONPATH=src python3 scripts/run_proxy_pipeline.py \
      --case CaseB_debug \
      --runs 200 \
      --seed 123 \
      --band-min 0.2 \
      --band-max 3.0 \
      --families nucleon_like rho_like pion_like \
      --output reports/CaseB_debug_pipeline
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def run_cmd(cmd: list[str]):
    print(f"[pipeline] running: {' '.join(cmd)}", flush=True)
    env = os.environ.copy()
    env.setdefault("PYTHONWARNINGS", "ignore::RuntimeWarning")
    subprocess.run(cmd, check=True, env=env)


def main():
    parser = argparse.ArgumentParser(description="Run sweep + proxy analysis pipeline")
    parser.add_argument("--case", default="CaseB_debug", help="Case name for sweep")
    parser.add_argument("--runs", type=int, default=200, help="Runs for sweep")
    parser.add_argument("--seed", type=int, default=123, help="Seed for sweep")
    parser.add_argument("--band-min", type=float, default=0.2, help="Band min (GeV)")
    parser.add_argument("--band-max", type=float, default=3.0, help="Band max (GeV)")
    parser.add_argument(
        "--families",
        nargs="+",
        default=["nucleon_like", "rho_like", "pion_like"],
        help="Families to analyze (names or paths)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed"),
        help="Output root for analysis outputs",
    )
    parser.add_argument(
        "--tag-and-catalog",
        action="store_true",
        help="If set, run tag_s2_zones and catalog_families_s2 after proxies CSV is generated.",
    )
    args = parser.parse_args()

    def resolve_output_dir(base: Path, case: str) -> Path:
        if base == Path("reports"):
            return Path("data/processed") / case / "combined"
        if base == Path("data/processed"):
            return base / case / "combined"
        return base

    # Step 1: agnostic sweep to global outputs
    sweep_cmd = [
        "python3",
        "-m",
        "study05.run_sweep",
        "--case",
        args.case,
        "--runs",
        str(args.runs),
        "--seed",
        str(args.seed),
        "--band-min",
        str(args.band_min),
        "--band-max",
        str(args.band_max),
        "--no-plots",
    ]
    run_cmd(sweep_cmd)

    # Step 2: proxy analysis using global results
    print("[pipeline] sweep completed, starting proxy analysis", flush=True)
    analyze_cmd = [
        "python3",
        "-m",
        "study05.analyze_proxies",
        "--case",
        args.case,
        "--output",
        str(args.output),
        "--families",
    ] + args.families
    run_cmd(analyze_cmd)

    if args.tag_and_catalog:
        resolved_out = resolve_output_dir(args.output, args.case)
        proxies_csv = resolved_out / f"{args.case}_all_runs_proxies.csv"
        tagged_csv = resolved_out / f"{args.case}_all_runs_tagged.csv"
        print("[pipeline] tagging S2 zones", flush=True)
        run_cmd(
            [
                "python3",
                "-m",
                "study05.tag_s2_zones",
                "--proxies-csv",
                str(proxies_csv),
                "--output",
                str(tagged_csv),
            ]
        )
        print("[pipeline] cataloging families vs S2", flush=True)
        catalog_out = resolved_out / "catalog_s2"
        run_cmd(
            [
                "python3",
                "-m",
                "study05.catalog_families_s2",
                "--proxies-csv",
                str(tagged_csv),
                "--families",
            ]
            + args.families
            + ["--output", str(catalog_out)]
        )


if __name__ == "__main__":
    main()
