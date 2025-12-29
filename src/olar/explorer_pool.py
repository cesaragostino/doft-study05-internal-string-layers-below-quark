"""Explorer V4 pool/sampling layer (DOF-only)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _extract_blocks(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("blocks", "promoted_blocks"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        results = raw.get("results")
        if isinstance(results, dict) and isinstance(results.get("blocks"), list):
            return results["blocks"]
    return []


def load_simple_blocks(path: Path) -> List[Dict[str, Any]]:
    raw = _load_json(path)
    blocks = _extract_blocks(raw)
    if not blocks:
        raise RuntimeError(f"No blocks found in {path}")
    return blocks


def load_dna_catalog(path: Path, id_key: str = "block_id") -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        raise RuntimeError(f"DNA catalog missing: {path}")
    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise RuntimeError(f"DNA catalog empty: {path}")
    fieldnames = reader.fieldnames or []
    required_cols = {
        id_key,
        "dof_grade",
        "dof_family_id",
        "dof_family_friendly",
        "genes_min",
        "omega_ref_proxy",
    }
    missing_cols = sorted(col for col in required_cols if col not in fieldnames)
    if missing_cols:
        raise RuntimeError(f"DNA catalog missing columns: {missing_cols}")
    dna_map: Dict[str, Dict[str, Any]] = {}
    seen: set[str] = set()
    for row in rows:
        key = row.get(id_key)
        if key is None or key == "":
            raise RuntimeError(f"DNA catalog missing {id_key} value")
        key_str = str(key)
        if key_str in seen:
            raise RuntimeError(f"DNA catalog duplicate {id_key}: {key_str}")
        seen.add(key_str)
        dna_map[key_str] = row
    return dna_map


def build_block_pool(
    blocks: List[Dict[str, Any]],
    dna_map: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> List[Dict[str, Any]]:
    require_dna = bool(cfg.get("require_dna", True))
    block_id_key = str(cfg.get("block_id_key", "block_id"))
    allowed_grades = {str(g).upper() for g in (cfg.get("allowed_dof_grades") or [])}
    allowed_families = {str(f) for f in (cfg.get("allowed_family_ids") or [])}
    denied_families = {str(f) for f in (cfg.get("denied_family_ids") or [])}

    pool: List[Dict[str, Any]] = []
    for block in blocks:
        block_id = block.get(block_id_key)
        if block_id is None or block_id == "":
            if require_dna:
                raise RuntimeError(f"Missing {block_id_key} in simple_blocks.json (required for Explorer-1)")
            pool.append(block)
            continue
        dna = dna_map.get(str(block_id))
        if not dna:
            if require_dna:
                raise RuntimeError(f"Missing DNA for {block_id_key}={block_id}")
            pool.append(block)
            continue
        dof_grade = str(dna.get("dof_grade", "") or dna.get("dna_grade", "")).upper()
        dof_family_id = str(dna.get("dof_family_id", "") or "")
        dof_family_friendly = str(dna.get("dof_family_friendly", "") or "")
        if allowed_grades and dof_grade not in allowed_grades:
            continue
        if allowed_families and dof_family_id not in allowed_families:
            continue
        if denied_families and dof_family_id in denied_families:
            continue
        block = dict(block)
        block["genes_min"] = {
            "dof_grade": dof_grade,
            "dof_family_id": dof_family_id,
            "dof_family_friendly": dof_family_friendly,
        }
        pool.append(block)
    return pool
