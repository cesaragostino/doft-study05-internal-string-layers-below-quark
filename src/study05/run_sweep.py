"""CLI helpers to run Study05 sweeps and persist results.

Usage example (from repository root):
    PYTHONPATH=src python -m study05.run_sweep --case CaseA_2layers --runs 20
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from study05.core import (
    build_dynamical_matrix,
    compute_eigenfrequencies,
    compute_mode_spacings,
    count_modes_in_band,
    energy_gev_to_mass_kg,
    generate_configuration,
    omega_to_energy_gev,
    summarise_spacings,
)

DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_PROCESSED_DIR = Path("data/processed")


def _serialize_run_config(config) -> Dict:
    return {
        "case_name": config.case_name,
        "f_Q_Hz": config.f_Q,
        "R_S1_Q": config.R_S1_Q,
        "R_S2_S1": config.R_S2_S1,
        "R_S3_S2": config.R_S3_S2,
        "N": {"Q": config.N_Q, "S1": config.N_S1, "S2": config.N_S2, "S3": config.N_S3},
        "memory_terms_per_link": [len(ic.memory_kernel.taus) for ic in config.inter_layer_couplings or []],
        "delays": [ic.delay for ic in config.inter_layer_couplings or []],
        "intra_couplings": len(config.intra_layer_couplings or []),
        "inter_coupling_links": [
            len(ic.coupling_matrix) for ic in config.inter_layer_couplings or []
        ],
        "complexity": config.complexity,
    }


def _plot_spacing_histogram(spacings: np.ndarray, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    plt.figure()
    plt.hist(spacings, bins=50, density=True)
    plt.xlabel("ΔE (GeV)")
    plt.ylabel("Probability density")
    plt.title("Mode spacings")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_spectrum(energies: np.ndarray, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    plt.figure()
    x = np.arange(len(energies))
    plt.stem(x, energies, use_line_collection=True)
    plt.xlabel("Mode index")
    plt.ylabel("Energy (GeV)")
    plt.title("Mode spectrum (all layers)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _ensure_dirs(raw_dir: Path, processed_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)


def run_sweep(
    case: str,
    runs: int,
    seed: Optional[int],
    max_complexity: int,
    n_q: int,
    n_s1: int,
    n_s2: int,
    n_s3: int,
    band_min: float,
    band_max: float,
    attempts: int,
    save_plots: bool,
    raw_dir: Path = DEFAULT_RAW_DIR,
    processed_dir: Path = DEFAULT_PROCESSED_DIR,
):
    rng = np.random.default_rng(seed)
    _ensure_dirs(raw_dir, processed_dir)

    run_inputs: List[Dict] = []
    run_outputs: List[Dict] = []
    spacings_all: List[np.ndarray] = []
    band_counts: List[int] = []
    rejected = 0
    example_spectrum: Optional[np.ndarray] = None

    for run_idx in range(runs):
        config = generate_configuration(
            case=case,
            rng=rng,
            n_q=n_q,
            n_s1=n_s1,
            n_s2=n_s2,
            n_s3=n_s3,
            max_complexity=max_complexity,
            attempts=attempts,
        )
        if config is None:
            rejected += 1
            continue

        run_inputs.append(_serialize_run_config(config))

        D = build_dynamical_matrix(
            modes=config.modes or [],
            intra_couplings=config.intra_layer_couplings or [],
            inter_couplings=config.inter_layer_couplings or [],
        )
        omegas = compute_eigenfrequencies(D)
        energies_gev = omega_to_energy_gev(omegas)
        if example_spectrum is None:
            example_spectrum = energies_gev.copy()

        band_mask = (energies_gev >= band_min) & (energies_gev <= band_max)
        band_energies = energies_gev[band_mask]
        band_counts.append(int(band_energies.size))
        spacings = compute_mode_spacings(band_energies)
        spacings_all.append(spacings)

        run_outputs.append(
            {
                "run_id": run_idx,
                "complexity": config.complexity,
                "energies_gev": energies_gev.tolist(),
                "band_energies_gev": band_energies.tolist(),
                "band_masses_kg": energy_gev_to_mass_kg(band_energies).tolist(),
                "band_spacing_gev": spacings.tolist(),
                "band_count": int(band_energies.size),
            }
        )

    all_spacings = np.concatenate(spacings_all) if spacings_all else np.array([])
    spacing_stats = summarise_spacings(all_spacings)
    summary = {
        "case": case,
        "runs_requested": runs,
        "runs_valid": len(run_outputs),
        "runs_rejected": rejected,
        "band_count_mean": float(np.mean(band_counts)) if band_counts else 0.0,
        "band_count_std": float(np.std(band_counts)) if band_counts else 0.0,
        "spacing_stats": spacing_stats,
        "band_window_gev": [band_min, band_max],
    }

    raw_payload = {"seed": seed, "max_complexity": max_complexity, "inputs": run_inputs}
    processed_payload = {
        "summary": summary,
        "runs": run_outputs,
    }

    raw_path = raw_dir / "study05_sweep_params.json"
    processed_path = processed_dir / "study05_sweep_results.json"

    raw_path.write_text(json.dumps(raw_payload, indent=2))
    processed_path.write_text(json.dumps(processed_payload, indent=2))

    if save_plots and example_spectrum is not None:
        spectrum_path = processed_dir / "study05_example_spectrum.png"
        _plot_spectrum(example_spectrum, spectrum_path)

    if save_plots and all_spacings.size > 0:
        spacing_path = processed_dir / "study05_spacing_histogram.png"
        _plot_spacing_histogram(all_spacings, spacing_path)

    return summary, raw_path, processed_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Study05 oscillator sweeps.")
    parser.add_argument("--case", choices=["CaseA_2layers", "CaseB_3layers"], default="CaseA_2layers")
    parser.add_argument(
        "--runs",
        type=int,
        default=20,
        help="Number of run attempts (some may be rejected by complexity).",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument(
        "--max-complexity", type=int, default=8, help="Maximum complexity (C) allowed for a run."
    )
    parser.add_argument("--n-q", type=int, default=1, help="Modes in layer Q.")
    parser.add_argument("--n-s1", type=int, default=3, help="Modes in layer S1.")
    parser.add_argument("--n-s2", type=int, default=3, help="Modes in layer S2.")
    parser.add_argument("--n-s3", type=int, default=3, help="Modes in layer S3 (Case B only).")
    parser.add_argument("--band-min", type=float, default=0.0, help="Min band energy (GeV).")
    parser.add_argument("--band-max", type=float, default=3.0, help="Max band energy (GeV).")
    parser.add_argument(
        "--attempts",
        type=int,
        default=20,
        help="Max attempts per run to satisfy complexity constraint.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable plot generation to speed up headless runs.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Directory to store raw parameters.",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=DEFAULT_PROCESSED_DIR,
        help="Directory to store processed outputs.",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    summary, raw_path, processed_path = run_sweep(
        case=args.case,
        runs=args.runs,
        seed=args.seed,
        max_complexity=args.max_complexity,
        n_q=args.n_q,
        n_s1=args.n_s1,
        n_s2=args.n_s2,
        n_s3=args.n_s3,
        band_min=args.band_min,
        band_max=args.band_max,
        attempts=args.attempts,
        save_plots=not args.no_plots,
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
    )
    print(json.dumps({"summary": summary, "raw_path": str(raw_path), "processed_path": str(processed_path)}, indent=2))


if __name__ == "__main__":
    main()
