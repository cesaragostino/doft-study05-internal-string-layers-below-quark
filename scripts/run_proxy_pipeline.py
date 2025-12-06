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
        default=Path("reports/CaseB_debug_pipeline"),
        help="Output directory for analysis",
    )
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
