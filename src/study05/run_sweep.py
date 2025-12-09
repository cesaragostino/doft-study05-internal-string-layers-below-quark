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
try:
    import yaml
except ImportError:
    yaml = None
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
DEFAULT_LAYER_THRESHOLDS = {
    "S2": {
        "band_fraction_dominant": 0.5,
        "band_fraction_sub": 0.1,
        "compactness_dom": 1.0,
        "compactness_sub": 0.5,
        "total_fraction_eps": 1e-3,
        "noise_highfreq_min": 0.2,
    },
    "S3": {
        "band_fraction_dominant": 0.4,
        "band_fraction_sub": 0.05,
        "compactness_dom": 0.8,
        "compactness_sub": 0.4,
        "total_fraction_eps": 1e-3,
        "noise_highfreq_min": 0.2,
    },
}


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


def _serialize_theta(config: SimulationConfig) -> Dict:
    modes = [
        {
            "layer": m.layer.name,
            "index": m.index,
            "omega0": m.omega0,
            "mass": m.mass,
            "gamma": m.gamma,
        }
        for m in config.modes
    ]
    intra = [
        {
            "i": {"layer": c.i[0].name, "index": c.i[1]},
            "j": {"layer": c.j[0].name, "index": c.j[1]},
            "k_ij0": c.k_ij0,
        }
        for c in config.intra_layer_couplings
    ]
    inter = []
    for ic in config.inter_layer_couplings:
        links = []
        for (i_deep, j_sh), ker in ic.links.items():
            links.append(
                {
                    "i_deep": i_deep,
                    "j_shallow": j_sh,
                    "taus0": ker.taus0,
                    "amps0": ker.amps0,
                }
            )
        inter.append(
            {
                "deep_layer": ic.deep_layer.name,
                "shallow_layer": ic.shallow_layer.name,
                "g0": ic.g0,
                "links": links,
            }
        )
    return {
        "modes": modes,
        "intra_couplings": intra,
        "inter_couplings": inter,
    }


def _ensure_dirs(raw_dir: Path, processed_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)


def _case_dirs(raw_dir: Path, processed_dir: Path, case: str) -> tuple[Path, Path]:
    raw_case = raw_dir / case
    processed_case = processed_dir / case
    _ensure_dirs(raw_case, processed_case)
    return raw_case, processed_case


def _load_layer_state_config(path: Path) -> Dict[str, Dict]:
    if yaml is None or not path.exists():
        return {}
    try:
        with path.open() as f:
            data = yaml.safe_load(f)
            return data or {}
    except Exception:
        return {}


def _load_engine_config(path: Optional[Path]) -> Dict:
    if path is None or not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


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


def _weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    if values.size == 0 or weights.size == 0:
        return 0.0
    w_sum = np.sum(weights)
    if w_sum <= 0:
        return 0.0
    mean = np.sum(weights * values) / w_sum
    var = np.sum(weights * (values - mean) ** 2) / w_sum
    return float(np.sqrt(var))


def _layer_summary(
    layer_name: str,
    energies: np.ndarray,
    weights: List[Dict[str, float]],
    band_mask: np.ndarray,
    band_max: float,
    thresholds: Dict[str, float],
) -> Dict[str, object]:
    """Compute per-layer fractions and classify state."""
    all_weights = np.array([w.get(layer_name, 0.0) for w in weights]) if weights else np.array([])
    total_fraction = float(np.mean(all_weights)) if all_weights.size else 0.0

    band_weights = all_weights[band_mask] if all_weights.size else np.array([])
    band_fraction = float(np.mean(band_weights)) if band_weights.size else 0.0

    out_weights = all_weights[~band_mask] if all_weights.size else np.array([])
    outband_fraction = float(np.mean(out_weights)) if out_weights.size else 0.0

    highfreq_mask = energies > band_max
    highfreq_weights = all_weights[highfreq_mask] if all_weights.size else np.array([])
    highfreq_fraction = float(np.mean(highfreq_weights)) if highfreq_weights.size else 0.0

    # compactness: inverse of weighted std of energies where weight>0 in band
    band_energy = energies[band_mask]
    w_positive = band_weights[band_weights > 0]
    e_positive = band_energy[band_weights > 0] if band_weights.size else np.array([])
    std_band = _weighted_std(e_positive, w_positive) if w_positive.size else 0.0
    band_compactness = float(1.0 / (std_band + 1e-6)) if std_band > 0 else 0.0

    state = "mixed"
    if total_fraction < thresholds.get("total_fraction_eps", 1e-3):
        state = "absent"
    else:
        bf_dom = thresholds.get("band_fraction_dominant", 0.5)
        bf_sub = thresholds.get("band_fraction_sub", 0.1)
        comp_dom = thresholds.get("compactness_dom", 1.0)
        comp_sub = thresholds.get("compactness_sub", 0.5)
        noise_min = thresholds.get("noise_highfreq_min", 0.2)

        if band_fraction >= bf_dom and band_compactness >= comp_dom:
            state = "structural_dominant"
        elif band_fraction >= bf_sub and band_compactness >= comp_sub:
            state = "structural_sub"
        elif (band_fraction < bf_sub) and (highfreq_fraction >= noise_min or outband_fraction >= noise_min):
            state = "noise_tail"
        else:
            state = "mixed"

    return {
        "band_fraction": band_fraction,
        "total_fraction": total_fraction,
        "band_compactness": band_compactness,
        "outband_fraction": outband_fraction,
        "highfreq_fraction": highfreq_fraction,
        "state": state,
    }


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
    output_root: Optional[Path] = None,
    layer_state_config: Optional[Dict] = None,
    sim_params_cfg: Optional[Dict] = None,
):
    rng = np.random.default_rng(seed)
    if output_root:
        raw_dir = Path(output_root) / "raw"
        processed_dir = Path(output_root)
    raw_case_dir, processed_case_dir = _case_dirs(raw_dir, processed_dir, case)
    if family_spec:
        raw_case_dir = raw_case_dir / family_spec.name
        processed_case_dir = processed_case_dir / family_spec.name
    else:
        raw_case_dir = raw_case_dir / "global"
        processed_case_dir = processed_case_dir / "global"
    _ensure_dirs(raw_case_dir, processed_case_dir)
    sim_params = SimulationParams(**sim_params_cfg) if sim_params_cfg else SimulationParams()

    layer_state_config = layer_state_config or {}
    lock_thresholds = layer_state_config.get("lock_thresholds", {})
    s2_state_cfg = layer_state_config.get("s2_state", {})

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
        s2_band_fraction = (
            sum(1 for item in band_dominant_layers if item and item["layer"] == "S2") / band_energies.size
            if band_energies.size > 0
            else 0.0
        )
        s3_band_fraction = (
            sum(1 for item in band_dominant_layers if item and item["layer"] == "S3") / band_energies.size
            if band_energies.size > 0
            else 0.0
        )

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

        # Layer summaries (S2/S3 focus)
        layer_summaries: Dict[str, Dict] = {}
        for layer in layer_order:
            lname = layer.name
            thresholds = DEFAULT_LAYER_THRESHOLDS.get(lname, DEFAULT_LAYER_THRESHOLDS.get("S2", {}))
            layer_summaries[lname] = _layer_summary(
                layer_name=lname,
                energies=energies_gev,
                weights=weights_peaks,
                band_mask=band_mask,
                band_max=band_max,
                thresholds=thresholds,
            )

        s2_state = layer_summaries.get("S2", {}).get("state", "absent")
        s3_state = layer_summaries.get("S3", {}).get("state", "absent")
        has_s3_dominant = s3_state == "structural_dominant"

        # lock_quality based on band fraction
        lock_quality_Q = layer_summaries.get("Q", {}).get("band_fraction", float("nan"))
        lock_quality_S1 = layer_summaries.get("S1", {}).get("band_fraction", float("nan"))
        lock_quality_S2 = layer_summaries.get("S2", {}).get("band_fraction", float("nan"))
        lock_quality_S3 = layer_summaries.get("S3", {}).get("band_fraction", float("nan"))

        # Relative thresholds (defaults can be overridden via YAML)
        T_Q_rel_min = lock_thresholds.get("T_Q_rel_min", lock_thresholds.get("T_Q", 0.5))
        T_S1_rel_min = lock_thresholds.get("T_S1_rel_min", lock_thresholds.get("T_S1", 0.1))
        T_S2_rel_min = lock_thresholds.get("T_S2_rel_min", lock_thresholds.get("T_S2", 0.1))

        def _finite(x: float) -> float:
            return float(x) if np.isfinite(x) else 0.0

        lock_Q_f = _finite(lock_quality_Q)
        lock_S1_f = _finite(lock_quality_S1)
        lock_S2_f = _finite(lock_quality_S2)
        lock_S3_f = _finite(lock_quality_S3)
        structural_mass = lock_Q_f + lock_S1_f + lock_S2_f + lock_S3_f

        if structural_mass <= 0:
            structure_tier = "none"
            q_rel = s1_rel = s2_rel = 0.0
        else:
            q_rel = lock_Q_f / structural_mass
            s1_rel = lock_S1_f / structural_mass
            s2_rel = lock_S2_f / structural_mass
            if q_rel < T_Q_rel_min:
                structure_tier = "none"
            elif s1_rel < T_S1_rel_min and s2_rel < T_S2_rel_min:
                structure_tier = "level1"
            elif s1_rel >= T_S1_rel_min and s2_rel < T_S2_rel_min:
                structure_tier = "level2"
            else:
                structure_tier = "level3"

        s2_band_fraction_weight = layer_summaries.get("S2", {}).get("band_fraction", 0.0)
        none_max = s2_state_cfg.get("none_max_fraction", 1e-3)
        latent_max = s2_state_cfg.get("latent_max_fraction", 0.15)
        if s2_band_fraction_weight < none_max:
            s2_state_label = "none"
        elif s2_band_fraction_weight <= latent_max:
            s2_state_label = "latent"
        else:
            s2_state_label = "structural"

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
                "spacing_mean": float(np.mean(spacings)) if spacings.size else float("nan"),
                "spacing_std": float(np.std(spacings)) if spacings.size else float("nan"),
                "spacing_min": float(np.min(spacings)) if spacings.size else float("nan"),
                "spacing_max": float(np.max(spacings)) if spacings.size else float("nan"),
                "band_count": int(band_energies.size),
                "accepted_for_spacing": accepted_band,
                "family_match": family_match,
                "family_distance": family_distance.__dict__ if family_distance else None,
                "band_weights": band_weights,
                "band_dominant_layers": band_dominant_layers,
                "has_s2_dominant": has_s2_dominant,
                "s2_band_fraction": s2_band_fraction,
                "s3_band_fraction": s3_band_fraction,
                "has_s3_dominant": has_s3_dominant,
                "s2_state": s2_state_label,
                "s3_state": s3_state,
                "s2_total_fraction": layer_summaries.get("S2", {}).get("total_fraction"),
                "s3_total_fraction": layer_summaries.get("S3", {}).get("total_fraction"),
                "s2_band_compactness": layer_summaries.get("S2", {}).get("band_compactness"),
                "s3_band_compactness": layer_summaries.get("S3", {}).get("band_compactness"),
                "s2_outband_fraction": layer_summaries.get("S2", {}).get("outband_fraction"),
                "s3_outband_fraction": layer_summaries.get("S3", {}).get("outband_fraction"),
                "s2_highfreq_fraction": layer_summaries.get("S2", {}).get("highfreq_fraction"),
                "s3_highfreq_fraction": layer_summaries.get("S3", {}).get("highfreq_fraction"),
                "lock_quality_Q": lock_quality_Q,
                "lock_quality_S1": lock_quality_S1,
                "lock_quality_S2": lock_quality_S2,
                "structure_tier": structure_tier,
                "layers_order": [l.name for l in layer_order],
                "b_trace": sim_result["b_series"].tolist(),
                "t_trace": sim_result["times"].tolist(),
                "dt_used": sim_result.get("dt_used"),
                "R_S1_Q": config.R_S1_Q,
                "R_S2_S1": config.R_S2_S1,
                "R_S3_S2": config.R_S3_S2,
                "g_couplings": [ic.g0 for ic in config.inter_layer_couplings],
                "memory_taus": [tau for ic in config.inter_layer_couplings for k in ic.links.values() for tau in k.taus0],
                "memory_amps": [amp for ic in config.inter_layer_couplings for k in ic.links.values() for amp in k.amps0],
                "theta_internal": _serialize_theta(config),
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
    parser.add_argument("--case", type=str, default="Core3L_Hadron", help="Case name (default Core3L_Hadron).")
    parser.add_argument(
        "--engine-config",
        type=Path,
        default=Path("data/raw/config/core/engine_core3.json"),
        help="Engine configuration JSON (defines layers, integration, band window).",
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
    parser.add_argument("--n-q", type=int, default=None, help="Modes in layer Q.")
    parser.add_argument("--n-s1", type=int, default=None, help="Modes in layer S1.")
    parser.add_argument("--n-s2", type=int, default=None, help="Modes in layer S2.")
    parser.add_argument("--n-s3", type=int, default=None, help="Modes in layer S3 (optional).")
    parser.add_argument("--band-min", type=float, default=None, help="Min band energy (GeV).")
    parser.add_argument("--band-max", type=float, default=None, help="Max band energy (GeV).")
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
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Override base outputs: raw=<root>/raw, processed=<root>/processed.",
    )
    parser.add_argument(
        "--layer-states",
        type=Path,
        default=Path("data/raw/config/layer_states.yaml"),
        help="Layer thresholds config (YAML).",
    )
    parser.add_argument("--family-name", type=str, default=None, help="Predefined family name.")
    parser.add_argument("--family-config", type=Path, default=None, help="Path to family JSON config.")
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    engine_cfg = _load_engine_config(args.engine_config)

    # Override case/band/modes from engine config when provided
    if engine_cfg:
        if args.case in ("Core3L_Hadron", "CaseA_2layers", "CaseB_3layers", "CaseB_debug") or not args.case:
            args.case = engine_cfg.get("name", args.case)
        spec_layers = {l["name"]: l for l in engine_cfg.get("layers", []) if "name" in l}
        args.n_q = args.n_q if args.n_q is not None else int(spec_layers.get("Q", {}).get("n_modes", DEFAULT_N_Q))
        args.n_s1 = args.n_s1 if args.n_s1 is not None else int(
            spec_layers.get("S1", {}).get("n_modes", DEFAULT_N_INTERNAL)
        )
        args.n_s2 = args.n_s2 if args.n_s2 is not None else int(spec_layers.get("S2", {}).get("n_modes", 2))
        args.n_s3 = args.n_s3 if args.n_s3 is not None else int(spec_layers.get("S3", {}).get("n_modes", 0))
        spec_band = engine_cfg.get("spectrum", {})
        if args.band_min is None:
            args.band_min = float(spec_band.get("band_min", DEFAULT_BAND_MIN))
        if args.band_max is None:
            args.band_max = float(spec_band.get("band_max", DEFAULT_BAND_MAX))
        # integration defaults
        spec_int = engine_cfg.get("integration", {})
        dt_cfg = spec_int.get("dt")
        t_max_cfg = spec_int.get("t_max")
        sim_params_cfg = None
        if dt_cfg and t_max_cfg:
            total_steps = int(float(t_max_cfg) / float(dt_cfg))
            sim_params_cfg = {"dt": float(dt_cfg), "total_steps": total_steps}
        else:
            sim_params_cfg = None
    else:
        args.n_q = args.n_q if args.n_q is not None else DEFAULT_N_Q
        args.n_s1 = args.n_s1 if args.n_s1 is not None else DEFAULT_N_INTERNAL
        args.n_s2 = args.n_s2 if args.n_s2 is not None else 2
        args.n_s3 = args.n_s3 if args.n_s3 is not None else 0
        if args.band_min is None:
            args.band_min = DEFAULT_BAND_MIN
        if args.band_max is None:
            args.band_max = DEFAULT_BAND_MAX
        sim_params_cfg = None
    layer_cfg = _load_layer_state_config(args.layer_states)
    family_spec = None
    family_fp = None
    family_priors = None

    if args.family_config:
        family_spec = load_family_spec(args.family_config)
    elif args.family_name:
        predefined = {
            "Nucleon_like": Path("data/raw/legacy/sm_families/nucleon_like.json"),
            "Rho_like": Path("data/raw/legacy/sm_families/rho_like.json"),
            "Pion_like": Path("data/raw/legacy/sm_families/pion_like.json"),
        }
        if args.family_name in predefined and predefined[args.family_name].exists():
            family_spec = load_family_spec(predefined[args.family_name])

    if family_spec:
        family_fp = build_fingerprint(family_spec)
        family_priors = make_priors_for_family(family_spec, family_fp)
        # Override band window if provided by family
        args.band_min, args.band_max = family_spec.energy_window

    # Resolve dirs to detect existing outputs (after family is known)
    raw_dir = args.raw_dir
    processed_dir = args.processed_dir
    if args.output_root:
        raw_dir = Path(args.output_root) / "raw"
        processed_dir = Path(args.output_root)

    raw_case_dir, processed_case_dir = _case_dirs(raw_dir, processed_dir, args.case)
    if family_spec:
        raw_case_dir = raw_case_dir / family_spec.name
        processed_case_dir = processed_case_dir / family_spec.name
    else:
        raw_case_dir = raw_case_dir / "global"
        processed_case_dir = processed_case_dir / "global"
    raw_path = raw_case_dir / "study05_sweep_params.json"
    processed_path = processed_case_dir / "study05_sweep_results.json"

    if raw_path.exists() and processed_path.exists():
        msg = {
            "status": "skip",
            "reason": "existing sweep outputs detected; reuse without rerun",
            "raw_path": str(raw_path),
            "processed_path": str(processed_path),
        }
        print(json.dumps(msg, indent=2))
        return

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
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        output_root=None,
        layer_state_config=layer_cfg,
        sim_params_cfg=sim_params_cfg,
    )
    print(
        json.dumps(
            {"summary": summary, "raw_path": str(raw_path), "processed_path": str(processed_path)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
