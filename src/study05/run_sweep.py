"""CLI helpers to run Study05 sweeps (v0.1 with memory/state-space)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from study05 import analysis, plots
from study05.config import (
    DEFAULT_BAND_MAX,
    DEFAULT_BAND_MIN,
    DEFAULT_MAX_COMPLEXITY,
    DEFAULT_N_INTERNAL,
    DEFAULT_N_Q,
)
from study05.state_space import eigen_spectrum
from study05.sweep import SimulationConfig, generate_configuration, state_matrix_from_config

DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_PROCESSED_DIR = Path("data/processed")
TARGET_ENERGY_GEV = 2.0


def _serialize_run_config(config: SimulationConfig) -> Dict:
    return {
        "case_name": config.case_name,
        "f_Q_Hz": config.f_Q,
        "R_S1_Q": config.R_S1_Q,
        "R_S2_S1": config.R_S2_S1,
        "R_S3_S2": config.R_S3_S2,
        "N": {"Q": config.N_Q, "S1": config.N_S1, "S2": config.N_S2, "S3": config.N_S3},
        "memory_terms": config.memory_terms,
        "complexity": config.complexity,
    }


def _ensure_dirs(raw_dir: Path, processed_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)


def _case_dirs(raw_dir: Path, processed_dir: Path, case: str) -> tuple[Path, Path]:
    raw_case = raw_dir / case
    processed_case = processed_dir / case
    _ensure_dirs(raw_case, processed_case)
    return raw_case, processed_case


def _rescale_energies(energies: np.ndarray, target: float = TARGET_ENERGY_GEV) -> tuple[np.ndarray, float]:
    """Rescale energies so a reference low mode lands near target."""
    energies_sorted = np.sort(energies[energies > 0])
    if energies_sorted.size == 0:
        return energies, 1.0
    ref = energies_sorted[min(2, energies_sorted.size - 1)]  # median of lowest three (or lowest if <3)
    scale = target / ref if ref > 0 else 1.0
    return energies * scale, scale


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
    raw_case_dir, processed_case_dir = _case_dirs(raw_dir, processed_dir, case)

    run_inputs: List[Dict] = []
    run_outputs: List[Dict] = []
    spacings_all: List[np.ndarray] = []
    band_counts: List[int] = []
    rejected = 0
    accepted_runs_for_spacing = 0
    example_run = None

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

        A, index_map, n_z = state_matrix_from_config(config)
        eigvals, eigvecs = eigen_spectrum(A)
        energies_all = analysis.eigvals_to_energies_gev(eigvals)
        weights_full = analysis.layer_weights(eigvecs, config.modes, index_map)

        # drop near-zero energies (spurious neutral eigenvalues)
        energy_eps = 1e-9
        nonzero_mask = energies_all > energy_eps
        energies_gev = energies_all[nonzero_mask]
        weights_filtered = [w for keep, w in zip(nonzero_mask, weights_full) if keep]

        energies_gev, scale = _rescale_energies(energies_gev, target=TARGET_ENERGY_GEV)

        band_mask = (energies_gev >= band_min) & (energies_gev <= band_max)
        band_indices = np.where(band_mask)[0]
        band_energies = energies_gev[band_indices]
        band_counts.append(int(band_energies.size))

        band_weights = []
        for idx in band_indices:
            band_weights.append({"energy_gev": float(energies_gev[idx]), "weights": weights_filtered[idx]})

        accepted_band = 3 <= band_energies.size <= 12
        spacings = analysis.compute_spacings(band_energies) if accepted_band else np.array([])
        if accepted_band:
            spacings_all.append(spacings)
            accepted_runs_for_spacing += 1
            if example_run is None:
                example_run = {"energies": band_energies.copy(), "weights": [weights_filtered[i] for i in band_indices]}

        run_outputs.append(
            {
                "run_id": run_idx,
                "state_dim": int(A.shape[0]),
                "n_modes": len(config.modes),
                "n_memory_terms": config.memory_terms,
                "complexity": config.complexity,
                "energy_scale": scale,
                "energies_gev": energies_gev.tolist(),
                "band_energies_gev": band_energies.tolist(),
                "band_masses_kg": analysis.energies_to_masses_kg(band_energies).tolist(),
                "band_spacing_gev": spacings.tolist(),
                "band_count": int(band_energies.size),
                "accepted_for_spacing": accepted_band,
                "band_weights": band_weights,
            }
        )

    all_spacings = np.concatenate(spacings_all) if spacings_all else np.array([])
    spacing_stats = analysis.summarise_spacings(all_spacings)
    summary = {
        "case": case,
        "runs_requested": runs,
        "runs_valid": len(run_outputs),
        "runs_rejected": rejected,
        "band_count_mean": float(np.mean(band_counts)) if band_counts else 0.0,
        "band_count_std": float(np.std(band_counts)) if band_counts else 0.0,
        "spacing_stats": spacing_stats,
        "band_window_gev": [band_min, band_max],
        "runs_accepted_for_spacing": accepted_runs_for_spacing,
    }

    raw_payload = {"seed": seed, "max_complexity": max_complexity, "inputs": run_inputs}
    processed_payload = {
        "summary": summary,
        "runs": run_outputs,
    }

    raw_path = raw_case_dir / "study05_sweep_params.json"
    processed_path = processed_case_dir / "study05_sweep_results.json"

    raw_path.write_text(json.dumps(raw_payload, indent=2))
    processed_path.write_text(json.dumps(processed_payload, indent=2))

    if save_plots:
        if example_run:
            sorted_idx = np.argsort(example_run["energies"])
            energies_sorted = np.array(example_run["energies"])[sorted_idx]
            weights_sorted = [example_run["weights"][i] for i in sorted_idx]
            plots.plot_spectrum(
                energies_sorted,
                processed_case_dir / "study05_example_band_spectrum.png",
                title="Hadronic-band spectrum",
            )
            plots.plot_layer_heatmap(
                energies_sorted.tolist(),
                weights_sorted,
                layers_order=["Q", "S1", "S2", "S3"],
                output_path=processed_case_dir / "study05_example_band_heatmap.png",
            )
        if all_spacings.size > 0:
            plots.plot_spacing_histogram(all_spacings, processed_case_dir / "study05_spacing_histogram.png")

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
        "--max-complexity", type=int, default=DEFAULT_MAX_COMPLEXITY, help="Maximum complexity (C) allowed per run."
    )
    parser.add_argument("--n-q", type=int, default=DEFAULT_N_Q, help="Modes in layer Q.")
    parser.add_argument("--n-s1", type=int, default=DEFAULT_N_INTERNAL, help="Modes in layer S1.")
    parser.add_argument("--n-s2", type=int, default=DEFAULT_N_INTERNAL, help="Modes in layer S2.")
    parser.add_argument("--n-s3", type=int, default=DEFAULT_N_INTERNAL, help="Modes in layer S3 (Case B only).")
    parser.add_argument("--band-min", type=float, default=DEFAULT_BAND_MIN, help="Min band energy (GeV).")
    parser.add_argument("--band-max", type=float, default=DEFAULT_BAND_MAX, help="Max band energy (GeV).")
    parser.add_argument(
        "--attempts",
        type=int,
        default=30,
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
    print(
        json.dumps(
            {"summary": summary, "raw_path": str(raw_path), "processed_path": str(processed_path)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
