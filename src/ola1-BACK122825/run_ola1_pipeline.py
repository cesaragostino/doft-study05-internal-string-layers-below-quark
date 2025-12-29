"""Single-entry pipeline runner for Ola1 post-sweep processing (DNA-first)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional


def _run_step(label: str, cmd: Iterable[str]) -> None:
    print(f"[ola1_pipeline] {label}", flush=True)
    print(f"[ola1_pipeline] cmd: {' '.join(cmd)}", flush=True)
    subprocess.run(list(cmd), check=True)

def _remove_if_exists(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
            print(f"[ola1_pipeline] removed stale file: {path}", flush=True)
    except Exception as exc:
        raise RuntimeError(f"Failed to remove {path}: {exc}") from exc

def _remove_glob(base: Path, pattern: str) -> None:
    for path in base.glob(pattern):
        if path.is_file():
            _remove_if_exists(path)


def _with_pythonpath(cmd: Iterable[str]) -> list[str]:
    env = os.environ
    if "PYTHONPATH" not in env or not env["PYTHONPATH"]:
        os.environ["PYTHONPATH"] = "src"
    return list(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Ola1 pipeline after sweep (DNA-first).")
    parser.add_argument("--case", required=True, help="Case name, e.g. Ola1_3-2-5")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/ola1"))
    parser.add_argument("--results-json", type=Path, default=None, help="runs_partial.jsonl path")
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--selection-config", type=Path, default=Path("data/raw/wave1_selection.json"))
    parser.add_argument("--selection-log", type=Path, default=None)
    parser.add_argument("--digest-dir", type=Path, default=Path("data/processed/digest/ola1"))
    parser.add_argument("--max-blocks-per-particle", type=int, default=10000)
    parser.add_argument("--harmonic-mode-config", type=Path, default=None)
    parser.add_argument("--hbar-sim-output", type=Path, default=None)
    parser.add_argument("--skip-analyze", action="store_true")
    parser.add_argument("--skip-dna", action="store_true")
    parser.add_argument("--skip-report", action="store_true")
    args = parser.parse_args()

    processed_dir = args.processed_dir
    processed_dir.mkdir(parents=True, exist_ok=True)

    proxies_csv = processed_dir / f"{args.case}_all_runs_proxies.csv"
    zoo_matches_csv = processed_dir / "zoo_matches.csv"
    simple_blocks_json = processed_dir / "simple_blocks.json"
    selection_log = args.selection_log or (processed_dir / "ola1_blocks_selection.csv")
    hbar_out = args.hbar_sim_output or (processed_dir / "hbar_sim_calibration.json")
    report_path = processed_dir / f"{args.case}_ola1_report.md"
    dna_catalog = processed_dir / "dof_dna_catalog.csv"

    _remove_glob(processed_dir, "*_all_runs_proxies*.csv")
    _remove_glob(processed_dir, "zoo_matches*.csv")
    _remove_glob(processed_dir, "best_match_per_run*.csv")
    _remove_glob(processed_dir, "dof_dna_catalog*.csv")
    _remove_glob(processed_dir, "simple_blocks*.json")
    _remove_glob(processed_dir, "ola1_blocks_selection*.csv")
    _remove_glob(processed_dir, "hbar_sim_calibration*.json")
    _remove_glob(processed_dir, "*_ola1_report*.md")
    if args.digest_dir.exists():
        for path in args.digest_dir.glob("*"):
            if path.is_file():
                _remove_if_exists(path)

    if not args.skip_analyze:
        if args.results_json is None:
            raise SystemExit("--results-json is required unless --skip-analyze is set.")
        _run_step(
            "analyze_proxies",
            _with_pythonpath(
                [
                    sys.executable,
                    "-m",
                    "ola1.analyze_proxies",
                    "--case",
                    args.case,
                    "--output",
                    str(processed_dir),
                    "--results-json",
                    str(args.results_json),
                ]
            ),
        )

    if not args.skip_dna:
        _run_step(
            "dof_dna_catalog",
            _with_pythonpath(
                [
                    sys.executable,
                    "-m",
                    "ola1.ola1_dof_dna_catalog",
                    "--proxies-csv",
                    str(proxies_csv),
                    "--sm-universe",
                    str(args.sm_universe),
                    "--output",
                    str(dna_catalog),
                ]
            ),
        )

    match_args = [
        sys.executable,
        "-m",
        "ola1.match_sm_ola1",
        "--update-proxies",
        "--proxies-csv",
        str(proxies_csv),
        "--sm-universe",
        str(args.sm_universe),
        "--output",
        str(processed_dir),
    ]
    if args.harmonic_mode_config:
        match_args.extend(["--harmonic-mode-config", str(args.harmonic_mode_config)])
    _run_step("match_sm_ola1 (phase1)", _with_pythonpath(match_args))

    _run_step(
        "promote_simple_blocks (phase1)",
        _with_pythonpath(
            [
                sys.executable,
                "-m",
                "ola1.promote_simple_blocks",
                "--proxies-csv",
                str(proxies_csv),
                "--zoo-matches-csv",
                str(zoo_matches_csv),
                "--sm-universe",
                str(args.sm_universe),
                "--selection-config",
                str(args.selection_config),
                "--selection-log",
                str(selection_log),
                "--output",
                str(simple_blocks_json),
                "--digest",
                str(args.digest_dir),
                "--max-blocks-per-particle",
                str(args.max_blocks_per_particle),
            ]
        ),
    )

    _remove_if_exists(hbar_out)
    _run_step(
        "hbar_sim_calibration",
        _with_pythonpath(
            [
                sys.executable,
                "-m",
                "ola1.hbar_sim_calibration",
                "--blocks",
                str(simple_blocks_json),
                "--sm-universe",
                str(args.sm_universe),
                "--proxies-csv",
                str(proxies_csv),
                "--output",
                str(hbar_out),
            ]
        ),
    )

    match_args2 = [
        sys.executable,
        "-m",
        "ola1.match_sm_ola1",
        "--use-mass-sim",
        "--update-proxies",
        "--proxies-csv",
        str(proxies_csv),
        "--sm-universe",
        str(args.sm_universe),
        "--hbar-sim",
        str(hbar_out),
        "--output",
        str(processed_dir),
    ]
    if args.harmonic_mode_config:
        match_args2.extend(["--harmonic-mode-config", str(args.harmonic_mode_config)])
    _run_step("match_sm_ola1 (phase2)", _with_pythonpath(match_args2))

    _run_step(
        "promote_simple_blocks (phase2)",
        _with_pythonpath(
            [
                sys.executable,
                "-m",
                "ola1.promote_simple_blocks",
                "--proxies-csv",
                str(proxies_csv),
                "--zoo-matches-csv",
                str(zoo_matches_csv),
                "--sm-universe",
                str(args.sm_universe),
                "--selection-config",
                str(args.selection_config),
                "--selection-log",
                str(selection_log),
                "--output",
                str(simple_blocks_json),
                "--digest",
                str(args.digest_dir),
                "--max-blocks-per-particle",
                str(args.max_blocks_per_particle),
            ]
        ),
    )

    if not args.skip_report:
        _run_step(
            "ola1_status_report",
            _with_pythonpath(
                [
                    sys.executable,
                    "-m",
                    "ola1.ola1_status_report",
                    "--case",
                    args.case,
                    "--processed-dir",
                    str(processed_dir),
                    "--output",
                    str(report_path),
                ]
            ),
        )


if __name__ == "__main__":
    main()
