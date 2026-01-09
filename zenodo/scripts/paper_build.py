#!/usr/bin/env python3
"""Build paper datasets and final figures."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    print(f"[paper_build] cmd: {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper data + figures.")
    parser.add_argument(
        "--olas",
        default="ola2_paper,ola3_paper,ola4_paper",
        help="Comma-separated processed ola directories (e.g. ola2_paper,ola3_paper,ola4_paper).",
    )
    parser.add_argument("--processed-root", default="data/processed")
    parser.add_argument("--data-dir", default="paper/data")
    parser.add_argument("--figures-dir", default="paper/figures")
    args = parser.parse_args()

    ola_names = [name.strip() for name in args.olas.split(",") if name.strip()]
    ola_dirs = [str(Path(args.processed_root) / name) for name in ola_names]

    data_cmd = [
        sys.executable,
        "scripts/paper_metrics_pack.py",
        "--out-root",
        args.data_dir,
        "--skip-plots",
        "--all",
    ]
    for ola_dir in ola_dirs:
        data_cmd.extend(["--ola-dir", ola_dir])
    _run(data_cmd)

    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in ola_names:
        src = Path(args.processed_root) / name / "catalog" / f"genome_layers_{name}.csv"
        if not src.exists():
            print(f"[paper_build] WARNING missing genome csv: {src}", flush=True)
            continue
        dst = data_dir / f"genome_layers_{name}.csv"
        dst.write_bytes(src.read_bytes())

    metrics_args = {}
    for name in ola_names:
        metrics_args[name] = str(Path(args.data_dir) / name / f"paper_metrics_{name}.csv")

    fig_cmd = [
        sys.executable,
        "scripts/paper_figures_final.py",
        "--metrics-ola2",
        metrics_args.get("ola2_paper", ""),
        "--metrics-ola3",
        metrics_args.get("ola3_paper", ""),
        "--metrics-ola4",
        metrics_args.get("ola4_paper", ""),
        "--genome-ola2",
        str(Path(args.data_dir) / "genome_layers_ola2_paper.csv"),
        "--genome-ola3",
        str(Path(args.data_dir) / "genome_layers_ola3_paper.csv"),
        "--genome-ola4",
        str(Path(args.data_dir) / "genome_layers_ola4_paper.csv"),
        "--out-dir",
        args.figures_dir,
    ]
    _run(fig_cmd)


if __name__ == "__main__":
    main()
