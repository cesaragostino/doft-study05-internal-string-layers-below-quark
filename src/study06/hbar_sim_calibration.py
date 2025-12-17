"""Calibrate hbar_sim from Ola1 blocks using omega_ref -> mass_sim_gev."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from study06.sm_matching import load_universe


def _to_float(val: Any) -> float | None:
    try:
        v = float(val)
    except Exception:
        return None
    return v if np.isfinite(v) else None


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"{path} no contiene una lista de bloques.")
    return data


def _save_blocks(path: Path, blocks: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blocks, indent=2))


def _load_sm_masses(sm_path: Path) -> Dict[str, float]:
    uni = load_universe(sm_path)
    catalog = uni.get("particles", [])
    masses = {}
    for p in catalog:
        name = p.get("name")
        m = _to_float(p.get("sm_mass_gev"))
        if name and m is not None:
            masses[name] = m
    return masses


def _weighted_median(vals: np.ndarray, weights: np.ndarray) -> float | None:
    if vals.size == 0 or weights.size == 0:
        return None
    order = np.argsort(vals)
    vals_sorted = vals[order]
    w_sorted = weights[order]
    cumsum = np.cumsum(w_sorted)
    cutoff = 0.5 * np.sum(w_sorted)
    idx = np.searchsorted(cumsum, cutoff)
    idx = min(idx, vals_sorted.size - 1)
    return float(vals_sorted[idx])


def _write_calibration(path: Path, payload: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
    print(f"[hbar_sim] escrito {path} (hbar_sim={payload.get('hbar_sim'):.6g}, n_used={payload.get('n_used')}, dropped={payload.get('n_rejected')})")


def _update_proxies(proxies_path: Path, hbar: float) -> None:
    rows: List[Dict[str, Any]] = []
    with proxies_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            mass_row = row.get("mass_sim_gev")
            omega_row = _to_float(row.get("omega_ref"))
            mass_val = _to_float(mass_row)
            if mass_val is None and omega_row is not None and hbar is not None:
                mass_val = hbar * omega_row
            row["mass_sim_gev"] = mass_val if mass_val is not None else ""
            rows.append(row)
    fieldnames = sorted({k for r in rows for k in r.keys()})
    with proxies_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[hbar_sim] proxies actualizados con mass_sim_gev -> {proxies_path}")


def main():
    parser = argparse.ArgumentParser(description="Calibrar hbar_sim a partir de omega_ref en Ola1.")
    parser.add_argument("--blocks", type=Path, default=Path("data/processed/ola1/simple_blocks.json"))
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ola1/hbar_sim_calibration.json"))
    parser.add_argument("--proxies-csv", type=Path, default=None, help="Opcional: actualizar mass_sim_gev en proxies.")
    parser.add_argument("--blocks-output", type=Path, default=None, help="Opcional: escribir bloques enriquecidos en otro path.")
    args = parser.parse_args()

    blocks = _load_blocks(args.blocks)
    sm_masses = _load_sm_masses(args.sm_universe)

    candidates = []
    for b in blocks:
        grade = str(b.get("grade", "")).upper()
        ms = b.get("match_score") or {}
        if grade not in {"A", "B"}:
            continue
        if not bool(ms.get("has_enough_levels_full")):
            continue
        omega = _to_float(b.get("omega_ref")) or _to_float(b.get("omega_ref_interp"))
        if omega is None or omega <= 0:
            continue
        pname = b.get("particle_name")
        m_sm = sm_masses.get(str(pname))
        if m_sm is None:
            continue
        q_lock = None
        lq = b.get("lock_quality") or {}
        try:
            q_lock = float(lq.get("Q"))
        except Exception:
            q_lock = None
        d_total = _to_float(ms.get("d_total")) or 0.0
        candidates.append({"block": b, "omega_ref": omega, "sm_mass": m_sm, "q_lock": q_lock, "d_total": d_total})

    if not candidates:
        raise ValueError("hbar_sim: no hay bloques elegibles con omega_ref y sm_mass_gev.")

    # cluster fundamental: omega0 = p10; keep within ±10%
    omega_all = np.array([c["omega_ref"] for c in candidates if c["omega_ref"] is not None], dtype=float)
    if omega_all.size == 0:
        raise ValueError("hbar_sim: sin omegas válidos.")
    omega0 = float(np.percentile(omega_all, 10))
    cluster_tol = 0.10
    clustered = [c for c in candidates if abs(c["omega_ref"] - omega0) / max(omega0, 1e-9) <= cluster_tol]
    if not clustered:
        clustered = candidates

    # compute h_i = m_sm / omega
    h_vals = []
    weights = []
    kept = []
    for c in clustered:
        h_i = c["sm_mass"] / c["omega_ref"]
        if h_i <= 0 or not np.isfinite(h_i):
            continue
        h_vals.append(h_i)
        q_lock = c.get("q_lock") if c.get("q_lock") is not None else 0.0
        d_total = c.get("d_total") if c.get("d_total") is not None else 0.0
        w = float(q_lock) / (1.0 + float(d_total)) if (q_lock is not None) else 1.0
        if not np.isfinite(w) or w <= 0:
            w = 1.0
        weights.append(w)
        kept.append(c)
    h_vals = np.array(h_vals, dtype=float)
    weights = np.array(weights, dtype=float)
    if h_vals.size == 0:
        raise ValueError("hbar_sim: no se pudieron construir h_i válidos.")
    # trim percentiles
    lo, hi = np.percentile(h_vals, [10, 90])
    mask = (h_vals >= lo) & (h_vals <= hi)
    h_trim = h_vals[mask]
    w_trim = weights[mask]
    kept_trim = [k for k, m in zip(kept, mask) if m]
    hbar_final = _weighted_median(h_trim, w_trim)
    if hbar_final is None:
        raise ValueError("hbar_sim: weighted median falló.")

    # payload
    payload = {
        "hbar_sim": hbar_final,
        "units": "GeV per rad/time_unit",
        "n_used": len(kept_trim),
        "n_rejected": len(candidates) - len(kept_trim),
        "omega0": omega0,
        "cluster_tol_rel": cluster_tol,
        "h_i_percentiles": {
            "p10": float(lo),
            "p50": float(np.percentile(h_vals, 50)),
            "p90": float(hi),
        },
    }
    _write_calibration(args.output, payload)

    # enrich blocks with mass_sim_gev
    out_blocks_path = args.blocks_output or args.blocks
    for b in blocks:
        omega = _to_float(b.get("omega_ref")) or _to_float(b.get("omega_ref_interp"))
        if omega is None:
            b["mass_sim_gev"] = None
        else:
            b["mass_sim_gev"] = hbar_final * omega
    _save_blocks(out_blocks_path, blocks)

    # optional proxies update
    if args.proxies_csv and args.proxies_csv.exists():
        _update_proxies(args.proxies_csv, hbar_final)


if __name__ == "__main__":
    main()
