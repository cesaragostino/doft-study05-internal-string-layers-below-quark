"""Bridge Ola3 blocks into Ola3 reloaded block format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _as_float(val: Any) -> float | None:
    try:
        return float(val)
    except Exception:
        return None


def _build_block(raw: Dict[str, Any]) -> Dict[str, Any]:
    species_id = raw.get("id") or raw.get("species_id") or raw.get("name")
    omega_eff = _as_float(raw.get("omega_eff")) or _as_float(raw.get("best_metrics", {}).get("omega_eff"))
    mass = _as_float(raw.get("mass")) or _as_float(raw.get("M_final")) or _as_float(raw.get("mass_gev"))
    lock_quality = raw.get("lock_quality") or {}
    if not lock_quality and raw.get("quality") is not None:
        qv = _as_float(raw.get("quality"))
        if qv is not None:
            lock_quality = {"Q": qv, "S1": 0.0, "S2": 0.0}
    return {
        "id": species_id,
        "block_id": species_id,
        "particle_name": raw.get("particle_name") or species_id,
        "family": raw.get("family") or "species",
        "mass": mass,
        "mass_units": raw.get("mass_units") or "GeV",
        "F_m": omega_eff,
        "f_m": omega_eff,
        "omega_eff": omega_eff,
        "lock_quality": lock_quality,
        "quality": raw.get("quality"),
        "origin_run_id": raw.get("source_run"),
        "composition": raw.get("composition") or raw.get("particles") or [],
        "seed_stability": raw.get("seed_stability"),
        "n_trials": raw.get("n_trials"),
        "n_viable": raw.get("n_viable"),
    }


def convert(input_path: Path, output_path: Path) -> int:
    data = _load_json(input_path)
    if not isinstance(data, list):
        raise ValueError("ola3_blocks.json debe ser una lista de bloques.")
    converted: List[Dict[str, Any]] = []
    for raw in data:
        if not isinstance(raw, dict):
            continue
        converted.append(_build_block(raw))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(converted, indent=2, ensure_ascii=True))
    return len(converted)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert ola3_blocks.json to legacy Ola2 blocks format.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/ola3/ola3_blocks.json"),
        help="Archivo ola3_blocks.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ola3/ola2_blocks_from_ola3.json"),
        help="Salida en formato legacy Ola2 blocks.",
    )
    args = parser.parse_args()
    count = convert(args.input, args.output)
    print(f"[ola2_blocks_from_ola3] escrito {args.output} ({count} blocks)")


if __name__ == "__main__":
    main()
