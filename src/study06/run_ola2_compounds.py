"""Generate Ola2 compounds from promoted blocks using declarative rules.

Note: This implementation builds combinatorial compounds (block selections + template)
and evaluates them with lightweight fingerprints. It does not re-run the DOFT integrator
for the compound; instead it uses block parameters (ratios, structure_tier, s2_state)
and SM catalog spacing to score viability.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np


def _load_json(path: Path):
    return json.loads(path.read_text())


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else []


def _load_sm_catalog(path: Path) -> Dict[str, Dict[str, Any]]:
    data = _load_json(path)
    return {d["name"]: d for d in data}


def _tier_rank(tier: str) -> int:
    order = {"none": 0, "level1": 1, "level2": 2, "level3": 3}
    return order.get(str(tier), 0)


def _normalize_s2(state: Any) -> str:
    s = str(state or "").lower()
    if s.startswith("structural"):
        return "structural"
    return s


def _rel_delta(a: float, b: float) -> float:
    if not np.isfinite(a) or not np.isfinite(b):
        return float("inf")
    if a == 0 and b == 0:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b), 1e-9)


def _sample_blocks(pool: List[Dict[str, Any]], families: Sequence[str], k: int) -> List[Dict[str, Any]]:
    filtered = [b for b in pool if (not families or b.get("family") in families)]
    if len(filtered) < k:
        return []
    return random.sample(filtered, k)


def build_compound(
    target: Dict[str, Any],
    template: Dict[str, Any],
    blocks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    ratios_R_S1_Q = [b.get("theta_internal", {}).get("R_S1_Q") for b in blocks]
    ratios_R_S2_S1 = [b.get("theta_internal", {}).get("R_S2_S1") for b in blocks]
    ratios_R_S3_S2 = [b.get("theta_internal", {}).get("R_S3_S2") for b in blocks if b.get("theta_internal")]

    max_rel_delta_R_S1_Q = max(_rel_delta(a, b) for a in ratios_R_S1_Q for b in ratios_R_S1_Q) if ratios_R_S1_Q else float("inf")
    max_rel_delta_R_S2_S1 = max(_rel_delta(a, b) for a in ratios_R_S2_S1 for b in ratios_R_S2_S1) if ratios_R_S2_S1 else float("inf")
    max_rel_delta_R_S3_S2 = max(_rel_delta(a, b) for a in ratios_R_S3_S2 for b in ratios_R_S3_S2) if ratios_R_S3_S2 else float("inf")

    structure_tier_compound = min((_tier_rank(b.get("structure_tier")) for b in blocks), default=0)
    s2_states = [_normalize_s2(b.get("s2_state")) for b in blocks]
    s2_state_compound = "none"
    if any(s == "structural" for s in s2_states):
        s2_state_compound = "structural"
    elif any(s == "latent" for s in s2_states):
        s2_state_compound = "latent"

    # Simple d_total proxy: average of block match scores for the target type
    d_totals = []
    for b in blocks:
        m = b.get("match_score", {})
        if m:
            d = m.get("d_total")
            if np.isfinite(d):
                d_totals.append(d)
    d_total_target = float(np.mean(d_totals)) if d_totals else float("nan")

    return {
        "target": target.get("name"),
        "target_type": target.get("type"),
        "template_name": template.get("name"),
        "block_ids": [b.get("block_id") for b in blocks],
        "structure_tier_compound": structure_tier_compound,
        "s2_state_compound": s2_state_compound,
        "max_rel_delta_R_S1_Q": max_rel_delta_R_S1_Q,
        "max_rel_delta_R_S2_S1": max_rel_delta_R_S2_S1,
        "max_rel_delta_R_S3_S2": max_rel_delta_R_S3_S2,
        "d_total_target": d_total_target,
        "enough_levels": len(blocks) >= target.get("blocks_per_compound", len(blocks)),
    }


def label_viability(row: Dict[str, Any], eval_cfg: Dict[str, Any]) -> str:
    min_tier = eval_cfg.get("min_structure_tier", "level2")
    min_tier_rank = _tier_rank(min_tier)
    allowed_s2 = set(_normalize_s2(s) for s in eval_cfg.get("allowed_s2_states", ["latent", "structural"]))
    if row.get("structure_tier_compound", 0) < min_tier_rank:
        return "NO"
    if _normalize_s2(row.get("s2_state_compound")) not in allowed_s2:
        return "NO"
    if not row.get("enough_levels"):
        return "NO"
    d_total = row.get("d_total_target", float("inf"))
    d_yes = eval_cfg.get("d_total_yes", float("inf"))
    d_poss = eval_cfg.get("d_total_possible", float("inf"))
    if np.isfinite(d_total) and d_total < d_yes:
        return "YES"
    if np.isfinite(d_total) and d_total < d_poss:
        return "POSSIBLE"
    return "NO"


def run_from_rules(rules_path: Path):
    rules = _load_json(rules_path)
    blocks_path = Path(rules["blocks_input"])
    blocks = _load_blocks(blocks_path)
    if not blocks:
        print(json.dumps({"status": "skip", "reason": "no_blocks", "blocks_input": str(blocks_path)}))
        return
    templates = {t["name"]: t for t in _load_json(Path(rules["templates_json"]))}
    catalog = _load_sm_catalog(Path(rules["sm_catalog"]))
    runs_per_target = int(rules.get("runs_per_target", 100))

    all_compounds: List[Dict[str, Any]] = []
    for tgt_cfg in rules.get("targets", []):
        target_name = tgt_cfg.get("name")
        target = catalog.get(target_name, {"name": target_name, "type": tgt_cfg.get("type")})
        families = tgt_cfg.get("allowed_block_families", [])
        k_blocks = int(tgt_cfg.get("blocks_per_compound", 3))
        template_names = tgt_cfg.get("templates", [])
        fp_constraints = tgt_cfg.get("fingerprint_constraints", {})
        eval_cfg = tgt_cfg.get("evaluation", {})
        out_compounds = Path(tgt_cfg.get("output", {}).get("compounds_csv", f"data/processed/ola2/raw/compounds_{target_name}.csv"))
        out_viability = Path(tgt_cfg.get("output", {}).get("viability_csv", f"data/processed/ola2/viability/viability_{target_name}.csv"))

        for i in range(runs_per_target):
            tmpl_name = random.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            picked = _sample_blocks(blocks, families, k_blocks)
            if not picked or tmpl is None:
                continue
            compound = build_compound(target, tmpl, picked)
            # apply fingerprint constraints
            if fp_constraints:
                if compound["max_rel_delta_R_S1_Q"] > fp_constraints.get("max_rel_delta_R_S1_Q", float("inf")):
                    continue
                if compound["max_rel_delta_R_S2_S1"] > fp_constraints.get("max_rel_delta_R_S2_S1", float("inf")):
                    continue
                if compound["max_rel_delta_R_S3_S2"] > fp_constraints.get("max_rel_delta_R_S3_S2", float("inf")):
                    continue
            compound["label"] = label_viability(compound, eval_cfg)
            all_compounds.append(compound)

        # save compounds CSV for this target
        out_compounds.parent.mkdir(parents=True, exist_ok=True)
        if all_compounds:
            fieldnames = sorted({k for row in all_compounds for k in row.keys()})
            with out_compounds.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_compounds)

        # save viability summary
        out_viability.parent.mkdir(parents=True, exist_ok=True)
        if all_compounds:
            with out_viability.open("w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["target", "template_name", "label", "d_total_target", "structure_tier_compound", "s2_state_compound", "max_rel_delta_R_S1_Q", "max_rel_delta_R_S2_S1", "max_rel_delta_R_S3_S2"],
                )
                writer.writeheader()
                for row in all_compounds:
                    writer.writerow(
                        {
                            "target": row.get("target"),
                            "template_name": row.get("template_name"),
                            "label": row.get("label"),
                            "d_total_target": row.get("d_total_target"),
                            "structure_tier_compound": row.get("structure_tier_compound"),
                            "s2_state_compound": row.get("s2_state_compound"),
                            "max_rel_delta_R_S1_Q": row.get("max_rel_delta_R_S1_Q"),
                            "max_rel_delta_R_S2_S1": row.get("max_rel_delta_R_S2_S1"),
                            "max_rel_delta_R_S3_S2": row.get("max_rel_delta_R_S3_S2"),
                        }
                    )


def main():
    parser = argparse.ArgumentParser(description="Run Ola2 compound generation from rules.")
    parser.add_argument("--rules-json", type=Path, required=True, help="wave2_compounds rules file.")
    args = parser.parse_args()
    run_from_rules(args.rules_json)


if __name__ == "__main__":
    main()
