"""Generate DOF DNA catalog from sweep proxies (no SM naming)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from ola1.sm_matching import compute_match_stats, extract_levels, load_universe


def _to_float(value) -> Optional[float]:
    try:
        f = float(value)
        if np.isfinite(f):
            return f
    except Exception:
        pass
    return None


R1_EDGES = [0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 10.0]
S2S1_EDGES = [-1.0, 0.90, 1.05, 1.20, 10.0]
BAND_COUNT_EDGES = [-1, 10, 15, 20, 25, 31]
RHO_LOCK_EDGES = [0, 0.2, 0.3, 0.4, 0.5, 1.0]

BAND_LABELS = ["lowBands", "midBands", "hiBands", "vhiBands", "maxBands"]


def _is_missing(value: Optional[float]) -> bool:
    return value is None or not np.isfinite(value)


def _grade_from_dof(lock_quality_q: Optional[float], participation_entropy: Optional[float], rho_lock: Optional[float]) -> str:
    if _is_missing(lock_quality_q) or _is_missing(participation_entropy):
        return "C"
    if lock_quality_q < 0.995 or participation_entropy > 0.03:
        return "C"
    if lock_quality_q >= 0.998 and participation_entropy <= 0.01 and rho_lock is not None and np.isfinite(rho_lock):
        if rho_lock >= 0.16:
            return "A"
    return "B"


def _bin_index(value: Optional[float], edges: List[float]) -> str:
    if value is None or not np.isfinite(value):
        return "na"
    v = float(value)
    if v < edges[0] or v > edges[-1]:
        return "oob"
    for idx, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        if idx == len(edges) - 2:
            if lo <= v <= hi:
                return str(idx)
        else:
            if lo <= v < hi:
                return str(idx)
    return "oob"


def _label_from_bin(bin_idx: str, labels: List[str]) -> str:
    try:
        idx = int(bin_idx)
    except Exception:
        return "unknown"
    if 0 <= idx < len(labels):
        return labels[idx]
    return "unknown"


def _s1q_label(bin_idx: str) -> str:
    try:
        idx = int(bin_idx)
    except Exception:
        return "S1Q_binNA"
    return f"S1Q_bin{idx}"


def _family_id(r1_bin: str, s2s1_bin: str, band_bin: str, rho_bin: str, dof_grade: str) -> str:
    fp = f"r1={r1_bin}|r2={s2s1_bin}|bc={band_bin}|rho={rho_bin}|grade={dof_grade}"
    digest = hashlib.sha1(fp.encode("ascii")).hexdigest()[:4].upper()
    return f"F{digest}"


def _family_friendly(
    dof_grade: str,
    lock_quality_q: Optional[float],
    participation_entropy: Optional[float],
    band_bin: str,
    r1_bin: str,
    s2s1_bin: str,
) -> str:
    if dof_grade == "C":
        return "REJECTED"
    lock_label = "LOCKED" if lock_quality_q is not None and np.isfinite(lock_quality_q) and lock_quality_q >= 0.998 else "SOFT_LOCK"
    ent_label = (
        "lowEnt"
        if participation_entropy is not None
        and np.isfinite(participation_entropy)
        and participation_entropy <= 0.01
        else "midEnt"
    )
    band_label = _label_from_bin(band_bin, BAND_LABELS)
    r1_label = _s1q_label(r1_bin)
    return f"{lock_label}_{ent_label}_{band_label}_{r1_label}_S2S1_bin{s2s1_bin}"


def _fill_harmonic_fields(rows: List[Dict], hbar_sim: Optional[float]) -> int:
    filled = 0
    k_tol = 0.07
    for row in rows:
        k_used = row.get("k_used")
        dominant_parity = row.get("dominant_parity")
        sector_conf = row.get("sector_confidence")
        if k_used not in (None, "", "nan") and dominant_parity and sector_conf not in (None, "", "nan"):
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


def _cluster_id(r1: Optional[float], r2: Optional[float]) -> str:
    if r1 is None or r2 is None:
        return ""
    return f"R1_{r1!r}_R2_{r2!r}"


def _omega_ref_proxy(row: Dict[str, object]) -> float:
    omega_ref_interp = _to_float(row.get("omega_ref_interp"))
    if omega_ref_interp is not None:
        return omega_ref_interp
    omega_ref = _to_float(row.get("omega_ref"))
    if omega_ref is not None:
        return omega_ref
    raise RuntimeError(f"omega_ref_proxy missing or non-finite for run_id={row.get('run_id')}")


def _genes_min(row: Dict[str, object], omega_ref_proxy: float) -> str:
    payload = {
        "omega_ref_proxy": omega_ref_proxy,
        "rho_lock": _to_float(row.get("rho_lock")),
        "lock_quality_S1": _to_float(row.get("lock_quality_S1")),
        "participation_entropy": _to_float(row.get("participation_entropy")),
        "omega_eff": _to_float(row.get("omega_eff")),
        "structure_tier": str(row.get("structure_tier") or ""),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate DOF DNA catalog from proxies.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1/dof_dna_catalog.csv"))
    parser.add_argument("--hbar-sim", type=Path, default=None)
    parser.add_argument("--use-mass-sim", action="store_true", help="Ignored for DNA; kept for compatibility.")
    parser.add_argument("--with-sm-trace", action="store_true", help="Include SM trace columns for audit.")
    parser.add_argument("--update-proxies", action="store_true")
    parser.add_argument("--cluster-radii", action="store_true")
    args = parser.parse_args()

    with args.proxies_csv.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    hbar_sim = None
    if args.hbar_sim and args.hbar_sim.exists():
        try:
            data_h = json.loads(args.hbar_sim.read_text())
            hbar_sim = float(data_h.get("hbar_sim"))
        except Exception:
            hbar_sim = None

    filled = _fill_harmonic_fields(rows, hbar_sim)
    if filled:
        print(f"[dof_dna] harmonic fields filled in {filled} rows")

    dna_rows: List[Dict[str, object]] = []
    if args.use_mass_sim:
        print("[dof_dna] --use-mass-sim ignored: DNA catalog uses raw band_energies_gev only.")

    catalog = []
    if args.with_sm_trace:
        universe = load_universe(args.sm_universe)
        catalog = universe.get("particles", [])

    for row in rows:
        run_id = row.get("run_id")
        if run_id in (None, ""):
            raise RuntimeError("DNA catalog row missing run_id")
        levels_full = extract_levels(row.get("band_energies_gev", "[]"))

        r1 = _to_float(row.get("R_S1_Q"))
        r2 = _to_float(row.get("R_S2_S1"))
        band_count = _to_float(row.get("band_count"))
        rho_lock = _to_float(row.get("rho_lock"))
        lock_quality_q = _to_float(row.get("lock_quality_Q"))
        participation_entropy = _to_float(row.get("participation_entropy"))
        dof_grade = _grade_from_dof(lock_quality_q, participation_entropy, rho_lock)
        r1_bin = _bin_index(r1, R1_EDGES)
        s2s1_bin = _bin_index(r2, S2S1_EDGES)
        band_bin = _bin_index(band_count, BAND_COUNT_EDGES)
        rho_bin = _bin_index(rho_lock, RHO_LOCK_EDGES)
        dof_family_id = _family_id(r1_bin, s2s1_bin, band_bin, rho_bin, dof_grade)
        dof_family_friendly = _family_friendly(
            dof_grade,
            lock_quality_q,
            participation_entropy,
            band_bin,
            r1_bin,
            s2s1_bin,
        )

        sm_best_name = ""
        sm_d_total = None
        sm_jpc = ""
        if args.with_sm_trace:
            best_raw = float("inf")
            for particle in catalog:
                levels = [e for e in levels_full if _in_window(e, particle.get("energy_window", [0.0, 10.0]))]
                res = compute_match_stats(levels, particle.get("masses_gev", []), particle.get("tolerances", {}))
                if np.isfinite(res["d_total"]) and res["d_total"] < best_raw:
                    best_raw = res["d_total"]
                    sm_best_name = str(particle.get("name", ""))
                    sm_jpc = str(particle.get("jpc", "") or "")
            sm_d_total = best_raw if np.isfinite(best_raw) else None
        cluster_id = _cluster_id(r1, r2) if args.cluster_radii else ""
        omega_ref_proxy = _omega_ref_proxy(row)
        genes_min = _genes_min(row, omega_ref_proxy)
        dna_rows.append(
            {
                "run_id": run_id,
                "dof_grade": dof_grade,
                "dof_family_id": dof_family_id,
                "dof_family_friendly": dof_family_friendly,
                "omega_ref_proxy": omega_ref_proxy,
                "genes_min": genes_min,
                "R_S1_Q": row.get("R_S1_Q"),
                "R_S2_S1": row.get("R_S2_S1"),
                "dominant_parity": row.get("dominant_parity"),
                "lock_Q0_S1_0_1-1_ratio": row.get("lock_Q0_S1_0_1-1_ratio"),
                "band_count": row.get("band_count"),
                "rho_lock": row.get("rho_lock"),
                "lock_quality_Q": row.get("lock_quality_Q"),
                "participation_entropy": row.get("participation_entropy"),
                "dna_cluster_id": cluster_id,
            }
        )
        if args.with_sm_trace:
            dna_rows[-1]["sm_best_name"] = sm_best_name
            dna_rows[-1]["sm_d_total"] = sm_d_total
            dna_rows[-1]["sm_jpc"] = sm_jpc

    if args.cluster_radii:
        counts: Dict[str, int] = {}
        for r in dna_rows:
            cid = r.get("dna_cluster_id") or ""
            counts[cid] = counts.get(cid, 0) + 1
        for r in dna_rows:
            r["dna_cluster_size"] = counts.get(r.get("dna_cluster_id") or "", 0)

    dna_rows.sort(key=lambda r: (r.get("run_id") is None, r.get("run_id")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_id",
        "dof_grade",
        "dof_family_id",
        "dof_family_friendly",
        "omega_ref_proxy",
        "genes_min",
        "R_S1_Q",
        "R_S2_S1",
        "dominant_parity",
        "lock_Q0_S1_0_1-1_ratio",
        "band_count",
        "rho_lock",
        "lock_quality_Q",
        "participation_entropy",
        "dna_cluster_id",
    ]
    if args.cluster_radii:
        fieldnames.append("dna_cluster_size")
    if args.with_sm_trace:
        fieldnames.extend(["sm_best_name", "sm_d_total", "sm_jpc"])
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dna_rows)
    print(f"[dof_dna] catalog escrito -> {args.output}")

    if args.update_proxies:
        fieldnames = sorted({k for r in rows for k in r.keys()})
        with args.proxies_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[dof_dna] proxies updated -> {args.proxies_csv}")


def _in_window(val: float, window):
    try:
        lo, hi = window
        v = float(val)
        return lo <= v <= hi
    except Exception:
        return False


if __name__ == "__main__":
    main()
