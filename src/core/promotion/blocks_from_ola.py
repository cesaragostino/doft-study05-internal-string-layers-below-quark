"""Promote OlaN entities into Ola(N+1) blocks (V1)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.ids.hashing import hash_file
from core.ids.time import utc_now_iso
from core.io.jsonl import iter_jsonl


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _resolve(path_str: Optional[str], base: Path) -> Optional[Path]:
    if not path_str:
        return None
    path = Path(path_str)
    if path.is_absolute():
        return path
    return base / path


def _as_float(val: Any) -> Optional[float]:
    try:
        f = float(val)
        if math.isfinite(f):
            return f
    except Exception:
        return None
    return None


def _load_blocks(blocks_path: Path, key_field: str = "block_id") -> Dict[str, Dict[str, Any]]:
    data = _load_json(blocks_path)
    if not isinstance(data, list):
        raise ValueError("simple_blocks.json must be a list.")
    blocks: Dict[str, Dict[str, Any]] = {}
    for row in data:
        if not isinstance(row, dict):
            continue
        key = row.get(key_field)
        if not key:
            continue
        blocks[str(key)] = row
    return blocks


def _load_genome_rows(genome_path: Path) -> Dict[str, Dict[str, Any]]:
    rows: Dict[str, Dict[str, Any]] = {}
    with genome_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            eid = row.get("entity_id")
            if not eid:
                continue
            rows[str(eid)] = row
    return rows


def _resolve_prev_blocks(
    run_inputs_path: Optional[Path],
    ola_from: int,
    blocks_prev_override: Optional[Path],
) -> Path:
    if blocks_prev_override is not None:
        return blocks_prev_override
    if run_inputs_path is None:
        raise ValueError("Missing --blocks-prev or --run-inputs.")
    run_inputs = _load_json(run_inputs_path)
    inputs = (run_inputs.get("inputs") or {}).get(f"ola{ola_from - 1}") or {}
    prev_path = inputs.get("simple_blocks_json")
    if not prev_path:
        raise ValueError(f"simple_blocks_json not found for ola{ola_from - 1} in run inputs.")
    return _resolve(str(prev_path), run_inputs_path.parent)  # type: ignore[arg-type]


def _build_nodes(
    block_ids: List[Any],
    blocks_by_id: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[float]]:
    nodes: List[Dict[str, Any]] = []
    omega_refs: List[float] = []
    for idx, block_id in enumerate(block_ids):
        block_key = str(block_id)
        block = blocks_by_id.get(block_key)
        if block is None:
            raise ValueError(f"Missing block_id in simple_blocks.json: {block_key}")
        omega_ref = _as_float(block.get("omega_ref"))
        if omega_ref is None:
            raise ValueError(f"Missing omega_ref in block {block_key}")
        theta_internal = block.get("theta_internal")
        if theta_internal is None:
            raise ValueError(f"Missing theta_internal in block {block_key}")
        nodes.append(
            {
                "node_index": idx,
                "source_block_id": block_key,
                "omega_ref": omega_ref,
                "theta_internal": theta_internal,
            }
        )
        omega_refs.append(omega_ref)
    return nodes, omega_refs


def promote_blocks(
    entities_path: Path,
    genome_path: Path,
    blocks_prev_path: Path,
    output_path: Path,
    dna_output_path: Optional[Path],
    ola_from: int,
    ola_to: int,
) -> int:
    entities_hash = f"sha256:{hash_file(entities_path)}"
    genome_hash = f"sha256:{hash_file(genome_path)}"
    blocks_prev_hash = f"sha256:{hash_file(blocks_prev_path)}"
    code_hash = f"sha256:{hash_file(Path(__file__))}"

    genome_rows = _load_genome_rows(genome_path)
    blocks_by_id = _load_blocks(blocks_prev_path)

    selected: List[Tuple[str, Dict[str, Any], Dict[str, Any]]] = []
    for entity in iter_jsonl(entities_path):
        eid = entity.get("entity_id")
        if not eid:
            continue
        genome_row = genome_rows.get(str(eid))
        if not genome_row:
            continue
        attractor_class = genome_row.get("attractor_class")
        evals_total = _as_float(genome_row.get("sweep_evals_total"))
        if attractor_class != "FUNCTIONAL_LOCK":
            continue
        if evals_total is None or int(evals_total) <= 0:
            continue
        selected.append((str(eid), entity, genome_row))

    selected.sort(key=lambda item: item[0])
    promoted: List[Dict[str, Any]] = []
    dna_rows: List[Dict[str, str]] = []
    for eid, entity, genome_row in selected:
        assignment = entity.get("assignment")
        if not isinstance(assignment, dict):
            raise ValueError(f"Entity {eid} missing assignment.")
        block_ids = assignment.get("block_ids")
        if not isinstance(block_ids, list):
            raise ValueError(f"Entity {eid} missing assignment.block_ids list.")
        block_key_used = assignment.get("block_key_used")
        if block_key_used != "block_id":
            raise ValueError(f"Entity {eid} block_key_used must be block_id.")
        template_name = entity.get("template_name")
        if not template_name:
            raise ValueError(f"Entity {eid} missing template_name.")
        edges = entity.get("edges")
        if not isinstance(edges, list):
            raise ValueError(f"Entity {eid} missing edges list.")
        canonical = entity.get("canonical_node_order")
        if not isinstance(canonical, list):
            raise ValueError(f"Entity {eid} missing canonical_node_order list.")
        if len(block_ids) != len(canonical):
            raise ValueError(f"Entity {eid} block_ids length mismatch with canonical_node_order.")

        nodes, omega_refs = _build_nodes(block_ids, blocks_by_id)
        omega_ref_proxy = _as_float(genome_row.get("omega_ref_proxy"))
        if omega_ref_proxy is None:
            omega_ref_proxy = sum(omega_refs) / len(omega_refs) if omega_refs else None
        if omega_ref_proxy is None or not math.isfinite(omega_ref_proxy):
            raise ValueError(f"Entity {eid} missing omega_ref_proxy.")

        # Contract: S6 ignores any *_friendly columns from genome layers.
        dof_grade = genome_row.get("dof_grade") or ""
        dof_family_id = genome_row.get("confirmed_family_id") or ""
        family_friendly = dof_family_id
        if not dof_family_id:
            print(f"[core_promotion] WARNING: Promoting block {eid} without family classification.")

        promoted.append(
            {
                "schema_version": "olar_block_v1",
                "ola_from": ola_from,
                "ola_to": ola_to,
                "block_id": eid,
                "omega_ref": omega_ref_proxy,
                "dof_grade": str(dof_grade),
                "dof_family_id": str(dof_family_id),
                "dof_family_friendly": str(family_friendly),
                "genes_min": {},
                "theta_internal": {
                    "template_name": entity.get("template_name"),
                    "edges": edges,
                    "nodes": nodes,
                },
                "provenance": {
                    "source_entity_id": eid,
                    "source_ola": ola_from,
                    "inputs": {
                        "entities_hash": entities_hash,
                        "genome_hash": genome_hash,
                        "blocks_prev_hash": blocks_prev_hash,
                    },
                    "code_hash": code_hash,
                    "timestamp_utc": utc_now_iso(),
                    "machine": {
                        "python": platform.python_version(),
                        "platform": platform.platform(),
                    },
                },
            }
        )
        dna_rows.append(
            {
                "block_id": eid,
                "dof_grade": str(dof_grade),
                "dof_family_id": str(dof_family_id),
                "dof_family_friendly": str(family_friendly),
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(promoted, indent=2, ensure_ascii=True))
    if dna_output_path is not None:
        dna_output_path.parent.mkdir(parents=True, exist_ok=True)
        with dna_output_path.open("w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["block_id", "dof_grade", "dof_family_id", "dof_family_friendly"]
            )
            writer.writeheader()
            writer.writerows(dna_rows)
    return len(promoted)


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote OlaN entities into Ola(N+1) blocks (V1).")
    parser.add_argument("--ola-from", type=int, required=True, help="Source Ola number.")
    parser.add_argument("--ola-to", type=int, required=True, help="Target Ola number.")
    parser.add_argument("--run-inputs", type=Path, help="Path to doft_run_inputs_v4.json.")
    parser.add_argument("--entities", type=Path, help="Override entities.jsonl path.")
    parser.add_argument("--genome", type=Path, help="Override genome_layers_olaN_taxonomy.csv path.")
    parser.add_argument("--blocks-prev", type=Path, help="Override simple_blocks.json from Ola(N-1).")
    parser.add_argument("--output", type=Path, help="Output blocks JSON path.")
    parser.add_argument("--dna-output", type=Path, help="Output dof_dna_catalog.csv path.")
    args = parser.parse_args()

    base_dir = Path.cwd()
    run_inputs_path = args.run_inputs
    if run_inputs_path is not None:
        base_dir = run_inputs_path.parent

    ola_from = args.ola_from
    ola_to = args.ola_to
    entities_path = args.entities or Path(f"data/processed/ola{ola_from}/catalog/entities.jsonl")
    genome_path = args.genome or Path(
        f"data/processed/ola{ola_from}/catalog/genome_layers_ola{ola_from}_taxonomy.csv"
    )
    blocks_prev_path = _resolve_prev_blocks(run_inputs_path, ola_from, args.blocks_prev)
    output_path = args.output or Path(f"data/processed/ola{ola_to}/inputs/blocks_from_ola{ola_from}.json")
    dna_output_path = args.dna_output or Path(
        f"data/processed/ola{ola_to}/inputs/dof_dna_catalog_from_ola{ola_from}.csv"
    )

    print("[core_promotion] Wiring Check:")
    print(f"- entities_jsonl={entities_path.resolve()}")
    print(f"- genome_layers_csv={genome_path.resolve()}")
    print(f"- blocks_prev_json={blocks_prev_path.resolve()}")
    print(f"- output_blocks_json={output_path.resolve()}")
    print(f"- output_dna_csv={dna_output_path.resolve()}")

    count = promote_blocks(
        entities_path=entities_path,
        genome_path=genome_path,
        blocks_prev_path=blocks_prev_path,
        output_path=output_path,
        dna_output_path=dna_output_path,
        ola_from=ola_from,
        ola_to=ola_to,
    )
    print(f"[core_promotion] promoted_blocks={count}")


if __name__ == "__main__":
    main()
