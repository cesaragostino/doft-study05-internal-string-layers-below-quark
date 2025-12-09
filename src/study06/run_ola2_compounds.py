"""Generate Ola2 compounds from promoted blocks using declarative rules.

This version builds a physical compound (nested DOFT) by stitching together Ola1 blocks
with their full `theta_internal`, adds cross-block Q–Q couplings per template edges,
integrates with the Study05 engine, extracts spectra/proxies, and matches against SM.
No filtering: every attempt writes one row (stable or unstable) to the compounds CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from study05.couplings import Coupling, InterLayerCoupling, MemoryKernel
from study05.layers import Layer, Mode
from study05.run_sweep import _layer_summary, _rescale_energies
from study05.simulation import SimulationParams, simulate
from study05.simulation import compute_fft_spectrum  # noqa: F401 (implicit via simulate return)
from study05.simulation import pick_peaks


def _load_json(path: Path):
    return json.loads(path.read_text())


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else []


def _load_sm_catalog(path: Path) -> Dict[str, Dict[str, Any]]:
    data = _load_json(path)
    particles = data.get("particles", data)
    return {d["name"]: d for d in particles}


def _tier_rank(tier: str) -> int:
    order = {"none": 0, "level1": 1, "level2": 2, "level3": 3}
    return order.get(str(tier), 0)


def _normalize_s2(state: Any) -> str:
    s = str(state or "").lower()
    if s.startswith("structural"):
        return "structural"
    return s


def _rel_delta(a: float, b: float) -> float:
    if not np.isfinite(a) or not np.isfinite(b):
        return float("inf")
    if a == 0 and b == 0:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b), 1e-9)


def _clean_ratios(vals: List[Any]) -> List[float]:
    cleaned: List[float] = []
    for x in vals:
        try:
            v = float(x)
        except Exception:
            continue
        if np.isfinite(v):
            cleaned.append(v)
    return cleaned


def _max_rel_delta(vals: List[float]) -> float:
    if len(vals) <= 1:
        return 0.0
    return max(_rel_delta(a, b) for a in vals for b in vals)


def _sample_blocks(pool: List[Dict[str, Any]], families: Sequence[str], k: int) -> List[Dict[str, Any]]:
    filtered = [b for b in pool if (not families or b.get("family") in families)]
    if len(filtered) < k:
        return []
    # weighted by inverse d_total to prefer better matches but keep diversity
    weights = []
    for b in filtered:
        d = b.get("match_score", {}).get("d_total")
        try:
            d = float(d)
        except Exception:
            d = np.inf
        w = 1.0 / (1.0 + d) if np.isfinite(d) else 0.1
        weights.append(max(w, 1e-3))
    chosen = random.choices(filtered, weights=weights, k=k)
    return chosen


def _build_mode(layer_name: str, idx: int, omega0: float, mass: float, gamma: float) -> Mode:
    return Mode(layer=Layer[layer_name], index=idx, omega0=float(omega0), mass=float(mass), gamma=float(gamma))


def _build_intra(intra_def: List[Dict[str, Any]], idx_map: Dict[Tuple[str, int], int]) -> List[Coupling]:
    couplings: List[Coupling] = []
    for c in intra_def:
        li = c.get("i", {})
        lj = c.get("j", {})
        key_i = (li.get("layer"), int(li.get("index", 0)))
        key_j = (lj.get("layer"), int(lj.get("index", 0)))
        if key_i not in idx_map or key_j not in idx_map:
            continue
        couplings.append(
            Coupling(
                i=(Layer[key_i[0]], idx_map[key_i]),
                j=(Layer[key_j[0]], idx_map[key_j]),
                k_ij0=float(c.get("k_ij0", 0.0)),
            )
        )
    return couplings


def _build_inter(inter_def: List[Dict[str, Any]], idx_map: Dict[Tuple[str, int], int]) -> List[InterLayerCoupling]:
    inters: List[InterLayerCoupling] = []
    for ic in inter_def:
        try:
            deep_layer = Layer[ic.get("deep_layer")]
            shallow_layer = Layer[ic.get("shallow_layer")]
        except Exception:
            continue
        g0 = float(ic.get("g0", 0.0))
        links = {}
        for link in ic.get("links", []):
            i_deep = int(link.get("i_deep", 0))
            j_sh = int(link.get("j_shallow", 0))
            taus0 = [float(t) for t in link.get("taus0", [])]
            amps0 = [float(a) for a in link.get("amps0", [])]
            links[(i_deep, j_sh)] = MemoryKernel(taus0=taus0, amps0=amps0)
        inters.append(InterLayerCoupling(deep_layer=deep_layer, shallow_layer=shallow_layer, links=links, g0=g0))
    return inters


def build_compound_system(blocks: List[Dict[str, Any]], template: Dict[str, Any], env_ranges: Dict[str, List[float]]):
    modes: List[Mode] = []
    intra: List[Coupling] = []
    inter: List[InterLayerCoupling] = []
    idx_map: Dict[Tuple[str, int], int] = {}
    # Add block internals
    for b in blocks:
        theta = b.get("theta_internal") or {}
        block_modes = theta.get("modes", [])
        offset_layer_idx: Dict[str, int] = {}
        for m in block_modes:
            lname = m.get("layer")
            idx_old = int(m.get("index", 0))
            idx_new = sum(1 for key in idx_map if key[0] == lname)
            idx_map[(lname, idx_old)] = idx_new
            mode_obj = _build_mode(lname, idx_new, m.get("omega0", 1.0), m.get("mass", 1.0), m.get("gamma", 0.01))
            modes.append(mode_obj)
            offset_layer_idx[lname] = offset_layer_idx.get(lname, 0) + 1
        intra.extend(_build_intra(theta.get("intra_couplings", []), idx_map))
        inter.extend(_build_inter(theta.get("inter_couplings", []), idx_map))

    # Cross-block Q-Q couplings per template edges
    k_range = env_ranges.get("k_edge", [0.1, 1.0])
    g_range = env_ranges.get("g_edge", [0.0, 0.0])
    layer_Q_indices = [key for key in idx_map if key[0] == "Q"]
    # Map block order to Q index 0 per block
    block_q_indices: List[int] = []
    for b in blocks:
        theta = b.get("theta_internal") or {}
        q_modes = [m for m in theta.get("modes", []) if m.get("layer") == "Q"]
        if not q_modes:
            block_q_indices.append(None)
        else:
            old_idx = int(q_modes[0].get("index", 0))
            block_q_indices.append(idx_map.get(("Q", old_idx)))

    for edge in template.get("edges", []):
        if len(edge) != 2:
            continue
        i, j = edge
        if i >= len(block_q_indices) or j >= len(block_q_indices):
            continue
        qi = block_q_indices[i]
        qj = block_q_indices[j]
        if qi is None or qj is None:
            continue
        k_edge = random.uniform(*k_range)
        # g_edge optional: we approximate viscous coupling by adding to gamma of Q modes
        g_edge = random.uniform(*g_range)
        # spring coupling
        intra.append(Coupling(i=(Layer.Q, qi), j=(Layer.Q, qj), k_ij0=k_edge))
        # approximate viscous by slightly increasing damping
        modes[qi].gamma += g_edge
        modes[qj].gamma += g_edge

    return modes, intra, inter


def compute_proxies_from_sim(sim_result: Dict[str, Any], modes: List[Mode], band_min: float, band_max: float):
    spectrum = sim_result["spectrum"]
    layer_to_idx = sim_result["layer_to_idx"]
    omega_peaks, weights_peaks = pick_peaks(spectrum=spectrum, modes=modes, layer_to_idx=layer_to_idx, sim_params=SimulationParams())
    energies_gev, scale = _rescale_energies(omega_peaks)
    band_mask = (energies_gev >= band_min) & (energies_gev <= band_max)
    band_energies = energies_gev[band_mask]
    band_weights = [w for keep, w in zip(band_mask, weights_peaks) if keep]
    spacings = np.diff(np.sort(band_energies))
    layer_order = [Layer.Q, Layer.S1, Layer.S2]
    layer_summaries = {}
    for layer in layer_order:
        lname = layer.name
        layer_summaries[lname] = _layer_summary(
            layer_name=lname,
            energies=energies_gev,
            weights=weights_peaks,
            band_mask=band_mask,
            band_max=band_max,
            thresholds={},
        )
    s2_state = layer_summaries.get("S2", {}).get("state", "absent")
    s2_band_fraction = layer_summaries.get("S2", {}).get("band_fraction", 0.0)
    lock_quality_Q = layer_summaries.get("Q", {}).get("band_fraction", float("nan"))
    lock_quality_S1 = layer_summaries.get("S1", {}).get("band_fraction", float("nan"))
    lock_quality_S2 = layer_summaries.get("S2", {}).get("band_fraction", float("nan"))
    return {
        "energies_gev": energies_gev.tolist(),
        "band_energies_gev": band_energies.tolist(),
        "band_spacing_gev": spacings.tolist(),
        "band_count": int(band_energies.size),
        "spacing_mean": float(np.mean(spacings)) if spacings.size else float("nan"),
        "spacing_std": float(np.std(spacings)) if spacings.size else float("nan"),
        "lock_quality_Q": lock_quality_Q,
        "lock_quality_S1": lock_quality_S1,
        "lock_quality_S2": lock_quality_S2,
        "s2_state": s2_state,
        "s2_band_fraction": s2_band_fraction,
    }


def compute_match(levels: List[float], particle: Dict) -> Dict:
    win = particle.get("energy_window", [0.0, 10.0])
    levels_win = [e for e in levels if win[0] <= e <= win[1]]
    masses = particle.get("masses_gev", [])
    if not levels_win or not masses:
        return {"enough_levels": False, "d_spacing": float("nan"), "d_mass": float("nan"), "d_total": float("nan")}
    target_spacings = np.diff(masses)
    sim_spacings_full = np.diff(levels_win)
    enough = len(levels_win) >= len(masses)
    min_len = min(sim_spacings_full.size, target_spacings.size)
    sim_spacings = sim_spacings_full[:min_len] if min_len else np.array([])
    tgt_spacings = target_spacings[:min_len] if min_len else np.array([])
    spacing_rel = particle.get("tolerances", {}).get("spacing_rel", 0.2)
    mass_abs = particle.get("tolerances", {}).get("mass_abs", 0.1)

    if sim_spacings.size and tgt_spacings.size:
        d_spacing = float(np.mean(np.abs(sim_spacings - tgt_spacings) / (spacing_rel * tgt_spacings + 1e-9)))
    else:
        d_spacing = float("nan")

    sim_masses = np.array(levels_win[: len(masses)])
    tgt_masses = np.array(masses)
    if sim_masses.size and tgt_masses.size == sim_masses.size:
        d_mass = float(np.mean(np.abs(sim_masses - tgt_masses) / (mass_abs + 1e-9)))
    else:
        d_mass = float("nan")

    d_total = np.nansum([d_spacing, d_mass])
    return {
        "enough_levels": enough,
        "d_spacing": d_spacing,
        "d_mass": d_mass,
        "d_total": d_total,
    }


def run_from_rules(rules_path: Path, seed: int | None = None):
    rng = random.Random(seed)
    rules = _load_json(rules_path)
    blocks_path = Path(rules["blocks_input"])
    blocks = _load_blocks(blocks_path)
    if not blocks:
        print(json.dumps({"status": "skip", "reason": "no_blocks", "blocks_input": str(blocks_path)}))
        return
    templates = {t["name"]: t for t in _load_json(Path(rules["templates_json"]))}
    catalog = _load_sm_catalog(Path(rules["sm_universe"]))
    runs_per_target = int(rules.get("runs_per_target", 100))

    for tgt_cfg in rules.get("targets", []):
        target_name = tgt_cfg.get("name")
        target = catalog.get(target_name, {"name": target_name, "type": tgt_cfg.get("type")})
        families = tgt_cfg.get("allowed_block_families", [])
        k_blocks = int(tgt_cfg.get("blocks_per_compound", 3))
        template_names = tgt_cfg.get("templates", [])
        fp_constraints = tgt_cfg.get("fingerprint_constraints", {})
        env_ranges = tgt_cfg.get("environment_ranges", {})
        out_compounds = Path(tgt_cfg.get("output", {}).get("compounds_csv", f"data/processed/ola2/raw/compounds_{target_name}.csv"))

        rows: List[Dict[str, Any]] = []
        for run_idx in range(runs_per_target):
            tmpl_name = rng.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            picked = _sample_blocks(blocks, families, k_blocks)
            if not picked or tmpl is None:
                rows.append({"status": "skipped", "reason": "no_blocks_or_template", "run_id": run_idx})
                continue

            try:
                modes, intra, inter = build_compound_system(picked, tmpl, env_ranges)
                sim_params = SimulationParams()
                sim_result = simulate(modes=modes, intra_couplings=intra, inter_couplings=inter, sim_params=sim_params, rng=np.random.default_rng(rng.randint(0, 1_000_000)))
                band_min, band_max = tgt_cfg.get("band_min", 0.1), tgt_cfg.get("band_max", 3.0)
                proxies = compute_proxies_from_sim(sim_result, modes, band_min, band_max)
                levels = proxies.get("band_energies_gev", [])
                match = compute_match(levels, target)
                status = "ok"
            except FloatingPointError as e:
                status = "unstable"
                proxies = {}
                match = {"enough_levels": False, "d_spacing": float("nan"), "d_mass": float("nan"), "d_total": float("nan")}
            except Exception as e:
                status = "error"
                proxies = {}
                match = {"enough_levels": False, "d_spacing": float("nan"), "d_mass": float("nan"), "d_total": float("nan")}

            ratios_R_S1_Q = _clean_ratios([b.get("theta_internal", {}).get("R_S1_Q") for b in picked])
            ratios_R_S2_S1 = _clean_ratios([b.get("theta_internal", {}).get("R_S2_S1") for b in picked])
            ratios_R_S3_S2 = _clean_ratios([b.get("theta_internal", {}).get("R_S3_S2") for b in picked if b.get("theta_internal")])

            row = {
                "run_id": run_idx,
                "status": status,
                "target": target_name,
                "template_name": tmpl_name,
                "block_ids": [b.get("block_id") for b in picked],
                "structure_tier_min": min((_tier_rank(b.get("structure_tier")) for b in picked), default=0),
                "s2_state_blocks": [_normalize_s2(b.get("s2_state")) for b in picked],
                "max_rel_delta_R_S1_Q": _max_rel_delta(ratios_R_S1_Q),
                "max_rel_delta_R_S2_S1": _max_rel_delta(ratios_R_S2_S1),
                "max_rel_delta_R_S3_S2": _max_rel_delta(ratios_R_S3_S2),
                "match_d_total": match.get("d_total"),
                "match_d_spacing": match.get("d_spacing"),
                "match_d_mass": match.get("d_mass"),
                "enough_levels": match.get("enough_levels"),
            }
            row.update(proxies)
            rows.append(row)

        # save compounds CSV for this target
        out_compounds.parent.mkdir(parents=True, exist_ok=True)
        if rows:
            fieldnames = sorted({k for r in rows for k in r.keys()})
            with out_compounds.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Run Ola2 compound generation from rules (physical integration).")
    parser.add_argument("--rules-json", type=Path, required=True, help="wave2_compounds rules file.")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    run_from_rules(args.rules_json, seed=args.seed)


if __name__ == "__main__":
    main()
