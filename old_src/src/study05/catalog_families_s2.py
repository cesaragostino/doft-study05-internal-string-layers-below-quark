"""Catalog S2 dominance by family and zone using tagged proxies CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

import numpy as np


def parse_float(v: str):
    try:
        return float(v)
    except Exception:
        return float("nan")


def read_csv(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {k: parse_float(v) for k, v in row.items()}
            rows.append(parsed)
    return rows


def add_zone_tags(rows: List[Dict]) -> None:
    for row in rows:
        fe = float(row.get("first_energy", float("nan")))
        sm = float(row.get("spacing_mean", float("nan")))
        ds = float(row.get("Nucleon_like_d_spacing", float("nan")))

        core = (fe < 0.6) and (sm > 0.45) and (ds > 5.5)
        friendly = (fe < 0.8) and (sm > 0.50) and (ds > 5.5)
        extended = (fe < 0.8) and (sm > 0.45) and (ds > 6.0)

        zone = "out"
        if extended:
            zone = "extended"
        if friendly:
            zone = "friendly"
        if core:
            zone = "core"

        row["s2_zone"] = zone
        row["in_s2_core"] = int(core)
        row["in_s2_friendly"] = int(friendly)
        row["in_s2_extended"] = int(extended)


def choose_closest_family(row: Dict, families: List[str]) -> str:
    # use d_spacing if available; otherwise use a large value
    d_vals = {}
    for fam in families:
        key = f"{fam.capitalize() if fam.endswith('_like') else fam}_d_spacing"
        if key not in row:
            key = f"{fam}_d_spacing"
        val = row.get(key, float("nan"))
        d_vals[fam] = val if np.isfinite(val) else 1e9
    best = min(d_vals.items(), key=lambda kv: kv[1])
    return best[0]


def summarise_zone(rows: List[Dict], mask: np.ndarray, fam: str, fam_key: str) -> Dict:
    arr_first = np.array([r.get("first_energy", np.nan) for r in rows])
    arr_spacing = np.array([r.get("spacing_mean", np.nan) for r in rows])
    arr_d = np.array([r.get(fam_key, np.nan) for r in rows])
    has_s2 = np.array([r.get("has_s2_dominant", 0) for r in rows])
    n_runs = int(mask.sum())
    n_s2 = int((has_s2 * mask).sum())
    p_s2 = (n_s2 / n_runs) if n_runs else 0.0

    # avoid warnings when all values are NaN
    fe_mean = float(np.nanmean(arr_first[mask])) if np.isfinite(arr_first[mask]).any() else float("nan")
    sm_mean = float(np.nanmean(arr_spacing[mask])) if np.isfinite(arr_spacing[mask]).any() else float("nan")
    d_mask = mask & np.isfinite(arr_d)
    d_mean = float(np.mean(arr_d[d_mask])) if d_mask.any() else float("nan")

    return {
        "family": fam,
        "zone": None,  # fill later
        "n_runs": n_runs,
        "n_s2": n_s2,
        "p_s2": p_s2,
        "first_energy_mean": fe_mean if n_runs else float("nan"),
        "spacing_mean_mean": sm_mean if n_runs else float("nan"),
        "family_d_spacing_mean": d_mean if n_runs else float("nan"),
    }


def write_csv(rows: List[Dict], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Catalog families vs S2 by zones.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--families", nargs="+", required=True, help="Family names (lowercase, e.g., nucleon_like).")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    # Load proxies; fallback to untagged path if tagged not found
    proxies_path = args.proxies_csv
    if not proxies_path.exists():
        alt = Path(str(proxies_path).replace("_tagged", ""))
        if alt.exists():
            proxies_path = alt
    if not proxies_path.exists():
        raise SystemExit(f"Proxies CSV not found: {args.proxies_csv}")

    rows = read_csv(proxies_path)
    if not rows:
        raise SystemExit("No data in proxies CSV.")
    if "s2_zone" not in rows[0]:
        add_zone_tags(rows)

    families = [f for f in args.families]
    fam_keys = {fam: f"{fam}_d_spacing" for fam in families}
    closest = []
    for row in rows:
        closest.append(choose_closest_family(row, families))
    closest = np.array(closest)
    zones = np.array([row.get("s2_zone", "out") for row in rows])

    summary_rows: List[Dict] = []
    for fam in families:
        fam_mask = closest == fam
        fam_key = fam_keys[fam]
        base_stats = summarise_zone(rows, fam_mask, fam, fam_key)

        def add_zone(zone_name: str, zone_mask):
            stats = summarise_zone(rows, fam_mask & zone_mask, fam, fam_key)
            stats["zone"] = zone_name
            summary_rows.append(stats)

        add_zone("global", fam_mask)
        add_zone("core", fam_mask & (zones == "core"))
        add_zone("friendly", fam_mask & np.isin(zones, ["core", "friendly"]))
        add_zone("extended", fam_mask & np.isin(zones, ["core", "friendly", "extended"]))
        add_zone("out", fam_mask & (zones == "out"))

    write_csv(summary_rows, args.output / "family_zone_summary.csv")


if __name__ == "__main__":
    main()
