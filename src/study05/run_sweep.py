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
    LOG_FQ_MAX,
    LOG_FQ_MIN,
    sample_log_uniform,
)
from study05.families import (
    FamilyDistance,
    FamilyFingerprint,
    FamilyPriors,
    FamilySpec,
    build_fingerprint,
    compute_family_distance,
    load_family_spec,
    make_priors_for_family,
)
from study05.simulation import SimulationParams, pick_peaks, simulate
from study05.sweep import SimulationConfig, generate_configuration

DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_PROCESSED_DIR = Path("data/processed")
TARGET_ENERGY_GEV = 2.0


def _serialize_run_config(config: SimulationConfig) -> Dict:
    f_Q_hz = sample_log_uniform(LOG_FQ_MIN, LOG_FQ_MAX)
    f_S1_hz = f_Q_hz * config.R_S1_Q
    f_S2_hz = f_S1_hz * config.R_S2_S1
    f_S3_hz = f_S2_hz * config.R_S3_S2 if config.R_S3_S2 else None
    return {
        "case_name": config.case_name,
        "f_Q_base": config.f_Q,
        "f_Q_Hz": f_Q_hz,
        "f_S1_Hz": f_S1_hz,
        "f_S2_Hz": f_S2_hz,
        "f_S3_Hz": f_S3_hz,
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


def _rescale_energies(omegas: np.ndarray, target: float = TARGET_ENERGY_GEV) -> tuple[np.ndarray, float]:
    omegas = np.array(omegas)
    if omegas.size == 0:
        return omegas, 1.0
    anchor = omegas[min(2, omegas.size - 1)] if omegas.size >= 3 else omegas[0]
    scale = target / anchor if anchor > 0 else 1.0
    return omegas * scale, scale


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
    family_spec: Optional[FamilySpec] = None,
    family_fp: Optional[FamilyFingerprint] = None,
    family_priors: Optional[FamilyPriors] = None,
    raw_dir: Path = DEFAULT_RAW_DIR,
    processed_dir: Path = DEFAULT_PROCESSED_DIR,
):
    rng = np.random.default_rng(seed)
    raw_case_dir, processed_case_dir = _case_dirs(raw_dir, processed_dir, case)
    if family_spec:
        raw_case_dir = raw_case_dir / family_spec.name
        processed_case_dir = processed_case_dir / family_spec.name
        _ensure_dirs(raw_case_dir, processed_case_dir)
    sim_params = SimulationParams()

    run_inputs: List[Dict] = []
    run_outputs: List[Dict] = []
    spacings_all: List[np.ndarray] = []
    band_counts: List[int] = []
    rejected = 0
    unstable = 0
    accepted_runs_for_spacing = 0
    family_match_total = 0
    family_match_with_s2 = 0
    family_match_without_s2 = 0
    family_off_with_s2 = 0
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
            priors=family_priors,
        )
        if config is None:
            rejected += 1
            continue

        run_inputs.append(_serialize_run_config(config))

        try:
            sim_result = simulate(
                modes=config.modes,
                intra_couplings=config.intra_layer_couplings,
                inter_couplings=config.inter_layer_couplings,
                sim_params=sim_params,
                rng=rng,
            )
        except FloatingPointError:
            unstable += 1
            run_outputs.append(
                {
                    "run_id": run_idx,
                    "status": "unstable",
                    "n_modes": len(config.modes),
                    "n_memory_terms": config.memory_terms,
                    "complexity": config.complexity,
                    "energy_scale": None,
                    "energies_gev": [],
                    "band_energies_gev": [],
                    "band_spacing_gev": [],
                    "band_count": 0,
                    "accepted_for_spacing": False,
                    "band_weights": [],
                    "layers_order": [],
                    "b_trace": [],
                    "t_trace": [],
                    "dt_used": None,
                }
            )
            continue
        spectrum = sim_result["spectrum"]
        omega_peaks, weights_peaks = pick_peaks(
            spectrum=spectrum, modes=config.modes, layer_to_idx=sim_result["layer_to_idx"], sim_params=sim_params
        )
        energies_gev, scale = _rescale_energies(omega_peaks, target=TARGET_ENERGY_GEV)

        band_mask = (energies_gev >= band_min) & (energies_gev <= band_max)
        band_energies = energies_gev[band_mask]
        band_counts.append(int(band_energies.size))

        band_weights = [w for keep, w in zip(band_mask, weights_peaks) if keep]
        band_dominant_layers = []
        for w in band_weights:
            if not w:
                band_dominant_layers.append(None)
                continue
            layer_max = max(w.items(), key=lambda kv: kv[1])
            band_dominant_layers.append({"layer": layer_max[0], "weight": layer_max[1]})
        has_s2_dominant = any(item and item["layer"] == "S2" and item["weight"] >= 0.7 for item in band_dominant_layers)

        accepted_band = band_energies.size >= 3
        spacings = analysis.compute_spacings(band_energies[band_energies > 1e-4]) if accepted_band else np.array([])
        if accepted_band:
            spacings_all.append(spacings)
            accepted_runs_for_spacing += 1
            if example_run is None:
                example_run = {"energies": band_energies.copy(), "weights": band_weights}

        layer_order = [layer for layer, idx in sorted(sim_result["layer_to_idx"].items(), key=lambda kv: kv[1])]

        family_match = False
        family_distance: Optional[FamilyDistance] = None
        if family_fp and accepted_band:
            family_distance = compute_family_distance(
                sim_levels=band_energies.tolist(),
                sim_widths=None,
                fingerprint=family_fp,
                use_widths=False,
            )
            family_match = family_distance.is_match
            if family_match:
                family_match_total += 1
                if has_s2_dominant:
                    family_match_with_s2 += 1
                else:
                    family_match_without_s2 += 1
            elif has_s2_dominant:
                family_off_with_s2 += 1

        run_outputs.append(
            {
                "run_id": run_idx,
                "status": "ok",
                "n_modes": len(config.modes),
                "n_memory_terms": config.memory_terms,
                "complexity": config.complexity,
                "energy_scale": scale,
                "energies_gev": energies_gev.tolist(),
                "band_energies_gev": band_energies.tolist(),
                "band_spacing_gev": spacings.tolist(),
                "band_count": int(band_energies.size),
                "accepted_for_spacing": accepted_band,
                "family_match": family_match,
                "family_distance": family_distance.__dict__ if family_distance else None,
                "band_weights": band_weights,
                "band_dominant_layers": band_dominant_layers,
                "has_s2_dominant": has_s2_dominant,
                "layers_order": [l.name for l in layer_order],
                "b_trace": sim_result["b_series"].tolist(),
                "t_trace": sim_result["times"].tolist(),
                "dt_used": sim_result.get("dt_used"),
            }
        )

    all_spacings = np.concatenate(spacings_all) if spacings_all else np.array([])
    spacing_stats = analysis.summarise_spacings(all_spacings)
    d_totals = [r["family_distance"]["d_total"] for r in run_outputs if r.get("family_distance")]
    family_distance_stats = {
        "d_total_mean": float(np.mean(d_totals)) if d_totals else float("nan"),
        "d_total_std": float(np.std(d_totals)) if d_totals else float("nan"),
        "d_total_min": float(np.min(d_totals)) if d_totals else float("nan"),
        "d_total_max": float(np.max(d_totals)) if d_totals else float("nan"),
    }
    runs_with_s2_dominant = sum(
        1
        for r in run_outputs
        if r.get("status") == "ok" and r.get("has_s2_dominant")
    )

    summary = {
        "case": case,
        "runs_requested": runs,
        "runs_valid": len(run_outputs) - unstable,
        "runs_unstable": unstable,
        "runs_rejected": rejected,
        "band_count_mean": float(np.mean(band_counts)) if band_counts else 0.0,
        "band_count_std": float(np.std(band_counts)) if band_counts else 0.0,
        "spacing_stats": spacing_stats,
        "band_window_gev": [band_min, band_max],
        "runs_accepted_for_spacing": accepted_runs_for_spacing,
        "runs_with_s2_dominant": runs_with_s2_dominant,
        "family": family_spec.__dict__ if family_spec else None,
        "family_fingerprint": family_fp.__dict__ if family_fp else None,
        "family_match_stats": {
            "runs_family_match_total": family_match_total,
            "runs_family_match_with_s2": family_match_with_s2,
            "runs_family_match_without_s2": family_match_without_s2,
            "runs_off_family_with_s2": family_off_with_s2,
        },
        "family_distance_stats": family_distance_stats if family_spec else None,
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
    parser.add_argument(
        "--case", choices=["CaseA_2layers", "CaseB_3layers", "CaseB_debug"], default="CaseA_2layers"
    )
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
    parser.add_argument("--n-s2", type=int, default=2, help="Modes in layer S2.")
    parser.add_argument("--n-s3", type=int, default=0, help="Modes in layer S3 (Case B only).")
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
    parser.add_argument("--family-name", type=str, default=None, help="Predefined family name.")
    parser.add_argument("--family-config", type=Path, default=None, help="Path to family JSON config.")
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    family_spec = None
    family_fp = None
    family_priors = None

    if args.family_config:
        family_spec = load_family_spec(args.family_config)
    elif args.family_name:
        predefined = {
            "Nucleon_like": Path("data/raw/config/nucleon_like.json"),
            "Rho_like": Path("data/raw/config/rho_like.json"),
            "Pion_like": Path("data/raw/config/pion_like.json"),
        }
        if args.family_name in predefined and predefined[args.family_name].exists():
            family_spec = load_family_spec(predefined[args.family_name])

    if family_spec:
        family_fp = build_fingerprint(family_spec)
        family_priors = make_priors_for_family(family_spec, family_fp)
        # Override band window if provided by family
        args.band_min, args.band_max = family_spec.energy_window

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
        family_spec=family_spec,
        family_fp=family_fp,
        family_priors=family_priors,
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
