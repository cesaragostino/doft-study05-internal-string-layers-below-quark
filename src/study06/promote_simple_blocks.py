"""Promote simple blocks (Ola1) from sweep proxies and SM matches."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np


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
        if name == "pion":
            return 1, 2.0, 1, {"none", "latent", "structural"}
        if name == "rho":
            return 1, 3.0, 2, {"latent", "structural"}
        return 1, 3.0, 2, {"latent", "structural"}
    if ptype == "baryon":
        return 2, 4.0, 3, {"latent", "structural"}
    # default conservative
    return 2, 3.0, 2, {"latent", "structural"}


def main():
    parser = argparse.ArgumentParser(description="Promote simple blocks from Ola1 sweeps.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--zoo-matches-csv", type=Path, required=True)
    parser.add_argument("--sm-catalog", type=Path, default=Path("data/raw/sm_catalog/particles.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/blocks/simple_blocks.json"))
    parser.add_argument("--digest", type=Path, default=Path("data/processed/digest/blocks"), help="Directory to store promoted block summary.")
    parser.add_argument("--d-total-max", type=float, default=None, help="Deprecated: per-particle thresholds are used instead.")
    parser.add_argument("--max-blocks-per-particle", type=int, default=10)
    args = parser.parse_args()

    proxies = read_proxies(args.proxies_csv)
    matches = read_matches(args.zoo_matches_csv)
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
    catalog = json.loads(args.sm_catalog.read_text())
    cat_by_name = {p["name"]: p for p in catalog}
    proxy_by_run = {str(r.get("run_id")): r for r in proxies}

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

    blocks: List[Dict] = []
    blocks_per_particle: Dict[str, int] = {}
    rejected_rows: List[Dict] = []

    for run_id, match in best_by_run.items():
        target = match.get("target_name")
        particle = cat_by_name.get(target or "")
        proxy_row = proxy_by_run.get(str(run_id))

        def reject(reason: str):
            rejected_rows.append(
                {
                    "run_id": run_id,
                    "best_target": target,
                    "type": particle.get("type") if particle else "",
                    "best_d_total": match.get("d_total"),
                    "structure_tier": proxy_row.get("structure_tier") if proxy_row else "",
                    "s2_state": proxy_row.get("s2_state") if proxy_row else "",
                    "enough_levels": match.get("enough_levels"),
                    "reason": reason,
                }
            )

        if particle is None:
            reject("unknown_particle")
            continue
        if proxy_row is None:
            reject("missing_proxy")
            continue

        min_tier_rank, max_d_total, min_levels, allowed_s2 = _threshold_for(particle)
        structure_tier = proxy_row.get("structure_tier", "none")
        if _tier_rank(structure_tier) < min_tier_rank:
            reject("tier_too_low")
            continue

        d_total = match.get("d_total", np.inf)
        if not np.isfinite(d_total) or d_total > max_d_total:
            reject("distance_high")
            continue

        s2_state_norm = _normalize_s_state(proxy_row.get("s2_state"))
        if not _allowed_s2(s2_state_norm, allowed_s2):
            reject("s2_state_blocked")
            continue

        # enough_levels: use zoo flag as primary, but allow per-particle relaxation via n_levels_sim
        enough_flag = bool(match.get("enough_levels"))
        if not enough_flag:
            levels = _family_level_count(proxy_row, match.get("family"))
            enough_flag = levels >= min_levels
        if not enough_flag:
            reject("not_enough_levels")
            continue
        # max blocks per particle
        cnt = blocks_per_particle.get(target, 0)
        if cnt >= args.max_blocks_per_particle:
            reject("max_blocks_reached")
            continue
        blocks_per_particle[target] = cnt + 1

        block_id = f"{target}_block_{cnt+1:04d}"
        block = {
            "block_id": block_id,
            "origin_run_id": proxy_row.get("run_id"),
            "particle_name": target,
            "family": particle.get("family"),
            "type": particle.get("type"),
            "structure_tier": structure_tier,
            "lock_quality": {
                "Q": proxy_row.get("lock_quality_Q"),
                "S1": proxy_row.get("lock_quality_S1"),
                "S2": proxy_row.get("lock_quality_S2"),
            },
            "s2_state": s2_state_norm,
            "s2_band_fraction": proxy_row.get("s2_band_fraction"),
            "match_score": {
                "d_total": match.get("d_total"),
                "d_spacing": match.get("d_spacing"),
                "d_mass": match.get("d_mass"),
            },
            "theta_internal": {
                "R_S1_Q": proxy_row.get("R_S1_Q"),
                "R_S2_S1": proxy_row.get("R_S2_S1"),
                "R_S3_S2": proxy_row.get("R_S3_S2"),
                "g_couplings": proxy_row.get("g_couplings"),
                "memory_taus": proxy_row.get("memory_taus"),
                "memory_amps": proxy_row.get("memory_amps"),
            },
        }
        theta_full = run_theta.get(str(proxy_row.get("run_id")))
        if theta_full:
            block["theta_internal"] = theta_full
        blocks.append(block)

    out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(blocks, indent=2))

    # Save rejected candidates for visibility
    if rejected_rows:
        rej_path = out_path.parent / "simple_blocks_rejected.csv"
        with rej_path.open("w", newline="") as f:
            fieldnames = ["run_id", "best_target", "type", "best_d_total", "structure_tier", "s2_state", "enough_levels", "reason"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rejected_rows:
                writer.writerow(row)

    # Optional digest copy for a concise promoted-blocks snapshot
    if args.digest:
        args.digest.mkdir(parents=True, exist_ok=True)
        (args.digest / out_path.name).write_text(out_path.read_text())


if __name__ == "__main__":
    main()
