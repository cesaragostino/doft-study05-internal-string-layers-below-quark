"""Match per-run spectra against SM catalog (Ola1)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from study06.sm_matching import compute_match_stats, extract_levels, load_universe


def parse_proxies_csv(path: Path) -> List[Dict]:
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


def _to_float(value) -> Optional[float]:
    try:
        f = float(value)
        if np.isfinite(f):
            return f
    except Exception:
        pass
    return None


def _to_int(value) -> Optional[int]:
    f = _to_float(value)
    if f is None:
        return None
    try:
        return int(round(f))
    except Exception:
        return None


def _load_harmonic_mode_config(path: Path) -> Dict:
    defaults = {
        "schema_version": "harmonic_mode_matching_v1",
        "sector_confidence_min": 0.60,
        "policy_on_low_conf": "ignore",
        "action_on_mismatch": "reject",
    }
    if not path or not path.exists():
        return defaults
    try:
        data = json.loads(path.read_text())
        out = defaults.copy()
        out.update({k: v for k, v in data.items() if v is not None})
        return out
    except Exception:
        return defaults


def _evaluate_harmonic_policy(
    row: Dict, particle: Dict, config: Dict
) -> Tuple[str, str, str, List[int], Optional[int], Optional[str], Optional[float]]:
    policy = (particle.get("doft") or {}).get("postulate_lock_mode") or {}
    preferred_parity = str(policy.get("preferred_parity", "any")).lower()
    allowed_k = policy.get("allowed_k", [1, 2, 3, 4, 5])
    if not isinstance(allowed_k, list):
        allowed_k = [1, 2, 3, 4, 5]

    k_used = _to_int(row.get("k_used"))
    dominant_parity = row.get("dominant_parity")
    if isinstance(dominant_parity, str):
        dominant_parity = dominant_parity.lower().strip()
    sector_conf = _to_float(row.get("sector_confidence"))
    conf_min = _to_float(config.get("sector_confidence_min")) or 0.0
    low_conf_policy = str(config.get("policy_on_low_conf", "ignore")).lower()
    action_on_mismatch = str(config.get("action_on_mismatch", "reject")).lower()

    if sector_conf is None or k_used is None or dominant_parity not in {"odd", "even"}:
        return ("ignore", "missing_fields", preferred_parity, allowed_k, k_used, dominant_parity, sector_conf)
    if sector_conf < conf_min:
        return (low_conf_policy, "low_confidence", preferred_parity, allowed_k, k_used, dominant_parity, sector_conf)

    parity_mismatch = preferred_parity in {"odd", "even"} and dominant_parity != preferred_parity
    k_mismatch = allowed_k and k_used not in allowed_k
    if parity_mismatch or k_mismatch:
        reasons = []
        if parity_mismatch:
            reasons.append("parity_mismatch")
        if k_mismatch:
            reasons.append("k_mismatch")
        return (action_on_mismatch, "|".join(reasons), preferred_parity, allowed_k, k_used, dominant_parity, sector_conf)
    return ("pass", "", preferred_parity, allowed_k, k_used, dominant_parity, sector_conf)


def _fill_harmonic_fields(rows: List[Dict], hbar_sim: Optional[float]) -> int:
    filled = 0
    k_tol = 0.07
    for row in rows:
        k_used = _to_int(row.get("k_used"))
        dominant_parity = row.get("dominant_parity")
        sector_conf = _to_float(row.get("sector_confidence"))
        if k_used is not None and dominant_parity and sector_conf is not None:
            continue

        omega_raw = _to_float(row.get("omega_ref") or row.get("omega_ref_interp"))
        if omega_raw is None:
            continue
        energies = extract_levels(row.get("band_energies_gev", "[]"))
        energies = [e for e in energies if np.isfinite(e)]
        if not energies or not hbar_sim:
            continue
        omega_band = statistics.median(energies) / float(hbar_sim)
        if omega_band <= 0:
            continue
        ratio = omega_raw / omega_band
        k_scores = {}
        score_sum = 0.0
        for k in range(1, 6):
            score = math.exp(-((ratio - k) ** 2) / (2 * (k_tol**2)))
            k_scores[k] = score
            score_sum += score
        k_used = max(k_scores, key=lambda k: k_scores[k])
        dominant_parity = "odd" if k_used % 2 == 1 else "even"
        sector_conf = (k_scores[k_used] / score_sum) if score_sum > 0 else 0.0
        omega_eff = omega_raw / float(k_used)
        mass_sim_used = hbar_sim * omega_eff if hbar_sim is not None else None

        row["k_used"] = k_used
        row["dominant_parity"] = dominant_parity
        row["sector_confidence"] = f"{sector_conf:.6g}"
        row["omega_eff"] = f"{omega_eff:.12g}"
        if mass_sim_used is not None:
            row["mass_sim_used_gev"] = f"{mass_sim_used:.12g}"
        filled += 1
    return filled


def main():
    parser = argparse.ArgumentParser(description="Match spectra against SM catalog (Ola1).")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument(
        "--harmonic-mode-config",
        type=Path,
        default=Path("data/raw/harmonic_mode_matching.json"),
        help="Config for harmonic mode policy matching (optional).",
    )
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1"))
    parser.add_argument("--digest", type=Path, default=Path("data/processed/digest/ola1"), help="Directory to store summary outputs.")
    parser.add_argument(
        "--hbar-sim",
        type=Path,
        default=None,
        help="Optional path to hbar_sim_calibration.json to compute mass_sim_gev when proxies lack it.",
    )
    parser.add_argument(
        "--use-mass-sim",
        action="store_true",
        help="Usar mass_sim_gev/omega_ref en lugar de band_energies_gev para el matching. Útil en fase 2/3.",
    )
    parser.add_argument(
        "--update-proxies",
        action="store_true",
        help="Escribir k_used/parity/sector_confidence/mass_sim_used_gev en el proxies CSV.",
    )
    args = parser.parse_args()

    universe = load_universe(args.sm_universe)
    catalog = universe.get("particles", [])
    harmonic_cfg = _load_harmonic_mode_config(args.harmonic_mode_config)
    rows = parse_proxies_csv(args.proxies_csv)
    match_rows: List[Dict] = []
    best_rows: List[Dict] = []

    hbar_sim = None
    if args.hbar_sim and args.hbar_sim.exists():
        try:
            data_h = json.loads(args.hbar_sim.read_text())
            hbar_sim = float(data_h.get("hbar_sim"))
        except Exception:
            hbar_sim = None
    else:
        # fallback: default locations
        for cand in [Path("data/processed/ola1/hbar_sim_calibration.json"), Path("data/processed/ola1-chaos/hbar_sim_calibration.json")]:
            if cand.exists():
                try:
                    data_h = json.loads(cand.read_text())
                    hbar_sim = float(data_h.get("hbar_sim"))
                    break
                except Exception:
                    hbar_sim = None

    filled = _fill_harmonic_fields(rows, hbar_sim)
    if filled:
        print(f"[match_sm_ola1] harmonic fields filled in {filled} rows")

    for row in rows:
        mass_sim = None
        if args.use_mass_sim:
            mass_sim = row.get("mass_sim_used_gev")
            if mass_sim is None:
                mass_sim = row.get("mass_sim_gev")
            if mass_sim is None and hbar_sim is not None:
                omega_ref = row.get("omega_ref") or row.get("omega_ref_interp")
                try:
                    omega_ref_f = float(omega_ref)
                    if np.isfinite(omega_ref_f):
                        mass_sim = hbar_sim * omega_ref_f
                except Exception:
                    pass
        levels_full = []
        if args.use_mass_sim and mass_sim is not None:
            try:
                m_val = float(mass_sim)
                if np.isfinite(m_val):
                    levels_full = [m_val]
            except Exception:
                levels_full = []
        if not levels_full:
            levels_full = extract_levels(row.get("band_energies_gev", "[]"))
        run_id = row.get("run_id", row.get("id", len(match_rows)))
        best = {"run_id": run_id, "best_target": None, "best_family": None, "best_d_total": float("inf")}
        best_raw = float("inf")
        second: Dict[str, object] = {"target": None, "family": None, "d_total": float("inf")}
        for particle in catalog:
            levels = [e for e in levels_full if _in_window(e, particle.get("energy_window", [0.0, 10.0]))]
            res = compute_match_stats(levels, particle.get("masses_gev", []), particle.get("tolerances", {}))
            if np.isfinite(res["d_total"]) and res["d_total"] < best_raw:
                best_raw = res["d_total"]
            (
                policy_action,
                policy_reason,
                policy_preferred_parity,
                policy_allowed_k,
                run_k_used,
                run_parity,
                run_conf,
            ) = _evaluate_harmonic_policy(row, particle, harmonic_cfg)
            policy_rejected = policy_action == "reject"
            match_rows.append(
                {
                    "run_id": run_id,
                    "target_name": particle["name"],
                    "family": particle.get("family"),
                    "type": particle.get("type"),
                    "jpc": particle.get("jpc"),
                    "d_total": res["d_total"],
                    "d_spacing": res["d_spacing"],
                    "d_mass": res["d_mass"],
                    "enough_levels_full": int(res["has_enough_levels_full"]),
                    "enough_levels_partial": int(res["has_enough_levels_partial"]),
                    "n_levels_sim": res["n_levels_sim"],
                    "policy_status": policy_action,
                    "policy_reason": policy_reason,
                    "policy_rejected": int(policy_rejected),
                    "policy_preferred_parity": policy_preferred_parity,
                    "policy_allowed_k": json.dumps(policy_allowed_k, ensure_ascii=True),
                    "run_dominant_parity": run_parity,
                    "run_k_used": run_k_used,
                    "run_sector_confidence": run_conf,
                }
            )
            if np.isfinite(res["d_total"]):
                if res["d_total"] < best["best_d_total"]:
                    # shift best to second
                    second = {
                        "target": best.get("best_target"),
                        "family": best.get("best_family"),
                        "d_total": best.get("best_d_total"),
                    }
                    best.update(
                        {
                            "best_target": particle["name"],
                            "best_family": particle.get("family"),
                            "best_d_total": res["d_total"],
                        }
                    )
                elif res["d_total"] < second.get("d_total", float("inf")):
                    second = {"target": particle["name"], "family": particle.get("family"), "d_total": res["d_total"]}
        # margin
        delta_margin = None
        if np.isfinite(best.get("best_d_total", np.inf)) and np.isfinite(second.get("d_total", np.inf)):
            delta_margin = second.get("d_total") - best.get("best_d_total")
        best["second_best_target"] = second.get("target")
        best["second_best_family"] = second.get("family")
        best["second_best_d_total"] = second.get("d_total")
        best["delta_margin"] = delta_margin
        best_rows.append(best)

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    zoo_path = out_dir / "zoo_matches.csv"
    best_path = out_dir / "best_match_per_run.csv"
    with zoo_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=match_rows[0].keys())
        writer.writeheader()
        writer.writerows(match_rows)

    with best_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=best_rows[0].keys())
        writer.writeheader()
        writer.writerows(best_rows)

    # Optional digest copy for quick lookup of best matches
    if args.digest:
        args.digest.mkdir(parents=True, exist_ok=True)
        digest_best = args.digest / best_path.name
        digest_best.write_text(best_path.read_text())

    if args.update_proxies:
        fieldnames = sorted({k for r in rows for k in r.keys()})
        with args.proxies_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[match_sm_ola1] proxies updated -> {args.proxies_csv}")



def _in_window(val: float, window):
    try:
        lo, hi = window
        v = float(val)
        return lo <= v <= hi
    except Exception:
        return False


if __name__ == "__main__":
    main()
