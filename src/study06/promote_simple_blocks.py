"""Promote simple blocks (Ola1) from sweep proxies and SM matches."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from study06.sm_matching import load_universe


DEFAULT_SELECTION = {
    "band_count_max": 7,
    "lock_quality_Q_min": 0.35,
    "structure_tier_min": "level1",
    "log_rejections": True,
    "grades": {
        "use_d_total_for_grades_only": True,
        "grade_A_d_total_max": 0.5,
        "grade_B_d_total_max": 1.5,
    },
}


def read_proxies(path: Path) -> List[Dict]:
    rows = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                try:
                    parsed[k] = float(v)
                except Exception:
                    parsed[k] = v
            rows.append(parsed)
    return rows


def _hash_text(text: str) -> str:
    try:
        import hashlib

        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    except Exception:
        return ""


def read_matches(path: Path) -> List[Dict]:
    rows = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                try:
                    parsed[k] = float(v)
                except Exception:
                    parsed[k] = v
            rows.append(parsed)
    return rows


def _tier_rank(tier: str) -> int:
    order = {"none": 0, "level1": 1, "level2": 2, "level3": 3}
    return order.get(str(tier), 0)


def _normalize_s_state(state: Optional[str]) -> str:
    s = (str(state or "")).lower()
    if s.startswith("structural"):
        return "structural"
    return s


def _family_level_count(proxy_row: Dict, family: Optional[str]) -> int:
    if not family:
        return 0
    target_key = f"{family}_n_levels_sim".lower()
    for k, v in proxy_row.items():
        if str(k).lower() == target_key:
            try:
                return int(float(v))
            except Exception:
                return 0
    return 0


def _allowed_s2(state: Optional[str], allowed: Set[str]) -> bool:
    return _normalize_s_state(state) in allowed


def _threshold_for(particle: Dict) -> Tuple[int, float, int, Set[str]]:
    """Return (min_tier_rank, max_d_total, min_levels, allowed_s2_states)."""
    ptype = particle.get("type")
    name = particle.get("name")
    if ptype == "meson":
        d_yes = 0.3
        min_levels = 1 if name == "pion" else 2
        return 1, d_yes, min_levels, {"none", "latent", "structural"}
    if ptype == "effective_quark":
        return 1, 0.5, 1, {"none", "latent", "structural"}
    if ptype == "baryon":
        # handled via complex cores
        return 3, float("inf"), 3, {"latent", "structural"}
    # default conservative
    return 2, 0.5, 2, {"none", "latent", "structural"}


def main():
    parser = argparse.ArgumentParser(description="Promote simple blocks from Ola1 sweeps.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--zoo-matches-csv", type=Path, required=True)
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1/simple_blocks.json"))
    parser.add_argument(
        "--digest",
        type=Path,
        default=Path("data/processed/digest/ola1"),
        help="Directory to store promoted block summary.",
    )
    parser.add_argument(
        "--selection-config",
        type=Path,
        default=Path("data/raw/wave1_selection.json"),
        help="Selection thresholds for Ola1->Ola2 physical filters.",
    )
    parser.add_argument(
        "--selection-log",
        type=Path,
        default=Path("data/processed/ola1/ola1_blocks_selection.csv"),
        help="Optional CSV log of accepted/rejected runs.",
    )
    parser.add_argument("--d-total-max", type=float, default=None, help="Deprecated: ignored.")
    parser.add_argument("--max-blocks-per-particle", type=int, default=5000)
    args = parser.parse_args()

    proxies = read_proxies(args.proxies_csv)
    matches = read_matches(args.zoo_matches_csv)
    # selection config
    sel_cfg = DEFAULT_SELECTION
    sel_cfg_path_str = ""
    sel_cfg_hash = ""
    if args.selection_config and args.selection_config.exists():
        try:
            import json as _json

            sel_cfg_path_str = str(args.selection_config)
            sel_text = args.selection_config.read_text()
            sel_cfg_hash = _hash_text(sel_text)
            loaded = _json.loads(sel_text) or {}
            sel_cfg = {**sel_cfg, **loaded}
            if "grades" in loaded:
                sel_cfg["grades"] = {**DEFAULT_SELECTION["grades"], **loaded.get("grades", {})}
            print(f"[promote_simple_blocks] Loaded selection config from {sel_cfg_path_str}")
        except Exception:
            print("[promote_simple_blocks] Failed to load selection config; using defaults.")
            sel_cfg = DEFAULT_SELECTION
    else:
        print("[promote_simple_blocks] Using default selection config.")
    # optional runs JSON to retrieve theta_internal
    runs_json = None
    if args.proxies_csv.name.endswith("_all_runs_proxies.csv"):
        case = args.proxies_csv.stem.replace("_all_runs_proxies", "")
        candidate = Path("data/processed/ola1") / case / "global" / "study05_sweep_results.json"
        if candidate.exists():
            runs_json = candidate
    if runs_json is None:
        candidate = Path(args.proxies_csv).parent.parent / "global" / "study05_sweep_results.json"
        if candidate.exists():
            runs_json = candidate
    run_theta: Dict[str, Dict] = {}
    if runs_json and runs_json.exists():
        try:
            data = json.loads(runs_json.read_text())
            for r in data.get("runs", []):
                run_theta[str(r.get("run_id"))] = r.get("theta_internal")
        except Exception:
            pass
    universe = load_universe(args.sm_universe)
    catalog = universe.get("particles", universe)
    cat_by_name = {p["name"]: p for p in catalog}
    proxy_by_run = {str(r.get("run_id")): r for r in proxies}

    def _to_float(val):
        try:
            return float(val)
        except Exception:
            return None

    def _as_bool(val) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            v = val.strip().lower()
            if v in {"true", "yes", "y", "1"}:
                return True
            if v in {"false", "no", "n", "0", ""}:
                return False
        return bool(val)

    # choose best match per run (lowest finite d_total)
    best_by_run: Dict[str, Dict] = {}
    for m in matches:
        rid = str(m.get("run_id"))
        d_total = m.get("d_total", np.inf)
        if not np.isfinite(d_total):
            continue
        prev = best_by_run.get(rid)
        if prev is None or d_total < prev.get("d_total", np.inf):
            best_by_run[rid] = m
    # ensure all runs from proxies are considered (even without match)
    all_run_ids = {str(r.get("run_id")) for r in proxies}

    blocks: List[Dict] = []
    blocks_per_particle: Dict[str, int] = {}
    rejected_rows: List[Dict] = []
    selection_log_rows: List[Dict[str, object]] = []
    baryon_candidates: List[Dict[str, object]] = []

    for run_id in all_run_ids:
        match = best_by_run.get(run_id)
        target = match.get("target_name") if match else None
        particle = cat_by_name.get(target or "") if match else None
        proxy_row = proxy_by_run.get(str(run_id))
        band_count_struct = proxy_row.get("band_count_structural") if proxy_row else None
        band_count = band_count_struct if band_count_struct is not None else proxy_row.get("band_count") if proxy_row else None
        band_count = _to_float(band_count)
        structural_cap_hit = False
        peak_cap_hit = False
        if proxy_row:
            structural_cap_hit = _as_bool(proxy_row.get("band_structural_cap_hit"))
            peak_cap_hit = _as_bool(proxy_row.get("peak_cap_hit"))
        raw_lock_q = proxy_row.get("lock_quality_Q") if proxy_row else None
        try:
            lock_q = float(raw_lock_q)
        except Exception:
            lock_q = None
        structure_tier = proxy_row.get("structure_tier", "none") if proxy_row else "none"
        reasons: List[str] = []

        def reject(reason: str):
            m = match or {}
            rejected_rows.append(
                {
                    "run_id": run_id,
                    "best_target": target,
                    "type": particle.get("type") if particle else "",
                    "best_d_total": m.get("d_total"),
                    "structure_tier": proxy_row.get("structure_tier") if proxy_row else "",
                    "s2_state": proxy_row.get("s2_state") if proxy_row else "",
                    "enough_levels_full": m.get("enough_levels_full"),
                    "enough_levels_partial": m.get("enough_levels_partial"),
                    "reason": reason,
                }
            )

        # Physical filters (no d_total here)
        try:
            band_count_max = float(sel_cfg.get("band_count_max", 1e9))
        except Exception:
            band_count_max = 1e9
        if band_count is not None and band_count > band_count_max:
            reasons.append(f"too_many_struct_bands>{band_count_max}")
        if structural_cap_hit or peak_cap_hit:
            reasons.append("structural_band_cap_hit")
        if lock_q is not None and lock_q < sel_cfg.get("lock_quality_Q_min", 0.0):
            reasons.append(f"low_Q_lock<{sel_cfg.get('lock_quality_Q_min')}")
        order = {"none": 0, "level1": 1, "level2": 2, "level3": 3}
        min_tier = sel_cfg.get("structure_tier_min", "level1")
        if order.get(str(structure_tier), 0) < order.get(str(min_tier), 0):
            reasons.append(f"tier_below_{min_tier}")

        if match is None or target is None:
            reasons.append("missing_match")
        else:
            try:
                n_levels_sim = float(match.get("n_levels_sim", 0))
            except Exception:
                n_levels_sim = 0.0
            if n_levels_sim <= 0:
                reasons.append("missing_levels")
        if particle is None:
            reasons.append("unknown_particle")
        if proxy_row is None:
            reasons.append("missing_proxy")

        if particle and particle.get("type") == "baryon":
            baryon_candidates.append(
                {
                    "run_id": run_id,
                    "best_target": target,
                    "best_d_total": (match or {}).get("d_total"),
                    "structure_tier": structure_tier,
                    "s2_state": proxy_row.get("s2_state") if proxy_row else "",
                    "band_count_structural": band_count,
                    "band_count": band_count,
                    "lock_quality_Q": lock_q,
                    "lock_quality_S1": proxy_row.get("lock_quality_S1") if proxy_row else None,
                    "lock_quality_S2": proxy_row.get("lock_quality_S2") if proxy_row else None,
                    "reasons": ";".join(reasons),
                    "selection_config_path": sel_cfg_path_str,
                    "selection_config_hash": sel_cfg_hash,
                }
            )

        # log selection decision
        if sel_cfg.get("log_rejections", False):
            selection_log_rows.append(
                {
                    "run_id": run_id,
                    "accepted": 0 if reasons else 1,
                    "reasons": ";".join(reasons) if reasons else "",
                    "band_count": band_count,
                    "lock_quality_Q": lock_q,
                    "structure_tier": structure_tier,
                    "d_total_best": (match or {}).get("d_total"),
                }
            )

        if reasons:
            reject(";".join(reasons))
            continue

        # max blocks per particle
        cnt = blocks_per_particle.get(target, 0)
        if cnt >= args.max_blocks_per_particle:
            reject("max_blocks_reached")
            continue
        blocks_per_particle[target] = cnt + 1

        block_id = f"{target}_block_{cnt+1:04d}"
        d_total = match.get("d_total", np.inf)
        grade_cfg = sel_cfg.get("grades", {})
        grade_A = grade_cfg.get("grade_A_d_total_max", 0.5)
        grade_B = grade_cfg.get("grade_B_d_total_max", 1.5)
        if np.isfinite(d_total) and d_total <= grade_A:
            grade = "A"
        elif np.isfinite(d_total) and d_total <= grade_B:
            grade = "B"
        else:
            grade = "C"
        s2_state_norm = _normalize_s_state(proxy_row.get("s2_state"))
        # derive a band-based s2 state for clarity
        try:
            s2_frac = float(proxy_row.get("s2_band_fraction", 0.0))
        except Exception:
            s2_frac = 0.0
        if s2_frac < 0.02:
            s2_state_band = "none"
        elif s2_frac < 0.12:
            s2_state_band = "latent"
        else:
            s2_state_band = "structural"
        # sanitise match distances (avoid NaN in JSON)
        def _nan_to_none(val):
            try:
                v = float(val)
                return v if np.isfinite(v) else None
            except Exception:
                return None
        d_spacing_clean = _nan_to_none(match.get("d_spacing"))
        d_mass_clean = _nan_to_none(match.get("d_mass"))
        d_total_clean = _nan_to_none(match.get("d_total"))
        block = {
            "block_id": block_id,
            "origin_run_id": proxy_row.get("run_id"),
            "particle_name": target,
            "family": particle.get("family"),
            "type": particle.get("type"),
            "grade": grade,
            "structure_tier": structure_tier,
            "lock_quality": {
                "Q": proxy_row.get("lock_quality_Q"),
                "S1": proxy_row.get("lock_quality_S1"),
                "S2": proxy_row.get("lock_quality_S2"),
            },
            "s2_state": s2_state_norm,
            "s2_state_band": s2_state_band,
            "s2_state_lock": proxy_row.get("s2_state_lock"),
            "band_count": band_count,
            "s2_band_fraction": proxy_row.get("s2_band_fraction"),
            "band_dom_counts_total": proxy_row.get("band_dom_counts_total"),
            "band_dom_counts_structural": proxy_row.get("band_dom_counts_structural"),
            "match_score": {
                "d_total": d_total_clean,
                "d_spacing": d_spacing_clean,
                "d_mass": d_mass_clean,
                "n_levels_sim": match.get("n_levels_sim"),
                "has_enough_levels_full": bool(match.get("enough_levels_full")),
                "has_enough_levels_partial": bool(match.get("enough_levels_partial")),
            },
            "theta_internal": {
                "R_S1_Q": proxy_row.get("R_S1_Q"),
                "R_S2_S1": proxy_row.get("R_S2_S1"),
                "R_S3_S2": proxy_row.get("R_S3_S2"),
                "g_couplings": proxy_row.get("g_couplings"),
                "memory_taus": proxy_row.get("memory_taus"),
                "memory_amps": proxy_row.get("memory_amps"),
                "n_memory_terms": proxy_row.get("n_memory_terms"),
                "memory_terms_by_layer": proxy_row.get("memory_terms_by_layer"),
            },
            "layer_energy_fraction": proxy_row.get("layer_energy_fraction"),
            "participation_entropy": proxy_row.get("participation_entropy"),
            "min_layer_fraction": proxy_row.get("min_layer_fraction"),
        }
        theta_full = run_theta.get(str(proxy_row.get("run_id")))
        if theta_full:
            block["theta_internal"] = theta_full
        blocks.append(block)

    out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(blocks, indent=2))

    # Console summary per particle
    if blocks:
        try:
            print("Block summary (particle_name):")
            by_particle: Dict[str, List[Dict]] = defaultdict(list)
            for b in blocks:
                by_particle[b.get("particle_name")].append(b)
            for name, arr in by_particle.items():
                d_vals = []
                for b in arr:
                    ms = b.get("match_score") or {}
                    dv = ms.get("d_total")
                    try:
                        d_vals.append(float(dv))
                    except Exception:
                        pass
                tiers = Counter(str(b.get("structure_tier")) for b in arr)
                s2_states = Counter(str(b.get("s2_state")) for b in arr)
                if d_vals:
                    stats = (np.min(d_vals), np.median(d_vals), np.max(d_vals))
                    stats_str = f"{stats[0]:.3f}/{stats[1]:.3f}/{stats[2]:.3f}"
                else:
                    stats_str = "nan/nan/nan"
                print(
                    f"- {name}: count={len(arr)} d_total[min/med/max]={stats_str} tiers={dict(tiers)} s2={dict(s2_states)}"
                )
        except Exception:
            pass

    if sel_cfg.get("log_rejections", False) and selection_log_rows and args.selection_log:
        args.selection_log.parent.mkdir(parents=True, exist_ok=True)
        with args.selection_log.open("w", newline="") as f:
            fieldnames = [
                "run_id",
                "accepted",
                "reasons",
                "band_count",
                "lock_quality_Q",
                "structure_tier",
                "d_total_best",
                "selection_config_path",
                "selection_config_hash",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in selection_log_rows:
                row["selection_config_path"] = sel_cfg_path_str
                row["selection_config_hash"] = sel_cfg_hash
                writer.writerow(row)

    # Save rejected candidates for visibility
    if rejected_rows:
        rej_path = out_path.parent / "simple_blocks_rejected.csv"
        with rej_path.open("w", newline="") as f:
            fieldnames = [
                "run_id",
                "best_target",
                "type",
                "best_d_total",
                "structure_tier",
                "s2_state",
                "enough_levels_full",
                "enough_levels_partial",
                "reason",
                "selection_config_path",
                "selection_config_hash",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rejected_rows:
                row["selection_config_path"] = sel_cfg_path_str
                row["selection_config_hash"] = sel_cfg_hash
                writer.writerow(row)

    # Save baryon candidates (excluded from simple blocks but kept as evidence)
    if baryon_candidates:
        baryon_dir = out_path.parent / "blocks"
        baryon_dir.mkdir(parents=True, exist_ok=True)
        baryon_path = baryon_dir / "baryon_candidates.csv"
        with baryon_path.open("w", newline="") as f:
            fieldnames = [
                "run_id",
                "best_target",
                "best_d_total",
                "structure_tier",
                "s2_state",
                "band_count_structural",
                "band_count",
                "lock_quality_Q",
                "lock_quality_S1",
                "lock_quality_S2",
                "reasons",
                "selection_config_path",
                "selection_config_hash",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in baryon_candidates:
                writer.writerow(row)

    # Optional digest copy for a concise promoted-blocks snapshot
    if args.digest:
        args.digest.mkdir(parents=True, exist_ok=True)
        (args.digest / out_path.name).write_text(out_path.read_text())


if __name__ == "__main__":
    main()
