"""Promote simple blocks (Ola1) from sweep proxies and SM matches."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

import numpy as np


def read_proxies(path: Path) -> List[Dict]:
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


def read_matches(path: Path) -> List[Dict]:
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


def main():
    parser = argparse.ArgumentParser(description="Promote simple blocks from Ola1 sweeps.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--zoo-matches-csv", type=Path, required=True)
    parser.add_argument("--sm-catalog", type=Path, default=Path("data/raw/sm_catalog/particles.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/blocks/simple_blocks.json"))
    parser.add_argument("--digest", type=Path, default=Path("digest/blocks"), help="Directory to store promoted block summary.")
    parser.add_argument("--d-total-max", type=float, default=0.3)
    parser.add_argument("--max-blocks-per-particle", type=int, default=10)
    args = parser.parse_args()

    proxies = read_proxies(args.proxies_csv)
    matches = read_matches(args.zoo_matches_csv)
    catalog = json.loads(args.sm_catalog.read_text())
    cat_by_name = {p["name"]: p for p in catalog}

    # group matches by target
    blocks: List[Dict] = []
    blocks_per_particle: Dict[str, int] = {}

    for match in matches:
        target = match.get("target_name")
        if target not in cat_by_name:
            continue
        particle = cat_by_name[target]
        if particle.get("type") != "meson":
            continue
        if not match.get("enough_levels"):
            continue
        if not np.isfinite(match.get("d_total", np.inf)) or match.get("d_total", np.inf) > args.d_total_max:
            continue
        run_id = match.get("run_id")
        # find proxy row
        proxy_row = next((r for r in proxies if str(r.get("run_id")) == str(run_id)), None)
        if proxy_row is None:
            continue
        structure_tier = proxy_row.get("structure_tier")
        s2_state = proxy_row.get("s2_state")
        if structure_tier not in ("level2", "level3"):
            continue
        if s2_state not in ("none", "latent"):
            continue

        cnt = blocks_per_particle.get(target, 0)
        if cnt >= args.max_blocks_per_particle:
            continue
        blocks_per_particle[target] = cnt + 1

        block_id = f"{target}_block_{cnt+1:04d}"
        block = {
            "block_id": block_id,
            "origin_run_id": proxy_row.get("run_id"),
            "particle_name": target,
            "family": particle.get("family"),
            "structure_tier": structure_tier,
            "lock_quality": {
                "Q": proxy_row.get("lock_quality_Q"),
                "S1": proxy_row.get("lock_quality_S1"),
                "S2": proxy_row.get("lock_quality_S2"),
            },
            "s2_state": s2_state,
            "s2_band_fraction": proxy_row.get("s2_band_fraction"),
            "match_score": {"d_total": match.get("d_total"), "d_spacing": match.get("d_spacing"), "d_mass": match.get("d_mass")},
            "theta_internal": {
                "R_S1_Q": proxy_row.get("R_S1_Q"),
                "R_S2_S1": proxy_row.get("R_S2_S1"),
                "R_S3_S2": proxy_row.get("R_S3_S2"),
                "g_couplings": proxy_row.get("g_couplings"),
                "memory_taus": proxy_row.get("memory_taus"),
                "memory_amps": proxy_row.get("memory_amps"),
            },
        }
        blocks.append(block)

    out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(blocks, indent=2))

    # Optional digest copy for a concise promoted-blocks snapshot
    if args.digest:
        args.digest.mkdir(parents=True, exist_ok=True)
        (args.digest / out_path.name).write_text(out_path.read_text())


if __name__ == "__main__":
    main()
