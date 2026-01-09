"""Fill missing mass_sim_used_gev in proxies CSV without touching the sweep."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Optional


def _to_float(value) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def _to_int(value) -> Optional[int]:
    f = _to_float(value)
    if f is None:
        return None
    try:
        return int(round(f))
    except Exception:
        return None


def _load_hbar(path: Path) -> Optional[float]:
    if not path or not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return float(data.get("hbar_sim"))
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing mass_sim_used_gev in proxies CSV.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--hbar-sim", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    hbar = _load_hbar(args.hbar_sim)
    if hbar is None:
        raise SystemExit("hbar_sim missing; provide a valid calibration JSON.")

    with args.proxies_csv.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "mass_sim_used_gev" not in fieldnames:
        fieldnames.append("mass_sim_used_gev")
    if "omega_eff" not in fieldnames:
        fieldnames.append("omega_eff")
    if "mass_sim_used_source" not in fieldnames:
        fieldnames.append("mass_sim_used_source")

    filled = 0
    kept = 0
    missing = 0
    for row in rows:
        msu = _to_float(row.get("mass_sim_used_gev"))
        if msu is not None:
            row["mass_sim_used_source"] = "existing"
            kept += 1
            continue

        k_used = _to_int(row.get("k_used"))
        omega_ref = _to_float(row.get("omega_ref"))
        if omega_ref is None:
            omega_ref = _to_float(row.get("omega_ref_interp"))

        if k_used and omega_ref is not None:
            omega_eff = omega_ref / float(k_used)
            mass_sim_used = hbar * omega_eff
            row["omega_eff"] = f"{omega_eff:.12g}"
            row["mass_sim_used_gev"] = f"{mass_sim_used:.12g}"
            row["mass_sim_used_source"] = "filled_from_omega_ref"
            filled += 1
        else:
            row["mass_sim_used_source"] = "missing"
            missing += 1

    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[fill_mass_sim_used] kept={kept} filled={filled} missing={missing} -> {args.output}")


if __name__ == "__main__":
    main()
