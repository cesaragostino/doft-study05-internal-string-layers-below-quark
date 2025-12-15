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
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

CHAOS_EPS = 1e-12


def _lock_entropy_norm_from_weights(weights: Dict[str, float]) -> float:
    q = max(float(weights.get("Q", 0.0)), 0.0)
    s1 = max(float(weights.get("S1", 0.0)), 0.0)
    s2 = max(float(weights.get("S2", 0.0)), 0.0)
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
    mass_min: float = 0.0,
) -> Dict[str, Any]:
    N = len(masses)
    if theta0 is None or theta0.shape != (N,):
        base = np.zeros(N)
    else:
        base = theta0
    theta = base + np.random.normal(0.0, sigma_theta_init, size=N)

    # Adjacency and weights normalized por grado
    edges = template.get("edges", [])
    A = np.zeros((N, N), dtype=float)
    for e in edges:
        if len(e) != 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i < 0 or j < 0 or i >= N or j >= N:
            continue
        A[i, j] = 1.0
        A[j, i] = 1.0
    deg = A.sum(axis=1)
    W = np.zeros_like(A)
    for i in range(N):
        if deg[i] > 0:
            W[i, :] = A[i, :] / deg[i]

    Z = 0.0 + 0.0j
    R_series: List[float] = []
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
        # coherence
        R_series.append(abs(np.exp(1j * theta).mean()))

    R_series = np.array(R_series)
    R_final = float(R_series[-1]) if R_series.size else float("nan")
    R_mean_lastW = float(np.mean(R_series[-window_W:])) if R_series.size >= window_W else float(np.mean(R_series))

    # phase variance over edges in last window
    if R_series.size >= window_W and edges:
        start_idx = T_ticks - window_W
        phases_last = theta  # at final tick
        # reconstruct history not stored; approximate with final diffs (cheap)
        delta_vars = []
        for i, j in edges:
            dtheta = (phases_last[int(i)] - phases_last[int(j)] + np.pi) % (2 * np.pi) - np.pi
            delta_vars.append(dtheta * dtheta)
        phase_var_lastW = float(np.mean(delta_vars)) if delta_vars else float("nan")
    else:
        phase_var_lastW = float("nan")

    success = (R_mean_lastW > 0.85) and (phase_var_lastW < 0.02) if np.isfinite(R_mean_lastW) else False
    if np.isfinite(R_final):
        success = success and (R_final > 0.90)

    # QualityLock
    if lock_quality:
        Q_vals = [float(lq.get("Q", 0.0)) for lq in lock_quality]
        qual_lock = float(np.clip(np.mean(Q_vals), 0.0, 1.0)) if Q_vals else None
        h_vals = [_lock_entropy_norm_from_weights(lq) for lq in lock_quality]
        qual_lock_alt = 1.0 - float(np.mean(h_vals)) if h_vals else None
        if qual_lock_alt is not None:
            QualityLock = qual_lock_alt if qual_lock is None else float(0.5 * (qual_lock + qual_lock_alt))
        else:
            QualityLock = qual_lock
    else:
        QualityLock = None

    sumM = float(np.sum(masses))
    E_bind = 0.0
    if QualityLock is not None and np.isfinite(R_final):
        E_bind = gamma * sumM * R_final * QualityLock
    E_bind = float(np.clip(E_bind, 0.0, gamma_max * sumM))
    M_final = sumM - E_bind
    if M_final < mass_min:
        M_final = mass_min
    mass_defect = sumM - M_final

    PE_tick_norm = _permutation_entropy(R_series, m=5, tau=1)

    return {
        "metrics": {
            "R_final": R_final,
            "R_mean_lastW": R_mean_lastW,
            "phase_var_lastW": phase_var_lastW,
            "PE_tick_norm": PE_tick_norm,
            "QualityLock": QualityLock,
        },
        "mass": {
            "sumM": sumM,
            "E_bind_mass": E_bind,
            "mass_defect": mass_defect,
            "M_final": M_final,
        },
        "result": {
            "success": bool(success),
            "reason": "locked" if success else "no_lock",
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
    parser.add_argument("--mass-min", type=float, default=0.0)
    args = parser.parse_args()

    genes = _load_genes(args.genes)
    template = _load_template(args.template)
    N = len(template.get("edges", [])) + 1  # crude guess
    masses = []
    omegas = []
    theta0 = []
    lockq = []
    for i in range(N):
        g = genes[i % len(genes)] if genes else {}
        m = g.get("mass") or g.get("mass_gev") or 1.0
        w = g.get("omega") or g.get("F_m") or g.get("f_m") or 1.0
        masses.append(float(m))
        omegas.append(float(w))
        t0 = g.get("theta0")
        theta0.append(float(t0) if t0 is not None else 0.0)
        lq = g.get("lock_quality") or {}
        lockq.append(lq)

    masses_arr = np.array(masses, dtype=float)
    omegas_arr = np.array(omegas, dtype=float)
    theta0_arr = np.array(theta0, dtype=float)

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
