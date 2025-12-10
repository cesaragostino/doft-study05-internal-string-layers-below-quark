"""Shared SM matching utilities for Ola1/Ola2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np


def load_universe(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def extract_levels(raw: Any, energy_window: Sequence[float] | None = None) -> List[float]:
    """Extract and optionally window band energies."""
    try:
        if isinstance(raw, str):
            vals = json.loads(raw)
        elif isinstance(raw, Iterable):
            vals = list(raw)
        else:
            vals = []
    except Exception:
        vals = []
    levels: List[float] = []
    for v in vals:
        try:
            f = float(v)
        except Exception:
            continue
        levels.append(f)
    levels = sorted(levels)
    if energy_window:
        lo, hi = energy_window
        levels = [x for x in levels if lo <= x <= hi]
    return levels


def compute_match_stats(
    levels: List[float],
    target_masses: Sequence[float],
    tolerances: Dict[str, float],
    min_levels_partial: int = 2,
) -> Dict[str, Any]:
    """Compute spacing/mass distances and enough-levels flags."""
    if not target_masses:
        return {
            "d_total": float("nan"),
            "d_spacing": float("nan"),
            "d_mass": float("nan"),
            "n_levels_sim": len(levels),
            "has_enough_levels_full": False,
            "has_enough_levels_partial": False,
        }
    spacing_rel = float(tolerances.get("spacing_rel", 0.2))
    mass_abs = float(tolerances.get("mass_abs", 0.1))

    tgt_masses = np.array(target_masses, dtype=float)
    lev = np.array(levels, dtype=float)
    n_levels_sim = int(lev.size)

    # Spacing distance on overlapping portion
    tgt_sp = np.diff(tgt_masses)
    sim_sp_full = np.diff(lev)
    min_len = min(sim_sp_full.size, tgt_sp.size)
    if min_len > 0:
        sim_sp = sim_sp_full[:min_len]
        tgt_sp_use = tgt_sp[:min_len]
        d_spacing = float(np.mean(np.abs(sim_sp - tgt_sp_use) / (spacing_rel * tgt_sp_use + 1e-9)))
    else:
        d_spacing = float("nan")

    # Mass distance on overlapping portion
    n_mass = min(lev.size, tgt_masses.size)
    if n_mass > 0:
        sim_m = lev[:n_mass]
        tgt_m = tgt_masses[:n_mass]
        d_mass = float(np.mean(np.abs(sim_m - tgt_m) / (mass_abs + 1e-9)))
    else:
        d_mass = float("nan")

    d_total = float(np.nansum([d_spacing, d_mass]))
    min_partial = min(len(target_masses), max(1, min_levels_partial))
    has_enough_levels_partial = n_levels_sim >= min_partial
    has_enough_levels_full = n_levels_sim >= len(target_masses)

    return {
        "d_total": d_total,
        "d_spacing": d_spacing,
        "d_mass": d_mass,
        "n_levels_sim": n_levels_sim,
        "has_enough_levels_full": has_enough_levels_full,
        "has_enough_levels_partial": has_enough_levels_partial,
    }
