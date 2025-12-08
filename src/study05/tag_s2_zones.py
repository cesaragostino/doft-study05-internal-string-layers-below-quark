"""Tag S2-friendly zones on an existing proxies CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def parse_float(v: str):
    try:
        return float(v)
    except Exception:
        return v


def read_csv(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {k: parse_float(v) for k, v in row.items()}
            rows.append(parsed)
    return rows, reader.fieldnames or []


def write_csv(rows: List[Dict], headers: List[str], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Tag S2 zones in proxies CSV.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows, headers = read_csv(args.proxies_csv)
    # Ensure new columns exist
    for col in ["s2_zone", "in_s2_core", "in_s2_friendly", "in_s2_extended"]:
        if col not in headers:
            headers.append(col)

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

    write_csv(rows, headers, args.output)


if __name__ == "__main__":
    main()
