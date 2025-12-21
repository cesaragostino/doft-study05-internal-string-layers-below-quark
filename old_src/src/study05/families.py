"""Family specifications and heuristics for Study05 sweeps."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class FamilySpec:
    name: str
    hadron_type: str
    masses_gev: List[float]
    widths_gev: Optional[List[float]] = None
    jpc: Optional[str] = None
    energy_window: Tuple[float, float] = (0.2, 3.0)


@dataclass
class FamilyFingerprint:
    n_levels_target: int
    target_spacings: List[float]
    spacing_tol: float
    target_widths: Optional[List[float]] = None


@dataclass
class FamilyPriors:
    R_S1_Q_range: Tuple[float, float]
    R_S2_S1_range: Tuple[float, float]
    g_QS1_scale_range: Tuple[float, float]
    g_S1S2_scale_range: Tuple[float, float]
    memory_strength_range: Tuple[float, float]
    suggested_N: Optional[Dict[str, int]] = None


@dataclass
class FamilyDistance:
    n_levels_sim: int
    spacings_sim: List[float]
    d_spacing: float
    d_widths: Optional[float]
    d_total: float
    is_match: bool


def load_family_spec(path: Path) -> FamilySpec:
    data = json.loads(path.read_text())
    return FamilySpec(
        name=data["name"],
        hadron_type=data.get("hadron_type", "meson"),
        masses_gev=data["masses_gev"],
        widths_gev=data.get("widths_gev"),
        jpc=data.get("jpc"),
        energy_window=tuple(data.get("energy_window", (0.2, 3.0))),
    )


def build_fingerprint(spec: FamilySpec) -> FamilyFingerprint:
    m = np.array(spec.masses_gev)
    win = spec.energy_window
    m = m[(m >= win[0]) & (m <= win[1])]
    m = np.sort(m)
    spacings = np.diff(m) if m.size >= 2 else np.array([])
    spacing_mean = float(np.mean(spacings)) if spacings.size else 0.0
    spacing_tol = 0.2 * spacing_mean if spacing_mean > 0 else 0.2
    return FamilyFingerprint(
        n_levels_target=int(m.size),
        target_spacings=spacings.tolist(),
        spacing_tol=spacing_tol,
        target_widths=spec.widths_gev,
    )


def make_priors_for_family(spec: FamilySpec, fp: FamilyFingerprint) -> FamilyPriors:
    n_levels = fp.n_levels_target
    # defaults
    R_S1_Q = (2.0, 3.0)
    R_S2_S1 = (1.6, 2.2)
    g_qs1 = (0.5, 1.0)
    g_s1s2 = (2.0, 4.0)
    mem_range = (0.5, 1.0)

    if n_levels <= 2:
        # push S2 higher / weaker
        R_S2_S1 = (2.5, 4.0)
        g_s1s2 = (0.5, 2.0)
    else:
        # encourage S2 to contribute
        spacing_mean = float(np.mean(fp.target_spacings)) if fp.target_spacings else 0.5
        if spacing_mean < 0.5:
            R_S1_Q = (1.5, 2.5)
            R_S2_S1 = (1.4, 1.8)
        elif spacing_mean > 0.8:
            R_S1_Q = (2.5, 3.5)
            R_S2_S1 = (1.8, 2.4)
        g_s1s2 = (g_qs1[0] * 1.5, g_qs1[1] * 2.0)

    if spec.hadron_type == "baryon":
        g_qs1 = tuple(1.5 * x for x in g_qs1)
        g_s1s2 = tuple(1.5 * x for x in g_s1s2)

    return FamilyPriors(
        R_S1_Q_range=R_S1_Q,
        R_S2_S1_range=R_S2_S1,
        g_QS1_scale_range=g_qs1,
        g_S1S2_scale_range=g_s1s2,
        memory_strength_range=mem_range,
        suggested_N={"Q": 3, "S1": 3, "S2": 2},
    )


def compare_spacings(sim_spacings: np.ndarray, target_spacings: List[float], tol: float) -> bool:
    if not len(target_spacings):
        return False
    sim = np.sort(sim_spacings)
    tgt = np.array(target_spacings)
    if sim.size < tgt.size:
        return False
    sim = sim[: tgt.size]
    return bool(np.all(np.abs(sim - tgt) <= tol))


def compute_family_distance(
    sim_levels: List[float],
    sim_widths: Optional[List[float]],
    fingerprint: FamilyFingerprint,
    use_widths: bool = False,
) -> FamilyDistance:
    n_sim = len(sim_levels)
    if n_sim < fingerprint.n_levels_target:
        return FamilyDistance(
            n_levels_sim=n_sim,
            spacings_sim=[],
            d_spacing=1e9,
            d_widths=None,
            d_total=1e9,
            is_match=False,
        )

    sim_levels_sorted = sorted(sim_levels)
    sim_spacings = [sim_levels_sorted[i + 1] - sim_levels_sorted[i] for i in range(len(sim_levels_sorted) - 1)]
    sim_spacings = sim_spacings[: max(0, fingerprint.n_levels_target - 1)]

    if not sim_spacings or not fingerprint.target_spacings:
        return FamilyDistance(
            n_levels_sim=n_sim,
            spacings_sim=sim_spacings,
            d_spacing=1e9,
            d_widths=None,
            d_total=1e9,
            is_match=False,
        )

    ds = 0.0
    for s_sim, s_target in zip(sim_spacings, fingerprint.target_spacings):
        ds += abs(s_sim - s_target) / fingerprint.spacing_tol
    ds = ds / max(1, len(fingerprint.target_spacings))

    dw = None
    d_total = ds
    if use_widths and fingerprint.target_widths is not None and sim_widths is not None:
        w_sim = sim_widths[: fingerprint.n_levels_target]
        w_tgt = fingerprint.target_widths[: fingerprint.n_levels_target]
        dw_acc = 0.0
        for ws, wt in zip(w_sim, w_tgt):
            scale = max(wt, 1e-6)
            dw_acc += abs(ws - wt) / scale
        dw = dw_acc / max(1, fingerprint.n_levels_target)
        d_total += dw

    is_match = d_total < 1.0
    return FamilyDistance(
        n_levels_sim=n_sim,
        spacings_sim=sim_spacings,
        d_spacing=ds,
        d_widths=dw,
        d_total=d_total,
        is_match=is_match,
    )
