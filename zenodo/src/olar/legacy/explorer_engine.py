"""Explorer V4 engine/evaluation layer (DOF-only)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

import numpy as np

CHAOS_EPS = 1e-12
MEM_EPS = 1e-12


def _wrap_angle(delta: np.ndarray) -> np.ndarray:
    return (delta + np.pi) % (2 * np.pi) - np.pi


def permutation_entropy_v1_cheapy(series: np.ndarray, m: int = 5, tau: int = 1) -> float | None:
    x = np.asarray(series, dtype=float)
    T = x.size
    if T < m * tau + 1:
        return None
    patterns: Dict[Tuple[int, ...], int] = {}
    for t in range(T - (m - 1) * tau):
        window = x[t : t + m * tau : tau]
        order = tuple(np.argsort(window, kind="stable"))
        patterns[order] = patterns.get(order, 0) + 1
    total = sum(patterns.values())
    if total == 0:
        return None
    probs = np.array(list(patterns.values()), dtype=float) / total
    return float(-np.sum(probs * np.log(np.clip(probs, CHAOS_EPS, 1.0))) / np.log(math.factorial(m)))


def _quality_from_r_series(r_series: np.ndarray, window_W: int) -> float | None:
    if r_series.size < window_W:
        return None
    r_last = r_series[-window_W:]
    std_r = float(np.std(r_last))
    std_max = 0.5
    return float(1.0 - min(std_r / std_max, 1.0))


def _entropy_quality_from_phases(theta_window: np.ndarray, bins: int = 12) -> float | None:
    if theta_window.size == 0:
        return None
    phases = np.mod(theta_window, 2 * np.pi).ravel()
    hist, _ = np.histogram(phases, bins=bins, range=(0.0, 2 * np.pi), density=True)
    hist = hist / max(hist.sum(), CHAOS_EPS)
    h_norm = -float(np.sum(hist * np.log(np.clip(hist, CHAOS_EPS, 1.0)))) / math.log(bins)
    return float(1.0 - h_norm)


def compute_metrics(structure: Dict[str, Any], engine_params: Dict[str, Any], seed: int) -> Dict[str, Any]:
    """Run DOF-only Kuramoto core and return metrics."""
    blocks = structure.get("blocks") or []
    edges = structure.get("edges") or []
    if not blocks:
        return {
            "R_final": float("nan"),
            "Z_final_abs": float("nan"),
            "R_mean_lastW": float("nan"),
            "phase_var_lastW": float("nan"),
            "edge_phase_diff_mean_lastW": float("nan"),
            "edge_phase_diff_std_lastW": float("nan"),
            "node_omega_mean_lastW": [],
            "node_omega_std_lastW": [],
            "omega_eff": float("nan"),
            "omega_eff_method": "rms",
        "PE_tick_norm_cheapy": float("nan"),
            "QualityLock": float("nan"),
            "entropy_quality": float("nan"),
            "memory_score_k10": float("nan"),
        }

    omegas_vals: List[float] = []
    for block in blocks:
        raw = block.get("omega_ref")
        if raw is None or raw == "":
            raise RuntimeError("Missing omega_ref for block in explorer_engine")
        try:
            val = float(raw)
        except Exception as exc:
            raise RuntimeError(f"Invalid omega_ref={raw!r} for block in explorer_engine") from exc
        if not np.isfinite(val):
            raise RuntimeError(f"Non-finite omega_ref={raw!r} for block in explorer_engine")
        omegas_vals.append(val)
    omegas = np.array(omegas_vals, dtype=float)

    dt = float(engine_params.get("dt", 1.0))
    T_ticks = int(engine_params.get("T_ticks", 200))
    window_W = int(engine_params.get("W", 20))
    K_local = float(engine_params.get("K_local", 0.45))
    kappa_global = float(engine_params.get("kappa_global", 0.30))
    tau_field = float(engine_params.get("tau_field", 120.0))
    sigma0 = float(engine_params.get("sigma0", 0.30))
    sigma_tc = float(engine_params.get("sigma_tc", 60.0))
    sigma_theta_init = float(engine_params.get("sigma_theta_init", 0.5))

    rng = np.random.default_rng(int(seed) % (2**32))

    N = len(omegas)
    theta = rng.uniform(0.0, 2 * np.pi, size=N)
    theta = theta + rng.normal(0.0, sigma_theta_init, size=N)

    A = np.zeros((N, N), dtype=float)
    for e in edges:
        if len(e) < 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i < 0 or j < 0 or i >= N or j >= N or i == j:
            continue
        A[i, j] = 1.0
        A[j, i] = 1.0
    deg_raw = A.sum(axis=1)
    W = np.zeros_like(A)
    for i in range(N):
        if deg_raw[i] > 0:
            W[i, :] = A[i, :] / deg_raw[i]

    Z = 0.0 + 0.0j
    R_series: List[float] = []
    theta_history: List[np.ndarray] = []
    for t in range(T_ticks):
        sigma_t = sigma0 * math.exp(-t / sigma_tc)
        Z = Z + (dt / tau_field) * (np.exp(1j * theta).mean() - Z)
        theta_diff = theta.reshape(-1, 1) - theta.reshape(1, -1)
        coupling = K_local * dt * np.sum(W * np.sin(-theta_diff), axis=1)
        global_term = kappa_global * dt * np.imag(Z * np.exp(-1j * theta))
        noise = sigma_t * dt * rng.normal(0.0, 1.0, size=N)
        theta = theta + omegas * dt + coupling + global_term + noise
        R_series.append(abs(np.exp(1j * theta).mean()))
        theta_history.append(theta.copy())

    r_series = np.array(R_series, dtype=float)
    if r_series.size == 0:
        R_final = float("nan")
        R_mean_lastW = float("nan")
    else:
        R_final = float(r_series[-1])
        R_mean_lastW = float(np.mean(r_series[-window_W:])) if r_series.size >= window_W else float("nan")

    Z_final_abs = float(abs(Z))
    phase_var_lastW = float("nan")
    edge_phase_diff_mean_lastW = float("nan")
    edge_phase_diff_std_lastW = float("nan")
    node_omega_mean_lastW: List[float] = []
    node_omega_std_lastW: List[float] = []
    omega_eff = float("nan")
    if r_series.size >= window_W:
        thetas_window = np.stack(theta_history[-window_W:], axis=0)
        if edges:
            delta_vars = []
            delta_samples = []
            for e in edges:
                if len(e) < 2:
                    continue
                i, j = int(e[0]), int(e[1])
                if i < 0 or j < 0 or i >= N or j >= N:
                    continue
                dtheta = _wrap_angle(thetas_window[:, i] - thetas_window[:, j])
                delta_vars.append(np.var(dtheta))
                delta_samples.append(np.abs(dtheta))
            if delta_vars:
                phase_var_lastW = float(np.mean(delta_vars))
            if delta_samples:
                stacked = np.concatenate(delta_samples, axis=0)
                edge_phase_diff_mean_lastW = float(np.mean(stacked))
                edge_phase_diff_std_lastW = float(np.std(stacked))
        if thetas_window.shape[0] >= 2:
            unwrapped = np.unwrap(thetas_window, axis=0)
            omega_series = np.diff(unwrapped, axis=0) / dt
            omega_mean = np.mean(omega_series, axis=0)
            omega_std = np.std(omega_series, axis=0)
            node_omega_mean_lastW = [float(v) for v in omega_mean]
            node_omega_std_lastW = [float(v) for v in omega_std]
            omega_eff = float(math.sqrt(np.mean(np.square(omega_mean))))

    PE_tick_norm = permutation_entropy_v1_cheapy(r_series, m=5, tau=1)
    if PE_tick_norm is None:
        PE_tick_norm = float("nan")

    memory_score_k10 = None
    if r_series.size >= 2:
        diff1 = r_series[1:] - r_series[:-1]
        mse1 = float(np.mean(diff1**2))
        if r_series.size >= 11:
            diff10 = r_series[10:] - r_series[:-10]
            mse10 = float(np.mean(diff10**2))
            memory_score_k10 = float(1.0 - mse1 / (mse10 + MEM_EPS))
    if memory_score_k10 is None:
        memory_score_k10 = float("nan")

    QualityLock = _quality_from_r_series(r_series, window_W)
    if QualityLock is None:
        QualityLock = float("nan")
    entropy_quality = _entropy_quality_from_phases(np.stack(theta_history[-window_W:], axis=0)) if r_series.size >= window_W else None
    if entropy_quality is None:
        entropy_quality = float("nan")

    return {
        "R_final": R_final,
        "Z_final_abs": Z_final_abs,
        "R_mean_lastW": R_mean_lastW,
        "phase_var_lastW": phase_var_lastW,
        "edge_phase_diff_mean_lastW": edge_phase_diff_mean_lastW,
        "edge_phase_diff_std_lastW": edge_phase_diff_std_lastW,
        "node_omega_mean_lastW": node_omega_mean_lastW,
        "node_omega_std_lastW": node_omega_std_lastW,
        "omega_eff": omega_eff,
        "omega_eff_method": "rms",
        "PE_tick_norm_cheapy": PE_tick_norm,
        "QualityLock": QualityLock,
        "entropy_quality": entropy_quality,
        "memory_score_k10": memory_score_k10,
    }


def gate_candidate(
    metrics: Dict[str, Any],
    thresholds: Dict[str, Any],
    viability_mode: str,
) -> Tuple[Dict[str, Any], List[str]]:
    def _finite(val: Any) -> bool:
        if not isinstance(val, (int, float)):
            return False
        try:
            return math.isfinite(float(val))
        except Exception:
            return False

    required = ["R_mean_lastW", "phase_var_lastW", "QualityLock", "memory_score_k10"]
    for key in required:
        val = metrics.get(key, float("nan"))
        if not _finite(val):
            return (
                {
                    "candidate": False,
                    "quality_lock_ok": False,
                    "memory_good": False,
                    "viability_mode": viability_mode,
                },
                [f"non_finite_{key}"],
            )
    reasons: List[str] = []
    r_min = float(thresholds.get("R_mean_lastW_min", 0.0))
    pv_max = float(thresholds.get("phase_var_lastW_max", 1e9))
    q_min = float(thresholds.get("quality_lock_min", 0.0))
    mem_min = float(thresholds.get("memory_score_k10_min", -1e9))

    r_val = float(metrics.get("R_mean_lastW", 0.0))
    pv_val = float(metrics.get("phase_var_lastW", 1.0))
    q_val = float(metrics.get("QualityLock", 0.0))
    mem_val = float(metrics.get("memory_score_k10", 0.0))

    quality_lock_ok = q_val >= q_min
    memory_good = mem_val >= mem_min
    if r_val < r_min:
        reasons.append("low_R_mean_lastW")
    if pv_val > pv_max:
        reasons.append("high_phase_var_lastW")
    if not quality_lock_ok:
        reasons.append("low_quality_lock")
    if not memory_good:
        reasons.append("low_memory_score_k10")

    tags_raw = {
        "candidate": len(reasons) == 0,
        "quality_lock_ok": quality_lock_ok,
        "memory_good": memory_good,
        "viability_mode": viability_mode,
    }
    return tags_raw, reasons
