"""Catalog complex cores (strong S2, level3) from Ola1 proxies."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from study06.sm_matching import compute_match_stats, extract_levels, load_universe


def _read_rows(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed: Dict[str, Any] = {}
            for k, v in row.items():
                try:
                    parsed[k] = float(v)
                except Exception:
                    parsed[k] = v
            rows.append(parsed)
    return rows


def _load_run_theta(proxies_path: Path) -> Dict[str, Dict[str, Any]]:
    """Try to locate sweep results to grab theta_internal per run."""
    case = proxies_path.stem.replace("_all_runs_proxies", "")
    candidates = [
        proxies_path.parent.parent / "global" / "study05_sweep_results.json",
        Path("data/processed/ola1") / case / "global" / "study05_sweep_results.json",
        Path("data/processed") / case / "global" / "study05_sweep_results.json",
        Path("data/raw") / case / "global" / "study05_sweep_results.json",
    ]
    for cand in candidates:
        if cand.exists():
            try:
                data = json.loads(cand.read_text())
                return {str(r.get("run_id")): r.get("theta_internal") for r in data.get("runs", [])}
            except Exception:
                return {}
    return {}


def main():
    parser = argparse.ArgumentParser(description="Catalog complex cores (strong S2, level3) from Ola1 proxies.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1/blocks/complex_cores.json"))
    parser.add_argument("--d-yes-baryon-core", type=float, default=0.6)
    args = parser.parse_args()

    rows = _read_rows(args.proxies_csv)
    run_theta = _load_run_theta(args.proxies_csv)
    uni = load_universe(args.sm_universe)
    baryons = [p for p in uni.get("particles", []) if p.get("type") == "baryon"]

    cores: List[Dict[str, Any]] = []
    for r in rows:
        tier = str(r.get("structure_tier", "")).lower()
        s2_state = str(r.get("s2_state", "")).lower()
        if not (tier == "level3" and s2_state.startswith("structural")):
            continue
        levels = extract_levels(r.get("band_energies_gev", "[]"))
        best = None
        for baryon in baryons:
            lvls = [e for e in levels if _in_window(e, baryon.get("energy_window", [0.0, 10.0]))]
            match = compute_match_stats(lvls, baryon.get("masses_gev", []), baryon.get("tolerances", {}))
            if not _is_finite(match.get("d_total")):
                continue
            if match["d_total"] >= args.d_yes_baryon_core:
                continue
            if best is None or match["d_total"] < best["match"]["d_total"]:
                best = {"target": baryon, "match": match}
        if not best:
            continue
        rid = int(float(r.get("run_id")))
        core_entry = {
            "core_id": f"core3L_run_{rid:04d}",
            "origin_run_id": rid,
            "matched_particle": best["target"]["name"],
            "family": best["target"].get("family"),
            "type": "baryon_candidate",
            "structure": {
                "structure_tier": r.get("structure_tier"),
                "lock_quality": {
                    "Q": r.get("lock_quality_Q"),
                    "S1": r.get("lock_quality_S1"),
                    "S2": r.get("lock_quality_S2"),
                },
                "s2_band_fraction": r.get("s2_band_fraction"),
                "s2_state": r.get("s2_state"),
            },
            "match_score": {
                "d_total": best["match"]["d_total"],
                "d_spacing": best["match"]["d_spacing"],
                "d_mass": best["match"]["d_mass"],
                "n_levels_sim": best["match"]["n_levels_sim"],
                "has_enough_levels_full": best["match"]["has_enough_levels_full"],
                "has_enough_levels_partial": best["match"]["has_enough_levels_partial"],
                "target_name": best["target"]["name"],
            },
            "theta_internal": run_theta.get(str(rid)),
        }
        cores.append(core_entry)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(cores, indent=2))


def _in_window(val: float, window):
    try:
        lo, hi = window
        v = float(val)
        return lo <= v <= hi
    except Exception:
        return False


def _is_finite(v: Any) -> bool:
    try:
        return float(v) == float(v)
    except Exception:
        return False


if __name__ == "__main__":
    main()
