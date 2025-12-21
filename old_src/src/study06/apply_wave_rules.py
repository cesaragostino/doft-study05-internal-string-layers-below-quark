"""Apply declarative wave rules (Ola1) to promote blocks."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed: Dict[str, Any] = {}
            for k, v in row.items():
                try:
                    parsed[k] = float(v)
                except Exception:
                    parsed[k] = v
            rows.append(parsed)
    return rows


def _best_match_per_run(zoo_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    best: Dict[str, Dict[str, Any]] = {}
    for row in zoo_rows:
        rid = str(row.get("run_id"))
        d_total = row.get("d_total")
        try:
            d_val = float(d_total)
        except Exception:
            continue
        prev = best.get(rid)
        if prev is None or (isinstance(prev.get("d_total"), (int, float)) and d_val < prev.get("d_total", 1e9)):
            best[rid] = {
                "best_target": row.get("target_name"),
                "best_family": row.get("family"),
                "best_type": row.get("type"),
                "best_d_total": d_val,
                "best_d_spacing": row.get("d_spacing"),
                "best_d_mass": row.get("d_mass"),
                "enough_levels": row.get("enough_levels"),
                "run_id": row.get("run_id"),
            }
    return best


def _passes_filter(row: Dict[str, Any], lower_map: Dict[str, Any], flt: Dict[str, Any]) -> bool:
    field = str(flt.get("field"))
    op = flt.get("op")
    val = flt.get("value")
    rv = row.get(field, lower_map.get(field.lower()))
    if op == "==":
        return rv == val
    if op == "in":
        return rv in val
    if op == "<=":
        return isinstance(rv, (int, float)) and rv <= val
    if op == ">=":
        return isinstance(rv, (int, float)) and rv >= val
    if op == "<":
        return isinstance(rv, (int, float)) and rv < val
    if op == ">":
        return isinstance(rv, (int, float)) and rv > val
    return False


def apply_rules(rules_path: Path):
    rules = json.loads(rules_path.read_text())
    inputs = rules.get("inputs", {})
    proxies_csv = Path(inputs.get("proxies_csv"))
    zoo_csv = Path(inputs.get("zoo_matches_csv"))
    proxies = _read_csv(proxies_csv)
    zoo_rows = _read_csv(zoo_csv)
    best = _best_match_per_run(zoo_rows)

    merged: List[Dict[str, Any]] = []
    for row in proxies:
        rid = str(row.get("run_id"))
        merged_row = dict(row)
        merged_row.update(best.get(rid, {}))
        merged.append(merged_row)

    selections = rules.get("selections", [])
    blocks_out_path = None
    rejected_rows: List[Dict[str, Any]] = []
    all_blocks: List[Dict[str, Any]] = []

    for sel in selections:
        filters = sel.get("filters", [])
        pick = sel.get("pick", {})
        output_cfg = sel.get("output", {})
        target_name = sel.get("target_name", sel.get("particle_name"))
        family = sel.get("family")
        sel_name = sel.get("name", target_name or "selection")

        filtered: List[Dict[str, Any]] = []
        for r in merged:
            lower_map = {str(k).lower(): v for k, v in r.items()}
            if all(_passes_filter(r, lower_map, f) for f in filters):
                filtered.append(r)
            else:
                rejected_rows.append(
                    {
                        "run_id": r.get("run_id"),
                        "best_target": r.get("best_target"),
                        "structure_tier": r.get("structure_tier"),
                        "s2_state": r.get("s2_state"),
                        "reason": "filters",
                    }
                )

        order_by = pick.get("order_by")
        ascending = pick.get("ascending", True)
        top_n = pick.get("n")
        if order_by:
            filtered = sorted(filtered, key=lambda r: r.get(order_by, float("inf")), reverse=not ascending)
        if isinstance(top_n, int):
            filtered = filtered[:top_n]

        include_fields = output_cfg.get("include_fields", [])
        block_type = output_cfg.get("block_type", "simple")
        append = output_cfg.get("append", False)
        blocks_path = Path(output_cfg.get("blocks_path", "data/processed/blocks/simple_blocks.json"))
        blocks_out_path = blocks_out_path or blocks_path

        existing: List[Dict[str, Any]] = []
        if append and blocks_path.exists():
            try:
                existing = json.loads(blocks_path.read_text())
            except Exception:
                existing = []

        start_idx = len(existing)
        blocks: List[Dict[str, Any]] = []
        for i, r in enumerate(filtered, start=1):
            block = {
                "block_id": f"{sel_name}_{start_idx + i:04d}",
                "origin_run_id": r.get("run_id"),
                "particle_name": target_name or r.get("best_target"),
                "family": family or r.get("best_family"),
                "type": r.get("best_type"),
                "structure_tier": r.get("structure_tier"),
                "lock_quality": {
                    "Q": r.get("lock_quality_Q"),
                    "S1": r.get("lock_quality_S1"),
                    "S2": r.get("lock_quality_S2"),
                },
                "s2_state": r.get("s2_state"),
                "s2_band_fraction": r.get("s2_band_fraction"),
                "match_score": {
                    "d_total": r.get("best_d_total"),
                    "d_spacing": r.get("best_d_spacing"),
                    "d_mass": r.get("best_d_mass"),
                },
            }
            for field in include_fields:
                block[field] = r.get(field)
            blocks.append(block)

        merged_blocks = existing + blocks if append else blocks
        blocks_path.parent.mkdir(parents=True, exist_ok=True)
        blocks_path.write_text(json.dumps(merged_blocks, indent=2))
        all_blocks.extend(blocks)

    # write rejected log if any
    if blocks_out_path:
        rej_path = blocks_out_path.parent / "simple_blocks_rejected.csv"
        rej_path.parent.mkdir(parents=True, exist_ok=True)
        if rejected_rows:
            fieldnames = sorted({k for row in rejected_rows for k in row.keys()})
            with rej_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rejected_rows)


def main():
    parser = argparse.ArgumentParser(description="Apply wave rules to promote blocks.")
    parser.add_argument("--rules-json", type=Path, required=True, help="Path to wave rules JSON (wave1).")
    args = parser.parse_args()
    apply_rules(args.rules_json)


if __name__ == "__main__":
    main()
