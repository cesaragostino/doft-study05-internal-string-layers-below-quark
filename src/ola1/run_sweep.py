"""CLI helpers to run Study05 sweeps (v0.1 with memory/state-space)."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import uuid
from typing import Dict, List, Optional

import numpy as np

from ola1 import analysis, plots
from ola1.config import (
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
from ola1.families import (
    FamilyDistance,
    FamilyFingerprint,
    FamilyPriors,
    FamilySpec,
    build_fingerprint,
    compute_family_distance,
    load_family_spec,
    make_priors_for_family,
)
from ola1.simulation import SimulationParams, pick_peaks, simulate
from ola1.layers import Layer
from ola1.sweep import SimulationConfig, generate_configuration

DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_PROCESSED_DIR = Path("data/processed")
TARGET_ENERGY_GEV = 2.0
OMEGA_MAX_CUTOFF = 12.0  # rad/s cutoff for fundamental peak search
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
CHAOS_EPS = 1e-12


def _lock_entropy_norm(values: List[float]) -> float:
    vals = np.array(values, dtype=float)
    k = vals.size if vals.size > 0 else 1
    s = float(np.sum(vals))
    if s <= CHAOS_EPS:
        p = np.ones(k) / k
    else:
        p = vals / s
    return float(-np.sum(p * np.log(np.clip(p, CHAOS_EPS, 1.0))) / np.log(k)) if k > 1 else 0.0


def _lock_entropy_norm_from_weights(weights: Dict[str, float]) -> float:
    """Compute normalized lock entropy from a weight dict (Q, S1, S2)."""
    return _lock_entropy_norm([float(weights.get("Q", 0.0)), float(weights.get("S1", 0.0)), float(weights.get("S2", 0.0))])


def _lock_entropy_norm_qs1s2(vec: List[float]) -> float:
    """Compute lock entropy using only Q, S1, S2 components from a vector that may include more layers."""
    if not vec:
        return 0.0
    trimmed = vec[:3]  # assume order Q, S1, S2 (ignore deeper layers for entropy)
    return _lock_entropy_norm(trimmed)


def _block_tier_from_weights(weights: Dict[str, float], min_fraction: float = 0.05) -> str:
    q = max(float(weights.get("Q", 0.0)), 0.0)
    s1 = max(float(weights.get("S1", 0.0)), 0.0)
    s2 = max(float(weights.get("S2", 0.0)), 0.0)
    total = q + s1 + s2
    if total <= CHAOS_EPS:
        return "none"
    if (s2 / total) > min_fraction:
        return "level2"
    if (s1 / total) > min_fraction:
        return "level1"
    return "none"


def _mixture_entropy_norm(values: List[float], bins: int = 30) -> float:
    if not values:
        return float("nan")
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0))
    total = hist.sum()
    if total <= 0:
        return float("nan")
    p = hist / total
    return float(-np.sum(p * np.log(np.clip(p, CHAOS_EPS, 1.0))) / np.log(bins))


def _structure_mix_entropy_norm(tiers: List[str]) -> float:
    if not tiers:
        return float("nan")
    unique, counts = np.unique(tiers, return_counts=True)
    k = len(p := counts / counts.sum())
    if k <= 1:
        return 0.0
    return float(-np.sum(p * np.log(np.clip(p, CHAOS_EPS, 1.0))) / np.log(k))


def _permutation_entropy(series: List[float], m: int = 5, tau: int = 1) -> float | None:
    x = np.asarray(series, dtype=float)
    T = x.size
    if T < m * tau + 1:
        return None
    patterns = {}
    for t in range(T - (m - 1) * tau):
        window = x[t : t + m * tau : tau]
        order = tuple(np.argsort(window, kind="stable"))
        patterns[order] = patterns.get(order, 0) + 1
    total = sum(patterns.values())
    if total == 0:
        return None
    probs = np.array(list(patterns.values()), dtype=float) / total
    return float(-np.sum(probs * np.log(np.clip(probs, CHAOS_EPS, 1.0))) / np.log(math.factorial(m)))


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


def _select_peak_and_interp(
    mag: np.ndarray,
    delta_f: float | None,
    omega_max_cutoff: float = OMEGA_MAX_CUTOFF,
    frac_of_max: float = 0.20,
    snr_min: float = 5.0,
):
    """Select fundamental peak and interpolate: returns (f_ref, omega_ref, peak_k, peak_delta, mag_km1, mag_k, mag_kp1)."""
    if mag is None or delta_f is None or not np.isfinite(delta_f) or delta_f <= 0:
        return (None, None, None, None, None, None, None)
    power = np.array(mag, dtype=float)
    n = power.size
    if n < 2:
        return (None, None, None, None, None, None, None)
    freqs = np.arange(n, dtype=float) * float(delta_f)
    mask_low = (freqs > 0.0) & (freqs <= omega_max_cutoff / (2 * np.pi) * (2 * np.pi))  # keep in omega units but with same cutoff
    idx_candidates = np.where(mask_low)[0]
    if idx_candidates.size == 0:
        idx_candidates = np.where(freqs > 0.0)[0]
    if idx_candidates.size == 0:
        return (None, None, None, None, None, None, None)
    mags_low = power[idx_candidates]
    max_low = float(np.max(mags_low)) if mags_low.size else 0.0
    median_low = float(np.median(mags_low[1:])) if mags_low.size > 1 else max_low
    # find first peak that passes both thresholds
    k_peak_local = None
    for k in idx_candidates:
        m = power[k]
        if max_low > 0 and m < frac_of_max * max_low:
            continue
        if median_low > 0 and (m / median_low) < snr_min:
            continue
        if k == 0:
            continue
        k_peak_local = k
        break
    if k_peak_local is None:
        # fallback to max in band (skip dc)
        k_peak_local = int(idx_candidates[int(np.argmax(mags_low))])
        if k_peak_local == 0 and idx_candidates.size > 1:
            k_peak_local = int(idx_candidates[1])
    # interpolation
    if k_peak_local <= 0 or k_peak_local >= n - 1:
        f_ref = float(k_peak_local * delta_f)
        omega_ref = 2 * np.pi * f_ref
        return (f_ref, omega_ref, int(k_peak_local), 0.0, None, float(power[k_peak_local]), None)
    m_km1 = float(power[k_peak_local - 1])
    m_k = float(power[k_peak_local])
    m_kp1 = float(power[k_peak_local + 1])
    denom = m_km1 - 2 * m_k + m_kp1
    delta = 0.0
    if np.isfinite(denom) and abs(denom) > 1e-12:
        delta = 0.5 * (m_km1 - m_kp1) / denom
        delta = float(np.clip(delta, -0.5, 0.5))
    f_ref = float((k_peak_local + delta) * delta_f)
    omega_ref = 2 * np.pi * f_ref
    return (f_ref, omega_ref, int(k_peak_local), delta, m_km1, m_k, m_kp1)


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
    debug_traces: int = 0,
    memory_cfg: Optional[Dict] = None,
    adaptive_cfg: Optional[Dict] = None,
    partial_flush_every: int = 0,
    engine_config_path: Optional[str] = None,
    engine_config_hash: Optional[str] = None,
    resume: bool = False,
    stop_file: Optional[str] = None,
    compute_entropy: bool = False,
):
    peak_selector_frac = 0.20
    peak_selector_frac_struct = 0.08
    peak_selector_snr_min = 5.0
    rng = np.random.default_rng(seed)
    run_session_id = uuid.uuid4().hex
    session_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    flatten = output_root is not None
    if output_root:
        raw_dir = Path(output_root) / "raw"
        processed_dir = Path(output_root)
    raw_case_dir, processed_case_dir = _case_dirs(raw_dir, processed_dir, case) if not flatten else (raw_dir, processed_dir)
    if not flatten:
        if family_spec:
            raw_case_dir = raw_case_dir / family_spec.name
            processed_case_dir = processed_case_dir / family_spec.name
        else:
            raw_case_dir = raw_case_dir / "global"
            processed_case_dir = processed_case_dir / "global"
        _ensure_dirs(raw_case_dir, processed_case_dir)
    else:
        _ensure_dirs(raw_case_dir, processed_case_dir)
    debug_dir = processed_case_dir / "debug"
    if debug_traces > 0:
        debug_dir.mkdir(parents=True, exist_ok=True)
    n_debug = min(debug_traces, runs)
    debug_indices: set[int] = set()
    if n_debug > 0:
        dbg_rng = np.random.default_rng(seed)
        debug_indices = set(dbg_rng.choice(runs, size=n_debug, replace=False).tolist())
    sim_params = SimulationParams(**sim_params_cfg) if sim_params_cfg else SimulationParams()

    partial_dir = processed_case_dir / "partial"
    partial_runs_path = None
    if partial_flush_every and partial_flush_every > 0:
        partial_dir.mkdir(parents=True, exist_ok=True)
        partial_runs_path = partial_dir / "runs_partial.jsonl"
        if partial_runs_path.exists() and not resume:
            partial_runs_path.unlink()  # start fresh for this sweep

    layer_state_config = layer_state_config or {}
    lock_thresholds = layer_state_config.get("lock_thresholds", {})
    s2_state_cfg = layer_state_config.get("s2_state", {})

    n_modes_min = n_q + n_s1 + n_s2 + n_s3
    if max_complexity > 0 and max_complexity <= n_modes_min:
        print(
            f"[run_sweep] WARNING: max_complexity={max_complexity} <= n_modes_total={n_modes_min}; memory terms will be forced to zero.",
            flush=True,
        )

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

    saved_since_print = 0
    partial_buffer: List[Dict] = []

    start_run_idx = 0
    if resume and partial_runs_path and partial_runs_path.exists():
        try:
            for line in partial_runs_path.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                run_outputs.append(rec)
                rid = rec.get("run_id")
                if isinstance(rid, (int, float)):
                    start_run_idx = max(start_run_idx, int(rid) + 1)
                if rec.get("status") == "ok":
                    band_counts.append(int(rec.get("band_count", 0)))
                    if rec.get("accepted_for_spacing"):
                        spacing_vals = np.array(rec.get("band_spacing_gev", []))
                        if spacing_vals.size:
                            spacings_all.append(spacing_vals)
                            accepted_runs_for_spacing += 1
                elif rec.get("status") == "rejected":
                    rejected += 1
                elif rec.get("status") == "unstable":
                    unstable += 1
            if run_outputs:
                # reuse session id to keep lineage; session_tag can stay new
                run_session_id = run_outputs[0].get("run_session_id", run_session_id)
        except Exception:
            run_outputs = []
            start_run_idx = 0

    current_mass_proxies: Dict[str, float | None] = {"M1": None, "M2": None, "M3": None, "omega_ref": None, "mass_sim_gev": None}

    # optional hbar_sim preload for live mass_sim logging
    hbar_sim_live = None
    for cand in [
        processed_dir / "hbar_sim_calibration.json",
        processed_dir.parent / "hbar_sim_calibration.json",
        processed_dir.parent / "ola1" / "hbar_sim_calibration.json",
        processed_dir.parent / "ola1-chaos" / "hbar_sim_calibration.json",
        Path("hbar_sim_calibration.json"),
    ]:
        if cand and cand.exists():
            try:
                data_h = json.loads(cand.read_text())
                hbar_sim_live = float(data_h.get("hbar_sim"))
                break
            except Exception:
                hbar_sim_live = None

    def _append_partial(record: Dict, flush_now: bool = False):
        nonlocal saved_since_print, partial_buffer
        if partial_runs_path and partial_flush_every > 0:
            partial_buffer.append(record)
            if flush_now or len(partial_buffer) >= partial_flush_every:
                with partial_runs_path.open("a") as pf:
                    for rec in partial_buffer:
                        pf.write(json.dumps(rec) + "\n")
                saved_since_print += len(partial_buffer)
                partial_buffer = []

    def _log_run_status(run_idx: int, status: str, e_internal: float | None = None):
        try:
            if e_internal is None or not math.isfinite(float(e_internal)):
                e_val = "nan"
            else:
                e_val = f"{float(e_internal):.6g}"
        except Exception:
            e_val = "nan"
        try:
            m1 = "nan"
            m2 = "nan"
            m3 = "nan"
            omg = "nan"
            m_sim = "nan"
            val_m1 = current_mass_proxies.get("M1")
            val_m2 = current_mass_proxies.get("M2")
            val_m3 = current_mass_proxies.get("M3")
            val_omega = current_mass_proxies.get("omega_ref")
            val_msim = current_mass_proxies.get("mass_sim_gev")
            if val_m1 is not None and math.isfinite(float(val_m1)):
                m1 = f"{float(val_m1):.6g}"
            if val_m2 is not None and math.isfinite(float(val_m2)):
                m2 = f"{float(val_m2):.6g}"
            if val_m3 is not None and math.isfinite(float(val_m3)):
                m3 = f"{float(val_m3):.6g}"
            if val_omega is not None and math.isfinite(float(val_omega)):
                omg = f"{float(val_omega):.6g}"
            if val_msim is not None and math.isfinite(float(val_msim)):
                m_sim = f"{float(val_msim):.6g}"
        except Exception:
            m1 = "nan"
            m2 = "nan"
            m3 = "nan"
            omg = "nan"
            m_sim = "nan"
        print(
            f"[run_sweep] run {run_idx + 1}/{runs} status={status} E_internal={e_val} omega_ref={omg} mass_sim={m_sim} M1={m1} M2={m2} M3={m3}",
            flush=True,
        )

    for run_idx in range(start_run_idx, runs):
        current_mass_proxies = {"M1": None, "M2": None, "M3": None, "omega_ref": None, "mass_sim_gev": None}
        if stop_file and Path(stop_file).exists():
            print(f"[run_sweep] stop-file detected at run {run_idx}/{runs}. Stopping gracefully.", flush=True)
            try:
                Path(stop_file).unlink()
            except Exception:
                pass
            break
        if saved_since_print:
            print(f"[run_sweep] run {run_idx + 1}/{runs} (partial_saved={saved_since_print})", flush=True)
            saved_since_print = 0
        else:
            print(f"[run_sweep] run {run_idx + 1}/{runs}", flush=True)
        config, gen_meta = generate_configuration(
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
            run_outputs.append(
                {
                    "run_session_id": run_session_id,
                    "engine_config_path": engine_config_path,
                    "engine_config_hash": engine_config_hash,
                    "run_id": run_idx,
                    "status": "rejected",
                    "reason": "complexity_exceeded",
                    "max_complexity": max_complexity,
                    "complexity_last": gen_meta.get("last_complexity"),
                    "n_modes_last": gen_meta.get("last_n_modes"),
                    "n_memory_terms_last": gen_meta.get("last_memory_terms"),
                    "complexity_estimated": gen_meta.get("last_complexity"),
                }
            )
            _append_partial(run_outputs[-1])
            _log_run_status(run_idx, "rejected", None)
            continue

        run_inputs.append(_serialize_run_config(config))

        debug_enabled = run_idx in debug_indices
        try:
            sim_result = simulate(
                modes=config.modes,
                intra_couplings=config.intra_layer_couplings,
                inter_couplings=config.inter_layer_couplings,
                sim_params=sim_params,
                rng=rng,
                debug=debug_enabled,
                memory_cfg=memory_cfg,
                adaptive_cfg=adaptive_cfg,
            )
        except FloatingPointError:
            unstable += 1
            run_outputs.append(
                {
                    "run_session_id": run_session_id,
                    "engine_config_path": engine_config_path,
                    "engine_config_hash": engine_config_hash,
                    "run_id": run_idx,
                    "status": "unstable",
                    "n_modes": len(config.modes),
                    "n_memory_terms": None,
                    "memory_taus": [],
                    "memory_amps": [],
                    "memory_enabled_effective": False,
                    "memory_abort_stage": "simulate_fpe",
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
            _append_partial(run_outputs[-1])
            _log_run_status(run_idx, "unstable", None)
            continue
        spectrum = sim_result["spectrum"]
        delta_omega = spectrum.get("delta_omega")
        delta_f = spectrum.get("delta_f")
        power_total = spectrum.get("power_total")
        per_mode = spectrum.get("per_mode")
        # identity channel: Q layer if available
        q_indices = [i for i, m in enumerate(config.modes) if m.layer == Layer.Q]
        if per_mode is not None and len(q_indices) > 0:
            try:
                mag_q = np.sum(per_mode[:, q_indices], axis=1)
            except Exception:
                mag_q = power_total
        else:
            mag_q = power_total
        f_ref, omega_ref_interp, fft_k_peak, fft_peak_delta, fft_mag_km1, fft_mag_k, fft_mag_kp1 = _select_peak_and_interp(
            mag_q,
            delta_f,
            omega_max_cutoff=OMEGA_MAX_CUTOFF,
            frac_of_max=peak_selector_frac,
            snr_min=peak_selector_snr_min,
        )
        peak_selector_mode = "default"
        omega_peaks, weights_peaks, peak_powers = pick_peaks(
            spectrum=spectrum, modes=config.modes, layer_to_idx=sim_result["layer_to_idx"], sim_params=sim_params
        )
        peaks_raw_count = len(omega_peaks)
        energies_gev, scale = _rescale_energies(omega_peaks, target=TARGET_ENERGY_GEV)

        band_mask = (energies_gev >= band_min) & (energies_gev <= band_max)
        band_energies = energies_gev[band_mask]
        peaks_kept_count = int(band_energies.size)
        band_counts.append(int(band_energies.size))

        band_weights = [w for keep, w in zip(band_mask, weights_peaks) if keep]
        band_powers = [p for keep, p in zip(band_mask, peak_powers) if keep]
        bands_all = []
        for e, pwr, w in zip(band_energies.tolist(), band_powers, band_weights):
            bands_all.append({"energy": e, "power": pwr, "weights": w})
        band_dominant_layers = []
        for w in band_weights:
            if not w:
                band_dominant_layers.append(None)
                continue
            layer_max = max(w.items(), key=lambda kv: kv[1])
            band_dominant_layers.append({"layer": layer_max[0], "weight": layer_max[1]})

        # structural subset: filter by relative power, cluster by proximity, take top-N
        structural_energies = []
        structural_dom_layers: List[str] = []
        structural_flags: List[str] = []
        power_capture = 0.0
        if band_energies.size > 0 and band_powers:
            max_power = max(band_powers)
            rel_floor = 0.03 * max_power
            candidates = [(e, pwr) for e, pwr in zip(band_energies.tolist(), band_powers) if pwr >= rel_floor]
            delta_min = 0.03
            candidates.sort(key=lambda x: x[0])
            clusters = []
            for e, pwr in candidates:
                if not clusters or abs(e - clusters[-1][-1][0]) >= delta_min:
                    clusters.append([(e, pwr)])
                else:
                    clusters[-1].append((e, pwr))
            structural_candidates = []
            for cl in clusters:
                cl.sort(key=lambda x: x[1], reverse=True)
                structural_candidates.append(cl[0])
            structural_candidates.sort(key=lambda x: x[1], reverse=True)
            cap = sim_params.structural_peak_cap
            if len(structural_candidates) > cap:
                structural_flags.append("structural_band_cap_hit")
            selected = structural_candidates[: min(len(structural_candidates), cap)]
            structural_energies = [e for e, _ in selected]
            power_capture = sum(p for _, p in structural_candidates[: min(len(structural_candidates), cap)]) / max(
                sum(band_powers), 1e-12
            )
            if power_capture < 0.5:
                structural_flags.append("structural_subset_low_capture")
            # dominant layer for structural peaks
            for e, _ in selected:
                try:
                    idx = band_energies.tolist().index(e)
                except ValueError:
                    structural_dom_layers.append(None)
                    continue
                dom = band_dominant_layers[idx] if idx < len(band_dominant_layers) else None
                structural_dom_layers.append(dom["layer"] if dom else None)
        structural_complex = (
            "structural_band_cap_hit" in structural_flags or "structural_subset_low_capture" in structural_flags
        )
        if structural_complex and peak_selector_frac_struct < peak_selector_frac:
            (
                f_ref,
                omega_ref_interp,
                fft_k_peak,
                fft_peak_delta,
                fft_mag_km1,
                fft_mag_k,
                fft_mag_kp1,
            ) = _select_peak_and_interp(
                mag_q,
                delta_f,
                omega_max_cutoff=OMEGA_MAX_CUTOFF,
                frac_of_max=peak_selector_frac_struct,
                snr_min=peak_selector_snr_min,
            )
            peak_selector_mode = "structural_low_frac"
        band_dom_counts_total: Dict[str, int] = {}
        for item in band_dominant_layers:
            if item and item.get("layer"):
                band_dom_counts_total[item["layer"]] = band_dom_counts_total.get(item["layer"], 0) + 1
        band_dom_counts_struct: Dict[str, int] = {}
        for layer in structural_dom_layers:
            if layer:
                band_dom_counts_struct[layer] = band_dom_counts_struct.get(layer, 0) + 1
        s2_band_fraction = (
            sum(1 for item in band_dominant_layers if item and item["layer"] == "S2") / band_energies.size
            if band_energies.size > 0
            else 0.0
        )
        s2_band_fraction_struct = (
            sum(1 for item in structural_dom_layers if item == "S2") / len(structural_dom_layers)
            if structural_dom_layers
            else 0.0
        )
        has_s2_dominant = s2_band_fraction > 0.0
        s3_band_fraction = (
            sum(1 for item in band_dominant_layers if item and item["layer"] == "S3") / band_energies.size
            if band_energies.size > 0
            else 0.0
        )
        # flag overflow but don't reject
        if band_energies.size > sim_params.max_peaks:
            structural_flags.append("band_overflow")

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

        debug_trace_path = None
        if debug_enabled and "debug_traces" in sim_result:
            debug_trace_path = debug_dir / f"run_{run_idx:04d}_traces.npz"
            dbg = sim_result["debug_traces"]
            inputs_arr = dbg.get("inputs")
            tau_eff_obj = np.array(dbg.get("tau_eff", []), dtype=object)
            z_arr = dbg.get("z")
            np.savez_compressed(debug_trace_path, inputs=inputs_arr, tau_eff=tau_eff_obj, z=z_arr)

        mem_taus_flat = [tau for ic in config.inter_layer_couplings for k in ic.links.values() for tau in k.taus0]
        mem_amps_flat = [amp for ic in config.inter_layer_couplings for k in ic.links.values() for amp in k.amps0]
        mem_terms_by_layer: Dict[str, int] = {}
        for ic in config.inter_layer_couplings:
            total_terms = sum(len(k.taus0) for k in ic.links.values())
            mem_terms_by_layer[ic.deep_layer.name] = mem_terms_by_layer.get(ic.deep_layer.name, 0) + total_terms
        memory_enabled_effective = bool(mem_taus_flat)
        expected_mem_terms = 0
        if memory_cfg and memory_cfg.get("modes_per_layer"):
            try:
                expected_mem_terms = sum(int(v) for v in memory_cfg.get("modes_per_layer", {}).values())
            except Exception:
                expected_mem_terms = 0
        mem_terms_mismatch = (mem_terms_by_layer and sum(mem_terms_by_layer.values()) != config.memory_terms)
        if mem_terms_mismatch:
            print(
                f"[run_sweep] WARNING: n_memory_terms({config.memory_terms}) != sum(mem_terms_by_layer)({sum(mem_terms_by_layer.values())}) for run {run_idx}",
                flush=True,
            )
        mem_issue = (
            memory_cfg
            and memory_cfg.get("enabled", False)
            and expected_mem_terms > 0
            and not mem_taus_flat
        )
        if mem_issue:
            msg = (
                f"[run_sweep] ERROR: memory.enabled=True and modes_per_layer>0 but no memory terms were instantiated (run {run_idx}); "
                "possible complexity cap or generation bug. Marking run as rejected."
            )
            print(msg, flush=True)
            rejected += 1
            run_outputs.append(
                {
                    "run_session_id": run_session_id,
                    "engine_config_path": engine_config_path,
                    "engine_config_hash": engine_config_hash,
                    "run_id": run_idx,
                    "status": "rejected",
                    "reason": "memory_not_applied",
                    "max_complexity": max_complexity,
                    "complexity": config.complexity,
                    "n_modes": len(config.modes),
                    "expected_memory_terms": expected_mem_terms,
                    "n_memory_terms": config.memory_terms,
                    "memory_taus": mem_taus_flat,
                    "memory_amps": mem_amps_flat,
                    "memory_enabled_effective": False,
                    "entropy_status": "skipped",
                    "entropy_reason": "compute_entropy_disabled" if not compute_entropy else "not_implemented",
                    "entropy_chaos": None,
                    "lyapunov_local": None,
                    "lyapunov_mean": None,
                    "phase_compactness": None,
                    "phase_occupancy": None,
                    "entropy_flags": None,
                }
            )
            _append_partial(run_outputs[-1])
            continue
        # derive auxiliary metrics for interpretability
        layer_energy_fraction = {
            "Q": lock_quality_Q,
            "S1": lock_quality_S1,
            "S2": lock_quality_S2,
        }
        try:
            import math as _math

            vals = [v for v in layer_energy_fraction.values() if v is not None and v > 0]
            if vals:
                p = np.array(vals, dtype=float)
                p = p / max(np.sum(p), 1e-12)
                participation_entropy = float(-np.sum(p * np.log(np.clip(p, 1e-12, 1))))
                min_layer_fraction = float(np.min(p))
            else:
                participation_entropy = None
                min_layer_fraction = None
        except Exception:
            participation_entropy = None
            min_layer_fraction = None

        s2_state_lock = s2_state_label
        # band-based state
        if s2_band_fraction_struct < none_max:
            s2_state_bands = "none"
        elif s2_band_fraction_struct <= latent_max:
            s2_state_bands = "latent"
        else:
            s2_state_bands = "structural"

        # Entropy/caos
        entropy_chaos = None
        if compute_entropy:
            block_entropies: List[float] = []
            q_values: List[float] = []
            block_tiers: List[str] = []
            min_layer_fraction_thr = float(s2_state_cfg.get("min_layer_fraction", 0.05))
            for w in band_weights:
                if not isinstance(w, dict):
                    continue
                block_entropies.append(_lock_entropy_norm_from_weights(w))
                q_values.append(float(w.get("Q", 0.0)))
                block_tiers.append(_block_tier_from_weights(w, min_fraction=min_layer_fraction_thr))

            # Global structural chaos: PE on lock_quality_S1 per tick (fraction of S1 energy)
            lock_s1_series: List[float] = []
            energies_series = sim_result.get("energies_series")
            if energies_series is not None and np.size(energies_series) > 0:
                for vec in energies_series:
                    e_q = float(vec[0]) if len(vec) > 0 else 0.0
                    e_s1 = float(vec[1]) if len(vec) > 1 else 0.0
                    e_s2 = float(vec[2]) if len(vec) > 2 else 0.0
                    total = e_q + e_s1 + e_s2
                    if total > CHAOS_EPS:
                        lock_s1_series.append(e_s1 / total)
                    else:
                        lock_s1_series.append(1.0 / 3.0)
            chaos_mode = "dynamic" if len(lock_s1_series) >= 6 else "ensemble"  # m=5,tau=1 ⇒ need ≥6
            PE_tick_norm = _permutation_entropy(lock_s1_series, m=5, tau=1) if chaos_mode == "dynamic" else None
            fraction_structured = (
                float(sum(1 for t in block_tiers if t != "none")) / len(block_tiers) if block_tiers else None
            )
            entropy_chaos = {
                "eps": CHAOS_EPS,
                "mean_H_lock_norm": float(np.mean(block_entropies)) if block_entropies else None,
                "std_H_lock_norm": float(np.std(block_entropies)) if block_entropies else None,
                "p90_H_lock_norm": float(np.percentile(block_entropies, 90)) if block_entropies else None,
                "fraction_structured": fraction_structured,
                "mean_Q": float(np.mean(q_values)) if q_values else None,
                "std_Q": float(np.std(q_values)) if q_values else None,
                "mixture_entropy_blocks_norm": _mixture_entropy_norm(block_entropies) if block_entropies else None,
                "structure_mix_norm": _structure_mix_entropy_norm(block_tiers) if block_tiers else None,
                "chaos_mode": chaos_mode,
                "PE_tick_norm": PE_tick_norm,
                "has_ticks": bool(lock_s1_series),
                "T_ticks": len(lock_s1_series) if chaos_mode == "dynamic" else None,
                "lock_S1_series": lock_s1_series if lock_s1_series else None,
                "notes": "PE sobre lock_quality_S1 por tick (fracción S1 global); sin serie → sólo métricas instantáneas/ensemble.",
            }
            entropy_status = "ok"
            entropy_reason = None
        else:
            entropy_status = "skipped"
            entropy_reason = "compute_entropy_disabled"
            entropy_chaos = None

        e_internal = sim_result.get("E_internal")

        # --- Lock mass/energy proxies (all in internal units) ---
        # Inputs
        H_layers = participation_entropy
        H_layers_max = math.log(3.0)
        band_count_run = int(band_energies.size)
        omega_peaks_raw = omega_peaks.tolist() if omega_peaks is not None else []
        omega_ref = omega_ref_interp if omega_ref_interp is not None else (float(min(omega_peaks_raw)) if omega_peaks_raw else None)

        # Layer volume proxy
        V_layers = float(math.exp(H_layers)) if H_layers is not None else None
        V_lock = (V_layers * band_count_run) if (V_layers is not None) else None

        # Static density
        D_stat = None
        if H_layers is not None and H_layers_max > 0:
            D_stat = 1.0 - (H_layers / H_layers_max)
            D_stat = max(0.0, min(1.0, D_stat))

        # Dynamic density from entropy_chaos over lock_S1_series
        D_dyn = None
        rho_lock = None
        if entropy_chaos:
            mh = entropy_chaos.get("mean_H_lock_norm")
            pe = entropy_chaos.get("PE_tick_norm")
            if mh is not None and pe is not None:
                try:
                    D_dyn_val = (1.0 - float(mh)) * (1.0 - float(pe))
                    D_dyn = max(0.0, min(1.0, D_dyn_val))
                except Exception:
                    D_dyn = None
        if D_stat is not None and D_dyn is not None:
            rho_lock = D_stat * D_dyn

        # Mass proxies
        M_spec = omega_ref
        M1 = None
        M2 = None
        M3 = None

        if V_lock is not None and D_stat is not None:
            M1 = V_lock * D_stat
        if omega_ref is not None and V_lock is not None and D_stat is not None:
            M2 = omega_ref * V_lock * D_stat
        if omega_ref is not None and V_lock is not None and rho_lock is not None:
            M3 = omega_ref * V_lock * rho_lock
        mass_sim_gev = None
        if hbar_sim_live is not None and omega_ref is not None:
            try:
                mass_sim_gev = hbar_sim_live * omega_ref
            except Exception:
                mass_sim_gev = None

        # snapshot for console logging
        current_mass_proxies["M1"] = M1
        current_mass_proxies["M2"] = M2
        current_mass_proxies["M3"] = M3
        current_mass_proxies["omega_ref"] = omega_ref
        current_mass_proxies["mass_sim_gev"] = mass_sim_gev

        run_record = {
            "run_session_id": run_session_id,
            "engine_config_path": engine_config_path,
            "engine_config_hash": engine_config_hash,
            "run_id": run_idx,
            "status": "ok",
            "n_modes": len(config.modes),
            "n_memory_terms": config.memory_terms,
            "expected_memory_terms": expected_mem_terms,
            "memory_terms_by_layer": mem_terms_by_layer,
            "memory_terms_mismatch": mem_terms_mismatch,
            "memory_enabled_effective": memory_enabled_effective,
            "max_complexity": max_complexity,
            "complexity": config.complexity,
            "energy_scale": scale,
            "peaks_raw_count": peaks_raw_count,
            "peaks_kept_count": peaks_kept_count,
            "energies_gev": energies_gev.tolist(),
            "band_energies_gev": band_energies.tolist(),
            "band_spacing_gev": spacings.tolist(),
            "spacing_mean": float(np.mean(spacings)) if spacings.size else float("nan"),
            "spacing_std": float(np.std(spacings)) if spacings.size else float("nan"),
            "spacing_min": float(np.min(spacings)) if spacings.size else float("nan"),
            "spacing_max": float(np.max(spacings)) if spacings.size else float("nan"),
            "band_count": int(band_energies.size),
            "band_structural_energies_gev": structural_energies,
            "band_count_structural": len(structural_energies),
            "band_structural_cap_hit": "structural_band_cap_hit" in structural_flags,
            "peak_cap": sim_params.structural_peak_cap,
            "peak_cap_hit": "structural_band_cap_hit" in structural_flags,
            "peaks_raw_count": peaks_raw_count,
            "peaks_kept_count": peaks_kept_count,
            "bands_all_json": json.dumps(bands_all),
            "bands_structural_json": json.dumps([{"energy": e} for e in structural_energies]),
            "band_power_capture": power_capture,
            "band_flags": structural_flags,
            "band_dom_counts_total": band_dom_counts_total,
            "band_dom_counts_structural": band_dom_counts_struct,
            "accepted_for_spacing": accepted_band,
            "family_match": family_match,
            "family_distance": family_distance.__dict__ if family_distance else None,
            "band_weights": band_weights,
            "band_dominant_layers": band_dominant_layers,
            "s2_band_fraction_total": s2_band_fraction,
            "has_s2_dominant": has_s2_dominant,
            "s2_band_fraction": s2_band_fraction,
            "s3_band_fraction": s3_band_fraction,
            "has_s3_dominant": has_s3_dominant,
            "s2_state": s2_state_label,
            "s2_state_lock": s2_state_lock,
            "s2_state_bands": s2_state_bands,
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
            "layer_energy_fraction": layer_energy_fraction,
            "participation_entropy": participation_entropy,
            "min_layer_fraction": min_layer_fraction,
            "structure_tier": structure_tier,
            "layers_order": [l.name for l in layer_order],
            "b_trace": sim_result["b_series"].tolist(),
            "t_trace": sim_result["times"].tolist(),
            "dt_used": sim_result.get("dt_used"),
            "E_internal": e_internal,
            "omega_peaks": omega_peaks_raw,
            "f_ref": f_ref,
            "omega_ref": omega_ref,
            "omega_ref_interp": omega_ref_interp,
            "delta_omega": delta_omega,
            "delta_f": delta_f,
            "dt_sample_fft": sim_result.get("dt_used") * sim_params.sample_stride if sim_result.get("dt_used") else None,
            "n_samples_fft": spectrum.get("n_samples"),
            "n_samples_fft_padded": spectrum.get("n_padded"),
            "T_obs_fft": spectrum.get("T_obs"),
            "fft_peak_index": fft_k_peak,
            "fft_peak_delta": fft_peak_delta,
            "fft_peak_mag_km1": fft_mag_km1,
            "fft_peak_mag_k": fft_mag_k,
            "fft_peak_mag_kp1": fft_mag_kp1,
            "V_layers": V_layers,
            "V_lock": V_lock,
            "D_stat": D_stat,
            "D_dyn": D_dyn,
            "rho_lock": rho_lock,
            "M_spec": M_spec,
            "M1": M1,
            "M2": M2,
            "M3": M3,
            "mass_sim_gev": mass_sim_gev,
            "entropy_status": entropy_status,
            "entropy_reason": entropy_reason,
            "lyapunov_local": None,
            "lyapunov_mean": None,
            "phase_compactness": None,
            "phase_occupancy": None,
            "entropy_flags": None,
            "entropy_chaos": entropy_chaos,
            "R_S1_Q": config.R_S1_Q,
            "R_S2_S1": config.R_S2_S1,
            "R_S3_S2": config.R_S3_S2,
            "g_couplings": [ic.g0 for ic in config.inter_layer_couplings],
            "memory_taus": mem_taus_flat,
            "memory_amps": mem_amps_flat,
            "theta_internal": _serialize_theta(config),
            "debug_trace_path": str(debug_trace_path) if debug_trace_path else None,
            "adaptive_lock": sim_result.get("adaptive_lock"),
        }
        run_outputs.append(run_record)
        flush_now = ((run_idx + 1) % partial_flush_every == 0) or (run_idx + 1 == runs)
        _append_partial(run_record, flush_now=flush_now)
        _log_run_status(run_idx, "ok", e_internal)

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
        "run_session_id": run_session_id,
        "session_tag": session_tag,
        "engine_config_path": engine_config_path,
        "engine_config_hash": engine_config_hash,
        "debug_trace_run_ids": sorted(debug_indices),
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

    raw_payload = {
        "seed": seed,
        "max_complexity": max_complexity,
        "engine_config_path": engine_config_path,
        "engine_config_hash": engine_config_hash,
        "run_session_id": run_session_id,
        "session_tag": session_tag,
        "inputs": run_inputs,
    }
    processed_payload = {
        "summary": summary,
        "runs": run_outputs,
    }

    suffix = f"{case}_" if flatten else ""
    raw_path = raw_case_dir / f"{suffix}study05_sweep_params.json"
    processed_path = processed_case_dir / f"{suffix}study05_sweep_results.json"

    raw_path.write_text(json.dumps(raw_payload, indent=2))
    processed_path.write_text(json.dumps(processed_payload, indent=2))
    # Also write timestamped copies to avoid collisions between sweeps
    raw_ts_path = raw_path.with_name(f"{raw_path.stem}_{session_tag}{raw_path.suffix}")
    processed_ts_path = processed_path.with_name(f"{processed_path.stem}_{session_tag}{processed_path.suffix}")
    raw_ts_path.write_text(json.dumps(raw_payload, indent=2))
    processed_ts_path.write_text(json.dumps(processed_payload, indent=2))

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
        default=Path("data/raw/engine_core3.json"),
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
        "--max-complexity",
        type=int,
        default=DEFAULT_MAX_COMPLEXITY,
        help="Maximum complexity (C) allowed per run. If <=0, no limit is enforced.",
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
        "--debug-traces",
        type=int,
        default=0,
        help="Guardar trazas detalladas para N corridas (inputs, tau_eff, z).",
    )
    parser.add_argument(
        "--layer-states",
        type=Path,
        default=Path("data/raw/layer_states.yaml"),
        help="Layer thresholds config (YAML).",
    )
    parser.add_argument("--family-name", type=str, default=None, help="Predefined family name.")
    parser.add_argument("--family-config", type=Path, default=None, help="Path to family JSON config.")
    parser.add_argument(
        "--partial-flush-every",
        type=int,
        default=0,
        help="If >0, append each run record to partial/runs_partial.jsonl (every run if set).",
    )
    parser.add_argument("--resume", action="store_true", help="Resume from existing partial/runs_partial.jsonl if present.")
    parser.add_argument(
        "--stop-file",
        type=str,
        default=None,
        help="If set, sweep stops gracefully when this file appears (checked every run).",
    )
    parser.add_argument(
        "--compute-entropy",
        action="store_true",
        default=True,
        help="Calcular métricas de entropía/caos en cada corrida (activado por defecto, pasar --no-compute-entropy si se quiere desactivar).",
    )
    parser.add_argument(
        "--no-compute-entropy",
        action="store_false",
        dest="compute_entropy",
        help="Desactivar métricas de entropía/caos.",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    engine_cfg = _load_engine_config(args.engine_config)
    engine_cfg_path = str(args.engine_config) if args.engine_config else None
    engine_cfg_hash = None
    if args.engine_config and args.engine_config.exists():
        import hashlib

        engine_cfg_hash = hashlib.sha256(args.engine_config.read_bytes()).hexdigest()

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
        if engine_cfg.get("max_complexity") is not None and args.max_complexity == DEFAULT_MAX_COMPLEXITY:
            try:
                args.max_complexity = int(engine_cfg.get("max_complexity"))
            except Exception:
                pass
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
        # optional spectrum overrides (e.g., structural peak cap)
        if spec_band.get("structural_peak_cap") is not None:
            if sim_params_cfg is None:
                sim_params_cfg = {}
            try:
                sim_params_cfg["structural_peak_cap"] = int(spec_band.get("structural_peak_cap"))
            except Exception:
                pass
        memory_cfg = engine_cfg.get("memory")
        adaptive_cfg = engine_cfg.get("adaptive_lock")
        peak_selector_cfg = spec_band.get("peak_selector", {})
        peak_selector_frac = float(peak_selector_cfg.get("frac_of_max", 0.20))
        peak_selector_frac_struct = float(peak_selector_cfg.get("frac_of_max_structural", 0.08))
        peak_selector_snr_min = float(peak_selector_cfg.get("snr_min", 5.0))
        # Dynamic t_max to ensure adaptive lock updates for low frequencies.
        if adaptive_cfg and adaptive_cfg.get("enabled") and sim_params_cfg and dt_cfg and t_max_cfg:
            try:
                dynamic_t_max = adaptive_cfg.get("dynamic_t_max", True)
                min_updates = int(adaptive_cfg.get("min_window_updates", 3))
                window_cycles = float(adaptive_cfg.get("window_cycles", 20.0))
                ref_layer = adaptive_cfg.get("ref_frequency_layer", "Q")
                min_omega = None
                if spec_layers and ref_layer in spec_layers:
                    freq_range = spec_layers.get(ref_layer, {}).get("freq_range")
                    if isinstance(freq_range, list) and freq_range:
                        min_omega = float(min(freq_range))
                if min_omega is None or min_omega <= 0:
                    min_omega = 1.0
                if dynamic_t_max and min_updates > 0:
                    window_duration = window_cycles * (2 * np.pi) / max(min_omega, 1e-8)
                    t_min_needed = min_updates * window_duration
                    t_max_base = float(t_max_cfg)
                    if t_min_needed > t_max_base:
                        t_max_used = t_min_needed
                        sim_params_cfg["total_steps"] = int(t_max_used / float(dt_cfg))
                        print(
                            "!!~~~## adaptive_lock t_max extended "
                            f"(base={t_max_base:.3f}, used={t_max_used:.3f}, "
                            f"min_omega={min_omega:.3f}, window_cycles={window_cycles:.1f}, "
                            f"min_updates={min_updates})"
                        )
            except Exception:
                pass
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
        memory_cfg = None
        adaptive_cfg = None
        peak_selector_frac = 0.20
        peak_selector_frac_struct = 0.08
        peak_selector_snr_min = 5.0
    layer_cfg = _load_layer_state_config(args.layer_states)
    family_spec = None
    family_fp = None
    family_priors = None

    if args.family_config:
        family_spec = load_family_spec(args.family_config)

    if family_spec:
        family_fp = build_fingerprint(family_spec)
        family_priors = make_priors_for_family(family_spec, family_fp)
        # Override band window if provided by family
        args.band_min, args.band_max = family_spec.energy_window

    # Default peak selector settings (may be overridden by engine config).
    peak_selector_frac = 0.20
    peak_selector_frac_struct = 0.08
    peak_selector_snr_min = 5.0

    # Resolve dirs to detect existing outputs (after family is known)
    raw_dir = args.raw_dir
    processed_dir = args.processed_dir
    flatten = args.output_root is not None
    if args.output_root:
        raw_dir = Path(args.output_root) / "raw"
        processed_dir = Path(args.output_root)

    if flatten:
        raw_path = raw_dir / f"{args.case}_study05_sweep_params.json"
        processed_path = processed_dir / f"{args.case}_study05_sweep_results.json"
    else:
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
        output_root=args.output_root,
        layer_state_config=layer_cfg,
        sim_params_cfg=sim_params_cfg,
        debug_traces=args.debug_traces,
        memory_cfg=memory_cfg,
        adaptive_cfg=adaptive_cfg,
        partial_flush_every=args.partial_flush_every,
        engine_config_path=engine_cfg_path,
        engine_config_hash=engine_cfg_hash,
        resume=args.resume,
        stop_file=args.stop_file,
        compute_entropy=args.compute_entropy,
    )
    print(
        json.dumps(
            {"summary": summary, "raw_path": str(raw_path), "processed_path": str(processed_path)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
