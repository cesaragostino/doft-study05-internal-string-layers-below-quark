"""Label Ola2 compounds viability based on thresholds."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Dict

import numpy as np


def label_row(row: Dict[str, Any], d_yes: float, d_possible: float, min_tier: int, allowed_s2) -> str:
    tier = int(float(row.get("structure_tier_compound", 0)))
    if tier < min_tier:
        return "NO"
    s2_state = str(row.get("s2_state_compound", "")).lower()
    if s2_state.startswith("structural"):
        s2_state = "structural"
    if s2_state not in allowed_s2:
        return "NO"
    d_total = row.get("d_total_target")
    try:
        d_val = float(d_total)
    except Exception:
        d_val = np.inf
    if np.isfinite(d_val) and d_val < d_yes:
        return "YES"
    if np.isfinite(d_val) and d_val < d_possible:
        return "POSSIBLE"
    return "NO"


def main():
    parser = argparse.ArgumentParser(description="Label Ola2 compounds viability.")
    parser.add_argument("--compounds-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--d-yes", type=float, default=3.0)
    parser.add_argument("--d-possible", type=float, default=5.0)
    parser.add_argument("--min-structure-tier", type=str, default="level2")
    parser.add_argument("--allowed-s2-states", nargs="+", default=["latent", "structural"])
    args = parser.parse_args()

    order = {"none": 0, "level1": 1, "level2": 2, "level3": 3}
    min_tier_rank = order.get(args.min_structure_tier, 2)
    allowed_s2 = {s.lower() for s in args.allowed_s2_states}

    rows = []
    with args.compounds_csv.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            row["label"] = label_row(row, args.d_yes, args.d_possible, min_tier_rank, allowed_s2)
            rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
