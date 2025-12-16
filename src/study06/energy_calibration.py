"""Energy calibration for Ola1 blocks.

Selects the best reference block, computes K, writes calibration JSON,
and optionally enriches simple_blocks.json with mass_gev.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from study06.sm_matching import load_universe


def _to_float(val: Any) -> float | None:
    try:
        f = float(val)
    except Exception:
        return None
    return f if math.isfinite(f) else None


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"energy calibration: expected a list in {path}")
    return data


def _pick_reference_block(blocks: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], str]:
    """Pick best block by grade (A then B), d_total, tie-break by block_id."""

    def _candidates_for(grade: str) -> List[Tuple[float, str, Dict[str, Any]]]:
        rows: List[Tuple[float, str, Dict[str, Any]]] = []
        for b in blocks:
            if str(b.get("grade", "")).upper() != grade:
                continue
            ms = b.get("match_score") or {}
            if not bool(ms.get("has_enough_levels_full")):
                continue
            d_total = _to_float(ms.get("d_total"))
            if d_total is None:
                continue
            block_id = str(b.get("block_id", ""))
            rows.append((d_total, block_id, b))
        rows.sort(key=lambda x: (x[0], x[1]))
        return rows

    for grade in ("A", "B"):
        cands = _candidates_for(grade)
        if cands:
            return cands[0][2], grade
    raise ValueError("energy calibration: no hay bloque elegible para calibración (grades A/B con enough_levels_full).")


def _lookup_particle(universe_path: Path, particle_name: str) -> Dict[str, Any]:
    universe = load_universe(universe_path)
    catalog = universe.get("particles", universe)
    by_name = {p.get("name"): p for p in catalog if isinstance(p, dict)}
    if particle_name not in by_name:
        raise ValueError(
            f"energy calibration: particle_name '{particle_name}' from reference block not found in sm_universe"
        )
    return by_name[particle_name]


def _resolve_ref_mass(particle: Dict[str, Any]) -> float:
    mass = _to_float(particle.get("sm_mass_gev"))
    if mass is not None:
        return mass
    masses_raw = particle.get("masses_gev") or []
    masses = [_to_float(m) for m in masses_raw]
    masses = [m for m in masses if m is not None]
    if masses:
        return float(sum(masses) / len(masses))
    raise ValueError("energy calibration: reference particle lacks sm_mass_gev and masses_gev.")


def _write_calibration(
    output_path: Path,
    ref_block: Dict[str, Any],
    ref_mass: float,
    e_internal_ref: float,
    K: float,
    sm_universe_tag: str,
    selection_grade: str,
) -> None:
    payload = {
        "reference_block_id": ref_block.get("block_id"),
        "reference_particle_name": ref_block.get("particle_name"),
        "reference_family": ref_block.get("family"),
        "E_internal_ref": e_internal_ref,
        "m_ref_gev": ref_mass,
        "scale_K": K,
        "selection_criteria": {
            "min_grade": selection_grade,
            "require_enough_levels_full": True,
        },
        "sm_universe_source": sm_universe_tag,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2))


def _update_blocks_with_mass(blocks: List[Dict[str, Any]], K: float) -> int:
    updated = 0
    for blk in blocks:
        e_internal = _to_float(blk.get("internal_energy"))
        if e_internal is None:
            continue
        blk["mass_gev"] = K * e_internal
        updated += 1
    return updated


def main():
    parser = argparse.ArgumentParser(description="Compute Ola1 energy calibration constant K and enrich blocks.")
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/processed/ola1-chaos/simple_blocks.json"),
        help="Path to simple_blocks.json produced by Ola1 promotion.",
    )
    parser.add_argument(
        "--sm-universe",
        type=Path,
        required=True,
        help="Path to the chosen SM universe catalog JSON.",
    )
    parser.add_argument(
        "--sm-universe-tag",
        type=str,
        default=None,
        help="Optional tag recorded in the calibration payload (default: stem of sm-universe file).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ola1-chaos/energy_calibration.json"),
        help="Where to write the calibration artifact.",
    )
    parser.add_argument(
        "--write-mass-gev",
        action="store_true",
        default=True,
        help="Write/refresh mass_gev = K * internal_energy into simple_blocks.json.",
    )
    parser.add_argument(
        "--no-write-mass-gev",
        dest="write_mass_gev",
        action="store_false",
        help="Skip writing mass_gev into blocks.",
    )
    parser.add_argument(
        "--blocks-output",
        type=Path,
        default=None,
        help="Optional alternate output path for blocks when writing mass_gev (defaults to --blocks).",
    )
    args = parser.parse_args()

    blocks_path = args.blocks
    blocks = _load_blocks(blocks_path)

    ref_block, selected_grade = _pick_reference_block(blocks)
    e_internal_ref = _to_float(ref_block.get("internal_energy"))
    if e_internal_ref is None or e_internal_ref <= 0.0:
        raise ValueError("energy calibration: reference block missing/invalid internal_energy.")

    particle_name = ref_block.get("particle_name")
    if not particle_name:
        raise ValueError("energy calibration: reference block lacks particle_name.")
    particle = _lookup_particle(args.sm_universe, particle_name)
    m_ref_gev = _resolve_ref_mass(particle)

    K = m_ref_gev / e_internal_ref

    sm_tag = args.sm_universe_tag or args.sm_universe.stem
    _write_calibration(args.output, ref_block, m_ref_gev, e_internal_ref, K, sm_tag, selected_grade)
    print(
        f"[energy_calibration] ref_block={ref_block.get('block_id')} particle={particle_name} "
        f"E_internal={e_internal_ref:.6g} m_ref={m_ref_gev:.6g} K={K:.6g}"
    )

    if args.write_mass_gev:
        out_path = args.blocks_output or blocks_path
        updated = _update_blocks_with_mass(blocks, K)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(blocks, indent=2))
        print(f"[energy_calibration] wrote mass_gev for {updated} blocks -> {out_path}")


if __name__ == "__main__":
    main()
