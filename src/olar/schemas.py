"""Schema helpers for DOFT recursive stack (V1)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


BLOCK_REQUIRED_FIELDS = (
    "block_id",
    "omega_ref",
    "dof_grade",
    "dof_family_id",
    "dof_family_friendly",
    "genes_min",
    "provenance",
)

THETA_INTERNAL_REQUIRED_FIELDS = (
    "schema_version",
    "modes",
)

ENTITY_REQUIRED_FIELDS = (
    "schema_version",
    "run_session_id",
    "timestamp_utc",
    "ola",
    "entity_id",
    "source_eval_id",
    "build_plan",
    "template_name",
    "edges",
    "canonical_node_order",
    "assignment",
    "parent_ids",
    "seed",
    "engine_params_bin_id",
    "metrics_summary",
    "tags_raw",
    "reasons_raw",
    "provenance",
)

ENTITY_REQUIRED_NESTED = {
    "assignment": ("block_ids", "block_key_used"),
}

EVALUATION_REQUIRED_FIELDS = (
    "schema_version",
    "run_session_id",
    "timestamp_utc",
    "ola",
    "role",
    "entity_id",
    "eval_id",
    "seed",
    "engine_params_bin_id",
    "engine_params",
    "metrics_raw",
    "tags_raw",
    "reasons_raw",
    "provenance",
)

EVALUATION_OPTIONAL_FIELDS: tuple[str, ...] = ()

EVALUATION_REQUIRED_NESTED: Dict[str, Iterable[str]] = {}

ATTEMPT_REQUIRED_FIELDS = (
    "schema_version",
    "run_session_id",
    "timestamp_utc",
    "ola",
    "role",
    "entity_id",
    "eval_id",
    "target",
    "build_plan",
    "template_name",
    "edges",
    "canonical_node_order",
    "assignment",
    "seed",
    "engine_params_bin_id",
    "engine_params",
    "metrics_raw",
    "tags_raw",
    "reasons_raw",
    "provenance",
)

ATTEMPT_REQUIRED_NESTED = {
    "assignment": ("block_ids", "block_key_used"),
}

GENOME_LAYER_REQUIRED_FIELDS = (
    "entity_id",
    "ola",
    "lineage",
    "genes_inherited",
    "genes_olaX",
    "robustness_score",
    "taxonomy_version",
    "taxonomy_kingdom",
    "taxonomy_family_id",
)


def missing_fields(record: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return [k for k in required if k not in record]


def validate_required(record: Dict[str, Any], required: Iterable[str]) -> Tuple[bool, List[str]]:
    missing = missing_fields(record, required)
    return (len(missing) == 0), missing


def validate_nested(record: Dict[str, Any], nested_required: Dict[str, Iterable[str]]) -> Tuple[bool, List[str]]:
    missing: List[str] = []
    for key, fields in nested_required.items():
        sub = record.get(key)
        if not isinstance(sub, dict):
            missing.append(key)
            continue
        for field in fields:
            if field not in sub:
                missing.append(f"{key}.{field}")
    return (len(missing) == 0), missing


def assert_required(record: Dict[str, Any], required: Iterable[str], nested: Dict[str, Iterable[str]] | None = None) -> None:
    ok, missing = validate_required(record, required)
    if nested:
        ok_nested, missing_nested = validate_nested(record, nested)
        missing.extend(missing_nested)
        ok = ok and ok_nested
    if not ok:
        raise ValueError(f"Missing required fields: {missing}")
