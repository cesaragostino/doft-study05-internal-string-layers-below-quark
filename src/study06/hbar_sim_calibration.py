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


def _fit_hbar(pairs: List[Tuple[float, float]]) -> float | None:
    if not pairs:
        return None
    w = np.array([p[0] for p in pairs], dtype=float)
    m = np.array([p[1] for p in pairs], dtype=float)
    denom = np.sum(w * w)
    if denom <= 0:
        return None
    return float(np.sum(w * m) / denom)


def _write_calibration(path: Path, hbar: float, used: List[Dict[str, Any]], dropped: List[Dict[str, Any]]):
    payload = {
        "hbar_sim": hbar,
        "n_used": len(used),
        "n_dropped_outliers": len(dropped),
        "used_blocks": used,
        "dropped_outliers": dropped,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
    print(f"[hbar_sim] escrito {path} (hbar_sim={hbar:.6g}, n_used={len(used)}, dropped={len(dropped)})")


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
        if omega is None:
            continue
        pname = b.get("particle_name")
        m_sm = sm_masses.get(str(pname))
        if m_sm is None:
            continue
        candidates.append({"block": b, "omega_ref": omega, "sm_mass": m_sm})

    if not candidates:
        raise ValueError("hbar_sim: no hay bloques elegibles con omega_ref y sm_mass_gev.")

    pairs = [(c["omega_ref"], c["sm_mass"]) for c in candidates]
    hbar_initial = _fit_hbar(pairs)
    if hbar_initial is None:
        raise ValueError("hbar_sim: no se pudo estimar hbar_sim (denom=0).")
    used = []
    dropped = []
    for c in candidates:
        est = hbar_initial * c["omega_ref"]
        rel_err = abs(est - c["sm_mass"]) / c["sm_mass"] if c["sm_mass"] != 0 else np.inf
        if rel_err > 0.5:
            dropped.append(
                {
                    "block_id": c["block"].get("block_id"),
                    "particle_name": c["block"].get("particle_name"),
                    "omega_ref": c["omega_ref"],
                    "sm_mass_gev": c["sm_mass"],
                    "rel_err_initial": rel_err,
                }
            )
        else:
            used.append(
                {
                    "block_id": c["block"].get("block_id"),
                    "particle_name": c["block"].get("particle_name"),
                    "omega_ref": c["omega_ref"],
                    "sm_mass_gev": c["sm_mass"],
                }
            )

    hbar_final = hbar_initial
    if used:
        hbar_refined = _fit_hbar([(u["omega_ref"], u["sm_mass_gev"]) for u in used])
        if hbar_refined is not None:
            hbar_final = hbar_refined

    _write_calibration(args.output, hbar_final, used, dropped)

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
