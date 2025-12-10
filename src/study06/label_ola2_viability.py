"""Label Ola2 compounds viability based on thresholds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Label Ola2 compounds viability.")
    parser.add_argument("--compounds-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--d-yes", type=float, default=0.25, help="Deprecated: use selection-config instead.")
    parser.add_argument("--d-possible", type=float, default=0.45, help="Deprecated: use selection-config instead.")
    parser.add_argument("--min-structure-tier", type=str, default="level2", help="Deprecated: use selection-config.")
    parser.add_argument("--allowed-s2-states", nargs="+", default=["latent", "structural"], help="Deprecated: use selection-config.")
    parser.add_argument(
        "--selection-config",
        type=Path,
        default=Path("data/raw/wave2_selection.json"),
        help="Selection/labeling config for Ola2 viability.",
    )
    parser.add_argument(
        "--selection-log",
        type=Path,
        default=Path("data/processed/ola2/ola2_selection_log.csv"),
        help="Optional CSV log of structural rejection reasons.",
    )
    parser.add_argument(
        "--digest",
        type=Path,
        default=Path("data/processed/digest/ola2"),
        help="Optional digest directory to copy viability summary.",
    )
    args = parser.parse_args()
    # selection config defaults
    default_cfg = {
        "global": {
            "log_rejections": True,
            "structure_tier_min_baryon": "level3",
            "allow_s2_states_baryon": ["structural", "latent"],
            "min_quark_blocks_baryon": 2,
            "max_bands_compound": 10,
            "min_band_count_compound": 2,
            "use_d_total_for_labels_only": True,
            "grade_yes_d_total_max": 2.0,
            "grade_possible_d_total_max": 5.0,
        },
        "targets": [],
    }
    if args.selection_config and args.selection_config.exists():
        try:
            loaded = json.loads(args.selection_config.read_text()) or {}
            cfg = default_cfg
            cfg["global"] = {**default_cfg["global"], **loaded.get("global", {})}
            cfg["targets"] = loaded.get("targets", [])
        except Exception:
            cfg = default_cfg
    else:
        cfg = default_cfg
    order = {"none": 0, "level1": 1, "level2": 2, "level3": 3}

    if not args.compounds_csv.exists():
        print(json.dumps({"status": "skip", "reason": "compounds_not_found", "path": str(args.compounds_csv)}))
        return

    rows = []
    selection_log: List[Dict[str, Any]] = []
    with args.compounds_csv.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            target = str(row.get("target", row.get("particle_name", "")))
            t_cfg = next((t for t in cfg.get("targets", []) if t.get("name") == target), None)
            gl = cfg["global"]
            tier_min = t_cfg.get("structure_tier_min") if t_cfg else gl.get("structure_tier_min_baryon", "level3")
            allowed_s2 = {s.lower() for s in (t_cfg.get("allow_s2_states") if t_cfg else gl.get("allow_s2_states_baryon", []))}
            min_quark = t_cfg.get("min_quark_blocks") if t_cfg else gl.get("min_quark_blocks_baryon", 0)
            max_bands = t_cfg.get("max_bands") if t_cfg else gl.get("max_bands_compound", 1e9)
            min_bands = t_cfg.get("min_band_count") if t_cfg else gl.get("min_band_count_compound", 0)
            d_yes = t_cfg.get("grade_yes_d_total_max") if t_cfg else gl.get("grade_yes_d_total_max", args.d_yes)
            d_poss = t_cfg.get("grade_possible_d_total_max") if t_cfg else gl.get("grade_possible_d_total_max", args.d_possible)

            reasons = []
            tier_str = str(row.get("structure_tier_compound", "none")).lower()
            tier_rank = order.get(tier_str, 0)
            if tier_rank < order.get(str(tier_min), 0):
                reasons.append("tier_below_min")
            s2_state = str(row.get("s2_state_compound", row.get("s2_state", ""))).lower()
            if s2_state.startswith("structural"):
                s2_state = "structural"
            if allowed_s2 and s2_state not in allowed_s2:
                reasons.append("s2_state_not_allowed")
            try:
                band_count = int(float(row.get("band_count", row.get("band_count_compound", 0))))
            except Exception:
                band_count = 0
            if band_count < min_bands:
                reasons.append("too_few_bands")
            if band_count > max_bands:
                reasons.append("too_many_bands")
            families = row.get("block_families", "")
            fam_list = []
            if isinstance(families, str):
                fam_list = [x.strip().lower() for x in families.strip("[]").split(",") if x.strip()]
            try:
                quark_blocks = sum(1 for f in fam_list if f == "quark_like")
            except Exception:
                quark_blocks = 0
            if quark_blocks < min_quark:
                reasons.append("too_few_quark_blocks")
            enough_partial = str(row.get("enough_levels_partial", "")).lower() in ("1", "true", "yes")
            if not enough_partial:
                reasons.append("not_enough_levels_for_match")

            if reasons:
                label = "NO"
                label_struct = "REJECT_STRUCTURAL"
            else:
                label_struct = "STRUCTURAL_OK"
                try:
                    d_val = float(row.get("match_d_total"))
                except Exception:
                    d_val = np.inf
                if np.isfinite(d_val) and d_val <= d_yes:
                    label = "YES"
                elif np.isfinite(d_val) and d_val <= d_poss:
                    label = "POSSIBLE"
                else:
                    label = "NO"

            row["label_structural"] = label_struct
            row["label"] = label
            row["quark_block_count"] = quark_blocks
            row["reasons"] = ";".join(reasons)
            rows.append(row)
            if gl.get("log_rejections", False) and args.selection_log:
                selection_log.append(
                    {
                        "target": target,
                        "template_name": row.get("template_name"),
                        "run_id": row.get("run_id"),
                        "label": label,
                        "label_structural": label_struct,
                        "match_d_total": row.get("match_d_total"),
                        "structure_tier_compound": row.get("structure_tier_compound"),
                        "s2_state_compound": row.get("s2_state_compound"),
                        "band_count": band_count,
                        "num_quark_blocks": quark_blocks,
                        "reasons": ";".join(reasons),
                    }
                )

    if not rows:
        print(json.dumps({"status": "skip", "reason": "no_compounds"}, indent=2))
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    if args.digest:
        args.digest.mkdir(parents=True, exist_ok=True)
        (args.digest / args.output.name).write_text(args.output.read_text())

    if selection_log and args.selection_log:
        args.selection_log.parent.mkdir(parents=True, exist_ok=True)
        with args.selection_log.open("w", newline="") as f:
            fieldnames = [
                "target",
                "template_name",
                "run_id",
                "label",
                "label_structural",
                "match_d_total",
                "structure_tier_compound",
                "s2_state_compound",
                "band_count",
                "num_quark_blocks",
                "reasons",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(selection_log)

    # Console summary per target / template
    if rows:
        try:
            from collections import defaultdict, Counter

            print("Ola2 viability summary:")
            by_target: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            by_target_template: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
            for r in rows:
                tgt = r.get("target")
                by_target[tgt].append(r)
                by_target_template[(tgt, r.get("template_name"))].append(r)

            def _summ(ar: List[Dict[str, Any]], prefix: str):
                labels = Counter(r.get("label") for r in ar)
                struct_ok = sum(1 for r in ar if r.get("label_structural") == "STRUCTURAL_OK")
                tiers = Counter(str(r.get("structure_tier_compound")) for r in ar)
                s2s = Counter(str(r.get("s2_state_compound")) for r in ar)
                d_vals = []
                for r in ar:
                    try:
                        d_vals.append(float(r.get("match_d_total")))
                    except Exception:
                        pass
                quarks = []
                for r in ar:
                    try:
                        quarks.append(int(r.get("quark_block_count", 0)))
                    except Exception:
                        pass
                d_str = "nan/nan/nan"
                if d_vals:
                    d_arr = np.array(d_vals, dtype=float)
                    d_str = f"{np.nanmin(d_arr):.3f}/{np.nanmedian(d_arr):.3f}/{np.nanmax(d_arr):.3f}"
                print(
                    f"{prefix}: n={len(ar)} struct_ok={struct_ok} labels={dict(labels)} d_total[min/med/max]={d_str} tiers={dict(tiers)} s2={dict(s2s)} quark_blocks_hist={dict(Counter(quarks))}"
                )

            for tgt, arr in by_target.items():
                _summ(arr, f"target={tgt}")
            for (tgt, tmpl), arr in by_target_template.items():
                _summ(arr, f"target={tgt}, template={tmpl}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
