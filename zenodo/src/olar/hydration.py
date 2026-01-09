"""Hydration helpers for Sweep S1 (DOF-only)."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from core.ids.hashing import hash_text, stable_dumps
from core.io.schema_validation import validate_theta_internal

DOF_DNA_FIELDS = (
    "dof_grade",
    "dof_family_id",
    "dof_family_friendly",
    "R_S1_Q",
    "R_S2_S1",
    "band_count",
    "rho_lock",
    "lock_quality_Q",
    "participation_entropy",
    "dominant_parity",
)


class BlockHydrationError(RuntimeError):
    """Raised when a block cannot be hydrated for sweep inputs."""


def build_hydrated_entity(
    entity: Dict[str, Any],
    blocks_by_id: Dict[str, Dict[str, Any]],
    dna_by_id: Dict[str, Dict[str, Any]],
    block_id_key: str = "block_id",
) -> Dict[str, Any]:
    assignment = entity.get("assignment") or {}
    block_ids = assignment.get("block_ids") or []
    if not isinstance(block_ids, list) or not block_ids:
        raise RuntimeError("Hydration requires assignment.block_ids list")
    edges = entity.get("edges") or []
    if not isinstance(edges, list):
        raise RuntimeError("Hydration requires edges list")

    node_inputs: List[Dict[str, Any]] = []
    theta_list: List[Dict[str, Any]] = []
    for idx, bid in enumerate(block_ids):
        block = blocks_by_id.get(str(bid))
        if not block:
            raise BlockHydrationError(f"Hydration missing block for {block_id_key}={bid}")
        dna = dna_by_id.get(str(bid))
        if not dna:
            raise BlockHydrationError(f"Hydration missing DNA for {block_id_key}={bid}")
        theta_internal = block.get("theta_internal")
        if not isinstance(theta_internal, dict) or not theta_internal:
            raise BlockHydrationError(f"Hydration missing theta_internal for {block_id_key}={bid}")
        try:
            validate_theta_internal(theta_internal)
        except ValueError as exc:
            raise BlockHydrationError(
                f"Hydration invalid theta_internal for {block_id_key}={bid}: {exc}"
            ) from exc
        try:
            json.dumps(theta_internal)
        except Exception as exc:
            raise BlockHydrationError(
                f"Hydration theta_internal not JSON-serializable for {block_id_key}={bid}"
            ) from exc
        genes_min = dna.get("genes_min")
        if not isinstance(genes_min, dict):
            genes_min = {}
        genes_min.setdefault("dof_grade", dna.get("dof_grade"))
        genes_min.setdefault("dof_family_id", dna.get("dof_family_id"))
        if not genes_min:
            genes_min = {field: dna.get(field) for field in DOF_DNA_FIELDS}
        node_inputs.append(
            {
                "node_index": idx,
                "block_id": block.get(block_id_key),
                "omega_ref": block.get("omega_ref"),
                "theta_internal": theta_internal,
                "origin_run_id": block.get("origin_run_id"),
                "dof_grade": dna.get("dof_grade"),
                "dof_family_id": dna.get("dof_family_id"),
                "genes_min": genes_min,
            }
        )
        theta_list.append(theta_internal)

    provenance = entity.get("provenance") or {}
    lineage = {
        "entity_id": entity.get("entity_id"),
        "source_eval_id": entity.get("source_eval_id"),
        "parent_ids": entity.get("parent_ids") or [],
    }
    theta_internal_digest = f"sha256:{hash_text(stable_dumps(theta_list))}"

    return {
        "entity_id": entity.get("entity_id"),
        "ola": entity.get("ola"),
        "template_name": entity.get("template_name"),
        "edges": edges,
        "canonical_node_order": entity.get("canonical_node_order"),
        "assignment": entity.get("assignment"),
        "parent_ids": entity.get("parent_ids"),
        "nodes": node_inputs,
        "engine_params_bin_id": entity.get("engine_params_bin_id"),
        "seed": entity.get("seed"),
        "provenance": {
            "blocks_hash": provenance.get("blocks_hash"),
            "dna_hash": provenance.get("dna_hash"),
            "block_id_key_used": provenance.get("block_id_key_used"),
        },
        "theta_internal_digest": theta_internal_digest,
        "topology": {"N": len(block_ids), "edges": edges},
        "lineage": lineage,
    }
