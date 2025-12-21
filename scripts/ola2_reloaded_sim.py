#!/usr/bin/env python3
"""
Simulador ligero para Ola2 (modelo de fases con memoria global).

Implementa la especificación de docs/STUDY05_ola2_reloaded_global_memory.md:
- Rehidratación de fases con ruido
- Topología con pesos normalizados por grado
- Campo global Z(t) con relajación tau_field
- Dinámica con acoplamiento local K_local, acoplamiento global kappa_global y ruido templado
- Métricas: R_final, R_mean_lastW, phase_var_lastW, PE sobre R(t)
- Masa efectiva con defecto de enlace (gamma)

Inputs mínimos:
- genes: JSON con una lista de bloques; cada item debe incluir (si está disponible):
    * mass (o mass_gev) opcional; default=1.0 si falta
    * omega (o F_m) opcional; default=1.0 si falta
    * lock_quality {Q,S1,S2} opcional; usado para QualityLock y H_block
    * theta0 opcional (radianes)
- template: JSON con campos "edges" (lista de pares) y opcionalmente "weights"

Salida:
- JSON con métricas bajo clave "ola2"
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

CHAOS_EPS = 1e-12
MEM_EPS = 1e-12


def _lock_entropy_norm_from_weights(weights: Dict[str, float]) -> float:
    def _to_float(val):
        try:
            return float(val)
        except Exception:
            return 0.0
    q = max(_to_float(weights.get("Q", 0.0)), 0.0)
    s1 = max(_to_float(weights.get("S1", 0.0)), 0.0)
    s2 = max(_to_float(weights.get("S2", 0.0)), 0.0)
    s = q + s1 + s2
    if s <= CHAOS_EPS:
        p = [1 / 3, 1 / 3, 1 / 3]
    else:
        p = [q / s, s1 / s, s2 / s]
    return float(-sum(pi * math.log(pi + CHAOS_EPS) for pi in p) / math.log(3))


def _permutation_entropy(series: np.ndarray, m: int = 5, tau: int = 1) -> float | None:
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


def _wrap_angle(delta: np.ndarray) -> np.ndarray:
    """Envuelve ángulos a [-pi, pi]."""
    return (delta + np.pi) % (2 * np.pi) - np.pi


def simulate_ola2(
    masses: np.ndarray,
    omegas: np.ndarray,
    theta0: np.ndarray | None,
    template: Dict[str, Any],
    lock_quality: List[Dict[str, float]] | None = None,
    dt: float = 1.0,
    T_ticks: int = 120,
    sigma0: float = 0.30,
    sigma_tc: float = 60.0,
    sigma_theta_init: float = 0.5,
    K_local: float = 0.15,
    kappa_global: float = 0.25,
    tau_field: float = 20.0,
    window_W: int = 20,
    gamma: float = 0.007,
    gamma_max: float = 0.02,
    mass_min: float = 0.01,
) -> Dict[str, Any]:
    N = len(masses)
    theta_base = (
        np.random.uniform(0.0, 2 * np.pi, size=N)
        if theta0 is None or theta0.shape != (N,)
        else theta0
    )
    theta = theta_base + np.random.normal(0.0, sigma_theta_init, size=N)

    # Adjacencia con pesos crudos y normalización por suma de pesos entrantes.
    edges = template.get("edges", [])
    weights_map = template.get("weights", {})
    A = np.zeros((N, N), dtype=float)
    for e in edges:
        if len(e) < 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i < 0 or j < 0 or i >= N or j >= N:
            continue
        raw_w = 1.0
        if len(e) >= 3:
            raw_w = float(e[2])
        elif weights_map:
            raw_w = float(weights_map.get(f"{i}-{j}", 1.0))
        A[i, j] = raw_w
        A[j, i] = raw_w
    deg_raw = A.sum(axis=1)
    W = np.zeros_like(A)
    for i in range(N):
        if deg_raw[i] > 0:
            W[i, :] = A[i, :] / deg_raw[i]
    degree_normalized = W.sum(axis=1)
    effective_degree = (A > 0).sum(axis=1).astype(int).tolist()

    Z = 0.0 + 0.0j
    R_series: List[float] = []
    theta_history: List[np.ndarray] = []
    E_local_series: List[float] = []
    dt = float(dt)
    for t in range(T_ticks):
        sigma_t = sigma0 * math.exp(-t / sigma_tc)
        # global field update
        Z = Z + (dt / tau_field) * ((np.exp(1j * theta).mean()) - Z)
        # coupling term
        theta_diff = theta.reshape(-1, 1) - theta.reshape(1, -1)
        coupling = K_local * dt * np.sum(W * np.sin(-theta_diff), axis=1)
        global_term = kappa_global * dt * np.imag(Z * np.exp(-1j * theta))
        noise = sigma_t * dt * np.random.normal(0.0, 1.0, size=N)
        theta = theta + omegas * dt + coupling + global_term + noise
        E_local_series.append(float(-K_local * np.sum(W * np.cos(-theta_diff))))
        # coherence
        R_series.append(abs(np.exp(1j * theta).mean()))
        theta_history.append(theta.copy())

    R_series = np.array(R_series)
    if R_series.size == 0:
        R_final_raw = float("nan")
        R_mean_lastW = float("nan")
    else:
        R_final_raw = float(R_series[-1])
        R_mean_lastW = float(np.mean(R_series[-window_W:])) if R_series.size >= window_W else float("nan")

    phase_var_lastW = float("nan")
    edge_phase_diff_mean_lastW = float("nan")
    edge_phase_diff_std_lastW = float("nan")
    skipped_edges = 0
    if R_series.size >= window_W and edges:
        thetas_window = np.stack(theta_history[-window_W:], axis=0)
        delta_vars = []
        delta_samples = []
        for e in edges:
            if len(e) < 2:
                skipped_edges += 1
                continue
            i, j = int(e[0]), int(e[1])
            if i < 0 or j < 0 or i >= N or j >= N:
                skipped_edges += 1
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
    if skipped_edges:
        print(f"[ola2_sim] skipped {skipped_edges} invalid edges (N={N})")

    insufficient_ticks = R_series.size < window_W
    success = False
    if not insufficient_ticks and np.isfinite(R_mean_lastW) and np.isfinite(phase_var_lastW):
        success = (R_mean_lastW > 0.85) and (phase_var_lastW < 0.02)
    R_final = float(np.clip(R_final_raw, 0.0, 1.0)) if np.isfinite(R_final_raw) else float("nan")
    if success and np.isfinite(R_final):
        success = R_final > 0.90

    # QualityLock
    QualityLock = None
    entropy_quality = None
    if lock_quality:
        def _to_float(val):
            try:
                return float(val)
            except Exception:
                return 0.0
        Q_vals = [_to_float(lq.get("Q", 0.0)) for lq in lock_quality]
        if Q_vals:
            QualityLock = float(np.clip(np.mean(Q_vals), 0.0, 1.0))
        h_vals = [_lock_entropy_norm_from_weights(lq) for lq in lock_quality]
        if h_vals:
            entropy_quality = 1.0 - float(np.mean(h_vals))

    sumM = float(np.sum(masses))
    E_bind = 0.0
    clamp_flag = False
    quality_for_mass = QualityLock if QualityLock is not None else entropy_quality
    if quality_for_mass is not None and np.isfinite(R_final):
        E_bind = gamma * sumM * R_final * quality_for_mass
    if E_bind > gamma_max * sumM:
        E_bind = gamma_max * sumM
        clamp_flag = True
    E_bind = float(np.clip(E_bind, 0.0, gamma_max * sumM))
    M_final = sumM - E_bind
    if M_final < mass_min:
        M_final = mass_min
        clamp_flag = True
    mass_defect = sumM - M_final

    PE_tick_norm = _permutation_entropy(R_series, m=5, tau=1)

    memory_score_k10 = None
    if R_series.size >= 2:
        diff1 = R_series[1:] - R_series[:-1]
        mse1 = float(np.mean(diff1**2))
        if R_series.size >= 11:
            diff10 = R_series[10:] - R_series[:-10]
            mse10 = float(np.mean(diff10**2))
            memory_score_k10 = float(1.0 - mse1 / (mse10 + MEM_EPS))

    E_local_series_arr = np.array(E_local_series, dtype=float)
    if E_local_series_arr.size == 0:
        E_local_final = float("nan")
        E_local_mean_lastW = float("nan")
        E_local_min_lastW = float("nan")
        E_local_max_lastW = float("nan")
    else:
        E_local_final = float(E_local_series_arr[-1])
        if E_local_series_arr.size >= window_W:
            window_vals = E_local_series_arr[-window_W:]
            E_local_mean_lastW = float(np.mean(window_vals))
            E_local_min_lastW = float(np.min(window_vals))
            E_local_max_lastW = float(np.max(window_vals))
        else:
            E_local_mean_lastW = float("nan")
            E_local_min_lastW = float("nan")
            E_local_max_lastW = float("nan")

    reason = "locked" if success else "no_lock"
    if insufficient_ticks:
        reason = "insufficient_ticks"
    elif clamp_flag:
        reason = "clamp_mass"

    return {
        "metrics": {
            "R_final": R_final,
            "Z_final_abs": float(abs(Z)),
            "R_mean_lastW": R_mean_lastW,
            "phase_var_lastW": phase_var_lastW,
            "edge_phase_diff_mean_lastW": edge_phase_diff_mean_lastW,
            "edge_phase_diff_std_lastW": edge_phase_diff_std_lastW,
            "PE_tick_norm": PE_tick_norm,
            "QualityLock": QualityLock,
            "entropy_quality": entropy_quality,
            "memory_score_k10": memory_score_k10,
            "E_local_final": E_local_final,
            "E_local_mean_lastW": E_local_mean_lastW,
            "E_local_min_lastW": E_local_min_lastW,
            "E_local_max_lastW": E_local_max_lastW,
        },
        "topology": {
            "nodes": N,
            "edges_count": len(edges),
            "degree_raw": deg_raw.tolist(),
            "degree_normalized": degree_normalized.tolist(),
            "effective_degree": effective_degree,
        },
        "mass": {
            "sumM": sumM,
            "E_bind_mass": E_bind,
            "mass_defect": mass_defect,
            "M_final": M_final,
        },
        "result": {
            "success": bool(success),
            "reason": reason,
        },
        "engine": {
            "dt": dt,
            "T_ticks": T_ticks,
            "W": window_W,
            "tau_field": tau_field,
            "K_local": K_local,
            "kappa_global": kappa_global,
            "sigma0": sigma0,
            "sigma_tc": sigma_tc,
            "sigma_theta_init": sigma_theta_init,
            "gamma": gamma,
        },
    }


def _load_genes(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else []


def _load_template(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _template_nodes(template: Dict[str, Any]) -> int:
    if "nodes" in template and template["nodes"] is not None:
        return int(template["nodes"])
    edges = template.get("edges", [])
    if edges:
        max_idx = max(max(int(e[0]), int(e[1])) for e in edges if len(e) >= 2)
        return max_idx + 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Simular Ola2 (modelo de fases con memoria global).")
    parser.add_argument("--genes", type=Path, required=True, help="JSON con lista de bloques (genes Ola1).")
    parser.add_argument("--template", type=Path, required=True, help="JSON con edges de la plantilla.")
    parser.add_argument("--output", type=Path, required=True, help="Ruta del JSON de salida.")
    parser.add_argument("--dt", type=float, default=1.0)
    parser.add_argument("--T-ticks", type=int, default=120)
    parser.add_argument("--sigma0", type=float, default=0.30)
    parser.add_argument("--sigma-tc", type=float, default=60.0)
    parser.add_argument("--sigma-theta-init", type=float, default=0.5)
    parser.add_argument("--K-local", type=float, default=0.15)
    parser.add_argument("--kappa-global", type=float, default=0.25)
    parser.add_argument("--tau-field", type=float, default=20.0)
    parser.add_argument("--window-W", type=int, default=20)
    parser.add_argument("--gamma", type=float, default=0.007)
    parser.add_argument("--gamma-max", type=float, default=0.02)
    parser.add_argument("--mass-min", type=float, default=0.01)
    args = parser.parse_args()

    genes = _load_genes(args.genes)
    template = _load_template(args.template)
    N = _template_nodes(template)
    if N <= 0:
        print("[ola2] plantilla sin nodos válidos", file=sys.stderr)
        sys.exit(1)

    if len(genes) != N:
        output = {
            "ola2": {
                "result": {"success": False, "reason": "geometry_mismatch"},
                "topology": {"nodes": N, "edges_count": len(template.get("edges", []))},
            }
        }
        args.output.write_text(json.dumps(output, indent=2))
        print(f"[ola2] geometry_mismatch: genes={len(genes)} nodes={N}", file=sys.stderr)
        sys.exit(1)

    masses = []
    omegas = []
    theta0 = []
    lockq = []
    for g in genes:
        m = g.get("mass") or g.get("mass_gev") or 1.0
        w = g.get("omega") or g.get("F_m") or g.get("f_m") or 1.0
        masses.append(float(m))
        omegas.append(float(w))
        t0 = g.get("theta0")
        theta0.append(float(t0) if t0 is not None else math.nan)
        lq = g.get("lock_quality") or {}
        lockq.append(lq)

    masses_arr = np.array(masses, dtype=float)
    omegas_arr = np.array(omegas, dtype=float)
    theta0_arr = np.array(theta0, dtype=float)
    theta0_arr = np.where(np.isnan(theta0_arr), np.random.uniform(0.0, 2 * np.pi, size=len(theta0_arr)), theta0_arr)

    result = simulate_ola2(
        masses=masses_arr,
        omegas=omegas_arr,
        theta0=theta0_arr,
        template=template,
        lock_quality=lockq,
        dt=args.dt,
        T_ticks=args.T_ticks,
        sigma0=args.sigma0,
        sigma_tc=args.sigma_tc,
        sigma_theta_init=args.sigma_theta_init,
        K_local=args.K_local,
        kappa_global=args.kappa_global,
        tau_field=args.tau_field,
        window_W=args.window_W,
        gamma=args.gamma,
        gamma_max=args.gamma_max,
        mass_min=args.mass_min,
    )

    output = {"ola2": result}
    args.output.write_text(json.dumps(output, indent=2))
    print(f"[ola2] escrito {args.output}")


if __name__ == "__main__":
    main()
