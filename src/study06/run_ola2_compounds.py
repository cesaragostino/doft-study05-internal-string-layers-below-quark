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
from study05.run_sweep import _layer_summary, _load_layer_state_config, _rescale_energies
from study05.simulation import SimulationParams, simulate
from study05.simulation import compute_fft_spectrum  # noqa: F401 (implicit via simulate return)
from study05.simulation import pick_peaks
from study06.sm_matching import compute_match_stats, extract_levels, load_universe


def _load_json(path: Path):
    return json.loads(path.read_text())


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else []


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
    fam_lower = {f.lower() for f in families} if families else set()
    filtered = [
        b
        for b in pool
        if (not fam_lower or str(b.get("family", "")).lower() in fam_lower)
    ]
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


def compute_proxies_from_sim(
    sim_result: Dict[str, Any],
    modes: List[Mode],
    band_min: float,
    band_max: float,
    layer_cfg: Dict[str, Any],
):
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
    s2_band_fraction = layer_summaries.get("S2", {}).get("band_fraction", 0.0)
    s2_state_raw = layer_summaries.get("S2", {}).get("state", "absent")
    lock_quality_Q = layer_summaries.get("Q", {}).get("band_fraction", float("nan"))
    lock_quality_S1 = layer_summaries.get("S1", {}).get("band_fraction", float("nan"))
    lock_quality_S2 = layer_summaries.get("S2", {}).get("band_fraction", float("nan"))
    lock_quality_S3 = layer_summaries.get("S3", {}).get("band_fraction", float("nan"))

    thresholds = layer_cfg.get("lock_thresholds", {}) if layer_cfg else {}
    T_Q_rel_min = thresholds.get("T_Q_rel_min", thresholds.get("T_Q", 0.5))
    T_S1_rel_min = thresholds.get("T_S1_rel_min", thresholds.get("T_S1", 0.1))
    T_S2_rel_min = thresholds.get("T_S2_rel_min", thresholds.get("T_S2", 0.1))

    def _finite(x: float) -> float:
        return float(x) if np.isfinite(x) else 0.0

    lock_Q_f = _finite(lock_quality_Q)
    lock_S1_f = _finite(lock_quality_S1)
    lock_S2_f = _finite(lock_quality_S2)
    lock_S3_f = _finite(lock_quality_S3)
    structural_mass = lock_Q_f + lock_S1_f + lock_S2_f + lock_S3_f
    if structural_mass <= 0:
        structure_tier = "none"
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

    s2_state_cfg = layer_cfg.get("s2_state", {}) if layer_cfg else {}
    none_max = s2_state_cfg.get("none_max_fraction", 1e-3)
    latent_max = s2_state_cfg.get("latent_max_fraction", 0.15)
    if s2_band_fraction < none_max:
        s2_state_label = "none"
    elif s2_band_fraction <= latent_max:
        s2_state_label = "latent"
    else:
        s2_state_label = "structural" if s2_state_raw.startswith("structural") else s2_state_raw
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
        "lock_quality_S3": lock_quality_S3,
        "structure_tier_compound": structure_tier,
        "s2_state": s2_state_label,
        "s2_band_fraction": s2_band_fraction,
    }


def run_from_rules(
    rules_path: Path,
    blocks_override: Path | None = None,
    sm_universe: Path | None = None,
    templates_path: Path | None = None,
    output_root: Path | None = None,
    seed: int | None = None,
    layer_states: Path | None = None,
):
    rng = random.Random(seed)
    rules = _load_json(rules_path)
    layer_cfg = _load_layer_state_config(layer_states or Path("data/raw/layer_states.yaml"))

    blocks_path = Path(blocks_override or rules.get("blocks_input", "data/processed/blocks/simple_blocks.json"))
    blocks = _load_blocks(blocks_path)
    if not blocks:
        print(json.dumps({"status": "skip", "reason": "no_blocks", "blocks_input": str(blocks_path)}))
        return

    templates_path = Path(templates_path or rules.get("templates_json", "data/raw/compound_templates.json"))
    templates = {t["name"]: t for t in _load_json(templates_path)}
    sm_path = Path(sm_universe or rules.get("sm_universe", "data/raw/sm_universe.json"))
    catalog = {p["name"]: p for p in load_universe(sm_path).get("particles", [])}
    runs_per_target_default = int(rules.get("runs_per_target", 100))
    env_root = rules.get("environment_ranges", {})

    def _env_range(key: str, fallback: List[float]) -> List[float]:
        val = env_root.get(key)
        if isinstance(val, list) and len(val) == 2:
            return val
        if f"{key}_min" in env_root and f"{key}_max" in env_root:
            return [env_root[f"{key}_min"], env_root[f"{key}_max"]]
        return fallback

    env_default = {
        "k_edge": _env_range("k_edge", [0.1, 1.0]),
        "g_edge": _env_range("g_edge", [0.0, 0.0]),
    }

    for tgt_cfg in rules.get("targets", []):
        target_name = tgt_cfg.get("name") or tgt_cfg.get("particle_name")
        target = catalog.get(target_name, {"name": target_name, "type": tgt_cfg.get("type")})
        families = [f.lower() for f in tgt_cfg.get("allowed_block_families", [])]
        k_blocks = int(tgt_cfg.get("blocks_per_compound", tgt_cfg.get("max_blocks_per_target_run", 3)))
        template_names = tgt_cfg.get("templates", [])
        env_ranges_cfg = tgt_cfg.get("environment_ranges", {}) or {}

        def _norm_range(cfg: Dict[str, Any], name: str, fallback: List[float]) -> List[float]:
            val = cfg.get(name)
            if isinstance(val, list) and len(val) == 2:
                return val
            if f"{name}_min" in cfg and f"{name}_max" in cfg:
                return [cfg[f"{name}_min"], cfg[f"{name}_max"]]
            return fallback

        env_ranges = {
            "k_edge": _norm_range(env_ranges_cfg, "k_edge", env_default["k_edge"]),
            "g_edge": _norm_range(env_ranges_cfg, "g_edge", env_default["g_edge"]),
        }
        runs_per_target = int(tgt_cfg.get("runs_per_target", runs_per_target_default))
        prefer_quark = bool(tgt_cfg.get("prefer_quark_like_for_baryons", rules.get("sampling", {}).get("prefer_quark_like_for_baryons", False)))
        out_base = output_root or Path("data/processed/ola2")
        out_compounds = Path(tgt_cfg.get("output", {}).get("compounds_csv", out_base / f"compounds_{target_name}.csv"))

        rows: List[Dict[str, Any]] = []
        for run_idx in range(runs_per_target):
            tmpl_name = rng.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            picked = _sample_blocks(blocks, families, k_blocks)
            if prefer_quark and target.get("type") == "baryon":
                quark_blocks = _sample_blocks(blocks, ["quark_like"], k_blocks)
                if quark_blocks:
                    picked = quark_blocks
            if not picked or tmpl is None:
                rows.append({"status": "skipped", "reason": "no_blocks_or_template", "run_id": run_idx})
                continue

            try:
                modes, intra, inter = build_compound_system(picked, tmpl, env_ranges)
                sim_params = SimulationParams()
                sim_result = simulate(
                    modes=modes,
                    intra_couplings=intra,
                    inter_couplings=inter,
                    sim_params=sim_params,
                    rng=np.random.default_rng(rng.randint(0, 1_000_000)),
                )
                band_min, band_max = tgt_cfg.get("band_min", 0.1), tgt_cfg.get("band_max", 3.0)
                proxies = compute_proxies_from_sim(sim_result, modes, band_min, band_max, layer_cfg)
                levels = extract_levels(proxies.get("band_energies_gev", []), target.get("energy_window"))
                match = compute_match_stats(levels, target.get("masses_gev", []), target.get("tolerances", {}))
                if len(levels) == 0:
                    status = "error"
                else:
                    status = "ok"
            except FloatingPointError:
                status = "unstable"
                proxies = {}
                match = {
                    "d_total": float("nan"),
                    "d_spacing": float("nan"),
                    "d_mass": float("nan"),
                    "has_enough_levels_full": False,
                    "has_enough_levels_partial": False,
                    "n_levels_sim": 0,
                }
            except Exception:
                status = "error"
                proxies = {}
                match = {
                    "d_total": float("nan"),
                    "d_spacing": float("nan"),
                    "d_mass": float("nan"),
                    "has_enough_levels_full": False,
                    "has_enough_levels_partial": False,
                    "n_levels_sim": 0,
                }

            ratios_R_S1_Q = _clean_ratios([b.get("theta_internal", {}).get("R_S1_Q") for b in picked])
            ratios_R_S2_S1 = _clean_ratios([b.get("theta_internal", {}).get("R_S2_S1") for b in picked])
            ratios_R_S3_S2 = _clean_ratios(
                [b.get("theta_internal", {}).get("R_S3_S2") for b in picked if b.get("theta_internal")]
            )
            num_quark_blocks = sum(
                1 for b in picked if str(b.get("family", "")).lower() == "quark_like" or str(b.get("particle_name", "")).startswith("quark_")
            )

            row = {
                "run_id": run_idx,
                "status": status,
                "target": target_name,
                "template_name": tmpl_name,
                "block_ids": [b.get("block_id") for b in picked],
                "block_families": [b.get("family") for b in picked],
                "structure_tier_min": min((_tier_rank(b.get("structure_tier")) for b in picked), default=0),
                "s2_state_blocks": [_normalize_s2(b.get("s2_state")) for b in picked],
                "max_rel_delta_R_S1_Q": _max_rel_delta(ratios_R_S1_Q),
                "max_rel_delta_R_S2_S1": _max_rel_delta(ratios_R_S2_S1),
                "max_rel_delta_R_S3_S2": _max_rel_delta(ratios_R_S3_S2),
                "match_d_total": match.get("d_total"),
                "match_d_spacing": match.get("d_spacing"),
                "match_d_mass": match.get("d_mass"),
                "enough_levels_full": match.get("has_enough_levels_full"),
                "enough_levels_partial": match.get("has_enough_levels_partial"),
                "enough_levels": bool(match.get("has_enough_levels_partial")) or bool(match.get("has_enough_levels_full")),
                "n_levels_sim": match.get("n_levels_sim"),
                "num_quark_blocks": num_quark_blocks,
            }
            row.update(proxies)
            row["band_count_compound"] = proxies.get("band_count")
            row["s2_band_fraction_compound"] = proxies.get("s2_band_fraction")
            row["structure_tier_compound"] = proxies.get("structure_tier_compound")
            row["s2_state_compound"] = proxies.get("s2_state")
            band_es = proxies.get("band_energies_gev") or []
            if isinstance(band_es, str):
                try:
                    import json as _json

                    band_es = _json.loads(band_es)
                except Exception:
                    band_es = []
            if band_es:
                try:
                    row["first_energy_compound"] = float(sorted(band_es)[0])
                    spacings = np.diff(np.sort(np.array(band_es, dtype=float)))
                    row["spacing_mean_compound"] = float(np.mean(spacings)) if spacings.size else float("nan")
                except Exception:
                    row["first_energy_compound"] = float("nan")
                    row["spacing_mean_compound"] = float("nan")
            rows.append(row)

        out_compounds.parent.mkdir(parents=True, exist_ok=True)
        if rows:
            fieldnames = sorted({k for r in rows for k in r.keys()})
            with out_compounds.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Run Ola2 compound generation from rules (physical integration).")
    parser.add_argument("--wave2-config", type=Path, default=Path("data/raw/wave2_compounds.json"), help="wave2 rules file.")
    parser.add_argument("--blocks-json", type=Path, default=Path("data/processed/ola1/simple_blocks.json"), help="Override simple blocks input.")
    parser.add_argument("--sm-universe", type=Path, default=None, help="Override SM universe catalog.")
    parser.add_argument("--templates-json", type=Path, default=None, help="Override compound templates.")
    parser.add_argument("--output-root", type=Path, default=Path("data/processed/ola2"), help="Base output directory.")
    parser.add_argument("--layer-states", type=Path, default=Path("data/raw/layer_states.yaml"))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    run_from_rules(
        args.wave2_config,
        blocks_override=args.blocks_json,
        sm_universe=args.sm_universe,
        templates_path=args.templates_json,
        output_root=args.output_root,
        seed=args.seed,
        layer_states=args.layer_states,
    )


if __name__ == "__main__":
    main()
