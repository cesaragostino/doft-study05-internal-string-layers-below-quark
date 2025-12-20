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


def _load_calibration_config(path: Path) -> Dict[str, Any]:
    defaults = {
        "schema_version": "hbar_sim_calibration_v2",
        "mode": "auto",
        "auto": {
            "q_lock_min": 0.9,
            "d_total_max": 1.5,
            "min_band_count": 2,
        },
        "seed": {
            "q_lock_min": 0.9,
            "band_count_exact": 2,
            "omega_max": 12.0,
            "seed_particle": "deuteron",
        },
    }
    if not path or not path.exists():
        return defaults
    try:
        data = json.loads(path.read_text())
    except Exception:
        return defaults
    cfg = defaults.copy()
    cfg.update({k: v for k, v in data.items() if v is not None})
    return cfg


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
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/raw/hbar_sim_calibration_config.json"),
        help="Config JSON con umbrales y modo de calibracion.",
    )
    parser.add_argument(
        "--seed-mode",
        action="store_true",
        help="Usar solo semillas (Q>=0.9, band_count==2, omega_ref bajo) y masa de deuteron para hbar_seed.",
    )
    args = parser.parse_args()

    blocks = _load_blocks(args.blocks)
    sm_masses = _load_sm_masses(args.sm_universe)
    cfg = _load_calibration_config(args.config)
    mode = "seed" if args.seed_mode else str(cfg.get("mode", "auto")).lower()
    if mode not in {"seed", "auto"}:
        mode = "auto"
    cfg_seed = cfg.get("seed", {})
    cfg_auto = cfg.get("auto", {})

    candidates = []
    for b in blocks:
        grade = str(b.get("grade", "")).upper()
        ms = b.get("match_score") or {}
        try:
            q_lock = float((b.get("lock_quality") or {}).get("Q"))
        except Exception:
            q_lock = 0.0
        pname = b.get("particle_name")
        allow_unknown_by_lock = str(pname).lower() == "unknown" and q_lock >= 0.90
        if not args.seed_mode:
            if grade not in {"A", "B"} and not allow_unknown_by_lock:
                continue
            if not bool(ms.get("has_enough_levels_full")) and not allow_unknown_by_lock:
                continue
        omega = _to_float(b.get("omega_ref")) or _to_float(b.get("omega_ref_interp"))
        if omega is None or omega <= 0:
            continue
        if mode == "seed":
            # semillas: Q>=min, band_count exacto, omega_ref bajo
            try:
                band_count = int(float(b.get("band_count")))
            except Exception:
                band_count = 0
            q_lock_min = float(cfg_seed.get("q_lock_min", 0.9))
            band_exact = int(cfg_seed.get("band_count_exact", 2))
            omega_max = float(cfg_seed.get("omega_max", 12.0))
            if q_lock < q_lock_min or band_count != band_exact or omega <= 0 or omega > omega_max:
                continue
            seed_particle = cfg_seed.get("seed_particle")
            if seed_particle:
                pname = seed_particle
        m_sm = sm_masses.get(str(pname))
        if m_sm is None:
            continue
        if mode == "auto":
            q_lock_min = cfg_auto.get("q_lock_min")
            if q_lock_min is not None and q_lock < float(q_lock_min):
                continue
            d_total = ms.get("d_total")
            try:
                d_total = float(d_total)
            except Exception:
                d_total = None
            d_total_max = cfg_auto.get("d_total_max")
            if d_total_max is not None and d_total is not None and d_total > float(d_total_max):
                continue
            try:
                band_count = int(float(b.get("band_count")))
            except Exception:
                band_count = None
            min_band_count = cfg_auto.get("min_band_count")
            if min_band_count is not None and band_count is not None and band_count < int(min_band_count):
                continue
        d_total = _to_float(ms.get("d_total")) or 0.0
        candidates.append({"block": b, "omega_ref": omega, "sm_mass": m_sm, "q_lock": q_lock, "d_total": d_total})

    if not candidates:
        print("!! hbar_sim: no hay bloques elegibles con omega_ref y sm_mass_gev. ¿Faltan runs o grades A/B con matches full?", flush=True)
        return

    # cluster fundamental: omega0 = p10; keep within ±10%
    omega_all = np.array([c["omega_ref"] for c in candidates if c["omega_ref"] is not None], dtype=float)
    if omega_all.size == 0:
        print("!! hbar_sim: sin omegas válidos para calibrar.", flush=True)
        return
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
        w = float(q_lock) ** 2 if (q_lock is not None) else 1.0
        if not np.isfinite(w) or w <= 0:
            w = 1.0
        weights.append(w)
        kept.append(c)
    h_vals = np.array(h_vals, dtype=float)
    weights = np.array(weights, dtype=float)
    if h_vals.size == 0:
        print("!!~~~## hbar_sim: sin h_i válidos (candidatos filtrados a 0).", flush=True)
        raise ValueError("hbar_sim: no se pudieron construir h_i válidos.")
    # trim percentiles
    lo, hi = np.percentile(h_vals, [10, 90])
    mask = (h_vals >= lo) & (h_vals <= hi)
    h_trim = h_vals[mask]
    w_trim = weights[mask]
    kept_trim = [k for k, m in zip(kept, mask) if m]
    hbar_final = None
    fallback_reason = None
    if h_trim.size == 0 or w_trim.size == 0:
        h_trim = h_vals
        w_trim = weights
        kept_trim = kept
        fallback_reason = "trim_empty_used_full"
    hbar_final = _weighted_median(h_trim, w_trim)
    if hbar_final is None:
        print(
            f"!!~~~## hbar_sim: weighted median falló (candidatos={len(candidates)}, "
            f"clustered={len(clustered)}, kept_trim={len(kept_trim)}).",
            flush=True,
        )
        if h_vals.size > 0:
            hbar_final = float(np.median(h_vals))
            fallback_reason = (fallback_reason + "|") if fallback_reason else ""
            fallback_reason = f"{fallback_reason}fallback_unweighted_median"
        else:
            raise ValueError("hbar_sim: weighted median falló.")

    # payload
    payload = {
        "hbar_sim": hbar_final,
        "units": "GeV per rad/time_unit",
        "n_used": len(kept_trim),
        "n_rejected": len(candidates) - len(kept_trim),
        "omega0": omega0,
        "cluster_tol_rel": cluster_tol,
        "fallback_reason": fallback_reason,
        "h_i_percentiles": {
            "p10": float(lo),
            "p50": float(np.percentile(h_vals, 50)),
            "p90": float(hi),
        },
        "mode": mode,
        "seed_particle": cfg_seed.get("seed_particle") if mode == "seed" else None,
        "selection": {
            "auto": cfg_auto if mode == "auto" else None,
            "seed": cfg_seed if mode == "seed" else None,
            "grade_filter": None if mode == "seed" else "A/B with enough_levels_full",
        },
    }
    _write_calibration(args.output, payload)
    if len(kept_trim) < 10:
        print(f"!! hbar_sim: solo {len(kept_trim)} bloques usados para calibrar (recomendado >=10).", flush=True)

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
